from __future__ import annotations

import asyncio
import json
import logging
import urllib.parse
from typing import Any

import httpx

from orpheus.models import Track

logger = logging.getLogger(__name__)


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
            self._cache[query] = tracks
            return tracks
        except Exception as exc:
            logger.error("Deezer search error: %s", exc)
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

        # 1. Search YouTube candidates via yt-dlp
        query = f"{track.artist} - {track.title} audio".strip()
        candidates = await self._fetch_youtube_candidates(query)
        best_candidate = self._pick_best_candidate(candidates, track)

        if best_candidate and (best_candidate.get("url") or best_candidate.get("id")):
            video_url = best_candidate.get("url") or f"https://www.youtube.com/watch?v={best_candidate['id']}"
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

    async def _fetch_youtube_candidates(self, query: str) -> list[dict[str, Any]]:
        cmd = [
            "yt-dlp",
            f"ytsearch5:{query}",
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
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=12.0)
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

        track_title_lower = track.title.lower()
        track_artist_lower = track.artist.lower()
        target_dur = track.duration or 0.0

        for cand in candidates:
            cand_title = (cand.get("title") or "").lower()
            cand_channel = (cand.get("channel") or cand.get("uploader") or "").lower()
            cand_dur = float(cand.get("duration") or 0.0)

            dur_diff = abs(cand_dur - target_dur) if target_dur > 0 and cand_dur > 0 else 0.0
            is_topic = "topic" in cand_channel

            # Strict duration rejection:
            # <= 5s is fine. If topic channel, accept up to 15s. Otherwise penalize heavily.
            if target_dur > 0:
                if dur_diff > 15.0 and not is_topic:
                    continue
                if dur_diff > 30.0:
                    continue

            score = 100.0 - dur_diff * 2.0
            if track_title_lower in cand_title:
                score += 30.0
            if track_artist_lower in cand_title or track_artist_lower in cand_channel:
                score += 20.0
            if is_topic:
                score += 25.0

            # Exclude live, cover, remix unless track title explicitly has them
            for bad_word in ["live", "cover", "remix", "karaoke", "instrumental"]:
                if bad_word in cand_title and bad_word not in track_title_lower:
                    score -= 40.0

            if score > best_score:
                best_score = score
                best_cand = cand

        return best_cand

    async def _extract_direct_stream_url(self, video_url: str) -> str:
        cmd = [
            "yt-dlp",
            "-f",
            "bestaudio/best",
            "-g",
            "--no-warnings",
            "--quiet",
            video_url,
        ]
        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=12.0)
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
