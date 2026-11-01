from __future__ import annotations

import math

from rich.text import Text
from textual.widget import Widget

RAW_TITLE_LINES = [
    r" ██████╗  ██████╗  ██████╗  ██╗  ██╗ ███████╗ ██╗   ██╗ ███████╗",
    r"██╔═══██╗ ██╔══██╗ ██╔══██╗ ██║  ██║ ██╔════╝ ██║   ██║ ██╔════╝",
    r"██║   ██║ ██████╔╝ ██████╔╝ ███████║ █████╗   ██║   ██║ ███████╗",
    r"██║   ██║ ██╔══██╗ ██╔═══╝  ██╔══██║ ██╔══╝   ██║   ██║ ╚════██║",
    r"╚██████╔╝ ██║  ██║ ██║      ██║  ██║ ███████╗ ╚██████╔╝ ███████║",
    r" ╚═════╝  ╚═╝  ╚═╝ ╚═╝      ╚═╝  ╚═╝ ╚══════╝  ╚═════╝  ╚══════╝",
]


def get_title_lines(style: str = "pulse", frame: int = 0, accent_color: str = "cyan") -> list[str]:
    """Return stylized ASCII title lines with optional Wave/Pulse effects."""
    lines: list[str] = []
    style_lower = style.lower()

    for _row_idx, raw_line in enumerate(RAW_TITLE_LINES):
        out_chars: list[str] = []
        for col_idx, ch in enumerate(raw_line):
            if ch == " ":
                out_chars.append(" ")
                continue

            if style_lower == "pulse":
                phase = (col_idx - frame * 2) % 36
                if phase < 6:
                    out_chars.append("█" if ch in "█" else ch)
                elif phase < 12:
                    out_chars.append("▓" if ch in "█" else ch)
                else:
                    out_chars.append(ch)
            elif style_lower == "wave":
                wave_val = math.sin((col_idx * 0.3) + (frame * 0.2))
                if wave_val > 0.4:
                    out_chars.append("█" if ch in "█" else ch)
                elif wave_val > -0.2:
                    out_chars.append("▒" if ch in "█" else ch)
                else:
                    out_chars.append("░" if ch in "█" else ch)
            else:
                out_chars.append(ch)
        lines.append("".join(out_chars))
    return lines


class AsciiTitle(Widget):
    """3D ORPHEUS ASCII title with dynamic theme accent and sweep animation."""

    DEFAULT_CSS = """
    AsciiTitle {
        width: 100%;
        height: 6;
        content-align: center middle;
        background: transparent;
    }
    """

    def __init__(
        self,
        animation: str = "pulse",
        accent_color: str = "#00ffcc",
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

    def _get_palette(self) -> tuple[str, str, str, str]:
        accent = self.accent_color
        highlight = "bold #ffffff"
        mid = f"bold {accent}"
        base = f"{accent}"
        try:
            if hasattr(self.app, "current_theme") and self.app.current_theme:
                theme = self.app.current_theme
                is_dark = getattr(theme, "dark", True)
                theme_accent = getattr(theme, "accent", None) or getattr(theme, "primary", None)
                if theme_accent:
                    accent = str(theme_accent)
                theme_fg = getattr(theme, "foreground", None)
                theme_sec = getattr(theme, "secondary", None)
                if is_dark:
                    highlight = "bold #ffffff"
                    mid = f"bold {accent}"
                    base = f"{accent}"
                else:
                    # Light theme: use dark contrast color, never #ffffff which disappears!
                    highlight = f"bold {theme_sec or theme_fg or '#000000'}"
                    mid = f"bold {accent}"
                    base = f"{accent}"
        except Exception:
            pass
        return accent, highlight, mid, base

    def render_frame(self, width: int = 80) -> str:
        lines = get_title_lines(self.animation, self._frame, self.accent_color)
        centered_lines = [line.center(width) for line in lines]
        return "\n".join(centered_lines)

    def render(self) -> Text:
        accent, highlight, mid, base = self._get_palette()
        style_lower = self.animation.lower()
        text = Text()

        for row_idx, line in enumerate(RAW_TITLE_LINES):
            for col_idx, ch in enumerate(line):
                if ch == " ":
                    text.append(" ")
                    continue

                if style_lower == "pulse":
                    phase = (col_idx - self._frame * 2) % 36
                    if phase < 5:
                        ch_style = highlight
                    elif phase < 10:
                        ch_style = mid
                    else:
                        ch_style = base
                elif style_lower == "wave":
                    wave_val = math.sin((col_idx * 0.25) + (self._frame * 0.2))
                    if wave_val > 0.4:
                        ch_style = highlight
                    elif wave_val > -0.2:
                        ch_style = mid
                    else:
                        ch_style = base
                else:
                    ch_style = f"bold {accent}"

                text.append(ch, style=ch_style)

            if row_idx < len(RAW_TITLE_LINES) - 1:
                text.append("\n")

        return text
