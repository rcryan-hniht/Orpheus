from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Center, Middle
from textual.screen import Screen
from textual.widgets import Static

from orpheus.matrix import MatrixRain
from orpheus.title import AsciiTitle


class ShortcutBar(Static):
    """Dynamic minimalist bottom/central shortcut bar."""

    DEFAULT_CSS = """
    ShortcutBar {
        width: 100%;
        height: 3;
        content-align: center middle;
        margin-top: 2;
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
        items = self.get_items()
        for i, (bracket, label) in enumerate(items):
            text.append(bracket[0], style=f"bold {self.accent_color}")
            text.append(bracket[1:-1], style=f"bold {self.accent_color}")
            text.append(bracket[-1], style=f"bold {self.accent_color}")
            text.append(f" {label}", style="#a0a0a0")
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
        width: 100%;
        height: 100%;
        background: #050508;
    }

    #home-center {
        width: 100%;
        height: 100%;
        layer: top;
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
        with Middle(id="home-center"):
            with Center():
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
