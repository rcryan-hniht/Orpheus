from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import Static


@dataclass
class SettingItem:
    key: str
    label: str
    kind: str  # "select" | "toggle" | "number"
    options: list[Any] = field(default_factory=list)
    value: Any = None
    unit: str = ""
    min_val: float = 0.0
    max_val: float = 100.0
    step_val: float = 1.0

    def cycle_next(self) -> None:
        if self.kind == "toggle":
            self.value = not self.value
        elif self.kind == "select" and self.options:
            if self.value in self.options:
                idx = (self.options.index(self.value) + 1) % len(self.options)
                self.value = self.options[idx]
            else:
                self.value = self.options[0]
        elif self.kind == "number":
            self.value = min(self.max_val, round(self.value + self.step_val, 2))

    def cycle_prev(self) -> None:
        if self.kind == "toggle":
            self.value = not self.value
        elif self.kind == "select" and self.options:
            if self.value in self.options:
                idx = (self.options.index(self.value) - 1) % len(self.options)
                self.value = self.options[idx]
            else:
                self.value = self.options[-1]
        elif self.kind == "number":
            self.value = max(self.min_val, round(self.value - self.step_val, 2))

    def format_value(self) -> str:
        if self.kind == "toggle":
            return "On" if self.value else "Off"
        if self.kind == "number":
            return f"{self.value}{self.unit}"
        return str(self.value)


@dataclass
class SettingGroup:
    title: str
    items: list[SettingItem] = field(default_factory=list)


class SettingsView(Static):
    """Inner rendered view of settings groups and values."""

    def __init__(self, modal: SettingsModal) -> None:
        super().__init__()
        self.modal = modal

    def _get_accent(self) -> str:
        try:
            if hasattr(self.modal.app, "current_theme") and self.modal.app.current_theme:
                theme_accent = getattr(self.modal.app.current_theme, "accent", None)
                if theme_accent:
                    return str(theme_accent)
                theme_primary = getattr(self.modal.app.current_theme, "primary", None)
                if theme_primary:
                    return str(theme_primary)
        except Exception:
            pass
        return "#00ffcc"

    def render(self) -> Text:
        w = max(40, (self.size.width or 50) - 4)
        accent = self._get_accent()
        text = Text()

        flat_index = 0
        for g_idx, group in enumerate(self.modal.groups):
            # Group header
            header = f"── {group.title} ──"
            text.append(header.center(w) + "\n", style=f"bold {accent}")

            for item in group.items:
                is_selected = flat_index == self.modal.current_index
                val_str = item.format_value()

                if is_selected:
                    prefix = " ▶ "
                    val_display = f"◀ {val_str} ▶"
                    line_style = "bold white"
                    accent_style = f"bold {accent}"
                else:
                    prefix = "   "
                    val_display = f"  {val_str}  "
                    line_style = "#c0c0c0"
                    accent_style = "#a0a0a0"

                # Label on left, value on right
                label_part = f"{prefix}{item.label}: "
                padding = max(1, w - len(label_part) - len(val_display))

                row_text = Text()
                row_text.append(prefix, style=f"bold {accent}" if is_selected else "default")
                row_text.append(f"{item.label}: ", style=accent_style)
                row_text.append(" " * padding)
                row_text.append(val_display, style=line_style)
                text.append_text(row_text)
                text.append("\n")

                flat_index += 1

            if g_idx < len(self.modal.groups) - 1:
                text.append("\n")

        # Bottom hint bar
        text.append("\n")
        hints = Text()
        hints.append("↑↓", style=f"bold {accent}")
        hints.append(" nav   ")
        hints.append("←→", style=f"bold {accent}")
        hints.append(" change   ")
        hints.append("Enter", style=f"bold {accent}")
        hints.append(" save   ")
        hints.append("Esc", style=f"bold {accent}")
        hints.append(" cancel")
        text.append_text(hints)
        return text


class SettingsModal(ModalScreen[dict[str, Any] | None]):
    """Floating cyberpunk Settings modal dialog with live preview."""

    BINDINGS = [
        Binding("up", "prev_item", "Up", show=False),
        Binding("down", "next_item", "Down", show=False),
        Binding("left", "prev_val", "Left", show=False),
        Binding("right", "next_val", "Right", show=False),
        Binding("enter", "save", "Save", show=False),
        Binding("escape", "cancel", "Cancel", show=False),
    ]

    DEFAULT_CSS = """
    SettingsModal {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }

    #settings-dialog {
        width: 56;
        height: auto;
        max-height: 80%;
        border: solid $accent;
        background: $surface;
        padding: 1 2;
    }
    """

    def __init__(
        self,
        groups: list[SettingGroup],
        on_change: Callable[[str, Any], None] | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.groups = groups
        self.on_change = on_change
        self.current_index = 0
        # Snapshot initial values for cancellation
        self._initial_values: dict[str, Any] = {}
        for g in self.groups:
            for item in g.items:
                self._initial_values[item.key] = item.value

    @property
    def flat_items(self) -> list[SettingItem]:
        items: list[SettingItem] = []
        for g in self.groups:
            items.extend(g.items)
        return items

    def compose(self) -> ComposeResult:
        with Container(id="settings-dialog"):
            yield SettingsView(self)

    def _refresh_view(self) -> None:
        try:
            self.query_one(SettingsView).refresh()
        except Exception:
            pass

    def action_next_item(self) -> None:
        total = len(self.flat_items)
        if total > 0:
            self.current_index = (self.current_index + 1) % total
            self._refresh_view()

    def action_prev_item(self) -> None:
        total = len(self.flat_items)
        if total > 0:
            self.current_index = (self.current_index - 1) % total
            self._refresh_view()

    def action_next_val(self) -> None:
        items = self.flat_items
        if 0 <= self.current_index < len(items):
            item = items[self.current_index]
            item.cycle_next()
            if self.on_change:
                self.on_change(item.key, item.value)
            self._refresh_view()

    def action_prev_val(self) -> None:
        items = self.flat_items
        if 0 <= self.current_index < len(items):
            item = items[self.current_index]
            item.cycle_prev()
            if self.on_change:
                self.on_change(item.key, item.value)
            self._refresh_view()

    def action_save(self) -> None:
        results: dict[str, Any] = {item.key: item.value for item in self.flat_items}
        self.dismiss(results)

    def action_cancel(self) -> None:
        # Revert live preview
        if self.on_change:
            for k, v in self._initial_values.items():
                self.on_change(k, v)
        self.dismiss(None)
