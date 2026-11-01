from __future__ import annotations

import math
import time
from typing import Any

import httpx
from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Static

from orpheus.art import (
    encode_kitty_graphics,
    get_kitty_delete_command,
    get_placeholder_art,
    render_half_blocks,
    supports_kitty_graphics,
)
from orpheus.lyrics import LyricLine, active_line, parse_lrc
from orpheus.models import Lyrics, PlaybackState, Track

_ART_CACHE: dict[str, str] = {}


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
    """Renders album cover art using native Kitty Graphics on Ghostty/Kitty or ANSI half-blocks."""

    DEFAULT_CSS = """
    AlbumArtWidget {
        width: 100%;
        height: auto;
        content-align: center top;
        margin-bottom: 1;
        background: transparent;
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
        self._raw_bytes: bytes | None = None
        self._half_blocks: str = ""
        self._loaded_url = ""

    def on_mount(self) -> None:
        self._update_art()

    def on_unmount(self) -> None:
        if supports_kitty_graphics():
            self._write_terminal(get_kitty_delete_command())

    def set_cover_url(self, url: str) -> None:
        if url != self._loaded_url:
            self.cover_url = url
            self._update_art()

    def _update_art(self) -> None:
        if not self.cover_url:
            self._raw_bytes = None
            self._half_blocks = get_placeholder_art(28, 12)
            if supports_kitty_graphics():
                self._write_terminal(get_kitty_delete_command())
            self.refresh()
            return

        self._loaded_url = self.cover_url
        self.app.call_later(self._async_fetch_cover, self.cover_url)

    async def _async_fetch_cover(self, url: str) -> None:
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(url)
                if url != self.cover_url:
                    return
                if resp.status_code == 200:
                    raw = resp.content
                    self._raw_bytes = raw
                    self._half_blocks = render_half_blocks(raw, max_width=30, max_height=14)
                    self.refresh()
                    if supports_kitty_graphics():
                        self.set_timer(0.05, self._draw_kitty)
                    return
        except Exception:
            pass
        if url == self.cover_url:
            self._raw_bytes = None
            self._half_blocks = get_placeholder_art(28, 12)
            self.refresh()

    def _draw_kitty(self) -> None:
        if not self.is_mounted or not self._raw_bytes or not supports_kitty_graphics():
            return
        region = self.region
        cols = max(10, min(32, region.width or 28))
        rows = max(6, min(14, region.height or 12))
        offset_x = max(0, (region.width - cols) // 2)
        x = max(1, region.x + 1 + offset_x)
        y = max(1, region.y + 1)
        kitty_seq = encode_kitty_graphics(self._raw_bytes, cols=cols, rows=rows)
        move_and_draw = f"\033[s\033[{y};{x}H{kitty_seq}\033[u"
        self._write_terminal(move_and_draw)

    def _write_terminal(self, data: str) -> None:
        try:
            if hasattr(self.app, "_driver") and hasattr(self.app._driver, "write"):
                self.app._driver.write(data)
            else:
                import sys

                sys.stdout.write(data)
                sys.stdout.flush()
        except Exception:
            pass

    def render(self) -> Text:
        if supports_kitty_graphics() and self._raw_bytes:
            # Ghostty/Kitty: reserve empty rectangular area so native image shows through
            self.app.call_later(self._draw_kitty)
            h = max(6, min(14, self.size.height or 12))
            w = max(10, min(32, self.size.width or 28))
            return Text(" " * w + ("\n" + " " * w) * (h - 1))
        # Non-Ghostty/Kitty fallback: ANSI half-blocks
        if not self._half_blocks:
            return Text.from_ansi(get_placeholder_art(28, 12))
        return Text.from_ansi(self._half_blocks)


class SyncedLyricsWidget(Static):
    """Auto-scrolling LRCLIB synchronized lyrics with active line highlighting."""

    DEFAULT_CSS = """
    SyncedLyricsWidget {
        width: 100%;
        height: 100%;
        padding: 1 2;
        content-align: center middle;
        text-align: center;
        background: transparent;
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
        self._is_loading = False

    def _get_accent(self) -> str:
        try:
            if hasattr(self.app, "current_theme") and self.app.current_theme:
                theme_accent = getattr(self.app.current_theme, "accent", None)
                if theme_accent:
                    return str(theme_accent)
                theme_primary = getattr(self.app.current_theme, "primary", None)
                if theme_primary:
                    return str(theme_primary)
        except Exception:
            pass
        return "#00ffcc"

    def set_loading(self, loading: bool = True) -> None:
        self._is_loading = loading
        self.refresh()

    def set_lyrics(self, lyrics: Lyrics | None) -> None:
        self.lyrics = lyrics
        self._is_loading = False
        if lyrics and lyrics.synced:
            self.parsed_lines = parse_lrc(lyrics.synced)
        else:
            self.parsed_lines = []
        self.refresh()

    def set_position(self, seconds: float) -> None:
        self.current_position = seconds
        self.refresh()

    def render(self) -> Text:
        accent = self._get_accent()
        text = Text(justify="center")
        if self._is_loading:
            text.append("Loading lyrics...\n", style="italic #505050")
            return text

        if not self.lyrics or (not self.lyrics.synced and not self.lyrics.plain):
            text.append("No lyrics available for this track\n", style="italic #606060")
            return text

        if not self.parsed_lines:
            # Plain lyrics fallback
            if self.lyrics.plain:
                for line in self.lyrics.plain.splitlines():
                    text.append(line + "\n", style="#c0c0c0")
            else:
                text.append("No lyrics available for this track\n", style="italic #606060")
            return text

        active_idx = active_line(self.parsed_lines, self.current_position)

        # Intro indicator
        if active_idx < 0:
            text.append("• • •\n\n", style=f"bold {accent}")
        else:
            text.append("• • •\n\n", style="#404040")

        # Window of visible lines around active line
        window_size = max(16, (self.size.height or 18) - 4)
        start_idx = max(0, active_idx - (window_size // 2))
        end_idx = min(len(self.parsed_lines), start_idx + window_size)

        for i in range(start_idx, end_idx):
            line = self.parsed_lines[i]
            if not line.text.strip():
                text.append("\n")
                continue
            if i == active_idx:
                text.append(f"▶  {line.text}  ◀\n", style=f"bold {accent}")
            else:
                text.append(f"{line.text}\n", style="dim")

        return text


class CavaVisualizer(Static):
    """Dynamic Cava-like audio spectrum visualizer bar placed under the timeline."""

    BARS = (" ", " ", "▂", "▃", "▄", "▅", "▆", "▇", "█")

    DEFAULT_CSS = """
    CavaVisualizer {
        height: 1;
        width: 100%;
        content-align: center middle;
        margin-top: 1;
        background: transparent;
    }
    """

    def __init__(
        self,
        num_bars: int = 32,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.num_bars = num_bars
        self.is_playing = False
        self.is_paused = False
        self._heights: list[float] = [0.0] * num_bars
        self._t: float = 0.0
        self._timer = None

    def on_mount(self) -> None:
        self._timer = self.set_interval(0.08, self._tick)

    def set_playback(self, is_playing: bool, is_paused: bool) -> None:
        was_playing = self.is_playing and not self.is_paused
        self.is_playing = is_playing
        self.is_paused = is_paused
        now_playing = self.is_playing and not self.is_paused
        if was_playing != now_playing:
            self.refresh()

    def reset(self) -> None:
        self._heights = [0.0] * self.num_bars
        self._t = 0.0
        self.refresh()

    def _tick(self) -> None:
        if not self.is_playing:
            changed = False
            for i in range(self.num_bars):
                if self._heights[i] > 0.0:
                    self._heights[i] = max(0.0, self._heights[i] - 0.8)
                    changed = True
            if changed:
                self.refresh()
            return

        if self.is_paused:
            changed = False
            for i in range(self.num_bars):
                target = 0.8 if (i % 2 == 0) else 0.4
                if abs(self._heights[i] - target) > 0.1:
                    if self._heights[i] > target:
                        self._heights[i] = max(target, self._heights[i] - 0.6)
                    else:
                        self._heights[i] = min(target, self._heights[i] + 0.3)
                    changed = True
            if changed:
                self.refresh()
            return

        self._t += 0.08
        t = self._t
        # 124 BPM bass rhythm pulse
        beat = (max(0.0, math.sin(t * 2.06 * math.pi * 2))) ** 6

        for i in range(self.num_bars):
            norm = i / max(1, self.num_bars - 1)
            bass = beat * math.exp(-4.2 * norm) * 7.6
            mids = (math.sin(t * 4.6 + i * 0.42) * 0.5 + 0.5) * math.sin(norm * math.pi) * 5.4
            treble = (math.cos(t * 8.2 - i * 0.75) * 0.5 + 0.5) * (norm**1.35) * 4.0
            jitter = (math.sin(t * 16.0 + i * 2.1) * 0.5 + 0.5) * 1.2

            target = max(0.4, min(8.0, bass + mids + treble + jitter))
            if target > self._heights[i]:
                self._heights[i] = target
            else:
                self._heights[i] = max(0.0, self._heights[i] - 0.7)

        self.refresh()

    def _get_theme_styles(self) -> tuple[str, str, bool]:
        accent = "#00ffcc"
        fg = "#ffffff"
        is_dark = True
        try:
            if hasattr(self.app, "current_theme") and self.app.current_theme:
                theme = self.app.current_theme
                is_dark = getattr(theme, "dark", True)
                theme_accent = getattr(theme, "accent", None) or getattr(theme, "primary", None)
                if theme_accent:
                    accent = str(theme_accent)
                fg = str(getattr(theme, "foreground", "#ffffff" if is_dark else "#0b2545"))
        except Exception:
            pass
        return accent, fg, is_dark

    def render(self) -> Text:
        accent, _fg, _is_dark = self._get_theme_styles()
        text = Text()

        if not self.is_playing:
            for _ in range(self.num_bars):
                text.append(" ", style=f"dim {accent}")
            return text

        if self.is_paused:
            for h in self._heights:
                idx = min(8, int(round(h)))
                text.append(self.BARS[idx], style=f"dim {accent}")
            return text

        for h in self._heights:
            idx = min(8, int(round(h)))
            char = self.BARS[idx]
            if idx >= 6:
                text.append(char, style=f"bold {accent}")
            elif idx >= 1:
                text.append(char, style=f"{accent}")
            else:
                text.append(char, style=f"dim {accent}")

        return text


class NowPlayingFooter(Static):
    """Dynamic shortcut footer for Now Playing."""

    DEFAULT_CSS = """
    NowPlayingFooter {
        height: 1;
        width: 100%;
        content-align: center middle;
        margin-top: 1;
        background: transparent;
    }
    """

    def _get_accent(self) -> str:
        try:
            if hasattr(self.app, "current_theme") and self.app.current_theme:
                theme_accent = getattr(self.app.current_theme, "accent", None)
                if theme_accent:
                    return str(theme_accent)
                theme_primary = getattr(self.app.current_theme, "primary", None)
                if theme_primary:
                    return str(theme_primary)
        except Exception:
            pass
        return "#00ffcc"

    def render(self) -> Text:
        accent = self._get_accent()
        text = Text()
        items = [
            ("[?]", "Which key"),
            ("[space]", "Play/Pause"),
            ("→/←", "Seek"),
            ("Shift+→/←", "Next/Prev"),
            ("[r]", "Repeat"),
            ("[k]", "Karaoke"),
            ("[f]", "Find"),
            ("[S]", "Settings"),
            ("[q]", "Quit"),
            ("[Esc]", "Home"),
        ]
        for i, (k, desc) in enumerate(items):
            text.append(k, style=f"bold {accent}")
            text.append(f" {desc}", style="#808080")
            if i < len(items) - 1:
                text.append("    ")
        return text


class NowPlayingScreen(Screen):
    """Now Playing phase with 2-column layout: Art/Controls + Synced Lyrics."""

    BINDINGS = [
        Binding("question_mark", "which_key", "Which key", priority=True),
        Binding("?", "which_key", "Which key", priority=True, show=False),
        Binding("space", "toggle_playback", "Play/Pause", priority=True),
        Binding("s", "stop", "Stop", priority=True, show=False),
        Binding("left", "seek_backward", "Seek -5s", priority=True),
        Binding("right", "seek_forward", "Seek +5s", priority=True),
        Binding("shift+left", "prev_track", "Previous", priority=True),
        Binding("shift+right", "next_track", "Next", priority=True),
        Binding("r", "toggle_repeat", "Repeat", priority=True),
        Binding("k", "toggle_karaoke", "Karaoke", priority=True),
        Binding("f", "find", "Find", priority=True),
        Binding("S", "settings", "Settings", priority=True),
        Binding("q", "quit", "Quit", priority=True),
        Binding("escape", "go_home", "Home", priority=True),
    ]

    DEFAULT_CSS = """
    NowPlayingScreen {
        width: 100%;
        height: 100%;
        background: ansi_default;
        layout: vertical;
        padding: 1 2;
        overflow: hidden;
    }

    #now-playing-columns {
        width: 100%;
        height: 1fr;
    }

    #left-col {
        width: 44;
        height: 100%;
        border-right: solid $panel;
        padding: 0 1;
        align: center top;
        background: transparent;
        overflow-y: hidden;
    }

    #right-col {
        width: 1fr;
        height: 100%;
        padding: 0 1;
        background: transparent;
    }

    #track-title {
        text-style: bold;
        color: $foreground;
        content-align: center middle;
    }

    #track-artist-album {
        color: $accent;
        content-align: center middle;
        margin-bottom: 1;
    }

    #progress-container {
        height: 1;
        width: 100%;
        content-align: center middle;
        color: $foreground;
    }

    #np-cava {
        height: 1;
        width: 100%;
        content-align: center middle;
        margin-top: 1;
        background: transparent;
    }

    #badges-bar {
        height: 1;
        width: 100%;
        content-align: center middle;
        margin-top: 1;
        color: $accent;
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
                yield CavaVisualizer(id="np-cava")
                yield Static("", id="badges-bar")

            with Vertical(id="right-col"):
                yield SyncedLyricsWidget(id="np-lyrics")

        yield NowPlayingFooter(id="np-footer")

    def update_track(
        self, track: Track | None, lyrics: Lyrics | None = None, is_loading: bool = False
    ) -> None:
        self.current_track = track
        try:
            art_w = self.query_one("#np-album-art", AlbumArtWidget)
            art_w.set_cover_url(track.cover_url if track else "")
            title_text = track.title if track else "No Track Playing"
            self.query_one("#track-title", Static).update(title_text)
            artist_album = f"{track.artist} — {track.album}" if track else ""
            self.query_one("#track-artist-album", Static).update(artist_album)
            lyrics_w = self.query_one("#np-lyrics", SyncedLyricsWidget)
            if is_loading:
                lyrics_w.set_loading(True)
            else:
                lyrics_w.set_lyrics(lyrics)
            cava_w = self.query_one("#np-cava", CavaVisualizer)
            cava_w.reset()
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
            badges_text = f"{state_icon}   {repeat_badge}   {karaoke_badge}"
            self.query_one("#badges-bar", Static).update(badges_text)

            cava_w = self.query_one("#np-cava", CavaVisualizer)
            is_active = not state.idle and (state.position > 0 or not state.paused)
            cava_w.set_playback(is_playing=is_active, is_paused=state.paused)

            lyrics_w = self.query_one("#np-lyrics", SyncedLyricsWidget)
            lyrics_w.set_position(pos)
        except Exception:
            pass

    def calc_seek_delta(self, direction: str, now: float | None = None) -> float:
        """Calculate seek delta: single tap = ±5s, rapid double-tap (<=350ms) = ±10s."""
        current_time = time.monotonic() if now is None else now
        is_double = self._last_tap_dir == direction and (current_time - self._last_tap_time) <= 0.35
        self._last_tap_time = current_time
        self._last_tap_dir = direction
        return 10.0 if is_double else 5.0

    @property
    def safe_app(self) -> Any:
        try:
            return self.app
        except Exception:
            return getattr(self, "_app", None)

    async def action_seek_forward(self) -> None:
        delta = self.calc_seek_delta("forward")
        app = self.safe_app
        if app and hasattr(app, "action_seek"):
            res = app.action_seek(delta)
            if hasattr(res, "__await__"):
                await res

    async def action_seek_backward(self) -> None:
        delta = self.calc_seek_delta("backward")
        app = self.safe_app
        if app and hasattr(app, "action_seek"):
            res = app.action_seek(-delta)
            if hasattr(res, "__await__"):
                await res

    async def action_toggle_playback(self) -> None:
        app = self.safe_app
        if app and hasattr(app, "action_toggle_pause"):
            res = app.action_toggle_pause()
            if hasattr(res, "__await__"):
                await res

    async def action_stop(self) -> None:
        app = self.safe_app
        if app and hasattr(app, "action_stop"):
            res = app.action_stop()
            if hasattr(res, "__await__"):
                await res

    async def action_prev_track(self) -> None:
        app = self.safe_app
        if app and hasattr(app, "action_prev"):
            res = app.action_prev()
            if hasattr(res, "__await__"):
                await res

    async def action_next_track(self) -> None:
        app = self.safe_app
        if app and hasattr(app, "action_next"):
            res = app.action_next()
            if hasattr(res, "__await__"):
                await res

    def action_toggle_repeat(self) -> None:
        modes = ["off", "track", "all"]
        idx = (modes.index(self.repeat_mode) + 1) % len(modes)
        self.repeat_mode = modes[idx]
        app = self.safe_app
        if app and hasattr(app, "set_repeat_mode"):
            app.set_repeat_mode(self.repeat_mode)
        self.update_playback_state(self._playback_state)

    async def action_toggle_karaoke(self) -> None:
        self.karaoke_enabled = not self.karaoke_enabled
        app = self.safe_app
        if app and hasattr(app, "action_karaoke"):
            res = app.action_karaoke()
            if hasattr(res, "__await__"):
                await res
        self.update_playback_state(self._playback_state)

    def action_settings(self) -> None:
        app = self.safe_app
        if app and hasattr(app, "action_settings"):
            app.action_settings()

    def action_find(self) -> None:
        app = self.safe_app
        if app and hasattr(app, "switch_phase"):
            app.switch_phase("search")

    def action_quit(self) -> None:
        app = self.safe_app
        if app and hasattr(app, "exit"):
            app.exit()

    def action_go_home(self) -> None:
        app = self.safe_app
        if app and hasattr(app, "switch_phase"):
            app.switch_phase("home")

    def action_which_key(self) -> None:
        app = self.safe_app
        if app and hasattr(app, "action_which_key"):
            app.action_which_key()
