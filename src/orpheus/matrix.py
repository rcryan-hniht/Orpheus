from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any

from rich.text import Text
from textual.widget import Widget

# Authentic Japanese Katakana characters and Matrix digits (no ugly math symbols)
KATAKANA = "ｦｱｳｴｵｶｷｹｺｻｼｽｾｿﾀﾂﾃﾅﾆﾇﾈﾊﾋﾎﾏﾐﾑﾒﾓﾔﾕﾗﾘﾜｲｸﾁﾄﾉﾌﾍﾎﾕﾖﾙﾚﾛﾝ0123456789"


def _hex_to_rgb(hex_str: str) -> tuple[int, int, int]:
    s = hex_str.lstrip("#")
    if len(s) == 3:
        s = "".join(c * 2 for c in s)
    try:
        return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
    except Exception:
        return (0, 255, 102)


def _rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{max(0, min(255, r)):02x}{max(0, min(255, g)):02x}{max(0, min(255, b)):02x}"


def _interpolate_color(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> str:
    r = int(c1[0] + (c2[0] - c1[0]) * t)
    g = int(c1[1] + (c2[1] - c1[1]) * t)
    b = int(c1[2] + (c2[2] - c1[2]) * t)
    return _rgb_to_hex(r, g, b)


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

    @property
    def safe_app(self) -> Any:
        try:
            return self.app
        except Exception:
            return getattr(self, "_app", None)

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled
        if enabled:
            if self.is_mounted and not self._timer:
                try:
                    self._timer = self.set_interval(0.08, self._tick)
                except Exception:
                    pass
            if not self.columns:
                self.setup_columns(self.size.width or 80, self.size.height or 24)
            if self.is_mounted:
                self.refresh()
        else:
            if self._timer:
                try:
                    self._timer.stop()
                except Exception:
                    pass
                self._timer = None

    def on_mount(self) -> None:
        self.setup_columns(self.size.width or 80, self.size.height or 24)
        if self.enabled and not self._timer:
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
        accent = "#00ff66"
        bg = "#000000"
        try:
            app = self.safe_app
            if app and hasattr(app, "current_theme") and app.current_theme:
                theme = app.current_theme
                is_dark = getattr(theme, "dark", True)
                theme_accent = getattr(theme, "accent", None)
                theme_primary = getattr(theme, "primary", None)
                accent = str(theme_accent or theme_primary or "#00ff66")
                bg = str(getattr(theme, "background", "#000000" if is_dark else "#ffffff"))
        except Exception:
            pass

        accent_rgb = _hex_to_rgb(accent)
        bg_rgb = _hex_to_rgb(bg)

        head_style = "bold #ffffff" if is_dark else "bold #000000"
        upper_style = f"bold {accent}"
        mid_style = _interpolate_color(accent_rgb, bg_rgb, 0.40)
        tail_style = _interpolate_color(accent_rgb, bg_rgb, 0.75)

        for col in self.columns:
            if not col.active or col.x >= w:
                continue
            int_head = int(col.head_y)
            for y, ch in col.tail:
                if 0 <= y < h:
                    if y == int_head:
                        style = head_style
                    elif y >= int_head - 2:
                        style = upper_style
                    elif y >= int_head - 6:
                        style = mid_style
                    else:
                        style = tail_style
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
