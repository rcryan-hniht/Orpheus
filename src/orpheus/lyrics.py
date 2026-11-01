import bisect
import json
import math
import re
import time
from dataclasses import asdict, dataclass

import httpx

from .models import Lyrics, LyricsMatch, Track
from .storage import Database


@dataclass(frozen=True)
class LyricLine:
    time: float
    text: str


_TIMESTAMP = re.compile(r"\[(\d+):(\d{2})(?:\.(\d{1,3}))?\]")
_OFFSET = re.compile(r"\[offset:([+-]?\d+)\]", re.IGNORECASE)


def parse_lrc(content: str) -> list[LyricLine]:
    offset = _OFFSET.search(content)
    seconds_offset = int(offset.group(1)) / 1000 if offset else 0.0
    lines = []
    for line in content.splitlines():
        stamps = list(_TIMESTAMP.finditer(line))
        if not stamps:
            continue
        text = _TIMESTAMP.sub("", line).strip()
        for stamp in stamps:
            fraction = (stamp.group(3) or "").ljust(3, "0")
            seconds = int(stamp.group(1)) * 60 + int(stamp.group(2)) + int(fraction or 0) / 1000
            lines.append(LyricLine(max(0.0, seconds + seconds_offset), text))
    return sorted(lines, key=lambda line: line.time)


def active_line(lines: list[LyricLine], position: float, delay: float = 0.0) -> int:
    return bisect.bisect_right([line.time for line in lines], position - delay) - 1


class LyricsService:
    def __init__(self, db: Database, client: httpx.AsyncClient | None = None):
        self.db = db
        self.client = client or httpx.AsyncClient(
            timeout=8,
            headers={"User-Agent": "Orpheus/0.1 (lyrics lookup; https://lrclib.net)"},
        )

    async def search(self, query: str) -> list[LyricsMatch]:
        query = query.strip()
        if not query:
            return []
        try:
            response = await self.client.get("https://lrclib.net/api/search", params={"q": query})
            response.raise_for_status()
            records = response.json()
            if not isinstance(records, list):
                raise ValueError("invalid search response")
            matches = []
            for record in records[:20]:
                if not isinstance(record, dict):
                    raise ValueError("invalid search record")
                title = record.get("trackName")
                artist = record.get("artistName")
                album = record.get("albumName")
                duration = record.get("duration")
                plain = record.get("plainLyrics")
                synced = record.get("syncedLyrics")
                instrumental = record.get("instrumental")
                if (
                    not all(isinstance(value, str) for value in (title, artist, album))
                    or duration is not None
                    and (
                        isinstance(duration, bool)
                        or not isinstance(duration, (int, float))
                        or not math.isfinite(duration)
                        or duration < 0
                    )
                    or not isinstance(plain, (str, type(None)))
                    or not isinstance(synced, (str, type(None)))
                    or not isinstance(instrumental, bool)
                ):
                    raise ValueError("invalid search record fields")
                matches.append(
                    LyricsMatch(
                        title, artist, album, duration,
                        Lyrics(plain or "", synced or "", instrumental),
                    )
                )
            return matches
        except (httpx.HTTPError, ValueError) as exc:
            raise RuntimeError("Lyrics search unavailable; try again later") from exc

    def get_cached(self, track: Track) -> Lyrics | None:
        row = self.db.connection.execute(
            "SELECT result FROM lyrics_cache WHERE track_id = ? AND expires_at > ?",
            (track.id, time.time()),
        ).fetchone()
        return Lyrics(**json.loads(row[0])) if row and row[0] else None

    def cache_selection(self, track: Track, lyrics: Lyrics) -> None:
        with self.db.connection:
            self.db.connection.execute(
                "INSERT OR REPLACE INTO lyrics_cache VALUES (?, ?, ?)",
                (track.id, json.dumps(asdict(lyrics)), time.time() + 30 * 24 * 3600),
            )

    async def get(self, track: Track) -> Lyrics | None:
        row = self.db.connection.execute(
            "SELECT result, expires_at FROM lyrics_cache WHERE track_id = ?", (track.id,)
        ).fetchone()
        if row and row[1] > time.time():
            return Lyrics(**json.loads(row[0])) if row[0] else None

        params = {"track_name": track.title, "artist_name": track.artist}
        if track.album:
            params["album_name"] = track.album
        if track.duration is not None:
            params["duration"] = int(track.duration)
        try:
            response = await self.client.get("https://lrclib.net/api/get", params=params)
            if response.status_code == 404:
                result = None
            else:
                response.raise_for_status()
                data = response.json()
                if not isinstance(data, dict):
                    raise ValueError("invalid lyrics response")
                if (
                    not isinstance(data.get("plainLyrics"), (str, type(None)))
                    or not isinstance(data.get("syncedLyrics"), (str, type(None)))
                    or not isinstance(data.get("instrumental", False), bool)
                ):
                    raise ValueError("invalid lyrics fields")
                result = Lyrics(
                    plain=data.get("plainLyrics") or "",
                    synced=data.get("syncedLyrics") or "",
                    instrumental=bool(data.get("instrumental", False)),
                )
        except (httpx.HTTPError, ValueError) as exc:
            if row:
                return Lyrics(**json.loads(row[0])) if row[0] else None
            raise RuntimeError("Lyrics lookup unavailable; try again later") from exc
        with self.db.connection:
            self.db.connection.execute(
                "INSERT OR REPLACE INTO lyrics_cache VALUES (?, ?, ?)",
                (
                    track.id,
                    json.dumps(asdict(result)) if result else None,
                    time.time() + (30 * 24 * 3600 if result else 24 * 3600),
                ),
            )
        return result

    async def close(self) -> None:
        await self.client.aclose()
