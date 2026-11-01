"""Orpheus 3-phase Cyberpunk TUI application."""

from __future__ import annotations

import logging
from collections.abc import Callable
from pathlib import Path
from typing import Any

from textual.app import App
from textual.binding import Binding

from orpheus.albums import AlbumStore
from orpheus.glitch import GlitchOverlay
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
        Binding("space", "toggle_pause", "Play/Pause", show=False),
        Binding("s", "stop", "Stop", show=False),
        Binding("S", "settings", "Settings", show=False),
        Binding("f", "find", "Find", show=False),
    ]

    DEFAULT_CSS = """
    Screen {
        background: #050508;
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
        self.current_lyrics: Lyrics | None = None
        self.playback = PlaybackState()
        self.queue: list[Track] = []
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

        # Load local tracks
        self.run_worker(self._load_local_library, exclusive=True)

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
        """Switch operational phase with cyberpunk Glitch transition."""
        def apply_screen() -> None:
            if self.is_screen_installed(phase_name):
                self.switch_screen(phase_name)

        try:
            overlay = GlitchOverlay(duration_seconds=0.15, on_complete=apply_screen)
            self.screen.mount(overlay)
        except Exception:
            apply_screen()

    def play_resolved_track(self, track: Track) -> None:
        """Transition to Now Playing and resolve/stream audio without blocking UI."""
        self._generation += 1
        gen = self._generation
        self.current_track = track
        self.now_playing_screen.update_track(track, lyrics=None)
        self.home_screen.set_playing_state(True)
        self.switch_phase("now_playing")
        self.run_worker(self._async_resolve_and_play(track, gen), exclusive=False)

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
                    self.now_playing_screen.update_track(track, lyrics=lyrics)
            except Exception as exc:
                logger.warning("Lyrics error: %s", exc)

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
                track = self.current_track
                self.current_track = None
                if self.repeat_mode == "track":
                    self.play_resolved_track(track)
                elif self.queue:
                    next_t = self.queue.pop(0)
                    self.play_resolved_track(next_t)
                elif self.repeat_mode == "all" and self.local_tracks:
                    self.play_resolved_track(self.local_tracks[0])
                else:
                    self.home_screen.set_playing_state(False)
        except Exception:
            pass

    async def action_toggle_pause(self) -> None:
        if self.player:
            await self.player.toggle_pause()

    async def action_stop(self) -> None:
        if self.player:
            await self.player.stop()
        self.home_screen.set_playing_state(False)

    async def action_seek(self, delta: float) -> None:
        if self.player:
            new_pos = max(0.0, self.playback.position + delta)
            await self.player.seek(new_pos)

    async def action_prev(self) -> None:
        # If seek > 3s, restart current track
        if self.playback.position > 3.0 and self.player:
            await self.player.seek(0)
        elif self.queue:
            # Prev track from history if available
            pass

    async def action_next(self) -> None:
        if self.repeat_mode == "track" and self.current_track:
            self.play_resolved_track(self.current_track)
        elif self.queue:
            next_t = self.queue.pop(0)
            self.play_resolved_track(next_t)
        elif self.repeat_mode == "all" and self.local_tracks:
            self.play_resolved_track(self.local_tracks[0])

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
                stem_path = await self.separator.prepare(
                    self.current_track, rights_confirmed=True
                )
                if stem_path and self.player:
                    self._stem = stem_path
                    self._using_stem = True
                    await self.player.load(str(stem_path), start=self.playback.position)
            except Exception as exc:
                logger.warning("Karaoke error: %s", exc)

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
                        value=self.theme or "cyberpunk",
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
