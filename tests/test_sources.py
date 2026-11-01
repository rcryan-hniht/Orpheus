import asyncio
import json
import wave

import httpx
import pytest

from orpheus.sources import LicensedCatalogProvider, LocalProvider, YouTubeMetadataProvider


def test_local_search_recurses_and_skips_invalid_audio(tmp_path):
    album = tmp_path / "album"
    album.mkdir()
    with wave.open(str(album / "Hello.wav"), "wb") as sound:
        sound.setnchannels(1)
        sound.setsampwidth(2)
        sound.setframerate(8000)
        sound.writeframes(b"\0\0" * 8000)
    (album / "broken.mp3").write_text("not audio")
    tracks = LocalProvider(tmp_path)._scan("hello")
    assert len(tracks) == 1
    assert tracks[0].title == "Hello"
    assert tracks[0].duration == 1.0
    assert tracks[0].is_local and tracks[0].playable
    assert LocalProvider(tmp_path)._scan("absent") == []


def test_licensed_catalog_requires_license_and_safe_https_url(tmp_path):
    manifest = tmp_path / "catalog.json"
    manifest.write_text(
        json.dumps(
            [
                {
                    "title": "Free Song",
                    "url": "https://example.org/song.mp3",
                    "license": "CC BY 4.0",
                    "license_url": "https://creativecommons.org/licenses/by/4.0/",
                    "attribution": "Artist",
                }
            ]
        )
    )
    tracks = LicensedCatalogProvider(manifest)._load("free")
    assert len(tracks) == 1
    assert tracks[0].playable and tracks[0].source == "licensed"
    manifest.write_text(
        json.dumps(
            [
                {
                    "title": "Bad",
                    "url": "https://youtube.com/watch?v=x",
                    "license": "CC BY",
                    "license_url": "https://example.org/license",
                    "attribution": "Artist",
                }
            ]
        )
    )
    with pytest.raises(ValueError, match="catalog"):
        LicensedCatalogProvider(manifest)._load("")


@pytest.mark.parametrize(
    "url",
    [
        "https://music.youtube.com/watch.mp3",
        "https://youtube-nocookie.com/audio.mp3",
        "https://example.org/playlist.m3u",
        "http://example.org/song.mp3",
    ],
)
def test_catalog_rejects_non_audio_or_extraction_urls(tmp_path, url):
    manifest = tmp_path / "catalog.json"
    manifest.write_text(
        json.dumps(
            [
                {
                    "title": "Bad",
                    "url": url,
                    "license": "CC BY",
                    "license_url": "https://example.org/license",
                    "attribution": "Artist",
                }
            ]
        )
    )
    with pytest.raises(ValueError, match="catalog"):
        LicensedCatalogProvider(manifest)._load("")


def test_catalog_rejects_nonfinite_duration(tmp_path):
    manifest = tmp_path / "catalog.json"
    manifest.write_text(
        json.dumps(
            [
                {
                    "title": "Bad",
                    "url": "https://example.org/audio.mp3",
                    "duration": float("nan"),
                    "license": "CC BY",
                    "license_url": "https://example.org/license",
                    "attribution": "Artist",
                }
            ]
        )
    )
    with pytest.raises(ValueError, match="duration"):
        LicensedCatalogProvider(manifest)._load("")


def test_youtube_provider_returns_metadata_only():
    def reply(request):
        assert request.url.params["type"] == "video"
        return httpx.Response(
            200,
            json={
                "items": [
                    {
                        "id": {"videoId": "abc123"},
                        "snippet": {"title": "Video", "channelTitle": "Channel"},
                    }
                ]
            },
        )

    async def run():
        client = httpx.AsyncClient(transport=httpx.MockTransport(reply))
        tracks = await YouTubeMetadataProvider("key", client).search("video")
        assert len(tracks) == 1
        assert tracks[0].location == "https://music.youtube.com/watch?v=abc123"
        assert tracks[0].artist == ""  # Channel title is not a verified music artist.
        assert not tracks[0].playable
        await client.aclose()

    asyncio.run(run())
