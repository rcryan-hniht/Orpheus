import asyncio
from unittest.mock import AsyncMock, patch

import httpx

from orpheus.models import Track
from orpheus.resolver import AudioResolver, DeezerProvider


def test_deezer_provider_search():
    async def run():
        fake_payload = {
            "data": [
                {
                    "id": 12345,
                    "title": "Midnight City",
                    "artist": {"name": "M83", "id": 99},
                    "album": {
                        "title": "Hurry Up, We're Dreaming",
                        "cover_medium": "https://img.deezer.com/cover.jpg",
                    },
                    "duration": 243,
                }
            ]
        }

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.is_closed = False
        mock_resp = AsyncMock(spec=httpx.Response)
        mock_resp.status_code = 200
        mock_resp.json.return_value = fake_payload
        mock_client.get.return_value = mock_resp

        provider = DeezerProvider(client=mock_client)
        tracks = await provider.search("Midnight City")

        assert len(tracks) == 1
        t = tracks[0]
        assert t.title == "Midnight City"
        assert t.artist == "M83"
        assert t.album == "Hurry Up, We're Dreaming"
        assert t.duration == 243
        assert t.cover_url == "https://img.deezer.com/cover.jpg"
        assert t.source == "deezer"

    asyncio.run(run())


def test_audio_resolver_selects_closest_duration():
    async def run():
        track = Track(
            id="dz-123",
            title="Midnight City",
            artist="M83",
            album="Album",
            duration=240,
            location="",
            source="deezer",
        )

        fake_candidates = [
            {
                "title": "M83 - Midnight City (Official Live)",
                "duration": 310,
                "channel": "M83",
                "url": "https://youtube.com/v1",
                "id": "v1",
            },
            {
                "title": "M83 - Midnight City",
                "duration": 242,
                "channel": "M83 - Topic",
                "url": "https://youtube.com/v2",
                "id": "v2",
            },
            {
                "title": "Midnight City Remix",
                "duration": 240,
                "channel": "Random",
                "url": "https://youtube.com/v3",
                "id": "v3",
            },
        ]

        resolver = AudioResolver()

        with patch.object(
            resolver, "_fetch_youtube_candidates", new=AsyncMock(return_value=fake_candidates)
        ), patch.object(
            resolver,
            "_extract_direct_stream_url",
            new=AsyncMock(return_value="https://googlevideo.com/stream"),
        ):
            stream_url, source_name = await resolver.resolve_stream_url(track)
            assert stream_url == "https://googlevideo.com/stream"
            assert source_name == "youtube"

    asyncio.run(run())


def test_audio_resolver_fallback_to_jamendo_when_yt_fails():
    async def run():
        track = Track(
            id="dz-456",
            title="Neon Lights",
            artist="Synthwave",
            duration=180,
            location="",
            source="deezer",
        )

        resolver = AudioResolver(jamendo_client_id="test_key")

        with patch.object(
            resolver, "_fetch_youtube_candidates", new=AsyncMock(return_value=[])
        ), patch.object(
            resolver,
            "_fetch_jamendo_stream",
            new=AsyncMock(return_value="https://jamendo.com/audio.mp3"),
        ):
            stream_url, source_name = await resolver.resolve_stream_url(track)
            assert stream_url == "https://jamendo.com/audio.mp3"
            assert source_name == "jamendo"

    asyncio.run(run())
