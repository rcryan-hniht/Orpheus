from __future__ import annotations

import asyncio
from typing import Any

from rich.text import Text
from textual import events
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.coordinate import Coordinate
from textual.screen import Screen
from textual.widgets import DataTable, Input, Static

from orpheus.albums import AlbumsModal
from orpheus.models import Track
from orpheus.resolver import (
    DeezerProvider,
    extract_artist_name,
    is_artist_query,
    rank_tracks_by_query,
)


class SearchStatusBar(Static):
    """Bottom status bar with theme-aware accent brackets."""

    DEFAULT_CSS = """
    SearchStatusBar {
        height: 1;
        width: 100%;
        margin-top: 1;
        background: transparent;
    }
    """

    def _get_accent(self) -> str:
        try:
            if hasattr(self.app, "current_theme") and self.app.current_theme:
                theme_accent = getattr(self.app.current_theme, "accent", None)
                if theme_accent:
                    return str(theme_accent)
                theme_primary = getattr(self.app.current_theme, "primary", None)
                if theme_primary:
                    return str(theme_primary)
        except Exception:
            pass
        return "#00ffcc"

    def render(self) -> Text:
        accent = self._get_accent()
        text = Text()
        items = [
            ("[Alt+l]", "Toggle Split"),
            ("[a]", "Add to Album"),
            ("[Enter]", "Play"),
            ("[f]", "Find"),
            ("[S]", "Settings"),
            ("[q]", "Quit"),
            ("[Esc]", "Home"),
        ]
        for i, (k, desc) in enumerate(items):
            text.append(k, style=f"bold {accent}")
            text.append(f" {desc}", style="#909090")
            if i < len(items) - 1:
                text.append("    ")
        return text


class SearchScreen(Screen):
    """Search phase: Online Deezer search, arrow navigation, and [Alt+l] local split pane."""

    BINDINGS = [
        Binding("alt+l", "toggle_split", "Split/Single", priority=True),
        Binding("escape", "handle_escape", "Back/Clear", priority=True),
        Binding("tab", "switch_pane", "Switch Pane", priority=False),
        Binding("shift+tab", "switch_pane", "Switch Pane", priority=False),
        Binding("a", "add_to_album", "Add to Album", priority=True),
        Binding("f", "focus_search", "Find", priority=False),
        Binding("S", "settings", "Settings", priority=False),
        Binding("alt+s", "settings", "Settings", priority=True),
        Binding("q", "quit", "Quit", priority=False),
        Binding("ctrl+q", "quit", "Quit", priority=True),
    ]

    DEFAULT_CSS = """
    SearchScreen {
        width: 100%;
        height: 100%;
        background: ansi_default;
        layout: vertical;
        padding: 1 2;
        overflow: hidden;
    }

    #search-bar-box {
        height: 3;
        width: 100%;
        margin-bottom: 1;
    }

    #search-input {
        border: solid $accent;
        background: $surface;
        color: $foreground;
    }

    #search-panes {
        width: 100%;
        height: 1fr;
    }

    .search-pane {
        width: 1fr;
        height: 100%;
        border: solid $panel;
        padding: 0 1;
        background: transparent;
    }

    .pane-header {
        height: 1;
        width: 100%;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }
    """

    def __init__(
        self,
        deezer_provider: DeezerProvider | None = None,
        local_tracks: list[Track] | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.deezer_provider = deezer_provider or DeezerProvider()
        self.local_tracks = local_tracks or []
        self.split_view = False
        self._debounce_timer: asyncio.TimerHandle | None = None
        self._online_results: list[Track] = []
        self._active_pane = "online"
        self._search_generation = 0

    def compose(self) -> ComposeResult:
        with Vertical(id="search-bar-box"):
            yield Input(
                placeholder="Search songs or @artist to filter by artist...", id="search-input"
            )

        with Horizontal(id="search-panes"):
            with Vertical(id="online-pane", classes="search-pane"):
                yield Static(
                    "── ONLINE SEARCH (DEEZER) ──", id="online-header", classes="pane-header"
                )
                yield DataTable(id="online-table")

            with Vertical(id="local-pane", classes="search-pane"):
                yield Static("── LOCAL LIBRARY ──", id="local-header", classes="pane-header")
                yield DataTable(id="local-table")

        yield SearchStatusBar(id="search-status")

    def on_mount(self) -> None:
        # Hide local pane by default
        self.query_one("#local-pane").display = False

        # Init online table
        online_table = self.query_one("#online-table", DataTable)
        online_table.cursor_type = "row"
        online_table.add_columns("Title", "Artist", "Album", "Duration")

        # Init local table
        local_table = self.query_one("#local-table", DataTable)
        local_table.cursor_type = "row"
        local_table.add_columns("Title", "Artist", "Duration")
        self._populate_local_table()

        # Focus search input initially
        self.query_one("#search-input", Input).focus()

    def _get_active_table(self) -> DataTable:
        use_local = self._active_pane == "local" and self.split_view
        return self.query_one("#local-table" if use_local else "#online-table", DataTable)

    def on_key(self, event: events.Key) -> None:
        inp = self.query_one("#search-input", Input)
        table = self._get_active_table()
        if event.key in ("down", "tab"):
            if inp.has_focus:
                if table.row_count > 0:
                    event.prevent_default()
                    event.stop()
                    table.focus()
                    if table.cursor_row is None or table.cursor_row < 0:
                        table.cursor_coordinate = Coordinate(0, 0)
            elif table.has_focus and event.key == "tab" and not self.split_view:
                event.prevent_default()
                event.stop()
                inp.focus()
        elif event.key in ("up", "shift+tab", "backtab"):
            if table.has_focus:
                if (
                    event.key in ("shift+tab", "backtab")
                    or table.cursor_row is None
                    or table.cursor_row <= 0
                ):
                    event.prevent_default()
                    event.stop()
                    inp.focus()
            elif inp.has_focus and event.key in ("shift+tab", "backtab") and not self.split_view:
                if table.row_count > 0:
                    event.prevent_default()
                    event.stop()
                    table.focus()
        elif event.key in ("f", "ctrl+f"):
            if not inp.has_focus:
                event.prevent_default()
                event.stop()
                inp.focus()

    def _populate_local_table(self, query: str = "") -> None:
        table = self.query_one("#local-table", DataTable)
        table.clear()
        tracks = self.local_tracks
        if query:
            if is_artist_query(query):
                art_name = extract_artist_name(query).lower()
                tracks = [t for t in tracks if art_name in t.artist.lower()]
            else:
                q_lower = query.lower()
                tracks = [
                    t for t in tracks if q_lower in t.title.lower() or q_lower in t.artist.lower()
                ]
        for t in tracks:
            dur = int(t.duration) if t.duration else 0
            dur_str = f"{dur // 60}:{dur % 60:02d}" if t.duration else "--:--"
            table.add_row(t.title, t.artist, dur_str, key=t.id)

    def on_input_changed(self, event: Input.Changed) -> None:
        query = event.value.strip()
        self._search_generation += 1
        gen = self._search_generation
        if self._debounce_timer:
            self._debounce_timer.cancel()
        loop = asyncio.get_event_loop()
        self._debounce_timer = loop.call_later(
            0.4, lambda: asyncio.create_task(self._do_search(query, gen))
        )

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        query = event.value.strip()
        if not query:
            return

        if self._debounce_timer:
            self._debounce_timer.cancel()
            self._debounce_timer = None

        table = self._get_active_table()
        # If table is empty or search is still pending, execute search immediately
        if table.row_count == 0 or not self._online_results:
            self._search_generation += 1
            gen = self._search_generation
            await self._do_search(query, gen)

        track, queue, history = self._get_selected_track_and_context(row_idx=0)
        if track and hasattr(self.app, "load_playlist_and_play"):
            self.app.load_playlist_and_play(track, queue, history)
        elif track and hasattr(self.app, "play_resolved_track"):
            self.app.play_resolved_track(track)
        else:
            table.focus()

    async def _do_search(self, query: str, gen: int) -> None:
        if gen != self._search_generation or not self.is_mounted:
            return
        if not query:
            try:
                self.query_one("#online-table", DataTable).clear()
                self.query_one("#online-header", Static).update("── ONLINE SEARCH (DEEZER) ──")
            except Exception:
                pass
            self._online_results = []
            self._populate_local_table()
            return

        if is_artist_query(query):
            artist_name = extract_artist_name(query)
            try:
                self.query_one("#online-header", Static).update(
                    f"── ARTIST SEARCH: @{artist_name.upper()} (DEEZER) ──"
                )
            except Exception:
                pass
            tracks = await self.deezer_provider.search_by_artist(artist_name, limit=30)
            self._populate_local_table(query)
        else:
            try:
                self.query_one("#online-header", Static).update("── ONLINE SEARCH (DEEZER) ──")
            except Exception:
                pass
            raw_tracks = await self.deezer_provider.search(query, limit=25)
            tracks = rank_tracks_by_query(raw_tracks, query)
            self._populate_local_table(query)

        if gen != self._search_generation or not self.is_mounted:
            return
        self._online_results = tracks
        try:
            table = self.query_one("#online-table", DataTable)
            table.clear()
            for t in tracks:
                dur = int(t.duration) if t.duration else 0
                dur_str = f"{dur // 60}:{dur % 60:02d}" if t.duration else "--:--"
                table.add_row(t.title, t.artist, t.album, dur_str, key=t.id)
            if tracks:
                table.cursor_coordinate = Coordinate(0, 0)
        except Exception:
            pass

    def action_toggle_split(self) -> None:
        self.split_view = not self.split_view
        try:
            self.query_one("#local-pane").display = self.split_view
        except Exception:
            pass

    def action_switch_pane(self) -> None:
        if not self.split_view:
            try:
                inp = self.query_one("#search-input", Input)
                table = self.query_one("#online-table", DataTable)
                if inp.has_focus:
                    table.focus()
                else:
                    inp.focus()
            except Exception:
                pass
            return
        if self._active_pane == "online":
            self._active_pane = "local"
            self.query_one("#local-table", DataTable).focus()
        else:
            self._active_pane = "online"
            self.query_one("#online-table", DataTable).focus()

    @property
    def safe_app(self) -> Any:
        try:
            return self.app
        except Exception:
            return getattr(self, "_app", None)

    def action_handle_escape(self) -> None:
        inp = self.query_one("#search-input", Input)
        if inp.value:
            inp.value = ""
        else:
            app = self.safe_app
            if app and hasattr(app, "switch_phase"):
                app.switch_phase("home")

    def action_focus_search(self) -> None:
        try:
            self.query_one("#search-input", Input).focus()
        except Exception:
            pass

    def action_quit(self) -> None:
        app = self.safe_app
        if app and hasattr(app, "exit"):
            app.exit()

    def action_settings(self) -> None:
        app = self.safe_app
        if app and hasattr(app, "action_settings"):
            app.action_settings()

    def action_add_to_album(self) -> None:
        track = self._get_highlighted_track()
        if not track:
            return
        store = getattr(self.app, "album_store", None)
        if store:
            self.app.push_screen(AlbumsModal(store=store, target_track=track))

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        row_key = event.row_key.value if hasattr(event.row_key, "value") else str(event.row_key)
        track, queue, history = self._get_track_and_context_by_key(row_key)
        if not track:
            track, queue, history = self._get_selected_track_and_context()
        if track:
            if hasattr(self.app, "load_playlist_and_play"):
                self.app.load_playlist_and_play(track, queue, history)
            elif hasattr(self.app, "play_resolved_track"):
                self.app.play_resolved_track(track)

    def _get_track_and_context_by_key(
        self, row_key: str
    ) -> tuple[Track | None, list[Track], list[Track]]:
        use_local = self._active_pane == "local" and self.split_view
        track_list = self.local_tracks if use_local else self._online_results
        for i, t in enumerate(track_list):
            if t.id == row_key:
                selected = t
                queue = list(track_list[i + 1 :])
                history = list(track_list[:i])
                return selected, queue, history
        return None, [], []

    def _get_selected_track_and_context(
        self, row_idx: int | None = None
    ) -> tuple[Track | None, list[Track], list[Track]]:
        use_local = self._active_pane == "local" and self.split_view
        table_id = "#local-table" if use_local else "#online-table"
        track_list = self.local_tracks if use_local else self._online_results

        try:
            table = self.query_one(table_id, DataTable)
            idx = row_idx if row_idx is not None else table.cursor_row
            if idx is not None and 0 <= idx < table.row_count:
                row_key = table.coordinate_to_cell_key((idx, 0)).row_key.value
                for i, t in enumerate(track_list):
                    if t.id == row_key:
                        selected = t
                        queue = list(track_list[i + 1 :])
                        history = list(track_list[:i])
                        return selected, queue, history
        except Exception:
            pass
        return None, [], []

    def _get_highlighted_track(self) -> Track | None:
        track, _, _ = self._get_selected_track_and_context()
        return track
