import asyncio
from unittest.mock import AsyncMock, patch

import httpx

from orpheus.models import Track
from orpheus.resolver import (
    AudioResolver,
    DeezerProvider,
    extract_artist_name,
    is_artist_query,
)


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

        with (
            patch.object(
                resolver, "_fetch_youtube_candidates", new=AsyncMock(return_value=fake_candidates)
            ),
            patch.object(
                resolver,
                "_extract_direct_stream_url",
                new=AsyncMock(return_value="https://googlevideo.com/stream"),
            ),
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

        with (
            patch.object(resolver, "_fetch_youtube_candidates", new=AsyncMock(return_value=[])),
            patch.object(
                resolver,
                "_fetch_jamendo_stream",
                new=AsyncMock(return_value="https://jamendo.com/audio.mp3"),
            ),
        ):
            stream_url, source_name = await resolver.resolve_stream_url(track)
            assert stream_url == "https://jamendo.com/audio.mp3"
            assert source_name == "jamendo"

    asyncio.run(run())


def test_artist_query_parsing():
    assert is_artist_query("@artist DangRangTo") is True
    assert extract_artist_name("@artist DangRangTo") == "DangRangTo"

    assert is_artist_query("@DangRangTo") is True
    assert extract_artist_name("@DangRangTo") == "DangRangTo"

    assert is_artist_query("@artist:DangRangTo") is True
    assert extract_artist_name("@artist:DangRangTo") == "DangRangTo"

    assert is_artist_query("DangRangTo @artist") is True
    assert extract_artist_name("DangRangTo @artist") == "DangRangTo"

    assert is_artist_query("Trần Duy Hưng") is False
    assert extract_artist_name("Trần Duy Hưng") == "Trần Duy Hưng"


def test_artist_name_matches():
    from orpheus.resolver import artist_name_matches

    assert artist_name_matches("Huong Ly", "Huong Ly") is True
    assert artist_name_matches("Huong Ly", "Hương Ly") is True
    assert artist_name_matches("Huong Ly", "Hương Ly Official") is True
    assert artist_name_matches("Huong Ly", "Huong Ly, Duy Dong") is True
    assert artist_name_matches("DangRangTo", "Dangrangto") is True
    assert artist_name_matches("DangRangTo", "Đặng Rạng Tộ") is True

    # Rejection of fuzzy unrelated names
    assert artist_name_matches("Huong Ly", "Jungle") is False
    assert artist_name_matches("Huong Ly", "Hyolyn") is False
    assert artist_name_matches("Huong Ly", "Young Fly") is False
    assert artist_name_matches("Cam", "Camila Cabello") is False


def test_deezer_provider_search_by_artist():
    async def run():
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.is_closed = False

        async def fake_get(url):
            resp = AsyncMock(spec=httpx.Response)
            resp.status_code = 200
            if "search/artist" in url:
                resp.json.return_value = {"data": [{"id": 111, "name": "Dangrangto"}]}
            elif "artist/111/top" in url:
                resp.json.return_value = {
                    "data": [
                        {
                            "id": 999,
                            "title": "Trần Duy Hưng",
                            "artist": {"name": "Dangrangto"},
                            "album": {"title": "Single", "cover_medium": ""},
                            "duration": 195,
                            "link": "https://deezer.com/track/999",
                        }
                    ]
                }
            elif "search?q=" in url:
                resp.json.return_value = {"data": []}
            return resp

        mock_client.get = fake_get
        provider = DeezerProvider(client=mock_client)
        tracks = await provider.search_by_artist("Dangrangto")

        assert len(tracks) == 1
        assert tracks[0].title == "Trần Duy Hưng"
        assert tracks[0].artist == "Dangrangto"

    asyncio.run(run())


def test_deezer_provider_search_by_artist_rejects_unrelated_fuzzy_artists():
    async def run():
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.is_closed = False

        async def fake_get(url):
            resp = AsyncMock(spec=httpx.Response)
            resp.status_code = 200
            if "search/artist" in url:
                # Deezer fuzzy search returns Huong Ly, Jungle, and Hyolyn
                resp.json.return_value = {
                    "data": [
                        {"id": 10475653, "name": "Huong Ly"},
                        {"id": 436163, "name": "Jungle"},
                        {"id": 5554163, "name": "Hyolyn"},
                    ]
                }
            elif "artist/10475653/top" in url:
                resp.json.return_value = {
                    "data": [
                        {
                            "id": 101,
                            "title": "Vui Lắm Nha",
                            "artist": {"name": "Huong Ly"},
                            "album": {"title": "Vui Lắm Nha", "cover_medium": ""},
                            "duration": 180,
                            "link": "https://deezer.com/track/101",
                        }
                    ]
                }
            elif "artist/436163/top" in url:
                # Jungle tracks should NEVER be queried or included
                resp.json.return_value = {
                    "data": [
                        {
                            "id": 202,
                            "title": "Back On 74",
                            "artist": {"name": "Jungle"},
                            "album": {"title": "Volcano", "cover_medium": ""},
                            "duration": 210,
                            "link": "https://deezer.com/track/202",
                        }
                    ]
                }
            elif "albums" in url:
                resp.json.return_value = {"data": []}
            elif "search?q=" in url:
                resp.json.return_value = {
                    "data": [
                        {
                            "id": 102,
                            "title": "Thiệp Hồng Sai Tên",
                            "artist": {"name": "Huong Ly"},
                            "album": {"title": "Single", "cover_medium": ""},
                            "duration": 220,
                            "link": "https://deezer.com/track/102",
                        },
                        {
                            "id": 303,
                            "title": "Unholy",
                            "artist": {"name": "Sam Smith"},
                            "album": {"title": "Gloria", "cover_medium": ""},
                            "duration": 150,
                            "link": "https://deezer.com/track/303",
                        },
                    ]
                }
            return resp

        mock_client.get = fake_get
        provider = DeezerProvider(client=mock_client)
        tracks = await provider.search_by_artist("Huong Ly")

        # Must only contain Huong Ly tracks
        assert len(tracks) == 2
        assert all(t.artist == "Huong Ly" for t in tracks)
        assert [t.title for t in tracks] == ["Vui Lắm Nha", "Thiệp Hồng Sai Tên"]
        # Jungle and Sam Smith must be completely absent
        assert not any("Jungle" in t.artist for t in tracks)
        assert not any("Back On 74" in t.title for t in tracks)

    asyncio.run(run())


def test_audio_resolver_prioritizes_artist_title_queries():
    async def run():
        track = Track(
            id="dz-789",
            title="Trần Duy Hưng",
            artist="Dangrangto",
            duration=195,
            location="",
            source="deezer",
        )

        searched_queries = []

        async def fake_candidates(query, limit=8):
            searched_queries.append(query)
            if "Dangrangto Trần Duy Hưng" in query:
                return [
                    {
                        "title": "TRẦN DUY HƯNG - DANGRANGTO x TEUYUNGBOY (PROD. DONAL)",
                        "duration": 193,
                        "channel": "NCT Official",
                        "url": "https://youtube.com/watch?v=hitstory",
                        "id": "hitstory",
                    }
                ]
            return []

        resolver = AudioResolver()
        with (
            patch.object(resolver, "_fetch_youtube_candidates", new=fake_candidates),
            patch.object(
                resolver,
                "_extract_direct_stream_url",
                new=AsyncMock(return_value="https://googlevideo.com/stream-tdh"),
            ),
        ):
            stream_url, source = await resolver.resolve_stream_url(track)
            assert stream_url == "https://googlevideo.com/stream-tdh"
            assert source == "youtube"
            # First query searched should be clean "Dangrangto Trần Duy Hưng"
            assert searched_queries[0] == "Dangrangto Trần Duy Hưng"

    asyncio.run(run())
