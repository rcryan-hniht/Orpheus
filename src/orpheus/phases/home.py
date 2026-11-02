from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Vertical
from textual.screen import Screen
from textual.widgets import Static

from orpheus.matrix import MatrixRain
from orpheus.models import PlaybackState, Track
from orpheus.phases.now_playing import format_progress_bar
from orpheus.title import AsciiTitle


class ShortcutBar(Static):
    """Dynamic minimalist bottom shortcut bar."""

    DEFAULT_CSS = """
    ShortcutBar {
        dock: bottom;
        width: 100%;
        height: 1;
        margin-bottom: 1;
        content-align: center middle;
        background: transparent;
    }
    """

    def __init__(
        self,
        is_playing: bool = False,
        accent_color: str = "#00ffcc",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.is_playing = is_playing
        self.accent_color = accent_color

    def set_playing(self, is_playing: bool) -> None:
        self.is_playing = is_playing
        self.refresh()

    def _get_colors(self) -> tuple[str, str]:
        accent = self.accent_color
        dim = "#a0a0a0"
        try:
            if hasattr(self.app, "current_theme") and self.app.current_theme:
                theme = self.app.current_theme
                is_dark = getattr(theme, "dark", True)
                theme_accent = getattr(theme, "accent", None) or getattr(theme, "primary", None)
                if theme_accent:
                    accent = str(theme_accent)
                dim = "#a0a0a0" if is_dark else "#555555"
        except Exception:
            pass
        return accent, dim

    def get_items(self) -> list[tuple[str, str]]:
        if self.is_playing:
            return [
                ("[?]", "Which key"),
                ("[p]", "Playing"),
                ("[S]", "Settings"),
                ("[f]", "Find"),
                ("[q]", "Quit"),
            ]
        return [
            ("[?]", "Which key"),
            ("[S]", "Settings"),
            ("[f]", "Find"),
            ("[q]", "Quit"),
        ]

    def render_text(self) -> str:
        parts: list[str] = []
        for bracket, label in self.get_items():
            parts.append(f"{bracket} {label}")
        return "    ".join(parts)

    def render(self) -> Text:
        text = Text()
        accent, dim = self._get_colors()
        items = self.get_items()
        for i, (bracket, label) in enumerate(items):
            text.append(bracket[0], style=f"bold {accent}")
            text.append(bracket[1:-1], style=f"bold {accent}")
            text.append(bracket[-1], style=f"bold {accent}")
            text.append(f" {label}", style=dim)
            if i < len(items) - 1:
                text.append("    ")
        return text


class HomePlayingWidget(Static):
    """Compact now playing status under the home title."""

    DEFAULT_CSS = """
    HomePlayingWidget {
        width: 100%;
        height: auto;
        content-align: center middle;
        margin-top: 1;
        background: transparent;
        display: none;
    }
    """

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.track: Track | None = None
        self.state: PlaybackState = PlaybackState()
        self.album: str | None = None

    def set_playback(
        self,
        track: Track | None,
        state: PlaybackState,
        album: str | None = None,
    ) -> None:
        self.track = track
        self.state = state
        self.album = album
        is_active = track is not None and not state.idle and not state.ended
        self.display = is_active
        if is_active:
            self.refresh()

    def _get_theme_styles(self) -> tuple[str, str, str]:
        accent = "#00ffcc"
        fg = "#ffffff"
        dim = "#a0a0a0"
        try:
            app = getattr(self, "app", None) or getattr(self, "_app", None)
            if app and hasattr(app, "current_theme") and app.current_theme:
                theme = app.current_theme
                is_dark = getattr(theme, "dark", True)
                accent = str(
                    getattr(theme, "accent", None) or getattr(theme, "primary", None) or "#00ffcc"
                )
                fg = str(getattr(theme, "foreground", "#ffffff" if is_dark else "#000000"))
                dim = "#a0a0a0" if is_dark else "#666666"
        except Exception:
            pass
        return accent, fg, dim

    def render(self) -> Text:
        if not self.track or self.state.idle or self.state.ended:
            return Text("")

        accent, fg, dim = self._get_theme_styles()
        track = self.track
        state = self.state

        # Line 1: Track Title and Artist
        line1 = Text()
        state_icon = "⏸ " if state.paused else "▶ "
        line1.append(state_icon, style=f"bold {accent}")
        line1.append(track.title, style=f"bold {fg}")
        if track.artist:
            line1.append(f" — {track.artist}", style="dim")

        # Line 2: Phase and Album / Source
        line2 = Text()
        line2.append("[Phase: Now Playing]", style=f"bold {accent}")
        if self.album:
            line2.append("  •  ", style="dim")
            line2.append(f"[Album: {self.album}]", style=f"bold {fg}")
        elif track.source:
            source_label = (
                "Online Search" if track.source == "deezer" else track.source.capitalize()
            )
            line2.append("  •  ", style="dim")
            line2.append(f"[{source_label}]", style="dim")

        # Line 3: Timeline status
        line3 = Text()
        pos = state.position
        dur = state.duration if state.duration > 0 else (track.duration or 0.0)
        pos_str = f"{int(pos // 60)}:{int(pos % 60):02d}"
        bar = format_progress_bar(pos, dur, width=24)
        if dur > 0:
            rem = max(0.0, dur - pos)
            rem_str = f"-{int(rem // 60)}:{int(rem % 60):02d}"
            line3.append(pos_str, style="dim")
            line3.append(f"  {bar}  ", style=f"{accent}")
            line3.append(rem_str, style="dim")
        else:
            line3.append(pos_str, style="dim")
            line3.append(f"  {bar}", style=f"{accent}")

        return Text("\n").join([line1, line2, line3])

    def on_click(self) -> None:
        try:
            app = getattr(self, "app", None) or getattr(self, "_app", None)
            if app and hasattr(app, "switch_phase"):
                app.switch_phase("now_playing")
        except Exception:
            pass


class HomeScreen(Screen):
    """Cyberpunk Home screen with Matrix rain, 3D ASCII title, and dynamic shortcut bar."""

    BINDINGS = [
        Binding("question_mark", "which_key", "Which key", priority=True),
        Binding("?", "which_key", "Which key", priority=True, show=False),
        Binding("space", "toggle_playback", "Play/Pause", priority=True, show=False),
        Binding("f", "find", "Find", priority=True),
        Binding("S", "settings", "Settings", priority=True),
        Binding("p", "now_playing", "Now Playing", priority=True),
        Binding("s", "stop", "Stop", priority=True, show=False),
        Binding("q", "quit", "Quit", priority=True),
    ]

    DEFAULT_CSS = """
    HomeScreen {
        layers: base top;
        width: 100%;
        height: 100%;
        background: ansi_default;
        overflow: hidden;
    }

    #home-matrix {
        layer: base;
        width: 100%;
        height: 100%;
        background: transparent;
    }

    #home-container {
        layer: top;
        width: 100%;
        height: 100%;
        background: transparent;
    }

    #home-title-box {
        width: 100%;
        height: 1fr;
        align: center middle;
        background: transparent;
    }

    #home-title {
        width: 100%;
        height: 6;
        content-align: center middle;
        background: transparent;
    }

    #home-now-playing {
        width: 100%;
        height: auto;
        content-align: center middle;
        margin-top: 1;
        background: transparent;
        display: none;
    }

    #home-shortcuts {
        dock: bottom;
        width: 100%;
        height: 1;
        margin-bottom: 1;
        content-align: center middle;
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

    def compose(self) -> ComposeResult:
        yield MatrixRain(id="home-matrix")
        with Vertical(id="home-container"):
            with Center(id="home-title-box"):
                yield AsciiTitle(id="home-title")
                yield HomePlayingWidget(id="home-now-playing")
            yield ShortcutBar(id="home-shortcuts")

    def set_playing_state(self, is_playing: bool) -> None:
        try:
            bar = self.query_one(ShortcutBar)
            bar.set_playing(is_playing)
        except Exception:
            pass

    def update_playback(
        self,
        track: Track | None,
        state: PlaybackState,
        album: str | None = None,
    ) -> None:
        try:
            bar = self.query_one(ShortcutBar)
            is_active = track is not None and not state.idle and not state.ended
            bar.set_playing(is_active)
            widget = self.query_one("#home-now-playing", HomePlayingWidget)
            widget.set_playback(track, state, album)
        except Exception:
            pass

    def on_screen_resume(self) -> None:
        app = getattr(self, "app", None) or getattr(self, "_app", None)
        if app:
            track = getattr(app, "current_track", None)
            playback = getattr(app, "playback", PlaybackState())
            album = getattr(app, "current_album", None)
            self.update_playback(track, playback, album)

    def action_find(self) -> None:
        if hasattr(self.app, "switch_phase"):
            self.app.switch_phase("search")

    def action_which_key(self) -> None:
        if hasattr(self.app, "action_which_key"):
            self.app.action_which_key()

    def action_settings(self) -> None:
        if hasattr(self.app, "action_settings"):
            self.app.action_settings()

    def action_now_playing(self) -> None:
        if hasattr(self.app, "switch_phase"):
            self.app.switch_phase("now_playing")

    async def action_stop(self) -> None:
        if hasattr(self.app, "action_stop"):
            res = self.app.action_stop()
            if hasattr(res, "__await__"):
                await res

    async def action_toggle_playback(self) -> None:
        if hasattr(self.app, "action_toggle_pause"):
            await self.app.action_toggle_pause()

    def action_quit(self) -> None:
        self.app.exit()
