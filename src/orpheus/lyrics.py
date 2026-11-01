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


def clean_song_title(title: str) -> str:
    """Strip remix, lofi, cover, acoustic, and other version modifiers from song title."""
    if not title:
        return ""
    cleaned = title
    bracket_kw = "lofi|remix|acoustic|cover|live|version|speed|slowed|drill|edit|prod|feat|ft\\."
    bracket_pat = rf"\s*[\(\[](?:[^\)\]]*(?:{bracket_kw})[^\)\]]*?)[\)\]]"
    cleaned = re.sub(bracket_pat, "", cleaned, flags=re.IGNORECASE)

    dash_kw = "lofi|remix|acoustic|cover|live|version|speed|slowed|drill|edit"
    dash_pat = rf"\s*[-–—]\s*(?:{dash_kw}).*$"
    cleaned = re.sub(dash_pat, "", cleaned, flags=re.IGNORECASE)

    trail_kw = "|".join(
        [
            "lofi",
            "remix",
            "acoustic",
            "slowed",
            "reverb",
            "speed\\s*up",
            "cover",
            "karaoke",
            "instrumental",
            "live",
            "version",
        ]
    )
    trailing_pat = rf"\s+(?:{trail_kw})(?:[/\s].*)?$"
    cleaned = re.sub(trailing_pat, "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*[\(\[]\s*[\)\]]", "", cleaned)
    cleaned = cleaned.strip()
    return cleaned or title


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

        title_clean = clean_song_title(track.title) or track.title
        search_queries: list[dict[str, str]] = [{"all": title_clean}]
        if track.artist:
            search_queries.append({"track": title_clean, "artist": track.artist})
        search_queries.append({"track": title_clean})
        if track.title != title_clean:
            search_queries.append({"all": track.title})

        ua = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        base_params = {
            "reqtype": "default",
            "territory": "US",
            "searchtype": "track",
            "output": "json",
            "useragent": ua,
        }

        try:
            for q in search_queries:
                params = {**base_params, **q}
                resp = await self.lyricfind_client.get(
                    "https://lyrics.lyricfind.com/api/v1/search", params=params
                )
                if resp.status_code != 200:
                    continue
                try:
                    data = resp.json()
                except Exception:
                    continue

                tracks = data.get("tracks", [])
                if not isinstance(tracks, list):
                    continue

                for cand in tracks:
                    if not isinstance(cand, dict):
                        continue
                    c_title = cand.get("title", "")
                    c_artist = cand.get("artist", {}).get("name", "")
                    c_artists = [
                        a.get("name", "") for a in cand.get("artists", []) if isinstance(a, dict)
                    ]
                    matches = match_lyric_track(
                        title_clean, track.artist, c_title, c_artist
                    ) or any(
                        match_lyric_track(title_clean, track.artist, c_title, a_name)
                        for a_name in c_artists
                    )
                    if not matches and track.title != title_clean:
                        matches = match_lyric_track(track.title, track.artist, c_title, c_artist)

                    if matches:
                        raw_context = cand.get("context") or ""
                        plain_lyrics = ""
                        if raw_context:
                            plain_lyrics = re.sub(r"</?em>", "", raw_context).strip()
                        if not plain_lyrics:
                            plain_lyrics = (cand.get("lyrics") or "").strip()
                        if not plain_lyrics:
                            plain_lyrics = (cand.get("snippet") or "").strip()

                        if plain_lyrics:
                            return Lyrics(
                                plain=plain_lyrics,
                                synced="",
                                instrumental=bool(cand.get("instrumental", False)),
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

    async def _fetch_lyrics_network(self, track: Track) -> Lyrics | None:
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
            else:
                raise RuntimeError("Lyrics lookup unavailable; try again later") from exc

        # Prefer synchronized lyrics from LRCLIB; use LyricFind plain lyrics if available
        if lrclib_lyrics and lrclib_lyrics.synced:
            return Lyrics(
                plain=lrclib_lyrics.plain or (lf_lyrics.plain if lf_lyrics else ""),
                synced=lrclib_lyrics.synced,
                instrumental=lrclib_lyrics.instrumental,
            )
        elif lf_lyrics:
            return lf_lyrics
        return lrclib_lyrics

    async def get(self, track: Track) -> Lyrics | None:
        row = self.db.connection.execute(
            "SELECT result, expires_at FROM lyrics_cache WHERE track_id = ?", (track.id,)
        ).fetchone()
        if row and row[1] > time.time():
            return Lyrics(**json.loads(row[0])) if row[0] else None

        result: Lyrics | None = None
        try:
            result = await self._fetch_lyrics_network(track)
        except RuntimeError:
            if row:
                return Lyrics(**json.loads(row[0])) if row[0] else None
            raise

        # If lyrics not found for a remix/lofi version, search base title without duration limit
        if not result:
            clean_title = clean_song_title(track.title)
            if clean_title.casefold() != track.title.casefold():
                base_track = Track(
                    id=track.id,
                    title=clean_title,
                    location=track.location,
                    artist=track.artist,
                    album=track.album,
                    duration=None,
                    source=track.source,
                    license=track.license,
                    license_url=track.license_url,
                    attribution=track.attribution,
                    cover_url=track.cover_url,
                )
                try:
                    result = await self._fetch_lyrics_network(base_track)
                except Exception:
                    pass

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
