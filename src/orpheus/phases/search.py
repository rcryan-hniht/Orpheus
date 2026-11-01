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
    artist_name_matches,
    extract_artist_name,
    is_artist_query,
    rank_tracks_by_query,
)


class SearchStatusBar(Static):
    """Bottom status bar with theme-aware accent brackets."""

    DEFAULT_CSS = """
    SearchStatusBar {
        dock: bottom;
        height: 1;
        width: 100%;
        margin-top: 1;
        background: transparent;
    }
    """

    @property
    def safe_app(self) -> Any:
        try:
            return self.app
        except Exception:
            return getattr(self, "_app", None)

    def _get_accent(self) -> str:
        try:
            app = self.safe_app
            if app and hasattr(app, "current_theme") and app.current_theme:
                theme_accent = getattr(app.current_theme, "accent", None)
                if theme_accent:
                    return str(theme_accent)
                theme_primary = getattr(app.current_theme, "primary", None)
                if theme_primary:
                    return str(theme_primary)
        except Exception:
            pass
        return "#00ffcc"

    def render(self) -> Text:
        accent = self._get_accent()
        text = Text()
        is_playing = False
        try:
            app = self.safe_app
            if app and hasattr(app, "current_track") and app.current_track is not None:
                is_playing = True
        except Exception:
            pass

        items = [
            ("[?]", "Which key"),
        ]
        if is_playing:
            items.append(("[p]", "Playing"))
        items.extend(
            [
                ("[a]", "Add to Album"),
                ("[Enter]", "Play"),
                ("[f]", "Find"),
                ("[S]", "Settings"),
                ("[q]", "Quit"),
                ("[Esc]", "Home"),
            ]
        )
        for i, (k, desc) in enumerate(items):
            text.append(k, style=f"bold {accent}")
            text.append(f" {desc}", style="#909090")
            if i < len(items) - 1:
                text.append("    ")
        return text


class SearchScreen(Screen):
    """Search phase: Deezer search, navigation, [Alt+h] albums split, and [Alt+l] local split."""

    BINDINGS = [
        Binding("question_mark", "which_key", "Which key", priority=True),
        Binding("?", "which_key", "Which key", priority=True, show=False),
        Binding("alt+h", "toggle_albums_split", "Split Albums", priority=True),
        Binding("alt+l", "toggle_split", "Split/Single", priority=True),
        Binding("escape", "handle_escape", "Back/Clear", priority=True),
        Binding("tab", "switch_pane", "Switch Pane", priority=False),
        Binding("shift+tab", "switch_pane", "Switch Pane", priority=False),
        Binding("a", "add_to_album", "Add to Album", priority=True),
        Binding("d", "delete_item", "Delete", priority=False, show=False),
        Binding("p", "now_playing", "Now Playing", priority=False, show=False),
        Binding("s", "stop", "Stop", priority=False, show=False),
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
        dock: top;
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
        overflow: hidden;
    }

    .search-pane {
        width: 1fr;
        height: 100%;
        border: solid $panel;
        padding: 0 1;
        background: transparent;
        overflow: hidden;
    }

    .search-pane DataTable {
        height: 1fr;
        width: 100%;
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
        self.albums_split: bool = False
        self.local_split: bool = False
        self.current_selected_album: str | None = None
        self._debounce_timer: asyncio.TimerHandle | None = None
        self._online_results: list[Track] = []
        self._active_pane = "online"
        self._search_generation = 0

    @property
    def split_view(self) -> bool:
        return self.local_split

    @split_view.setter
    def split_view(self, val: bool) -> None:
        self.local_split = val

    def compose(self) -> ComposeResult:
        with Vertical(id="search-bar-box"):
            yield Input(
                placeholder="Search songs or @artist to filter by artist...", id="search-input"
            )

        with Horizontal(id="search-panes"):
            with Vertical(id="albums-pane", classes="search-pane"):
                yield Static("── MY ALBUMS ──", id="albums-header", classes="pane-header")
                yield DataTable(id="albums-table")

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
        # Hide albums and local panes by default
        self.query_one("#albums-pane").display = False
        self.query_one("#local-pane").display = False

        # Init albums table
        albums_table = self.query_one("#albums-table", DataTable)
        albums_table.cursor_type = "row"
        albums_table.add_columns("Album", "Tracks")
        self._populate_albums_table()

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

    def _get_visible_panes(self) -> list[tuple[str, DataTable]]:
        panes: list[tuple[str, DataTable]] = []
        if self.albums_split:
            try:
                panes.append(("albums", self.query_one("#albums-table", DataTable)))
            except Exception:
                pass
        try:
            panes.append(("online", self.query_one("#online-table", DataTable)))
        except Exception:
            pass
        if self.local_split:
            try:
                panes.append(("local", self.query_one("#local-table", DataTable)))
            except Exception:
                pass
        return panes

    def _get_active_table(self) -> DataTable:
        if self._active_pane == "albums" and self.albums_split:
            return self.query_one("#albums-table", DataTable)
        if self._active_pane == "local" and self.local_split:
            return self.query_one("#local-table", DataTable)
        return self.query_one("#online-table", DataTable)

    def on_key(self, event: events.Key) -> None:
        inp = self.query_one("#search-input", Input)
        table = self._get_active_table()
        if event.key in ("down", "tab"):
            if inp.has_focus:
                panes = self._get_visible_panes()
                if panes:
                    event.prevent_default()
                    event.stop()
                    target = panes[0]
                    self._active_pane = target[0]
                    target[1].focus()
                    if target[1].cursor_row is None or target[1].cursor_row < 0:
                        if target[1].row_count > 0:
                            target[1].cursor_coordinate = Coordinate(0, 0)
            elif not inp.has_focus and event.key == "tab":
                event.prevent_default()
                event.stop()
                self.action_switch_pane(reverse=False)
        elif event.key in ("up", "shift+tab", "backtab"):
            if not inp.has_focus:
                if (
                    event.key in ("shift+tab", "backtab")
                    or table.cursor_row is None
                    or table.cursor_row <= 0
                ):
                    event.prevent_default()
                    event.stop()
                    if event.key in ("shift+tab", "backtab"):
                        self.action_switch_pane(reverse=True)
                    else:
                        inp.focus()
            elif inp.has_focus and event.key in ("shift+tab", "backtab"):
                panes = self._get_visible_panes()
                if panes:
                    event.prevent_default()
                    event.stop()
                    target = panes[-1]
                    self._active_pane = target[0]
                    target[1].focus()
                    if target[1].cursor_row is None or target[1].cursor_row < 0:
                        if target[1].row_count > 0:
                            target[1].cursor_coordinate = Coordinate(0, 0)
        elif event.key in ("f", "ctrl+f"):
            if not inp.has_focus:
                event.prevent_default()
                event.stop()
                inp.focus()
        elif event.key == "s" and not inp.has_focus:
            event.prevent_default()
            event.stop()
            self.action_stop()
        elif event.key == "d" and not inp.has_focus:
            event.prevent_default()
            event.stop()
            self.action_delete_item()
        elif event.key == "p" and not inp.has_focus:
            event.prevent_default()
            event.stop()
            self.action_now_playing()

    def _populate_albums_table(self, query: str = "") -> None:
        try:
            table = self.query_one("#albums-table", DataTable)
            table.clear()
            store = getattr(self.safe_app, "album_store", None)
            if not store:
                return
            albums = store.list_albums()
            if query:
                q_lower = query.lower()
                albums = [a for a in albums if q_lower in a.lower()]
            for album_name in albums:
                tracks = store.get_album_tracks(album_name)
                count_str = f"{len(tracks)} tracks" if len(tracks) != 1 else "1 track"
                table.add_row(album_name, count_str, key=f"album:{album_name}")
        except Exception:
            pass

    def _populate_local_table(self, query: str = "") -> None:
        table = self.query_one("#local-table", DataTable)
        table.clear()
        tracks = self.local_tracks
        if query:
            if is_artist_query(query):
                art_name = extract_artist_name(query)
                tracks = [t for t in tracks if artist_name_matches(art_name, t.artist)]
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
        self.current_selected_album = None
        if not query:
            try:
                self.query_one("#online-table", DataTable).clear()
                self.query_one("#online-header", Static).update("── ONLINE SEARCH (DEEZER) ──")
            except Exception:
                pass
            self._online_results = []
            self._populate_local_table()
            self._populate_albums_table()
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
            self._populate_albums_table(query)
        else:
            try:
                self.query_one("#online-header", Static).update("── ONLINE SEARCH (DEEZER) ──")
            except Exception:
                pass
            raw_tracks = await self.deezer_provider.search(query, limit=25)
            tracks = rank_tracks_by_query(raw_tracks, query)
            self._populate_local_table(query)
            self._populate_albums_table(query)

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

    def action_toggle_albums_split(self) -> None:
        self.albums_split = not self.albums_split
        try:
            self.query_one("#albums-pane").display = self.albums_split
            if self.albums_split:
                self._populate_albums_table()
                self._active_pane = "albums"
                self.query_one("#albums-table", DataTable).focus()
            elif self._active_pane == "albums":
                self._active_pane = "online"
                self.query_one("#online-table", DataTable).focus()
        except Exception:
            pass

    def action_toggle_split(self) -> None:
        self.local_split = not self.local_split
        try:
            self.query_one("#local-pane").display = self.local_split
            if self.local_split:
                self._populate_local_table()
                self._active_pane = "local"
                self.query_one("#local-table", DataTable).focus()
            elif self._active_pane == "local":
                self._active_pane = "online"
                self.query_one("#online-table", DataTable).focus()
        except Exception:
            pass

    def action_switch_pane(self, reverse: bool = False) -> None:
        panes = self._get_visible_panes()
        if not panes:
            return
        inp = self.query_one("#search-input", Input)
        if inp.has_focus:
            target = panes[-1] if reverse else panes[0]
            self._active_pane = target[0]
            target[1].focus()
            if target[1].cursor_row is None and target[1].row_count > 0:
                target[1].cursor_coordinate = Coordinate(0, 0)
            return

        curr_idx = -1
        for i, (p_name, tbl) in enumerate(panes):
            if tbl.has_focus or self._active_pane == p_name:
                curr_idx = i
                break

        if curr_idx >= 0:
            if reverse:
                if curr_idx > 0:
                    prev_pane, prev_tbl = panes[curr_idx - 1]
                    self._active_pane = prev_pane
                    prev_tbl.focus()
                else:
                    inp.focus()
            else:
                if curr_idx < len(panes) - 1:
                    next_pane, next_tbl = panes[curr_idx + 1]
                    self._active_pane = next_pane
                    next_tbl.focus()
                else:
                    inp.focus()
        else:
            inp.focus()

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

    def action_stop(self) -> None:
        try:
            inp = self.query_one("#search-input", Input)
            if inp.has_focus:
                return
        except Exception:
            pass
        app = self.safe_app
        if app and hasattr(app, "action_stop"):
            res = app.action_stop()
            if hasattr(res, "__await__"):
                asyncio.create_task(res)

    def action_which_key(self) -> None:
        app = self.safe_app
        if app and hasattr(app, "action_which_key"):
            app.action_which_key()

    def action_now_playing(self) -> None:
        try:
            inp = self.query_one("#search-input", Input)
            if inp.has_focus:
                return
        except Exception:
            pass
        app = self.safe_app
        if app and getattr(app, "current_track", None) is not None and hasattr(app, "switch_phase"):
            app.switch_phase("now_playing")

    def action_delete_item(self) -> None:
        try:
            inp = self.query_one("#search-input", Input)
            if inp.has_focus:
                return
        except Exception:
            pass

        app = self.safe_app
        store = getattr(app, "album_store", None)
        if not store:
            return

        # Case 1: In #albums-table -> delete selected album
        if self._active_pane == "albums" and self.albums_split:
            try:
                tbl = self.query_one("#albums-table", DataTable)
                idx = tbl.cursor_row
                if idx is not None and 0 <= idx < tbl.row_count:
                    row_key = tbl.coordinate_to_cell_key((idx, 0)).row_key.value
                    if row_key.startswith("album:"):
                        alb_name = row_key[len("album:") :]
                        store.delete_album(alb_name)
                        if self.current_selected_album == alb_name:
                            self.current_selected_album = None
                            self._online_results = []
                            self.query_one("#online-table", DataTable).clear()
                            self.query_one("#online-header", Static).update(
                                "── ONLINE SEARCH (DEEZER) ──"
                            )
                        self._populate_albums_table()
            except Exception:
                pass
            return

        # Case 2: In #online-table with an album open -> remove track from album
        if self.current_selected_album:
            try:
                tbl = self.query_one("#online-table", DataTable)
                idx = tbl.cursor_row
                if idx is not None and 0 <= idx < tbl.row_count:
                    row_key = tbl.coordinate_to_cell_key((idx, 0)).row_key.value
                    store.remove_track(self.current_selected_album, row_key)
                    if app and hasattr(app, "queue"):
                        app.queue = [t for t in app.queue if t.id != row_key]
                    updated = store.get_album_tracks(self.current_selected_album)
                    self._online_results = updated
                    tbl.clear()
                    for t in updated:
                        dur = int(t.duration) if t.duration else 0
                        dur_str = f"{dur // 60}:{dur % 60:02d}" if t.duration else "--:--"
                        tbl.add_row(t.title, t.artist, t.album, dur_str, key=t.id)
                    alb_title = self.current_selected_album.upper()
                    header_text = f"── ALBUM: {alb_title} ({len(updated)} tracks) ──"
                    self.query_one("#online-header", Static).update(header_text)
                    if updated:
                        new_idx = min(idx, len(updated) - 1)
                        tbl.cursor_coordinate = Coordinate(new_idx, 0)
                    self._populate_albums_table()
            except Exception:
                pass

    def on_screen_resume(self) -> None:
        if self.albums_split:
            self._populate_albums_table()

    def action_add_to_album(self) -> None:
        track = self._get_highlighted_track()
        if not track:
            return
        store = getattr(self.app, "album_store", None)
        if store:
            self.app.push_screen(AlbumsModal(store=store, target_track=track))

    def _select_and_open_album(self, album_name: str, play_immediately: bool = False) -> None:
        self.current_selected_album = album_name
        store = getattr(self.safe_app, "album_store", None)
        if not store:
            return
        tracks = store.get_album_tracks(album_name)
        self._online_results = tracks
        try:
            table = self.query_one("#online-table", DataTable)
            table.clear()
            for t in tracks:
                dur = int(t.duration) if t.duration else 0
                dur_str = f"{dur // 60}:{dur % 60:02d}" if t.duration else "--:--"
                table.add_row(t.title, t.artist, t.album, dur_str, key=t.id)
            self.query_one("#online-header", Static).update(
                f"── ALBUM: {album_name.upper()} ({len(tracks)} tracks) ──"
            )
            if tracks:
                table.cursor_coordinate = Coordinate(0, 0)
                if play_immediately:
                    first_track = tracks[0]
                    queue = list(tracks[1:])
                    if hasattr(self.app, "load_playlist_and_play"):
                        self.app.load_playlist_and_play(first_track, queue, [], album=album_name)
                    elif hasattr(self.app, "play_resolved_track"):
                        self.app.play_resolved_track(first_track)
                    self._active_pane = "online"
                    table.focus()
        except Exception:
            pass

    def on_data_table_row_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if event.data_table.id == "albums-table":
            try:
                row_key = (
                    event.row_key.value if hasattr(event.row_key, "value") else str(event.row_key)
                )
                if row_key.startswith("album:"):
                    album_name = row_key[len("album:") :]
                    self._select_and_open_album(album_name, play_immediately=False)
            except Exception:
                pass

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        row_key = event.row_key.value if hasattr(event.row_key, "value") else str(event.row_key)
        if row_key.startswith("album:"):
            album_name = row_key[len("album:") :]
            self._select_and_open_album(album_name, play_immediately=True)
            return

        track, queue, history = self._get_track_and_context_by_key(row_key)
        if not track:
            track, queue, history = self._get_selected_track_and_context()
        if track:
            album = (
                self.current_selected_album
                if (not self.local_split and self._active_pane == "online")
                else None
            )
            effective_queue = queue if album else []
            if hasattr(self.app, "load_playlist_and_play"):
                self.app.load_playlist_and_play(track, effective_queue, history, album=album)
            elif hasattr(self.app, "play_resolved_track"):
                self.app.play_resolved_track(track)

    def _get_track_and_context_by_key(
        self, row_key: str
    ) -> tuple[Track | None, list[Track], list[Track]]:
        use_local = self._active_pane == "local" and self.local_split
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
        use_local = self._active_pane == "local" and self.local_split
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
