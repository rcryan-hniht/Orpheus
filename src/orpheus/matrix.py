from __future__ import annotations

import random
from dataclasses import dataclass, field

from rich.text import Text
from textual.widget import Widget

# Authentic Japanese Katakana characters and Matrix digits (no ugly math symbols)
KATAKANA = "ｦｱｳｴｵｶｷｹｺｻｼｽｾｿﾀﾂﾃﾅﾆﾇﾈﾊﾋﾎﾏﾐﾑﾒﾓﾔﾕﾗﾘﾜｲｸﾁﾄﾉﾌﾍﾎﾕﾖﾙﾚﾛﾝ0123456789"


@dataclass
class MatrixColumn:
    x: int
    head_y: float = -1.0
    speed: float = 1.0
    length: int = 12
    active: bool = False
    tail: list[tuple[int, str]] = field(default_factory=list)


class MatrixRain(Widget):
    """Full-screen cyber Matrix rain background widget."""

    DEFAULT_CSS = """
    MatrixRain {
        width: 100%;
        height: 100%;
        background: transparent;
    }
    """

    def __init__(
        self,
        density: float = 0.20,
        enabled: bool = True,
        speed_factor: float = 1.0,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.density = density
        self.enabled = enabled
        self.speed_factor = speed_factor
        self.columns: list[MatrixColumn] = []
        self._cur_width = 80
        self._cur_height = 24
        self._timer = None

    def on_mount(self) -> None:
        self.setup_columns(self.size.width or 80, self.size.height or 24)
        if self.enabled:
            self._timer = self.set_interval(0.08, self._tick)

    def on_resize(self) -> None:
        w = max(10, self.size.width)
        h = max(5, self.size.height)
        self.setup_columns(w, h)

    def setup_columns(self, width: int, height: int) -> None:
        self._cur_width = width
        self._cur_height = height
        cols: list[MatrixColumn] = []
        for x in range(width):
            col = MatrixColumn(
                x=x,
                head_y=random.uniform(-height, 0),
                speed=random.uniform(0.6, 1.4) * self.speed_factor,
                length=random.randint(6, max(7, height // 2)),
                active=random.random() < self.density,
            )
            cols.append(col)
        self.columns = cols

    def step(self) -> None:
        h = self._cur_height
        for col in self.columns:
            if not col.active:
                if random.random() < self.density * 0.1:
                    col.active = True
                    col.head_y = 0.0
                    col.speed = random.uniform(0.6, 1.4) * self.speed_factor
                    col.length = random.randint(6, max(7, h // 2))
                    col.tail = []
                continue

            col.head_y += col.speed
            int_y = int(col.head_y)

            # Update tail
            if not col.tail or col.tail[-1][0] != int_y:
                char = random.choice(KATAKANA)
                col.tail.append((int_y, char))

            # Dynamic matrix character mutation during rain
            if random.random() < 0.08 and col.tail:
                idx = random.randint(0, len(col.tail) - 1)
                col.tail[idx] = (col.tail[idx][0], random.choice(KATAKANA))

            # Trim tail
            cutoff = int_y - col.length
            col.tail = [(y, c) for y, c in col.tail if y > cutoff and y < h]

            # If head is past screen and tail is empty, deactivate
            if int_y - col.length >= h:
                col.active = False
                col.tail = []
                col.head_y = -1.0

    def _tick(self) -> None:
        if self.enabled:
            self.step()
            self.refresh()

    def render(self) -> Text:
        w = self._cur_width
        h = self._cur_height

        # Build grid
        grid: list[list[tuple[str, str]]] = [[(" ", "default") for _ in range(w)] for _ in range(h)]

        is_dark = True
        try:
            if hasattr(self.app, "current_theme") and self.app.current_theme:
                is_dark = getattr(self.app.current_theme, "dark", True)
        except Exception:
            pass
        head_style = "bold #ffffff" if is_dark else "bold #003311"

        for col in self.columns:
            if not col.active or col.x >= w:
                continue
            int_head = int(col.head_y)
            for y, ch in col.tail:
                if 0 <= y < h:
                    if y == int_head:
                        # Head character: bright glowing white on dark, dark forest green on light
                        style = head_style
                    elif y >= int_head - 2:
                        # Upper tail: electric neon green
                        style = "bold #00ff66"
                    elif y >= int_head - 6:
                        # Mid tail: authentic matrix green
                        style = "#00cc55"
                    else:
                        # Tail end: deep dark cyber green
                        style = "#005522"
                    grid[y][col.x] = (ch, style)

        text = Text()
        for row in range(h):
            row_text = Text()
            for col_idx in range(w):
                ch, style = grid[row][col_idx]
                row_text.append(ch, style=style)
            text.append_text(row_text)
            if row < h - 1:
                text.append("\n")
        return text
