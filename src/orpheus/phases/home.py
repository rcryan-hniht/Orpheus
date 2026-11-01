from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Vertical
from textual.screen import Screen
from textual.widgets import Static

from orpheus.matrix import MatrixRain
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
                ("[p]", "Playing"),
                ("[s]", "Stop"),
                ("[S]", "Settings"),
                ("[f]", "Find"),
                ("[q]", "Quit"),
            ]
        return [
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


class HomeScreen(Screen):
    """Cyberpunk Home screen with Matrix rain, 3D ASCII title, and dynamic shortcut bar."""

    BINDINGS = [
        Binding("f", "find", "Find", priority=True),
        Binding("S", "settings", "Settings", priority=True),
        Binding("p", "now_playing", "Now Playing", priority=True),
        Binding("s", "stop", "Stop", priority=True),
        Binding("q", "quit", "Quit", priority=True),
    ]

    DEFAULT_CSS = """
    HomeScreen {
        layers: base top;
        width: 100%;
        height: 100%;
        background: $background;
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
            yield ShortcutBar(id="home-shortcuts")

    def set_playing_state(self, is_playing: bool) -> None:
        try:
            bar = self.query_one(ShortcutBar)
            bar.set_playing(is_playing)
        except Exception:
            pass

    def action_find(self) -> None:
        if hasattr(self.app, "switch_phase"):
            self.app.switch_phase("search")

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

    def action_quit(self) -> None:
        self.app.exit()
