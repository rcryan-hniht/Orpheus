from dataclasses import dataclass


@dataclass(frozen=True)
class Track:
    id: str
    title: str
    location: str
    artist: str = ""
    album: str = ""
    duration: float | None = None
    source: str = "local"
    license: str = ""
    license_url: str = ""
    attribution: str = ""

    @property
    def is_local(self) -> bool:
        return self.source == "local"

    @property
    def playable(self) -> bool:
        return self.source in {"local", "licensed"}


@dataclass(frozen=True)
class PlaybackState:
    position: float = 0.0
    duration: float = 0.0
    paused: bool = False
    idle: bool = True
    volume: float = 100.0
    ended: bool = False


@dataclass(frozen=True)
class Lyrics:
    plain: str = ""
    synced: str = ""
    instrumental: bool = False


@dataclass(frozen=True)
class LyricsMatch:
    title: str
    artist: str
    album: str
    duration: float | None
    lyrics: Lyrics
