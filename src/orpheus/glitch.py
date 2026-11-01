from __future__ import annotations

import random
from typing import Callable

from rich.text import Text
from textual.widget import Widget

GLITCH_GLYPHS = "█▓▒░#%&/\\<>~@!=+*"
GLITCH_COLORS = ["#00ffcc", "#ff007f", "#39ff14", "#ffffff", "#7000ff"]


def generate_glitch_frame(width: int, height: int, intensity: float = 0.5) -> list[str]:
    """Generate a 2D text frame simulating scanline corruption and character tears."""
    width = max(10, width)
    height = max(5, height)

    frame: list[str] = []
    for _ in range(height):
        # Determine if this row is torn
        is_torn = random.random() < intensity
        row_chars: list[str] = [" " for _ in range(width)]

        if is_torn:
            # Shift characters or generate noisy clusters
            shift = random.randint(-8, 8)
            num_blocks = random.randint(1, max(2, int(width * 0.15)))
            for _ in range(num_blocks):
                start_x = random.randint(0, width - 1)
                block_len = random.randint(2, max(3, int(width * 0.3)))
                for x in range(start_x, min(width, start_x + block_len)):
                    mapped_x = (x + shift) % width
                    row_chars[mapped_x] = random.choice(GLITCH_GLYPHS)

        frame.append("".join(row_chars))
    return frame


class GlitchOverlay(Widget):
    """Full-screen cyberpunk glitch effect overlay lasting 200–300ms."""

    DEFAULT_CSS = """
    GlitchOverlay {
        width: 100%;
        height: 100%;
        layer: overlay;
        background: transparent;
    }
    """

    def __init__(
        self,
        duration_seconds: float = 0.25,
        on_complete: Callable[[], None] | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.duration_seconds = duration_seconds
        self.on_complete = on_complete
        self.total_frames = max(3, int(duration_seconds / 0.035))
        self.current_frame = 0
        self.is_active = True
        self._timer = None

    def on_mount(self) -> None:
        if self.is_active:
            self._timer = self.set_interval(0.035, self._next_frame)

    def _next_frame(self) -> None:
        self.current_frame += 1
        if self.current_frame >= self.total_frames:
            self.finish()
        else:
            self.refresh()

    def finish(self) -> None:
        self.is_active = False
        if self._timer:
            self._timer.stop()
            self._timer = None
        if self.on_complete:
            self.on_complete()
        try:
            self.remove()
        except Exception:
            pass

    def render(self) -> Text:
        if not self.is_active:
            return Text()

        w = self.size.width or 80
        h = self.size.height or 24
        # Intensity ramps up and then tapers down
        progress = self.current_frame / float(self.total_frames)
        intensity = 0.7 if 0.2 < progress < 0.8 else 0.35

        lines = generate_glitch_frame(w, h, intensity=intensity)
        text = Text()
        color = random.choice(GLITCH_COLORS)

        for i, line in enumerate(lines):
            line_text = Text()
            for ch in line:
                if ch != " ":
                    line_text.append(ch, style=f"bold {color}")
                else:
                    line_text.append(" ")
            text.append_text(line_text)
            if i < len(lines) - 1:
                text.append("\n")
        return text
