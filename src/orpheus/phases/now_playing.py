from __future__ import annotations

import time
from typing import Any

import httpx
from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Static

from orpheus.art import get_placeholder_art, render_half_blocks
from orpheus.lyrics import LyricLine, active_line, parse_lrc
from orpheus.models import Lyrics, PlaybackState, Track


def format_progress_bar(position: float, duration: float, width: int = 24) -> str:
    """Render a slim cyberpunk progress bar (━━━●────)."""
    if duration <= 0 or width <= 2:
        return "─" * width

    fraction = max(0.0, min(1.0, position / duration))
    knob_idx = int(fraction * (width - 1))

    parts: list[str] = []
    for i in range(width):
        if i < knob_idx:
            parts.append("━")
        elif i == knob_idx:
            parts.append("●")
        else:
            parts.append("─")
    return "".join(parts)


class AlbumArtWidget(Static):
    """Renders album cover art using Kitty Graphics Protocol or ANSI half-block downsampling."""

    DEFAULT_CSS = """
    AlbumArtWidget {
        width: 100%;
        height: auto;
        content-align: center middle;
        margin-bottom: 1;
    }
    """

    def __init__(
        self,
        cover_url: str = "",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.cover_url = cover_url
        self._rendered_art = ""
        self._loaded_url = ""

    def on_mount(self) -> None:
        self._update_art()

    def set_cover_url(self, url: str) -> None:
        if url != self._loaded_url:
            self.cover_url = url
            self._update_art()

    def _update_art(self) -> None:
        if not self.cover_url:
            self._rendered_art = get_placeholder_art(28, 12)
            self.refresh()
            return

        self._loaded_url = self.cover_url
        # Fetch cover image in background task
        self.app.call_later(self._async_fetch_cover, self.cover_url)

    async def _async_fetch_cover(self, url: str) -> None:
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    raw = resp.content
                    self._rendered_art = render_half_blocks(raw, max_width=28, max_height=12)
                    self.refresh()
                    return
        except Exception:
            pass
        self._rendered_art = get_placeholder_art(28, 12)
        self.refresh()

    def render(self) -> Text:
        if not self._rendered_art:
            return Text.from_ansi(get_placeholder_art(28, 12))
        return Text.from_ansi(self._rendered_art)


class SyncedLyricsWidget(Static):
    """Auto-scrolling LRCLIB synchronized lyrics with active line highlighting."""

    DEFAULT_CSS = """
    SyncedLyricsWidget {
        width: 100%;
        height: 100%;
        padding: 1 2;
    }
    """

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.lyrics: Lyrics | None = None
        self.parsed_lines: list[LyricLine] = []
        self.current_position = 0.0

    def set_lyrics(self, lyrics: Lyrics | None) -> None:
        self.lyrics = lyrics
        if lyrics and lyrics.synced:
            self.parsed_lines = parse_lrc(lyrics.synced)
        else:
            self.parsed_lines = []
        self.refresh()

    def set_position(self, pos: float) -> None:
        self.current_position = pos
        self.refresh()

    def render(self) -> Text:
        text = Text()
        if not self.lyrics:
            text.append("Loading lyrics...\n", style="italic #606060")
            return text

        if not self.parsed_lines:
            # Plain lyrics fallback
            if self.lyrics.plain:
                for line in self.lyrics.plain.splitlines():
                    text.append(line + "\n", style="#c0c0c0")
            else:
                text.append("No lyrics available\n", style="italic #606060")
            return text

        active_idx = active_line(self.parsed_lines, self.current_position)

        # Intro indicator
        if active_idx < 0:
            text.append("• • •\n\n", style="bold #00ffcc")
        else:
            text.append("• • •\n\n", style="#404040")

        # Window of visible lines around active line
        window_size = max(5, (self.size.height or 18) - 4)
        start_idx = max(0, active_idx - (window_size // 2))
        end_idx = min(len(self.parsed_lines), start_idx + window_size)

        for i in range(start_idx, end_idx):
            line = self.parsed_lines[i]
            if i == active_idx:
                text.append(f"▶  {line.text}\n", style="bold #00ffcc on #0c1815")
            elif i < active_idx:
                text.append(f"   {line.text}\n", style="#505050")
            else:
                text.append(f"   {line.text}\n", style="#909090")

        return text


class NowPlayingScreen(Screen):
    """Now Playing phase with 2-column layout: Art/Controls + Synced Lyrics."""

    BINDINGS = [
        Binding("space", "toggle_playback", "Play/Pause", priority=True),
        Binding("left", "seek_backward", "Seek -5s", priority=True),
        Binding("right", "seek_forward", "Seek +5s", priority=True),
        Binding("shift+left", "prev_track", "Previous", priority=True),
        Binding("shift+right", "next_track", "Next", priority=True),
        Binding("r", "toggle_repeat", "Repeat", priority=True),
        Binding("k", "toggle_karaoke", "Karaoke", priority=True),
        Binding("escape", "go_home", "Home", priority=True),
    ]

    DEFAULT_CSS = """
    NowPlayingScreen {
        width: 100%;
        height: 100%;
        background: #05050a;
        layout: vertical;
        padding: 1 2;
    }

    #now-playing-columns {
        width: 100%;
        height: 1fr;
    }

    #left-col {
        width: 44;
        height: 100%;
        border-right: solid #1a1a2e;
        padding-right: 2;
    }

    #right-col {
        width: 1fr;
        height: 100%;
        padding-left: 2;
    }

    #track-title {
        text-style: bold;
        color: #ffffff;
        content-align: center middle;
    }

    #track-artist-album {
        color: #00ffcc;
        content-align: center middle;
        margin-bottom: 1;
    }

    #progress-container {
        height: 1;
        width: 100%;
        content-align: center middle;
    }

    #badges-bar {
        height: 1;
        width: 100%;
        content-align: center middle;
        margin-top: 1;
    }

    #np-footer {
        height: 1;
        width: 100%;
        color: #606060;
        content-align: center middle;
        margin-top: 1;
    }
    """

    def __init__(
        self,
        current_track: Track | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.current_track = current_track
        self.repeat_mode = "off"  # "off" | "track" | "all"
        self.karaoke_enabled = False
        self._last_tap_time = 0.0
        self._last_tap_dir = ""
        self._playback_state = PlaybackState()

    def compose(self) -> ComposeResult:
        with Horizontal(id="now-playing-columns"):
            with Vertical(id="left-col"):
                yield AlbumArtWidget(
                    cover_url=self.current_track.cover_url if self.current_track else "",
                    id="np-album-art",
                )
                yield Static(
                    self.current_track.title if self.current_track else "No Track Playing",
                    id="track-title",
                )
                artist_album = (
                    f"{self.current_track.artist} — {self.current_track.album}"
                    if self.current_track
                    else ""
                )
                yield Static(artist_album, id="track-artist-album")
                yield Static("", id="progress-container")
                yield Static("", id="badges-bar")

            with Vertical(id="right-col"):
                yield SyncedLyricsWidget(id="np-lyrics")

        yield Static(
            "[space] play/pause  →/← seek  Shift+→/← next/prev  "
            "[r] repeat  [k] karaoke  [esc] back",
            id="np-footer",
        )

    def update_track(self, track: Track | None, lyrics: Lyrics | None = None) -> None:
        self.current_track = track
        try:
            art_w = self.query_one("#np-album-art", AlbumArtWidget)
            art_w.set_cover_url(track.cover_url if track else "")
            title_text = track.title if track else "No Track Playing"
            self.query_one("#track-title", Static).update(title_text)
            artist_album = f"{track.artist} — {track.album}" if track else ""
            self.query_one("#track-artist-album", Static).update(artist_album)
            lyrics_w = self.query_one("#np-lyrics", SyncedLyricsWidget)
            lyrics_w.set_lyrics(lyrics)
        except Exception:
            pass

    def update_playback_state(self, state: PlaybackState) -> None:
        self._playback_state = state
        try:
            pos = state.position
            dur = state.duration
            pos_str = f"{int(pos // 60)}:{int(pos % 60):02d}"
            rem = max(0.0, dur - pos)
            rem_str = f"-{int(rem // 60)}:{int(rem % 60):02d}"
            bar = format_progress_bar(pos, dur, width=20)
            self.query_one("#progress-container", Static).update(f"{pos_str}  {bar}  {rem_str}")

            repeat_badge = f"[Repeat: {self.repeat_mode.capitalize()}]"
            karaoke_badge = f"[Karaoke: {'On' if self.karaoke_enabled else 'Off'}]"
            state_icon = "⏸" if state.paused else "▶"
            vol = int(state.volume)
            badges_text = f"{state_icon}   {repeat_badge}   {karaoke_badge}   Vol: {vol}%"
            self.query_one("#badges-bar", Static).update(badges_text)

            lyrics_w = self.query_one("#np-lyrics", SyncedLyricsWidget)
            lyrics_w.set_position(pos)
        except Exception:
            pass

    def calc_seek_delta(self, direction: str, now: float | None = None) -> float:
        """Calculate seek delta: single tap = ±5s, rapid double-tap (<=350ms) = ±10s."""
        current_time = time.monotonic() if now is None else now
        is_double = (
            self._last_tap_dir == direction
            and (current_time - self._last_tap_time) <= 0.35
        )
        self._last_tap_time = current_time
        self._last_tap_dir = direction
        return 10.0 if is_double else 5.0

    @property
    def safe_app(self) -> Any:
        try:
            return self.app
        except Exception:
            return None

    def action_seek_forward(self) -> None:
        delta = self.calc_seek_delta("forward")
        app = self.safe_app
        if app and hasattr(app, "action_seek"):
            app.action_seek(delta)

    def action_seek_backward(self) -> None:
        delta = self.calc_seek_delta("backward")
        app = self.safe_app
        if app and hasattr(app, "action_seek"):
            app.action_seek(-delta)

    def action_toggle_playback(self) -> None:
        app = self.safe_app
        if app and hasattr(app, "action_toggle_pause"):
            app.action_toggle_pause()

    def action_prev_track(self) -> None:
        app = self.safe_app
        if app and hasattr(app, "action_prev"):
            app.action_prev()

    def action_next_track(self) -> None:
        app = self.safe_app
        if app and hasattr(app, "action_next"):
            app.action_next()

    def action_toggle_repeat(self) -> None:
        modes = ["off", "track", "all"]
        idx = (modes.index(self.repeat_mode) + 1) % len(modes)
        self.repeat_mode = modes[idx]
        app = self.safe_app
        if app and hasattr(app, "set_repeat_mode"):
            app.set_repeat_mode(self.repeat_mode)
        self.update_playback_state(self._playback_state)

    def action_toggle_karaoke(self) -> None:
        self.karaoke_enabled = not self.karaoke_enabled
        app = self.safe_app
        if app and hasattr(app, "action_karaoke"):
            app.action_karaoke()
        self.update_playback_state(self._playback_state)

    def action_go_home(self) -> None:
        app = self.safe_app
        if app and hasattr(app, "switch_phase"):
            app.switch_phase("home")
