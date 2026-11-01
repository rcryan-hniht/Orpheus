from __future__ import annotations

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.screen import ModalScreen
from textual.widgets import Static


class WhichKeyModal(ModalScreen[None]):
    """Theme-synced modal dialog displaying all Orpheus keyboard shortcuts."""

    BINDINGS = [
        Binding("escape", "dismiss_modal", "Close", priority=True),
        Binding("question_mark", "dismiss_modal", "Close", priority=True),
        Binding("?", "dismiss_modal", "Close", priority=True, show=False),
        Binding("q", "dismiss_modal", "Close", priority=True),
    ]

    DEFAULT_CSS = """
    WhichKeyModal {
        align: center middle;
        background: rgba(0, 0, 0, 0.7);
    }

    #which-key-box {
        width: 76;
        height: auto;
        max-height: 85%;
        border: double $accent;
        background: $surface;
        color: $foreground;
        padding: 1 2;
    }

    #which-key-scroll {
        width: 100%;
        height: auto;
        max-height: 26;
        scrollbar-size-vertical: 1;
        background: transparent;
    }

    #which-key-content {
        width: 100%;
        background: transparent;
    }

    #which-key-footer {
        content-align: center middle;
        margin-top: 1;
        background: transparent;
    }
    """

    def _get_theme_styles(self) -> tuple[str, str, str]:
        accent = "#00ffcc"
        dim = "#808080"
        fg = "#ffffff"
        try:
            if hasattr(self.app, "current_theme") and self.app.current_theme:
                theme = self.app.current_theme
                is_dark = getattr(theme, "dark", True)
                accent = str(getattr(theme, "accent", None) or getattr(theme, "primary", "#00ffcc"))
                fg = str(getattr(theme, "foreground", "#ffffff" if is_dark else "#0b2545"))
                dim = "#888888" if is_dark else "#555555"
        except Exception:
            pass
        return accent, dim, fg

    def compose(self) -> ComposeResult:
        with VerticalScroll(id="which-key-box"):
            yield Static(id="which-key-content")
            yield Static(id="which-key-footer")

    def on_mount(self) -> None:
        self._refresh_content()

    def _refresh_content(self) -> None:
        accent, dim, fg = self._get_theme_styles()
        sections: list[tuple[str, list[tuple[str, str]]]] = [
            (
                "GLOBAL SHORTCUTS",
                [
                    ("?", "Open this Which Key shortcuts guide"),
                    ("s", "Stop audio playback (works in any phase)"),
                    ("S / Alt+s", "Open Settings (Theme selection)"),
                    ("Ctrl+q / q", "Quit Orpheus"),
                ],
            ),
            (
                "SEARCH PHASE (ALBUMS & ONLINE SEARCH)",
                [
                    ("Tab / Shift+Tab", "Switch focus between Search, Albums, and Tracks"),
                    ("← / →", "Navigate between My Album and Search panes"),
                    ("@artist <name>", "Filter search strictly by artist name"),
                    ("Enter", "Play selected track or open album"),
                    ("a", "In Albums: New album; In Tracks: Add to album"),
                    ("m", "In Albums: Rename highlighted album"),
                    ("d", "In Albums: Delete album (confirm Yes/No); In Tracks: Remove"),
                    ("p", "Return to Now Playing screen (if playing)"),
                    ("s", "Stop playback (when navigating panes)"),
                    ("f", "Focus search input box"),
                    ("Esc", "Clear search query or return to Home"),
                ],
            ),
            (
                "NOW PLAYING PHASE",
                [
                    ("Space", "Play / Pause playback"),
                    ("s", "Stop playback"),
                    ("↑ / ↓", "Scroll lyrics up / down (also mouse wheel)"),
                    ("→ / ←", "Seek forward / backward 5s (10s on double-tap)"),
                    ("Shift+→ / Shift+←", "Play Next / Previous track in queue"),
                    ("r", "Cycle Repeat mode (Off → Track → All)"),
                    ("k", "Toggle AI Karaoke (demucs vocal isolation)"),
                    ("f", "Find songs (switch to Search phase)"),
                    ("Esc", "Return to Home phase"),
                ],
            ),
            (
                "HOME PHASE",
                [
                    ("f", "Find songs (open Search)"),
                    ("p", "Switch to Now Playing screen"),
                    ("s", "Stop playback"),
                    ("S", "Settings"),
                    ("q", "Quit"),
                ],
            ),
            (
                "ALBUM MANAGEMENT",
                [
                    (":", "Create new album directly"),
                    ("Enter", "Select / Add track to highlighted album"),
                    ("m", "Rename selected album"),
                    ("d", "Delete selected album"),
                    ("Esc", "Close album dialog"),
                ],
            ),
        ]

        full_text = Text()
        full_text.append("── WHICH KEY / SHORTCUTS ──\n\n", style=f"bold {accent}")
        for sec_idx, (sec_title, items) in enumerate(sections):
            full_text.append(f"  ── {sec_title} ──\n", style=f"bold {accent}")
            for k, desc in items:
                full_text.append("    ")
                full_text.append(f"{k:<18}", style=f"bold {accent}")
                full_text.append(f" {desc}\n", style=fg)
            if sec_idx < len(sections) - 1:
                full_text.append("\n")

        self.query_one("#which-key-content", Static).update(full_text)

        footer_text = Text()
        footer_text.append("[Esc / ? / q]", style=f"bold {accent}")
        footer_text.append(" Close", style=dim)
        self.query_one("#which-key-footer", Static).update(footer_text)

    def action_dismiss_modal(self) -> None:
        self.dismiss(None)
