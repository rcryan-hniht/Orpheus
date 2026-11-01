from __future__ import annotations

import bisect
import json
import math
import re
import time
import unicodedata
from dataclasses import asdict, dataclass
from difflib import SequenceMatcher

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


def normalize_lyric_match_text(text: str) -> str:
    """Normalize text for lyrics matching (accents, casing, punctuation stripped)."""
    if not text:
        return ""
    norm = unicodedata.normalize("NFKC", text).strip().casefold()
    clean = re.sub(r"\(.*?\)|\[.*?\]", "", norm)
    clean = re.sub(r"[^\w\s]", "", clean)
    return " ".join(clean.split())


def match_lyric_track(
    track_title: str, track_artist: str, candidate_title: str, candidate_artist: str
) -> bool:
    """Verify whether a candidate track strictly matches the requested song."""
    c_title_norm = normalize_lyric_match_text(candidate_title)
    t_title_norm = normalize_lyric_match_text(track_title)

    if not c_title_norm or not t_title_norm:
        return False

    if (
        c_title_norm == t_title_norm
        or c_title_norm.startswith(t_title_norm)
        or t_title_norm.startswith(c_title_norm)
        or t_title_norm in c_title_norm
        or c_title_norm in t_title_norm
    ):
        title_matches = True
    else:
        title_matches = SequenceMatcher(None, t_title_norm, c_title_norm).ratio() >= 0.75

    if not title_matches:
        return False

    t_artist_norm = normalize_lyric_match_text(track_artist)
    c_artist_norm = normalize_lyric_match_text(candidate_artist)
    if t_artist_norm and c_artist_norm:
        if (
            t_artist_norm == c_artist_norm
            or t_artist_norm in c_artist_norm
            or c_artist_norm in t_artist_norm
        ):
            artist_matches = True
        else:
            artist_matches = SequenceMatcher(None, t_artist_norm, c_artist_norm).ratio() >= 0.60
    else:
        artist_matches = True

    return title_matches and artist_matches


class LyricsService:
    def __init__(
        self,
        db: Database,
        client: httpx.AsyncClient | None = None,
        lyricfind_client: httpx.AsyncClient | None = None,
    ):
        self.db = db
        self.client = client or httpx.AsyncClient(
            timeout=8,
            headers={"User-Agent": "Orpheus/0.1 (lyrics lookup; https://lrclib.net)"},
        )
        if lyricfind_client is not None:
            self.lyricfind_client = lyricfind_client
            self._owns_lf_client = False
        elif client is None:
            self.lyricfind_client = httpx.AsyncClient(
                timeout=8,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (X11; Linux x86_64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
                    ),
                    "Accept": "application/json, text/html;q=0.9",
                },
            )
            self._owns_lf_client = True
        else:
            self.lyricfind_client = None
            self._owns_lf_client = False

    async def fetch_lyricfind(self, track: Track) -> Lyrics | None:
        """Search and retrieve matched song lyrics from https://lyrics.lyricfind.com/."""
        if not self.lyricfind_client or not track.title:
            return None
        query = f"{track.title} {track.artist}".strip()
        params = {
            "reqtype": "default",
            "territory": "US",
            "searchtype": "track",
            "all": query,
            "alltracks": "no",
            "output": "json",
            "useragent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        }
        try:
            resp = await self.lyricfind_client.get(
                "https://lyrics.lyricfind.com/api/v1/search", params=params
            )
            if resp.status_code != 200:
                return None
            data = resp.json()
            tracks = data.get("tracks", [])
            matched_candidate = None
            for cand in tracks:
                c_title = cand.get("title", "")
                c_artist = cand.get("artist", {}).get("name", "")
                if match_lyric_track(track.title, track.artist, c_title, c_artist):
                    matched_candidate = cand
                    break

            if not matched_candidate:
                return None

            plain_lyrics = matched_candidate.get("lyrics") or ""
            slug = matched_candidate.get("slug")
            if not plain_lyrics and slug:
                try:
                    page_resp = await self.lyricfind_client.get(
                        f"https://lyrics.lyricfind.com/lyrics/{slug}",
                        follow_redirects=True,
                    )
                    if page_resp.status_code == 200:
                        from bs4 import BeautifulSoup

                        soup = BeautifulSoup(page_resp.text, "html.parser")
                        tag = soup.find("script", id="__NEXT_DATA__")
                        if tag and tag.string:
                            next_data = json.loads(tag.string)
                            plain_lyrics = (
                                next_data.get("props", {})
                                .get("pageProps", {})
                                .get("songData", {})
                                .get("track", {})
                                .get("lyrics", "")
                            )
                except Exception:
                    pass

            if not plain_lyrics:
                snippet = matched_candidate.get("snippet", "")
                if snippet:
                    plain_lyrics = snippet.strip()

            if plain_lyrics:
                return Lyrics(
                    plain=plain_lyrics,
                    synced="",
                    instrumental=bool(matched_candidate.get("instrumental", False)),
                )
            return None
        except Exception:
            return None

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
                        title,
                        artist,
                        album,
                        duration,
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

        # 1. Search LyricFind
        lf_lyrics: Lyrics | None = None
        try:
            lf_lyrics = await self.fetch_lyricfind(track)
        except Exception:
            pass

        # 2. Search LRCLIB
        lrclib_lyrics: Lyrics | None = None
        params = {"track_name": track.title, "artist_name": track.artist}
        if track.album:
            params["album_name"] = track.album
        if track.duration is not None:
            params["duration"] = int(track.duration)
        try:
            response = await self.client.get("https://lrclib.net/api/get", params=params)
            if response.status_code == 404:
                lrclib_lyrics = None
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
                lrclib_lyrics = Lyrics(
                    plain=data.get("plainLyrics") or "",
                    synced=data.get("syncedLyrics") or "",
                    instrumental=bool(data.get("instrumental", False)),
                )
        except (httpx.HTTPError, ValueError) as exc:
            if lf_lyrics:
                lrclib_lyrics = None
            elif row:
                return Lyrics(**json.loads(row[0])) if row[0] else None
            else:
                raise RuntimeError("Lyrics lookup unavailable; try again later") from exc

        # Prefer synchronized lyrics from LRCLIB; use LyricFind plain lyrics if available
        if lrclib_lyrics and lrclib_lyrics.synced:
            result = Lyrics(
                plain=lrclib_lyrics.plain or (lf_lyrics.plain if lf_lyrics else ""),
                synced=lrclib_lyrics.synced,
                instrumental=lrclib_lyrics.instrumental,
            )
        elif lf_lyrics:
            result = lf_lyrics
        else:
            result = lrclib_lyrics

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
        if self._owns_lf_client and self.lyricfind_client:
            await self.lyricfind_client.aclose()
