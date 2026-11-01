from __future__ import annotations

import json
from dataclasses import asdict

from rich.text import Text
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Input, Static

from orpheus.models import Track
from orpheus.storage import Database


class AlbumStore:
    """Manages custom user albums and playlists in SQLite."""

    def __init__(self, db: Database) -> None:
        self.db = db
        self._init_tables()

    def _init_tables(self) -> None:
        with self.db.connection:
            self.db.connection.execute(
                "CREATE TABLE IF NOT EXISTS custom_albums ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "name TEXT UNIQUE NOT NULL)"
            )
            self.db.connection.execute(
                "CREATE TABLE IF NOT EXISTS custom_album_tracks ("
                "album_id INTEGER NOT NULL, "
                "track_id TEXT NOT NULL, "
                "track_data TEXT NOT NULL, "
                "position INTEGER NOT NULL, "
                "FOREIGN KEY(album_id) REFERENCES custom_albums(id) ON DELETE CASCADE)"
            )

    def create_album(self, name: str) -> None:
        name = name.strip()
        if not name:
            return
        with self.db.connection:
            self.db.connection.execute(
                "INSERT OR IGNORE INTO custom_albums (name) VALUES (?)", (name,)
            )

    def rename_album(self, old_name: str, new_name: str) -> None:
        new_name = new_name.strip()
        if not new_name or old_name == new_name:
            return
        with self.db.connection:
            self.db.connection.execute(
                "UPDATE OR IGNORE custom_albums SET name = ? WHERE name = ?", (new_name, old_name)
            )

    def delete_album(self, name: str) -> None:
        with self.db.connection:
            row = self.db.connection.execute(
                "SELECT id FROM custom_albums WHERE name = ?", (name,)
            ).fetchone()
            if row:
                album_id = row[0]
                self.db.connection.execute(
                    "DELETE FROM custom_album_tracks WHERE album_id = ?", (album_id,)
                )
                self.db.connection.execute(
                    "DELETE FROM custom_albums WHERE id = ?", (album_id,)
                )

    def add_track(self, album_name: str, track: Track) -> None:
        with self.db.connection:
            row = self.db.connection.execute(
                "SELECT id FROM custom_albums WHERE name = ?", (album_name,)
            ).fetchone()
            if not row:
                self.create_album(album_name)
                row = self.db.connection.execute(
                    "SELECT id FROM custom_albums WHERE name = ?", (album_name,)
                ).fetchone()
            if row:
                album_id = row[0]
                pos_row = self.db.connection.execute(
                    "SELECT MAX(position) FROM custom_album_tracks WHERE album_id = ?",
                    (album_id,),
                ).fetchone()
                pos = (pos_row[0] + 1) if pos_row and pos_row[0] is not None else 0
                track_json = json.dumps(asdict(track))
                self.db.connection.execute(
                    "INSERT INTO custom_album_tracks "
                    "(album_id, track_id, track_data, position) VALUES (?, ?, ?, ?)",
                    (album_id, track.id, track_json, pos),
                )

    def list_albums(self) -> list[str]:
        rows = self.db.connection.execute(
            "SELECT name FROM custom_albums ORDER BY name"
        ).fetchall()
        return [r[0] for r in rows]

    def get_album_tracks(self, album_name: str) -> list[Track]:
        row = self.db.connection.execute(
            "SELECT id FROM custom_albums WHERE name = ?", (album_name,)
        ).fetchone()
        if not row:
            return []
        album_id = row[0]
        rows = self.db.connection.execute(
            "SELECT track_data FROM custom_album_tracks WHERE album_id = ? ORDER BY position",
            (album_id,),
        ).fetchall()
        tracks: list[Track] = []
        for r in rows:
            try:
                tracks.append(Track(**json.loads(r[0])))
            except Exception:
                continue
        return tracks


class AlbumsView(Static):
    """Render list of albums for selection."""

    def __init__(self, modal: AlbumsModal) -> None:
        super().__init__()
        self.modal = modal

    def render(self) -> Text:
        w = max(40, (self.size.width or 48) - 4)
        text = Text()

        header = "── My Albums ──"
        text.append(header.center(w) + "\n\n", style="bold #00ffcc")

        items = self.modal.get_items()
        for idx, item in enumerate(items):
            is_selected = idx == self.modal.selected_index
            prefix = " ▶ " if is_selected else "   "
            style = "bold white on #1a1a2e" if is_selected else "#c0c0c0"
            text.append(prefix, style="bold #00ffcc" if is_selected else "default")
            text.append(item, style=style)
            text.append("\n")

        text.append("\n")
        hints = Text()
        hints.append("↑↓", style="bold #00ffcc")
        hints.append(" nav   ")
        hints.append("Enter", style="bold #00ffcc")
        hints.append(" choose   ")
        hints.append("[m]", style="bold #00ffcc")
        hints.append(" modify   ")
        hints.append("[d]", style="bold #00ffcc")
        hints.append(" delete   ")
        hints.append("Esc", style="bold #00ffcc")
        hints.append(" cancel")
        text.append_text(hints)
        return text


class AlbumsModal(ModalScreen[str | None]):
    """Modal for creating, selecting, renaming, and deleting custom albums."""

    BINDINGS = [
        Binding("up", "prev_item", "Up", show=False),
        Binding("down", "next_item", "Down", show=False),
        Binding("enter", "select_item", "Select", show=False),
        Binding("m", "modify_item", "Modify", show=False),
        Binding("d", "delete_item", "Delete", show=False),
        Binding("escape", "cancel", "Cancel", show=False),
    ]

    DEFAULT_CSS = """
    AlbumsModal {
        align: center middle;
        background: rgba(0, 0, 0, 0.75);
    }

    #albums-container {
        width: 52;
        height: auto;
        border: solid #00ffcc;
        background: #0d0d15;
        padding: 1 2;
    }

    #album-input {
        margin-top: 1;
        border: solid #00ffcc;
        background: #05050a;
    }
    """

    def __init__(
        self,
        store: AlbumStore,
        target_track: Track | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self.store = store
        self.target_track = target_track
        self.selected_index = 0
        self.mode = "list"  # "list" | "create" | "rename"

    def get_items(self) -> list[str]:
        albums = self.store.list_albums()
        return albums + ["[+ New Album]"]

    def compose(self) -> ComposeResult:
        with Container(id="albums-container"):
            with Vertical():
                yield AlbumsView(self)
                input_w = Input(placeholder="Album name...", id="album-input")
                input_w.display = False
                yield input_w

    def _refresh_view(self) -> None:
        try:
            self.query_one(AlbumsView).refresh()
        except Exception:
            pass

    def action_next_item(self) -> None:
        if self.mode != "list":
            return
        total = len(self.get_items())
        if total > 0:
            self.selected_index = (self.selected_index + 1) % total
            self._refresh_view()

    def action_prev_item(self) -> None:
        if self.mode != "list":
            return
        total = len(self.get_items())
        if total > 0:
            self.selected_index = (self.selected_index - 1) % total
            self._refresh_view()

    def action_select_item(self) -> None:
        items = self.get_items()
        if not (0 <= self.selected_index < len(items)):
            return

        choice = items[self.selected_index]
        if choice == "[+ New Album]":
            self.mode = "create"
            inp = self.query_one(Input)
            inp.value = ""
            inp.placeholder = "Enter new album name..."
            inp.display = True
            inp.focus()
        else:
            # Picked existing album
            if self.target_track:
                self.store.add_track(choice, self.target_track)
            self.dismiss(choice)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        if text:
            if self.mode == "create":
                self.store.create_album(text)
                if self.target_track:
                    self.store.add_track(text, self.target_track)
                self.dismiss(text)
            elif self.mode == "rename":
                items = self.get_items()
                old_name = items[self.selected_index]
                self.store.rename_album(old_name, text)
                self.mode = "list"
                inp = self.query_one(Input)
                inp.display = False
                self._refresh_view()

    def action_modify_item(self) -> None:
        items = self.get_items()
        if 0 <= self.selected_index < len(items) and items[self.selected_index] != "[+ New Album]":
            self.mode = "rename"
            inp = self.query_one(Input)
            inp.value = items[self.selected_index]
            inp.display = True
            inp.focus()

    def action_delete_item(self) -> None:
        items = self.get_items()
        if 0 <= self.selected_index < len(items) and items[self.selected_index] != "[+ New Album]":
            album_to_del = items[self.selected_index]
            self.store.delete_album(album_to_del)
            self.selected_index = max(0, self.selected_index - 1)
            self._refresh_view()

    def action_cancel(self) -> None:
        if self.mode != "list":
            self.mode = "list"
            try:
                inp = self.query_one(Input)
                inp.display = False
            except Exception:
                pass
            self._refresh_view()
        else:
            self.dismiss(None)
