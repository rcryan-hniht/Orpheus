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
                self.db.connection.execute("DELETE FROM custom_albums WHERE id = ?", (album_id,))

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
                self.db.connection.execute(
                    "DELETE FROM custom_album_tracks WHERE album_id = ? AND track_id = ?",
                    (album_id, track.id),
                )
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

    def remove_track(self, album_name: str, track_id: str) -> None:
        """Remove a track from a custom album."""
        with self.db.connection:
            row = self.db.connection.execute(
                "SELECT id FROM custom_albums WHERE name = ?", (album_name,)
            ).fetchone()
            if row:
                album_id = row[0]
                self.db.connection.execute(
                    "DELETE FROM custom_album_tracks WHERE album_id = ? AND track_id = ?",
                    (album_id, track_id),
                )

    def list_albums(self) -> list[str]:
        """List albums ordered by creation order (queue / FIFO)."""
        rows = self.db.connection.execute(
            "SELECT name FROM custom_albums ORDER BY id ASC"
        ).fetchall()
        return [r[0] for r in rows]

    def get_album_tracks(self, album_name: str) -> list[Track]:
        """Get tracks for an album ordered by addition order (queue / FIFO)."""
        row = self.db.connection.execute(
            "SELECT id FROM custom_albums WHERE name = ?", (album_name,)
        ).fetchone()
        if not row:
            return []
        album_id = row[0]
        rows = self.db.connection.execute(
            "SELECT track_data FROM custom_album_tracks "
            "WHERE album_id = ? ORDER BY position ASC, rowid ASC",
            (album_id,),
        ).fetchall()
        tracks: list[Track] = []
        for r in rows:
            try:
                tracks.append(Track(**json.loads(r[0])))
            except Exception:
                continue
        return tracks

    def find_album_for_track(self, track_id: str) -> tuple[str, list[Track]] | None:
        """Find custom album containing this track and return (album_name, tracks)."""
        row = self.db.connection.execute(
            "SELECT a.name FROM custom_albums a "
            "JOIN custom_album_tracks t ON a.id = t.album_id "
            "WHERE t.track_id = ? LIMIT 1",
            (track_id,),
        ).fetchone()
        if not row:
            return None
        album_name = row[0]
        tracks = self.get_album_tracks(album_name)
        return album_name, tracks


class AlbumsView(Static):
    """Render list of albums for selection."""

    can_focus = True

    def __init__(self, modal: AlbumsModal) -> None:
        super().__init__()
        self.modal = modal

    def _get_theme_styles(self) -> tuple[str, str, str, str, bool]:
        accent = "#00ffcc"
        fg = "#ffffff"
        panel = "#1a1a2e"
        surface = "#0d0d15"
        is_dark = True
        try:
            if hasattr(self.app, "current_theme") and self.app.current_theme:
                theme = self.app.current_theme
                is_dark = getattr(theme, "dark", True)
                accent = str(getattr(theme, "accent", None) or getattr(theme, "primary", "#00ffcc"))
                fg = str(getattr(theme, "foreground", "#ffffff" if is_dark else "#0b2545"))
                panel = str(getattr(theme, "panel", "#1a1a2e" if is_dark else "#d2e5ed"))
                surface = str(getattr(theme, "surface", "#0d0d15" if is_dark else "#e1eff5"))
        except Exception:
            pass
        return accent, fg, panel, surface, is_dark

    def render(self) -> Text:
        accent, fg, panel, _surface, is_dark = self._get_theme_styles()
        w = max(40, (self.size.width or 52) - 4)
        text = Text()

        header = "── My Albums ──"
        text.append(header.center(w) + "\n\n", style=f"bold {accent}")

        items = self.modal.get_items()
        for idx, item in enumerate(items):
            is_selected = idx == self.modal.selected_index
            prefix = " ▶ " if is_selected else "   "
            if is_selected:
                style = f"bold {fg} on {panel}"
                prefix_style = f"bold {accent}"
            else:
                style = f"{fg}" if is_dark else "dim"
                prefix_style = "default"

            text.append(prefix, style=prefix_style)
            text.append(item, style=style)
            text.append("\n")

        text.append("\n")
        hints = Text()
        hints.append("↑↓", style=f"bold {accent}")
        hints.append(" Nav  ")
        hints.append("Enter", style=f"bold {accent}")
        hints.append(" Choose  ")
        hints.append("[:]", style=f"bold {accent}")
        hints.append(" New  ")
        hints.append("[m]", style=f"bold {accent}")
        hints.append(" Rename  ")
        hints.append("[d]", style=f"bold {accent}")
        hints.append(" Del  ")
        hints.append("Esc", style=f"bold {accent}")
        hints.append(" Cancel")
        text.append_text(hints)
        return text


class AlbumsModal(ModalScreen[str | None]):
    """Modal for creating, selecting, renaming, and deleting custom albums."""

    BINDINGS = [
        Binding("up", "prev_item", "Up", show=False),
        Binding("down", "next_item", "Down", show=False),
        Binding("enter", "select_item", "Select", show=False),
        Binding("colon", "create_mode", "New Album", show=False),
        Binding("c", "create_mode", "New Album", show=False),
        Binding("m", "modify_item", "Modify", show=False),
        Binding("d", "delete_item", "Delete", show=False),
        Binding("escape", "cancel", "Cancel", show=False),
    ]

    DEFAULT_CSS = """
    AlbumsModal {
        align: center middle;
        background: rgba(0, 0, 0, 0.65);
    }

    #albums-container {
        width: 58;
        height: auto;
        border: solid $accent;
        background: $surface;
        color: $foreground;
        padding: 1 2;
    }

    #album-input {
        margin-top: 1;
        border: solid $accent;
        background: $panel;
        color: $foreground;
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

    def on_mount(self) -> None:
        try:
            self.query_one(AlbumsView).focus()
        except Exception:
            pass

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

    def action_create_mode(self) -> None:
        self.mode = "create"
        inp = self.query_one(Input)
        inp.value = ""
        inp.placeholder = "Enter new album name..."
        inp.display = True
        inp.focus()

    def action_select_item(self) -> None:
        items = self.get_items()
        if not (0 <= self.selected_index < len(items)):
            return

        choice = items[self.selected_index]
        if choice == "[+ New Album]":
            self.action_create_mode()
        else:
            # Picked existing album
            if self.target_track:
                self.store.add_track(choice, self.target_track)
                try:
                    self.app.notify(
                        f"Added '{self.target_track.title}' to '{choice}'",
                        title="Album Updated",
                        timeout=3.0,
                        markup=False,
                    )
                except Exception:
                    pass
            self.dismiss(choice)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        if text:
            if self.mode == "create":
                self.store.create_album(text)
                if self.target_track:
                    self.store.add_track(text, self.target_track)
                    try:
                        self.app.notify(
                            f"Added '{self.target_track.title}' to '{text}'",
                            title="Album Created",
                            timeout=3.0,
                            markup=False,
                        )
                    except Exception:
                        pass
                self.dismiss(text)
            elif self.mode == "rename":
                items = self.get_items()
                old_name = items[self.selected_index]
                self.store.rename_album(old_name, text)
                self.mode = "list"
                inp = self.query_one(Input)
                inp.display = False
                try:
                    self.query_one(AlbumsView).focus()
                except Exception:
                    pass
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
            try:
                self.app.notify(
                    f"Deleted album '{album_to_del}'",
                    title="Album Deleted",
                    timeout=3.0,
                    markup=False,
                )
            except Exception:
                pass

    def action_cancel(self) -> None:
        if self.mode != "list":
            self.mode = "list"
            try:
                inp = self.query_one(Input)
                inp.display = False
                self.query_one(AlbumsView).focus()
            except Exception:
                pass
            self._refresh_view()
        else:
            self.dismiss(None)
