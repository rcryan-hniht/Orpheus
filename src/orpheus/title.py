from __future__ import annotations

import math

from rich.text import Text
from textual.widget import Widget

RAW_TITLE_LINES = [
    r" ▄████▄  ██████╗ ██████╗ ██   ██ ███████╗██   ██ ███████╗",
    r"██▒   ██ ██   ██ ██   ██ ██   ██ ██      ██   ██ ██      ",
    r"██    ██ ██████╔ ██████╔ ███████ █████   ██   ██ ███████╗",
    r"██░   ██ ██   ██ ██      ██   ██ ██      ██   ██      ██ ",
    r" ▀████▀  ██   ██ ██      ██   ██ ███████╗ ▀████▀  ███████╝",
]


def get_title_lines(
    style: str = "pulse", frame: int = 0, accent_color: str = "cyan"
) -> list[str]:
    """Return stylized ASCII title lines with optional Wave/Pulse effects."""
    lines: list[str] = []
    style_lower = style.lower()

    for row_idx, raw_line in enumerate(RAW_TITLE_LINES):
        out_chars: list[str] = []
        for col_idx, ch in enumerate(raw_line):
            if ch == " ":
                out_chars.append(" ")
                continue

            if style_lower == "pulse":
                # Sweep brightness across characters horizontally
                phase = (col_idx - frame * 1.5) % 30
                if phase < 6:
                    out_chars.append("█" if ch in "█▀▄" else ch)
                elif phase < 12:
                    out_chars.append("▓" if ch in "█" else ch)
                else:
                    out_chars.append(ch)
            elif style_lower == "wave":
                # Vertical wave brightness offset
                wave_val = math.sin((col_idx * 0.3) + (frame * 0.2))
                if wave_val > 0.4:
                    out_chars.append("█" if ch in "█▀▄" else ch)
                elif wave_val > -0.2:
                    out_chars.append("▒" if ch in "█" else ch)
                else:
                    out_chars.append("░" if ch in "█" else ch)
            else:
                out_chars.append(ch)
        lines.append("".join(out_chars))
    return lines


class AsciiTitle(Widget):
    """Large 3D block-pixel ORPHEUS title with dynamic animation."""

    DEFAULT_CSS = """
    AsciiTitle {
        width: 100%;
        height: 6;
        content-align: center middle;
    }
    """

    def __init__(
        self,
        animation: str = "pulse",
        accent_color: str = "cyan",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.animation = animation
        self.accent_color = accent_color
        self._frame = 0
        self._timer = None

    def on_mount(self) -> None:
        if self.animation.lower() != "none":
            self._timer = self.set_interval(0.1, self._tick)

    def _tick(self) -> None:
        self._frame = (self._frame + 1) % 100
        self.refresh()

    def render_frame(self, width: int = 80) -> str:
        lines = get_title_lines(self.animation, self._frame, self.accent_color)
        centered_lines = [line.center(width) for line in lines]
        return "\n".join(centered_lines)

    def render(self) -> Text:
        w = max(60, self.size.width)
        lines = get_title_lines(self.animation, self._frame, self.accent_color)
        text = Text()
        for i, line in enumerate(lines):
            padding = max(0, (w - len(line)) // 2)
            styled_line = Text(" " * padding)
            styled_line.append(line, style=f"bold {self.accent_color}")
            text.append_text(styled_line)
            if i < len(lines) - 1:
                text.append("\n")
        return text
