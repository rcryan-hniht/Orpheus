from __future__ import annotations

import asyncio
import json
import logging
import re
import unicodedata
import urllib.parse
from typing import Any

import httpx

from orpheus.models import Track

logger = logging.getLogger(__name__)


def _normalize_for_match(text: str) -> str:
    """Normalize text by NFKC, lowercasing, and removing punctuation."""
    if not text:
        return ""
    norm = unicodedata.normalize("NFKC", text).strip().casefold()
    clean = re.sub(r"[^\w\s]", "", norm)
    return " ".join(clean.split())


def _extract_base_title(title: str) -> str:
    """Strip bracketed/parenthetical additions (e.g., '(Remix)', '[Official]')."""
    stripped = re.sub(r"\(.*?\)|\[.*?\]", "", title)
    return _normalize_for_match(stripped)


def is_artist_query(query: str) -> bool:
    """Return True if query signifies an artist search (e.g. '@DangRangTo')."""
    q = query.strip()
    return q.startswith("@") or "@artist" in q.lower()


def extract_artist_name(query: str) -> str:
    """Extract clean artist name from query (stripping '@artist:' or leading '@')."""
    q = query.strip()
    clean = re.sub(r"^@artist:?\s*", "", q, flags=re.IGNORECASE)
    if clean == q:
        clean = re.sub(r"^@\s*", "", q)
    if clean == q:
        clean = re.sub(r"\s*@artist:?\s*", "", q, flags=re.IGNORECASE)
    return clean.strip()


def rank_tracks_by_query(tracks: list[Track], query: str) -> list[Track]:
    """Sort tracks so that songs matching the search query are ranked at the top.

    Priority tiers:
    0: Exact title match (e.g. query == "như một người rưng", track == "Như Một Người Rưng")
    1: Base title match without parenthesized remixes/features
    2: Title starts with query
    3: Query is a word/substring in title
    4: Query is found in artist name
    5: Remaining results (preserving provider ranking)
    """
    clean_q = _normalize_for_match(query)
    if not clean_q or not tracks:
        return tracks

    def score_track(item: tuple[int, Track]) -> tuple[int, int, int]:
        idx, track = item
        clean_title = _normalize_for_match(track.title)
        base_title = _extract_base_title(track.title)
        clean_artist = _normalize_for_match(track.artist)

        if clean_title == clean_q:
            tier = 0
        elif base_title == clean_q:
            tier = 1
        elif clean_title.startswith(clean_q):
            tier = 2
        elif clean_q in clean_title:
            tier = 3
        elif clean_q in clean_artist:
            tier = 4
        else:
            tier = 5

        len_diff = abs(len(clean_title) - len(clean_q))
        return (tier, len_diff, idx)

    indexed_tracks = list(enumerate(tracks))
    indexed_tracks.sort(key=score_track)
    return [t for _, t in indexed_tracks]


class DeezerProvider:
    """Provides metadata and related tracks from the public Deezer API."""

    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client
        self._owns_client = client is None
        self._cache: dict[str, list[Track]] = {}

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or getattr(self._client, "is_closed", False) is True:
            self._client = httpx.AsyncClient(timeout=10.0)
            self._owns_client = True
        return self._client

    async def close(self) -> None:
        if self._owns_client and self._client and not self._client.is_closed:
            await self._client.aclose()

    async def search(self, query: str, limit: int = 25) -> list[Track]:
        query = query.strip()
        if not query:
            return []
        if query in self._cache:
            return self._cache[query]

        client = await self._get_client()
        url = f"https://api.deezer.com/search?q={urllib.parse.quote(query)}&limit={limit}"
        try:
            resp = await client.get(url)
            if resp.status_code != 200:
                logger.warning("Deezer API search status: %s", resp.status_code)
                return []
            data = resp.json()
            items = data.get("data", [])
            tracks: list[Track] = []
            for item in items:
                artist_info = item.get("artist") or {}
                album_info = item.get("album") or {}
                tracks.append(
                    Track(
                        id=f"dz-{item.get('id')}",
                        title=item.get("title", "Unknown"),
                        location=item.get("link", ""),
                        artist=artist_info.get("name", ""),
                        album=album_info.get("title", ""),
                        duration=float(item.get("duration", 0)),
                        source="deezer",
                        cover_url=album_info.get("cover_medium") or album_info.get("cover", ""),
                    )
                )
            tracks = rank_tracks_by_query(tracks, query)
            self._cache[query] = tracks
            return tracks
        except Exception as exc:
            logger.error("Deezer search error: %s", exc)
            return []

    async def search_by_artist(self, artist_name: str, limit: int = 30) -> list[Track]:
        artist_name = artist_name.strip()
        if not artist_name:
            return []
        cache_key = f"@artist:{artist_name.casefold()}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        client = await self._get_client()
        q_enc = urllib.parse.quote(artist_name)
        tracks: list[Track] = []
        seen: set[str] = set()

        try:
            art_task = client.get(f"https://api.deezer.com/search/artist?q={q_enc}&limit=3")
            track_task = client.get(f"https://api.deezer.com/search?q={q_enc}&limit={limit}")
            art_resp, track_resp = await asyncio.gather(
                art_task, track_task, return_exceptions=True
            )

            # 1. From artist ID, fetch top tracks
            if not isinstance(art_resp, Exception) and art_resp.status_code == 200:
                artists = art_resp.json().get("data", [])
                if artists:
                    top_tasks = [
                        client.get(f"https://api.deezer.com/artist/{a.get('id')}/top?limit={limit}")
                        for a in artists[:2]
                    ]
                    top_resps = await asyncio.gather(*top_tasks, return_exceptions=True)
                    for tr in top_resps:
                        if not isinstance(tr, Exception) and tr.status_code == 200:
                            for item in tr.json().get("data", []):
                                tid = f"dz-{item.get('id')}"
                                if tid not in seen:
                                    seen.add(tid)
                                    art_info = item.get("artist") or {}
                                    alb_info = item.get("album") or {}
                                    tracks.append(
                                        Track(
                                            id=tid,
                                            title=item.get("title", "Unknown"),
                                            location=item.get("link", ""),
                                            artist=art_info.get("name", ""),
                                            album=alb_info.get("title", ""),
                                            duration=float(item.get("duration", 0)),
                                            source="deezer",
                                            cover_url=alb_info.get("cover_medium")
                                            or alb_info.get("cover", ""),
                                        )
                                    )

            # 2. From general track search, keep tracks where artist name matches
            if not isinstance(track_resp, Exception) and track_resp.status_code == 200:
                clean_target = _normalize_for_match(artist_name)
                for item in track_resp.json().get("data", []):
                    tid = f"dz-{item.get('id')}"
                    cand_artist = _normalize_for_match((item.get("artist") or {}).get("name", ""))
                    if clean_target in cand_artist and tid not in seen:
                        seen.add(tid)
                        art_info = item.get("artist") or {}
                        alb_info = item.get("album") or {}
                        tracks.append(
                            Track(
                                id=tid,
                                title=item.get("title", "Unknown"),
                                location=item.get("link", ""),
                                artist=art_info.get("name", ""),
                                album=alb_info.get("title", ""),
                                duration=float(item.get("duration", 0)),
                                source="deezer",
                                cover_url=alb_info.get("cover_medium") or alb_info.get("cover", ""),
                            )
                        )

            self._cache[cache_key] = tracks
            return tracks
        except Exception as exc:
            logger.error("Deezer search_by_artist error: %s", exc)
            return []

    async def get_related(self, artist_id: str, limit: int = 10) -> list[Track]:
        if not artist_id:
            return []
        client = await self._get_client()
        top_url = f"https://api.deezer.com/artist/{artist_id}/top?limit={limit}"
        try:
            resp = await client.get(top_url)
            if resp.status_code != 200:
                return []
            items = resp.json().get("data", [])
            tracks: list[Track] = []
            for item in items:
                artist_info = item.get("artist") or {}
                album_info = item.get("album") or {}
                tracks.append(
                    Track(
                        id=f"dz-{item.get('id')}",
                        title=item.get("title", "Unknown"),
                        location=item.get("link", ""),
                        artist=artist_info.get("name", ""),
                        album=album_info.get("title", ""),
                        duration=float(item.get("duration", 0)),
                        source="deezer",
                        cover_url=album_info.get("cover_medium") or album_info.get("cover", ""),
                    )
                )
            return tracks
        except Exception as exc:
            logger.error("Deezer related error: %s", exc)
            return []


class AudioResolver:
    """Resolves Deezer track metadata into playable direct stream URLs."""

    def __init__(self, jamendo_client_id: str = "") -> None:
        self.jamendo_client_id = jamendo_client_id
        self._url_cache: dict[str, tuple[str, str]] = {}

    async def resolve_stream_url(self, track: Track) -> tuple[str, str]:
        """Return (stream_url, source_name) or raise RuntimeError if resolution fails."""
        if track.id in self._url_cache:
            return self._url_cache[track.id]

        if track.is_local:
            return track.location, "local"

        if track.source in {"youtube", "web"} and track.location:
            direct_url = await self._extract_direct_stream_url(track.location)
            if direct_url:
                self._url_cache[track.id] = (direct_url, track.source)
                return direct_url, track.source

        # 1. Search YouTube candidates via yt-dlp with query prioritization
        queries = [
            f"{track.artist} {track.title}".strip(),
            f"{track.title} {track.artist}".strip(),
            f"{track.artist} - {track.title} audio".strip(),
        ]
        best_candidate: dict[str, Any] | None = None
        for q in queries:
            if not q:
                continue
            candidates = await self._fetch_youtube_candidates(q, limit=8)
            best_candidate = self._pick_best_candidate(candidates, track)
            if best_candidate:
                break

        if best_candidate and (best_candidate.get("url") or best_candidate.get("id")):
            video_url = (
                best_candidate.get("url")
                or f"https://www.youtube.com/watch?v={best_candidate['id']}"
            )
            direct_url = await self._extract_direct_stream_url(video_url)
            if direct_url:
                self._url_cache[track.id] = (direct_url, "youtube")
                return direct_url, "youtube"

        # 2. Fallback to Jamendo if configured
        if self.jamendo_client_id:
            jamendo_stream = await self._fetch_jamendo_stream(track)
            if jamendo_stream:
                self._url_cache[track.id] = (jamendo_stream, "jamendo")
                return jamendo_stream, "jamendo"

        raise RuntimeError(f"Could not resolve audio stream for track: {track.title}")

    async def _fetch_youtube_candidates(self, query: str, limit: int = 8) -> list[dict[str, Any]]:
        cmd = [
            "yt-dlp",
            f"ytsearch{limit}:{query}",
            "--dump-json",
            "--flat-playlist",
            "--no-warnings",
            "--quiet",
        ]
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=12.0)
            except TimeoutError:
                try:
                    proc.kill()
                    await proc.wait()
                except Exception:
                    pass
                logger.warning("yt-dlp search process timed out")
                return []

            candidates: list[dict[str, Any]] = []
            for line in stdout.decode("utf-8", errors="ignore").splitlines():
                line = line.strip()
                if line:
                    try:
                        candidates.append(json.loads(line))
                    except Exception:
                        continue
            return candidates
        except Exception as exc:
            logger.warning("yt-dlp search error: %s", exc)
            return []

    def _pick_best_candidate(
        self, candidates: list[dict[str, Any]], track: Track
    ) -> dict[str, Any] | None:
        if not candidates:
            return None

        best_score = -999.0
        best_cand: dict[str, Any] | None = None

        clean_track_title = _normalize_for_match(track.title)
        clean_track_artist = _normalize_for_match(track.artist)
        target_dur = track.duration or 0.0

        for cand in candidates:
            cand_raw_title = cand.get("title") or ""
            cand_raw_channel = cand.get("channel") or cand.get("uploader") or ""
            cand_title_norm = _normalize_for_match(cand_raw_title)
            cand_channel_norm = _normalize_for_match(cand_raw_channel)
            cand_dur = float(cand.get("duration") or 0.0)

            dur_diff = abs(cand_dur - target_dur) if target_dur > 0 and cand_dur > 0 else 0.0
            is_topic = "topic" in cand_channel_norm

            title_matched = (
                clean_track_title in cand_title_norm or cand_title_norm in clean_track_title
            )
            artist_matched = (
                clean_track_artist in cand_title_norm or clean_track_artist in cand_channel_norm
            )

            # Duration rejection: allow MV intro/dialogue up to 45s when title/artist match
            if target_dur > 0:
                max_diff = (
                    45.0 if (title_matched and artist_matched) else 30.0 if title_matched else 15.0
                )
                if dur_diff > max_diff and not is_topic:
                    continue
                if dur_diff > 60.0:
                    continue

            score = 100.0 - dur_diff * 1.5
            if title_matched:
                score += 35.0
            if artist_matched:
                score += 25.0
            if is_topic:
                score += 25.0

            # Exclude live, cover, remix unless track title explicitly has them
            for bad_word in ["live", "cover", "remix", "karaoke", "instrumental"]:
                if bad_word in cand_title_norm and bad_word not in clean_track_title:
                    score -= 40.0

            if score > best_score:
                best_score = score
                best_cand = cand

        return best_cand

        return best_cand

    async def _extract_direct_stream_url(self, video_url: str) -> str:
        cmd = [
            "yt-dlp",
            "-f",
            "bestaudio/best",
            "-g",
            "--no-warnings",
            "--quiet",
            "--",
            video_url,
        ]
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=12.0)
            except TimeoutError:
                try:
                    proc.kill()
                    await proc.wait()
                except Exception:
                    pass
                logger.warning("yt-dlp stream extraction timed out")
                return ""

            url = stdout.decode("utf-8", errors="ignore").strip().splitlines()
            return url[0] if url else ""
        except Exception as exc:
            logger.warning("yt-dlp stream extraction error: %s", exc)
            return ""

    async def _fetch_jamendo_stream(self, track: Track) -> str | None:
        url = (
            f"https://api.jamendo.com/v3.0/tracks?"
            f"client_id={self.jamendo_client_id}&namesearch={urllib.parse.quote(track.title)}"
            f"&artist_name={urllib.parse.quote(track.artist)}&format=json&limit=1"
        )
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    results = resp.json().get("results", [])
                    if results and results[0].get("audio"):
                        return results[0]["audio"]
        except Exception as exc:
            logger.warning("Jamendo fetch error: %s", exc)
        return None
