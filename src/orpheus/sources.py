import asyncio
import hashlib
import html
import json
import math
from pathlib import Path
from urllib.parse import parse_qs, urlparse

import httpx
from mutagen import File as AudioFile
from mutagen import MutagenError

from .models import Track

_AUDIO_SUFFIXES = {".mp3", ".m4a", ".mp4", ".flac", ".ogg", ".opus", ".wav", ".aiff", ".ape"}


def _matches(track: Track, query: str) -> bool:
    return query.casefold() in " ".join((track.title, track.artist, track.album)).casefold()


class LocalProvider:
    def __init__(self, root: Path):
        self.root = Path(root)

    async def search(self, query: str = "") -> list[Track]:
        return await asyncio.to_thread(self._scan, query)

    def _scan(self, query: str) -> list[Track]:
        if not self.root.is_dir():
            return []
        tracks = []
        for path in sorted(self.root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in _AUDIO_SUFFIXES:
                continue
            try:
                audio = AudioFile(path, easy=True)
                if audio is None or audio.info is None:
                    continue
                tags = audio.tags or {}
                title = tags.get("title", [path.stem])[0]
                artist = tags.get("artist", [""])[0]
                album = tags.get("album", [""])[0]
                location = str(path.resolve())
                track = Track(
                    id="local:" + hashlib.sha256(location.encode()).hexdigest(),
                    title=str(title),
                    location=location,
                    artist=str(artist),
                    album=str(album),
                    duration=float(audio.info.length),
                )
                if _matches(track, query):
                    tracks.append(track)
            except (OSError, ValueError, TypeError, KeyError, MutagenError):
                continue
        return tracks


def _safe_url(value: str, *, media: bool) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or not host or parsed.username or parsed.password:
        return False
    if media:
        if host in {
            "youtube.com",
            "youtube-nocookie.com",
            "youtu.be",
            "googlevideo.com",
        } or host.endswith((".youtube.com", ".youtube-nocookie.com", ".googlevideo.com")):
            return False
        if Path(parsed.path).suffix.lower() not in _AUDIO_SUFFIXES:
            return False
    return True


class LicensedCatalogProvider:
    def __init__(self, manifest: Path):
        self.manifest = Path(manifest)

    async def search(self, query: str = "") -> list[Track]:
        return await asyncio.to_thread(self._load, query)

    def _load(self, query: str) -> list[Track]:
        try:
            entries = json.loads(self.manifest.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"Invalid catalog: {exc}") from exc
        if not isinstance(entries, list):
            raise ValueError("Invalid catalog: expected a list of tracks")
        tracks = []
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict) or not all(
                isinstance(entry.get(field), str) and entry[field].strip()
                for field in ("title", "url", "license", "license_url", "attribution")
            ):
                raise ValueError(
                    f"Invalid catalog entry {index + 1}: "
                    "title, url and license attribution are required"
                )
            if not _safe_url(entry["url"], media=True) or not _safe_url(
                entry["license_url"], media=False
            ):
                raise ValueError(
                    f"Invalid catalog entry {index + 1}: use HTTPS audio and license URLs"
                )
            duration = entry.get("duration")
            if duration is not None and (
                isinstance(duration, bool)
                or not isinstance(duration, (float, int))
                or not math.isfinite(duration)
                or duration < 0
            ):
                raise ValueError(
                    f"Invalid catalog entry {index + 1}: duration must be nonnegative seconds"
                )
            url = entry["url"]
            track = Track(
                id="licensed:" + hashlib.sha256(url.encode()).hexdigest(),
                title=entry["title"],
                location=url,
                artist=str(entry.get("artist") or ""),
                album=str(entry.get("album") or ""),
                duration=duration,
                source="licensed",
                license=entry["license"],
                license_url=entry["license_url"],
                attribution=entry["attribution"],
            )
            if _matches(track, query):
                tracks.append(track)
        return tracks


class YouTubeMetadataProvider:
    def __init__(self, api_key: str, client: httpx.AsyncClient | None = None):
        self.api_key = api_key
        self.client = client or httpx.AsyncClient(timeout=8)

    async def search(self, query: str) -> list[Track]:
        if not self.api_key:
            raise RuntimeError("YouTube Data API key is not configured")
        response = await self.client.get(
            "https://www.googleapis.com/youtube/v3/search",
            params={
                "part": "snippet",
                "type": "video",
                "maxResults": 20,
                "q": query,
                "key": self.api_key,
            },
        )
        response.raise_for_status()
        tracks = []
        for item in response.json().get("items", []):
            video_id = item.get("id", {}).get("videoId")
            snippet = item.get("snippet", {})
            if video_id and snippet.get("title"):
                tracks.append(
                    Track(
                        id="youtube:" + video_id,
                        title=html.unescape(snippet["title"]),
                        location="https://music.youtube.com/watch?v=" + video_id,
                        source="youtube",
                    )
                )
        return tracks

    async def close(self) -> None:
        await self.client.aclose()


def create_web_track(url: str) -> Track | None:
    if not isinstance(url, str):
        return None
    url = url.strip()
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        return None

    host = parsed.hostname.lower()
    if host in {"youtube.com", "www.youtube.com", "music.youtube.com", "m.youtube.com"}:
        qs = parse_qs(parsed.query)
        video_id = qs.get("v", [""])[0]
        if video_id:
            return Track(
                id=f"youtube:{video_id}",
                title=url,
                location=url,
                artist="YouTube",
                source="youtube",
            )
    elif host in {"youtu.be", "www.youtu.be"}:
        video_id = parsed.path.strip("/")
        if video_id:
            return Track(
                id=f"youtube:{video_id}",
                title=url,
                location=url,
                artist="YouTube",
                source="youtube",
            )

    path_name = Path(parsed.path).name
    title = path_name if path_name else url
    track_id = f"web:{hashlib.sha256(url.encode()).hexdigest()[:16]}"
    return Track(
        id=track_id,
        title=title,
        location=url,
        artist="Web Audio",
        source="web",
        attribution="Web Stream",
    )
