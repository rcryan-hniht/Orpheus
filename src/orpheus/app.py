"""Orpheus 3-phase Cyberpunk TUI application."""

from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

from textual.app import App
from textual.binding import Binding

from orpheus.albums import AlbumStore
from orpheus.lyrics import LyricsService
from orpheus.models import Lyrics, PlaybackState, Track
from orpheus.phases.home import HomeScreen
from orpheus.phases.now_playing import NowPlayingScreen
from orpheus.phases.search import SearchScreen
from orpheus.player import MpvPlayer
from orpheus.resolver import AudioResolver, DeezerProvider
from orpheus.settings import SettingGroup, SettingItem, SettingsModal
from orpheus.themes import DEFAULT_THEME, PRESET_LABELS, get_themes

logger = logging.getLogger(__name__)


class OrpheusApp(App[None]):
    """Orpheus cyberpunk terminal music player."""

    TITLE = "ORPHEUS"

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", priority=True),
        Binding("question_mark", "which_key", "Which key", priority=True),
        Binding("?", "which_key", "Which key", priority=True, show=False),
        Binding("space", "toggle_pause", "Play/Pause", show=False),
        Binding("s", "stop", "Stop", show=False),
        Binding("S", "settings", "Settings", show=False),
        Binding("f", "find", "Find", show=False),
    ]

    DEFAULT_CSS = """
    App {
        background: ansi_default;
    }
    Screen {
        background: ansi_default;
        overflow: hidden;
    }
    """

    def __init__(
        self,
        *,
        providers: dict[str, Any] | None = None,
        player: MpvPlayer | None = None,
        database: Any = None,
        lyrics: LyricsService | None = None,
        separator: Any = None,
        music_dir: Path | str | None = None,
        theme: str | None = None,
        browser_opener: Callable[[str], bool] | None = None,
        auto_update: bool = True,
    ) -> None:
        super().__init__()
        self.providers = providers or {}
        self.player = player
        self.database = database
        self.lyrics_service = lyrics
        self.separator = separator
        self.music_dir = Path(music_dir or Path.home() / "Music")
        self.browser_opener = browser_opener or (lambda url: True)
        self._auto_update = auto_update

        # Storage & resolvers
        self.album_store = AlbumStore(self.database) if self.database else None
        self.audio_resolver = AudioResolver()
        self.deezer_provider = DeezerProvider()

        # Audio state
        self.current_track: Track | None = None
        self.current_album: str | None = None
        self.last_played_track: Track | None = None
        self.last_album: str | None = None
        self.current_lyrics: Lyrics | None = None
        self.playback = PlaybackState()
        self.queue: list[Track] = []
        self.history: list[Track] = []
        self.local_tracks: list[Track] = []
        self.repeat_mode = "off"
        self._generation = 0
        self._poll_timer = None
        self._stem: Path | None = None
        self._using_stem = False

        # Theme
        supported = {slug for slug, _ in PRESET_LABELS}
        saved = self.database.get_theme() if self.database else None
        self._initial_theme = (
            theme if theme in supported else saved if saved in supported else DEFAULT_THEME
        )

    def on_mount(self) -> None:
        for t in get_themes():
            self.register_theme(t)
        self.theme = self._initial_theme
        if self.database:
            self.database.set_theme(self._initial_theme)

        # Load local tracks and initialize mpv
        self.run_worker(self._load_local_library, exclusive=True)
        self.run_worker(self._init_player, exclusive=False)

        # Screens
        self.home_screen = HomeScreen()
        self.search_screen = SearchScreen(
            deezer_provider=self.deezer_provider, local_tracks=self.local_tracks
        )
        self.now_playing_screen = NowPlayingScreen(current_track=self.current_track)

        self.install_screen(self.home_screen, name="home")
        self.install_screen(self.search_screen, name="search")
        self.install_screen(self.now_playing_screen, name="now_playing")

        self.push_screen("home")
        self._poll_timer = self.set_interval(0.5, self.poll_player)

    def watch_theme(self, old_theme: str | None, new_theme: str | None) -> None:
        if new_theme and self.database:
            self.database.set_theme(new_theme)
        try:
            self.screen.refresh(layout=True)
        except Exception:
            pass

    async def _init_player(self) -> None:
        if self.player and hasattr(self.player, "start"):
            try:
                await self.player.start()
            except Exception as exc:
                logger.warning("Could not auto-start mpv on startup: %s", exc)

    async def _load_local_library(self) -> None:
        if "local" in self.providers:
            try:
                tracks = await self.providers["local"].search("")
                self.local_tracks = tracks
                self.search_screen.local_tracks = tracks
                try:
                    self.search_screen._populate_local_table()
                except Exception:
                    pass
            except Exception as exc:
                logger.warning("Local scan error: %s", exc)

    def switch_phase(self, phase_name: str) -> None:
        """Switch operational phase directly and cleanly."""
        if phase_name != "now_playing":
            from orpheus.art import get_kitty_delete_command, supports_kitty_graphics

            if supports_kitty_graphics():
                try:
                    if hasattr(self, "_driver") and hasattr(self._driver, "write"):
                        self._driver.write(get_kitty_delete_command())
                except Exception:
                    pass

        if self.is_screen_installed(phase_name):
            self.switch_screen(phase_name)

    def load_playlist_and_play(
        self,
        track: Track,
        queue: list[Track] | None = None,
        history: list[Track] | None = None,
        album: str | None = None,
    ) -> None:
        """Load track list into queue and history, and start playing selected track."""
        self.current_album = album or ("playlist" if queue else None)
        self.queue = list(queue or [])
        self.history = list(history or [])
        self.play_resolved_track(track)

    def is_single_track_album(self) -> bool:
        alb = self.current_album or getattr(self, "last_album", None)
        if alb and self.album_store:
            tracks = self.album_store.get_album_tracks(alb)
            if tracks:
                return len(tracks) == 1
        return len(self.queue) == 0 and len(self.history) == 0

    def play_resolved_track(self, track: Track) -> None:
        """Transition to Now Playing and resolve/stream audio without blocking UI."""
        self.last_played_track = track
        self.last_album = self.current_album
        is_changing_track = self.current_track is not None and self.current_track != track
        if self.current_track and self.current_track != track:
            if not self.history or self.history[-1] != self.current_track:
                self.history.append(self.current_track)

        # Check if track belongs to an album in custom album store if album not already set
        if not self.current_album and self.album_store:
            found = self.album_store.find_album_for_track(track.id)
            if found:
                alb_name, alb_tracks = found
                self.current_album = alb_name
                for i, t in enumerate(alb_tracks):
                    if t.id == track.id:
                        self.queue = list(alb_tracks[i + 1 :])
                        break

        # If not in any album and user did not specify an album queue, stop after this track
        if not self.current_album:
            self.queue = []

        self._generation += 1
        gen = self._generation
        self.current_track = track
        self.now_playing_screen.update_track(track, lyrics=None, is_loading=True)
        self.home_screen.set_playing_state(True)
        self.switch_phase("now_playing")
        if is_changing_track and self.player:
            self.run_worker(self._silence_player_for_new_track(), exclusive=False)
        self.run_worker(self._async_resolve_and_play(track, gen), exclusive=False)

    async def _silence_player_for_new_track(self) -> None:
        if self.player:
            try:
                await self.player.stop()
            except Exception:
                pass

    async def _async_resolve_and_play(self, track: Track, gen: int) -> None:
        try:
            stream_url, source = await self.audio_resolver.resolve_stream_url(track)
            if gen != self._generation:
                return
            if self.player:
                await self.player.load(stream_url)
        except Exception as exc:
            logger.error("Failed to resolve audio: %s", exc)

        # Fetch lyrics
        if self.lyrics_service:
            try:
                lyrics = await self.lyrics_service.get(track)
                if gen == self._generation:
                    self.current_lyrics = lyrics
                    self.now_playing_screen.update_track(track, lyrics=lyrics, is_loading=False)
            except Exception as exc:
                logger.warning("Lyrics error: %s", exc)
                if gen == self._generation:
                    self.now_playing_screen.update_track(track, lyrics=None, is_loading=False)

    async def poll_player(self) -> None:
        if not self.player:
            return
        try:
            state = await self.player.snapshot()
            self.playback = state
            is_active = not state.idle and (state.position > 0 or not state.paused)
            self.home_screen.set_playing_state(is_active)
            self.now_playing_screen.update_playback_state(state)

            # Auto-advance when track ended
            if state.ended and self.current_track:
                ended_t = self.current_track
                self.last_played_track = ended_t
                self.last_album = self.current_album
                if not self.history or self.history[-1] != ended_t:
                    self.history.append(ended_t)
                self.current_track = None
                if self.is_single_track_album() and self.repeat_mode != "track":
                    await self.action_stop()
                elif self.repeat_mode == "track":
                    self.play_resolved_track(ended_t)
                elif self.current_album and self.queue:
                    # Switch to next song in the album
                    next_t = self.queue.pop(0)
                    self.play_resolved_track(next_t)
                elif self.current_album and self.repeat_mode == "all" and self.album_store:
                    album_tracks = self.album_store.get_album_tracks(self.current_album)
                    if album_tracks:
                        self.queue = list(album_tracks[1:])
                        self.play_resolved_track(album_tracks[0])
                    else:
                        self.current_album = None
                        await self.action_stop()
                else:
                    # If not in an album or album finished -> STOP!
                    self.current_album = None
                    self.queue = []
                    await self.action_stop()
        except Exception:
            pass

    async def action_toggle_pause(self) -> None:
        # If playback is stopped / ended or idle, and we have a last_played_track, replay it!
        is_inactive = (
            self.playback.idle
            or self.playback.ended
            or self.current_track is None
            or (self.playback.position <= 0.0 and self.playback.paused)
        )
        if is_inactive and getattr(self, "last_played_track", None) is not None:
            track = self.last_played_track
            alb = getattr(self, "last_album", None)
            if alb and self.album_store:
                alb_tracks = self.album_store.get_album_tracks(alb)
                q = alb_tracks[1:] if len(alb_tracks) > 1 else []
                self.load_playlist_and_play(track, queue=q, album=alb)
            else:
                self.play_resolved_track(track)
            return

        if self.player:
            await self.player.toggle_pause()

    async def action_stop(self) -> None:
        if self.player:
            await self.player.stop()
        self.current_album = None
        self.queue = []
        self.playback = PlaybackState(idle=True)
        self.home_screen.set_playing_state(False)
        try:
            if hasattr(self.now_playing_screen, "cava_bar"):
                self.now_playing_screen.cava_bar.set_playback(False, False)
                self.now_playing_screen.cava_bar.reset()
            self.now_playing_screen.update_playback_state(self.playback)
        except Exception:
            pass

    async def action_seek(self, delta: float) -> None:
        if self.is_single_track_album():
            return
        if self.player:
            new_pos = max(0.0, self.playback.position + delta)
            await self.player.seek(new_pos)

    async def action_prev(self) -> None:
        if self.is_single_track_album():
            return
        # If seek > 3s, restart current track
        if self.playback.position > 3.0 and self.player:
            await self.player.seek(0)
            return
        if self.history:
            prev_track = self.history.pop()
            if self.current_track:
                self.queue.insert(0, self.current_track)
            self._generation += 1
            gen = self._generation
            self.current_track = prev_track
            self.now_playing_screen.update_track(prev_track, lyrics=None)
            self.home_screen.set_playing_state(True)
            self.switch_phase("now_playing")
            self.run_worker(self._async_resolve_and_play(prev_track, gen), exclusive=False)
        elif self.player:
            await self.player.seek(0)

    async def action_next(self) -> None:
        if self.is_single_track_album():
            return
        if self.repeat_mode == "track" and self.current_track:
            self.play_resolved_track(self.current_track)
        elif self.current_album and self.queue:
            if self.current_track:
                self.history.append(self.current_track)
            next_t = self.queue.pop(0)
            self._generation += 1
            gen = self._generation
            self.current_track = next_t
            self.now_playing_screen.update_track(next_t, lyrics=None)
            self.home_screen.set_playing_state(True)
            self.switch_phase("now_playing")
            self.run_worker(self._async_resolve_and_play(next_t, gen), exclusive=False)
        elif self.current_album and self.repeat_mode == "all" and self.album_store:
            album_tracks = self.album_store.get_album_tracks(self.current_album)
            if album_tracks:
                self.queue = list(album_tracks[1:])
                self.play_resolved_track(album_tracks[0])
            else:
                await self.action_stop()
        elif self.queue:
            if self.current_track:
                self.history.append(self.current_track)
            next_t = self.queue.pop(0)
            self.play_resolved_track(next_t)
        else:
            await self.action_stop()

    def set_repeat_mode(self, mode: str) -> None:
        self.repeat_mode = mode

    async def action_karaoke(self) -> None:
        if not self.separator or not self.current_track:
            return
        if self._using_stem and self.current_track:
            # Switch back to original
            self._using_stem = False
            self.play_resolved_track(self.current_track)
        else:
            try:
                stem_path = await self.separator.prepare(self.current_track, rights_confirmed=True)
                if stem_path and self.player:
                    self._stem = stem_path
                    self._using_stem = True
                    await self.player.load(str(stem_path), start=self.playback.position)
            except Exception as exc:
                logger.warning("Karaoke error: %s", exc)

    def action_which_key(self) -> None:
        """Open Which Key shortcuts reference modal."""
        from orpheus.which_key import WhichKeyModal

        self.push_screen(WhichKeyModal())

    def action_settings(self) -> None:
        """Open floating cyberpunk settings modal."""
        groups = [
            SettingGroup(
                title="Appearance",
                items=[
                    SettingItem(
                        key="theme",
                        label="Color Theme",
                        kind="select",
                        options=[slug for slug, _ in PRESET_LABELS],
                        value=self.theme or DEFAULT_THEME,
                    ),
                    SettingItem(
                        key="matrix_rain",
                        label="Matrix Rain",
                        kind="toggle",
                        options=[True, False],
                        value=True,
                    ),
                    SettingItem(
                        key="title_anim",
                        label="Title Animation",
                        kind="select",
                        options=["Pulse", "Wave", "None"],
                        value="Pulse",
                    ),
                ],
            ),
            SettingGroup(
                title="Audio Source",
                items=[
                    SettingItem(
                        key="source_order",
                        label="Source Order",
                        kind="select",
                        options=["YouTube -> Jamendo", "Jamendo -> YouTube"],
                        value="YouTube -> Jamendo",
                    ),
                    SettingItem(
                        key="quality",
                        label="Audio Quality",
                        kind="select",
                        options=["Best", "Medium"],
                        value="Best",
                    ),
                ],
            ),
        ]

        def on_change(key: str, val: Any) -> None:
            if key == "theme":
                self.theme = val
            elif key == "matrix_rain":
                try:
                    matrix = self.home_screen.query_one("#home-matrix")
                    matrix.enabled = bool(val)
                except Exception:
                    pass
            elif key == "title_anim":
                try:
                    title = self.home_screen.query_one("#home-title")
                    title.animation = str(val)
                except Exception:
                    pass

        modal = SettingsModal(groups=groups, on_change=on_change)
        self.push_screen(modal)

    def action_find(self) -> None:
        self.switch_phase("search")

    async def close(self) -> None:
        if self._poll_timer:
            self._poll_timer.stop()
        if self.player:
            await self.player.close()
        if self.deezer_provider:
            await self.deezer_provider.close()
        if self.lyrics_service:
            await self.lyrics_service.close()
        if self.separator and hasattr(self.separator, "close"):
            await self.separator.close()
        for p in self.providers.values():
            if hasattr(p, "close"):
                await p.close()
        if self.database:
            self.database.close()
