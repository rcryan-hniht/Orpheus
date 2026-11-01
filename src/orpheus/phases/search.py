from __future__ import annotations

import asyncio

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import DataTable, Input, Static

from orpheus.albums import AlbumsModal
from orpheus.models import Track
from orpheus.resolver import DeezerProvider


class SearchScreen(Screen):
    """Search phase: Online Deezer search with debouncing and optional [Alt+l] local split pane."""

    BINDINGS = [
        Binding("alt+l", "toggle_split", "Split/Single", priority=True),
        Binding("escape", "handle_escape", "Back/Clear", priority=True),
        Binding("tab", "switch_pane", "Switch Pane", priority=True),
        Binding("shift+tab", "switch_pane", "Switch Pane", priority=True),
        Binding("a", "add_to_album", "Add to Album", priority=True),
    ]

    DEFAULT_CSS = """
    SearchScreen {
        width: 100%;
        height: 100%;
        background: #07070c;
        layout: vertical;
        padding: 1 2;
    }

    #search-bar-box {
        height: 3;
        width: 100%;
        margin-bottom: 1;
    }

    #search-input {
        border: solid #00ffcc;
        background: #0c0c14;
    }

    #search-panes {
        width: 100%;
        height: 1fr;
    }

    .search-pane {
        width: 1fr;
        height: 100%;
        border: solid #1a1a2e;
        padding: 0 1;
    }

    .pane-header {
        height: 1;
        width: 100%;
        text-style: bold;
        color: #00ffcc;
        margin-bottom: 1;
    }

    #search-status {
        height: 1;
        width: 100%;
        color: #707070;
        margin-top: 1;
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
            yield Input(placeholder="Type song or artist to search Deezer...", id="search-input")

        with Horizontal(id="search-panes"):
            with Vertical(id="online-pane", classes="search-pane"):
                yield Static("── ONLINE SEARCH (DEEZER) ──", classes="pane-header")
                yield DataTable(id="online-table")

            with Vertical(id="local-pane", classes="search-pane"):
                yield Static("── LOCAL LIBRARY ──", classes="pane-header")
                yield DataTable(id="local-table")

        yield Static(
            "[Alt+l] Toggle Local Split   [a] Add to Album   [Enter] Play   [Esc] Home",
            id="search-status",
        )

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

    def _populate_local_table(self) -> None:
        table = self.query_one("#local-table", DataTable)
        table.clear()
        for t in self.local_tracks:
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

    def on_input_submitted(self, event: Input.Submitted) -> None:
        table = self.query_one("#online-table", DataTable)
        if table.row_count > 0:
            table.focus()

    async def _do_search(self, query: str, gen: int) -> None:
        if gen != self._search_generation or not self.is_mounted:
            return
        if not query:
            try:
                self.query_one("#online-table", DataTable).clear()
            except Exception:
                pass
            self._online_results = []
            return

        tracks = await self.deezer_provider.search(query, limit=25)
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

    def action_handle_escape(self) -> None:
        inp = self.query_one("#search-input", Input)
        if inp.value:
            inp.value = ""
        else:
            if hasattr(self.app, "switch_phase"):
                self.app.switch_phase("home")

    def action_add_to_album(self) -> None:
        track = self._get_highlighted_track()
        if not track:
            return
        store = getattr(self.app, "album_store", None)
        if store:
            self.app.push_screen(AlbumsModal(store=store, target_track=track))

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        track = self._get_highlighted_track()
        if track and hasattr(self.app, "play_resolved_track"):
            self.app.play_resolved_track(track)

    def _get_highlighted_track(self) -> Track | None:
        use_local = self._active_pane == "local" and self.split_view
        table_id = "#local-table" if use_local else "#online-table"
        try:
            table = self.query_one(table_id, DataTable)
            if table.cursor_row is not None and 0 <= table.cursor_row < table.row_count:
                row_key = table.coordinate_to_cell_key((table.cursor_row, 0)).row_key.value
                if self._active_pane == "local" and self.split_view:
                    for t in self.local_tracks:
                        if t.id == row_key:
                            return t
                else:
                    for t in self._online_results:
                        if t.id == row_key:
                            return t
        except Exception:
            pass
        return None
