import asyncio

import httpx
import pytest

from orpheus.lyrics import LyricsService, active_line, parse_lrc
from orpheus.models import Lyrics, Track
from orpheus.storage import Database


def test_lrc_multiple_timestamps_offset_and_delay():
    lines = parse_lrc("[offset:500]\n[00:01.25][00:03.250]Hello\n[01:02.5]World")
    assert [(line.time, line.text) for line in lines] == [
        (1.75, "Hello"),
        (3.75, "Hello"),
        (63.0, "World"),
    ]
    assert active_line(lines, 2.0, delay=0.5) == -1
    assert active_line(lines, 2.25, delay=0.5) == 0
    assert active_line(lines, 63.1) == 2


def test_lrclib_result_is_cached_and_404_is_negative_cached(tmp_path):
    seen = []

    def reply(request):
        seen.append(request)
        if request.url.params["track_name"] == "Missing":
            return httpx.Response(404)
        assert request.url.params["artist_name"] == "Singer"
        return httpx.Response(
            200,
            json={"plainLyrics": "Words", "syncedLyrics": "[00:01.00]Words", "instrumental": False},
        )

    async def run():
        db = Database(tmp_path / "music.sqlite")
        client = httpx.AsyncClient(transport=httpx.MockTransport(reply))
        service = LyricsService(db, client)
        song = Track("1", "Song", "/song.mp3", artist="Singer")
        missing = Track("2", "Missing", "/missing.mp3", artist="Singer")
        assert (await service.get(song)).plain == "Words"
        assert (await service.get(song)).synced == "[00:01.00]Words"
        assert await service.get(missing) is None
        assert await service.get(missing) is None
        assert len(seen) == 2
        await client.aclose()
        db.close()

    asyncio.run(run())


def test_lrclib_network_error_uses_stale_cache(tmp_path):
    async def run():
        db = Database(tmp_path / "music.sqlite")
        track = Track("1", "Song", "/song.mp3", artist="Singer")
        good = LyricsService(
            db,
            httpx.AsyncClient(
                transport=httpx.MockTransport(
                    lambda request: httpx.Response(
                        200,
                        json={"plainLyrics": "Cached", "syncedLyrics": None, "instrumental": False},
                    )
                )
            ),
        )
        assert (await good.get(track)).plain == "Cached"
        await good.close()
        db.connection.execute("UPDATE lyrics_cache SET expires_at = 0")
        bad = LyricsService(
            db,
            httpx.AsyncClient(
                transport=httpx.MockTransport(
                    lambda request: (_ for _ in ()).throw(httpx.ConnectError("offline"))
                )
            ),
        )
        assert (await bad.get(track)).plain == "Cached"
        await bad.close()
        db.close()

    asyncio.run(run())


def test_lrclib_rejects_malformed_lyric_fields(tmp_path):
    async def run():
        db = Database(tmp_path / "music.sqlite")
        client = httpx.AsyncClient(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(
                    200,
                    json={"plainLyrics": ["not text"], "syncedLyrics": "", "instrumental": False},
                )
            )
        )
        service = LyricsService(db, client)
        with pytest.raises(RuntimeError, match="Lyrics lookup"):
            await service.get(Track("1", "Song", "/song.mp3"))
        await service.close()
        db.close()

    asyncio.run(run())


def test_search_returns_candidates_without_choosing_or_caching(tmp_path):
    requests = []

    def reply(request):
        requests.append(request)
        assert request.url.path == "/api/search"
        assert request.url.params["q"] == "A Song"
        return httpx.Response(
            200,
            json=[
                {
                    "trackName": "A Song",
                    "artistName": "Singer One",
                    "albumName": "Album One",
                    "duration": 211.5,
                    "plainLyrics": "First",
                    "syncedLyrics": None,
                    "instrumental": False,
                },
                {
                    "trackName": "A Song",
                    "artistName": "Singer Two",
                    "albumName": "Album Two",
                    "duration": 212,
                    "plainLyrics": None,
                    "syncedLyrics": "[00:01.00]Second",
                    "instrumental": False,
                },
            ],
        )

    async def run():
        db = Database(tmp_path / "music.sqlite")
        service = LyricsService(db, httpx.AsyncClient(transport=httpx.MockTransport(reply)))
        track = Track(
            "youtube:one", "A Song", "https://music.youtube.com/watch?v=one", source="youtube"
        )
        assert await service.search("   ") == []
        matches = await service.search("  A Song  ")
        from orpheus.models import LyricsMatch

        assert matches == [
            LyricsMatch("A Song", "Singer One", "Album One", 211.5, Lyrics(plain="First")),
            LyricsMatch(
                "A Song", "Singer Two", "Album Two", 212, Lyrics(synced="[00:01.00]Second")
            ),
        ]
        assert service.get_cached(track) is None
        service.cache_selection(track, matches[1].lyrics)
        assert service.get_cached(track) == matches[1].lyrics
        assert await service.get(track) == matches[1].lyrics
        assert len(requests) == 1
        await service.close()
        db.close()

    asyncio.run(run())


def test_search_caps_results_at_twenty(tmp_path):
    candidate = {
        "trackName": "Song",
        "artistName": "Artist",
        "albumName": "Album",
        "duration": 180,
        "plainLyrics": "Words",
        "syncedLyrics": None,
        "instrumental": False,
    }

    async def run():
        db = Database(tmp_path / "music.sqlite")
        service = LyricsService(
            db,
            httpx.AsyncClient(
                transport=httpx.MockTransport(
                    lambda request: httpx.Response(200, json=[candidate] * 21)
                )
            ),
        )
        assert len(await service.search("Song")) == 20
        await service.close()
        db.close()

    asyncio.run(run())


@pytest.mark.parametrize(
    "bad",
    [
        {},
        [
            {
                "trackName": "Song",
                "artistName": "Artist",
                "albumName": "Album",
                "duration": float("nan"),
                "plainLyrics": "Words",
                "syncedLyrics": None,
                "instrumental": False,
            }
        ],
        [
            {
                "trackName": "Song",
                "artistName": "Artist",
                "albumName": "Album",
                "duration": 180,
                "plainLyrics": ["bad"],
                "syncedLyrics": None,
                "instrumental": False,
            }
        ],
        [
            {
                "trackName": 1,
                "artistName": "Artist",
                "albumName": "Album",
                "duration": 180,
                "plainLyrics": "Words",
                "syncedLyrics": None,
                "instrumental": False,
            }
        ],
    ],
)
def test_search_rejects_malformed_results_without_leaking_details(tmp_path, bad):
    async def run():
        db = Database(tmp_path / "music.sqlite")
        service = LyricsService(
            db,
            httpx.AsyncClient(
                transport=httpx.MockTransport(lambda request: httpx.Response(200, json=bad))
            ),
        )
        with pytest.raises(RuntimeError, match="Lyrics search unavailable"):
            await service.search("Song")
        await service.close()
        db.close()

    asyncio.run(run())


def test_search_network_error_is_friendly(tmp_path):
    async def run():
        db = Database(tmp_path / "music.sqlite")
        service = LyricsService(
            db,
            httpx.AsyncClient(
                transport=httpx.MockTransport(
                    lambda request: (_ for _ in ()).throw(httpx.ConnectError("private-token"))
                )
            ),
        )
        with pytest.raises(RuntimeError, match="^Lyrics search unavailable; try again later$"):
            await service.search("Song")
        await service.close()
        db.close()

    asyncio.run(run())


def test_match_lyric_track_logic():
    from orpheus.lyrics import match_lyric_track

    # Exact match
    assert match_lyric_track("Imagine", "John Lennon", "Imagine", "John Lennon") is True
    # With parenthetical tag / remix
    remix = match_lyric_track("Imagine", "John Lennon", "Imagine (Remastered)", "John Lennon")
    assert remix is True
    # Vietnamese accents
    vn = match_lyric_track("Nơi Này Có Anh", "Sơn Tùng M-TP", "Nơi Này Có Anh", "Sơn Tùng M-TP")
    assert vn is True
    # Different song by same artist must fail
    assert match_lyric_track("Như Một Người Rưng", "OSAD", "Người Âm Phủ", "OSAD") is False
    # Empty title must fail
    assert match_lyric_track("", "OSAD", "Track", "OSAD") is False


def test_fetch_lyricfind_successful_match(tmp_path):
    import asyncio

    def reply_lf(request):
        assert "lyrics.lyricfind.com" in str(request.url)
        return httpx.Response(
            200,
            json={
                "tracks": [
                    {
                        "title": "Imagine",
                        "artist": {"name": "John Lennon"},
                        "snippet": "Imagine there's no heaven\nIt's easy if you try",
                        "slug": "john-lennon-imagine",
                        "instrumental": False,
                    }
                ]
            },
        )

    async def run():
        db = Database(tmp_path / "music.sqlite")
        lf_client = httpx.AsyncClient(transport=httpx.MockTransport(reply_lf))
        service = LyricsService(db, lyricfind_client=lf_client)
        track = Track("lf-1", "Imagine", "/imagine.mp3", artist="John Lennon")
        res = await service.fetch_lyricfind(track)
        assert res is not None
        assert "Imagine there's no heaven" in res.plain
        await service.close()
        db.close()

    asyncio.run(run())


def test_fetch_lyricfind_rejects_unmatched_song(tmp_path):
    import asyncio

    def reply_lf(request):
        return httpx.Response(
            200,
            json={
                "tracks": [
                    {
                        "title": "Người Âm Phủ",
                        "artist": {"name": "OSAD"},
                        "snippet": "Ba giờ anh còn chưa ngủ",
                    }
                ]
            },
        )

    async def run():
        db = Database(tmp_path / "music.sqlite")
        lf_client = httpx.AsyncClient(transport=httpx.MockTransport(reply_lf))
        service = LyricsService(db, lyricfind_client=lf_client)
        track = Track("lf-2", "Như Một Người Rưng", "/nhu-mot-nguoi-rung.mp3", artist="OSAD")
        res = await service.fetch_lyricfind(track)
        # Must be rejected because title does not match
        assert res is None
        await service.close()
        db.close()

    asyncio.run(run())
