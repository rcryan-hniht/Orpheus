import json
import sqlite3
from dataclasses import asdict
from pathlib import Path

from .models import Track


class Database:
    def __init__(self, path: Path):
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(path)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS delays (track_id TEXT PRIMARY KEY, seconds REAL NOT NULL)"
        )
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS queue (position INTEGER PRIMARY KEY, track TEXT NOT NULL)"
        )
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS lyrics_cache "
            "(track_id TEXT PRIMARY KEY, result TEXT, expires_at REAL NOT NULL)"
        )
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL)"
        )
        self.connection.commit()

    def get_theme(self) -> str | None:
        row = self.connection.execute("SELECT value FROM settings WHERE key = 'theme'").fetchone()
        return row[0] if row else None

    def set_theme(self, name: str) -> None:
        with self.connection:
            self.connection.execute(
                "INSERT INTO settings (key, value) VALUES ('theme', ?) "
                "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
                (name,),
            )

    def get_delay(self, track_id: str) -> float:
        row = self.connection.execute(
            "SELECT seconds FROM delays WHERE track_id = ?", (track_id,)
        ).fetchone()
        return row[0] if row else 0.0

    def set_delay(self, track_id: str, seconds: float) -> None:
        with self.connection:
            self.connection.execute(
                "INSERT OR REPLACE INTO delays VALUES (?, ?)", (track_id, seconds)
            )

    def load_queue(self) -> list[Track]:
        rows = self.connection.execute("SELECT track FROM queue ORDER BY position").fetchall()
        return [Track(**json.loads(row[0])) for row in rows]

    def save_queue(self, tracks: list[Track]) -> None:
        with self.connection:
            self.connection.execute("DELETE FROM queue")
            self.connection.executemany(
                "INSERT INTO queue VALUES (?, ?)",
                ((position, json.dumps(asdict(track))) for position, track in enumerate(tracks)),
            )

    def close(self) -> None:
        self.connection.close()
