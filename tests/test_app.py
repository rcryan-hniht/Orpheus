import asyncio
import sqlite3
import threading
from pathlib import Path

import pytest

pytest.importorskip("textual")

from textual.widgets import DataTable, Input, Static

from orpheus.app import OrpheusApp
from orpheus.models import Lyrics, LyricsMatch, PlaybackState, Track
from orpheus.storage import Database

LOCAL = Track("local:one", "First song", "/music/first.mp3", artist="Alice")
SECOND = Track("local:two", "Second song", "/music/second.mp3", artist="Bob")
THIRD = Track("local:three", "Third song", "/music/third.mp3", artist="Carol")
YOUTUBE = Track("youtube:xyz", "Video", "https://music.youtube.com/watch?v=xyz", source="youtube")


class Provider:
    def __init__(self, tracks):
        self.tracks = tracks

    async def search(self, query=""):
        return [track for track in self.tracks if query.casefold() in track.title.casefold()]


class Player:
    def __init__(self):
        self.loads = []
        self.state = PlaybackState(position=0, duration=60, paused=False, idle=False)
        self.closed = False
        self.stops = 0

    async def load(self, location, start=0, paused=False):
        self.loads.append((location, start, paused))
        self.state = PlaybackState(position=start, duration=60, paused=paused, idle=False)

    async def snapshot(self):
        return self.state

    async def toggle_pause(self):
        self.state = PlaybackState(
            position=self.state.position, duration=60, paused=not self.state.paused, idle=False
        )

    async def seek(self, seconds):
        self.state = PlaybackState(
            position=seconds, duration=60, paused=self.state.paused, idle=False
        )

    async def set_volume(self, volume):
        self.state = PlaybackState(
            position=self.state.position,
            duration=60,
            paused=self.state.paused,
            idle=False,
            volume=volume,
        )

    async def stop(self):
        self.stops += 1
        self.state = PlaybackState()

    async def close(self):
        self.closed = True


class LyricLookup:
    def __init__(self):
        self.wait_first = None
        self.closed = False
        self.matches = []
        self.cached = {}
        self.searches = []

    async def get(self, track):
        if track == LOCAL and self.wait_first is not None:
            await self.wait_first.wait()
        return Lyrics(synced=f"[00:00.00]{track.title}")

    async def close(self):
        self.closed = True

    async def search(self, query):
        self.searches.append(query)
        return self.matches

    def get_cached(self, track):
        return self.cached.get(track.id)

    def cache_selection(self, track, lyrics):
        self.cached[track.id] = lyrics


class Stems:
    async def prepare(self, track, rights_confirmed=False):
        assert rights_confirmed
        return Path("/stems/no_vocals.wav")

    async def close(self):
        pass


def make_app(tmp_path, tracks=(LOCAL, SECOND), player=None, lyrics=None, browser_opener=None):
    db = Database(tmp_path / "music.sqlite")
    player = player or Player()
    lyrics = lyrics or LyricLookup()
    app = OrpheusApp(
        providers={"local": Provider(tracks), "youtube": Provider([YOUTUBE])},
        player=player,
        database=db,
        lyrics=lyrics,
        separator=Stems(),
        music_dir=tmp_path,
        browser_opener=browser_opener or (lambda url: True),
    )
    return app, player, db


def test_search_play_and_consume_queue(tmp_path):
    async def scenario():
        app, player, db = make_app(tmp_path)
        async with app.run_test() as pilot:
            await app.workers.wait_for_complete()
            assert app.query_one("#tracks", DataTable).row_count == 2
            app.query_one("#tracks", DataTable).focus()
            await pilot.press("e")
            await pilot.pause()
            assert db.load_queue() == [LOCAL]
            await pilot.press("enter")
            await app.workers.wait_for_complete()
            assert player.loads[0][0] == LOCAL.location
            app.query_one("#queue", DataTable).focus()
            await pilot.press("enter")
            await app.workers.wait_for_complete()
            assert db.load_queue() == []
        await app.close()
        assert player.closed

    asyncio.run(scenario())


def test_youtube_opens_official_page_without_mpv_or_queue(tmp_path):
    async def scenario():
        opened = []
        app, player, db = make_app(tmp_path, browser_opener=lambda url: opened.append(url) or True)
        async with app.run_test() as pilot:
            app.query_one("#search", Input).value = "Video"
            app.query_one("#source").value = "youtube"
            await app.workers.wait_for_complete()
            table = app.query_one("#tracks", DataTable)
            table.focus()
            await pilot.press("enter")
            for _ in range(100):
                if app.current_track == YOUTUBE:
                    break
                await asyncio.sleep(0.01)
            assert app.current_track == YOUTUBE
            assert opened == [YOUTUBE.location]
            assert "browser" in str(app.query_one("#status", Static).render()).lower()
            for _ in range(100):
                if app.screen.__class__.__name__ == "LyricsPickerScreen":
                    break
                await asyncio.sleep(0.01)
            await pilot.press("escape")
            await pilot.press("e")
            await app.workers.wait_for_complete()
            assert player.loads == []
            assert db.load_queue() == []
            assert "youtube.com/watch" in str(app.query_one("#attribution", Static).render())
        await app.close()

    asyncio.run(scenario())


def test_failed_browser_open_keeps_local_playing(tmp_path):
    async def scenario():
        app, player, _ = make_app(tmp_path, browser_opener=lambda url: False)
        async with app.run_test() as pilot:
            await app.workers.wait_for_complete()
            app.query_one("#tracks", DataTable).focus()
            await pilot.press("enter")
            await app.workers.wait_for_complete()
            app.query_one("#search", Input).value = "Video"
            app.query_one("#source").value = "youtube"
            await app.workers.wait_for_complete()
            app.query_one("#tracks", DataTable).focus()
            await pilot.press("enter")
            await app.workers.wait_for_complete()
            assert app.current_track == LOCAL
            assert player.stops == 0
            assert player.loads == [(LOCAL.location, 0, False)]
        await app.close()

    asyncio.run(scenario())


def test_youtube_lyrics_require_choice_and_cached_choice_skips_picker(tmp_path):
    async def scenario():
        lyrics = LyricLookup()
        lyrics.matches = [
            LyricsMatch("Video", "Wrong artist", "A", 120, Lyrics(plain="Wrong words")),
            LyricsMatch(
                "Video", "Right artist", "B", 121,
                Lyrics(synced="[00:01.00]Chosen words\n[00:04.00]More words"),
            ),
        ]
        app, player, _ = make_app(tmp_path, lyrics=lyrics)
        async with app.run_test() as pilot:
            app.query_one("#search", Input).value = "Video"
            app.query_one("#source").value = "youtube"
            await app.workers.wait_for_complete()
            app.query_one("#tracks", DataTable).focus()
            await pilot.press("enter")
            for _ in range(100):
                if app.screen.__class__.__name__ == "LyricsPickerScreen":
                    break
                await asyncio.sleep(0.01)
            table = app.screen.query_one("#lyrics-results", DataTable)
            assert table.row_count == 2
            assert lyrics.get_cached(YOUTUBE) is None
            table.focus()
            table.move_cursor(row=1)
            await pilot.press("enter")
            await app.workers.wait_for_complete()
            pane = str(app.query_one("#lyrics", Static).render())
            assert "Chosen words" in pane and "More words" in pane
            assert "00:01" not in pane
            assert lyrics.get_cached(YOUTUBE) == lyrics.matches[1].lyrics
            assert player.loads == []
            app.query_one("#tracks", DataTable).focus()
            await pilot.press("enter")
            await app.workers.wait_for_complete()
            assert lyrics.searches == ["Video"]
        await app.close()

    asyncio.run(scenario())


def test_stale_browser_open_does_not_replace_new_local_track(tmp_path):
    def opener(url):
        started.set()
        released.wait(2)
        return True

    async def scenario():
        app, player, _ = make_app(tmp_path, browser_opener=opener)
        async with app.run_test() as pilot:
            await app.workers.wait_for_complete()
            app.query_one("#search", Input).value = "Video"
            app.query_one("#source").value = "youtube"
            await app.workers.wait_for_complete()
            app.query_one("#tracks", DataTable).focus()
            await pilot.press("enter")
            assert await asyncio.to_thread(started.wait, 2)
            app.query_one("#search", Input).value = "Second"
            app.query_one("#source").value = "local"
            for _ in range(100):
                if app.results == [SECOND]:
                    break
                await asyncio.sleep(0.01)
            assert app.results == [SECOND]
            app.query_one("#tracks", DataTable).focus()
            await pilot.press("enter")
            released.set()
            await app.workers.wait_for_complete()
            assert app.current_track == SECOND
            assert player.stops == 0
        await app.close()

    started, released = threading.Event(), threading.Event()
    asyncio.run(scenario())


def test_search_input_keeps_spaces_and_shortcut_letters(tmp_path):
    async def scenario():
        app, player, _ = make_app(tmp_path)
        async with app.run_test() as pilot:
            search = app.query_one("#search", Input)
            search.focus()
            await pilot.press("s", "space", "n", "g")
            assert search.value == "s ng"
            assert player.loads == []
        await app.close()

    asyncio.run(scenario())


def test_late_lyrics_cannot_replace_new_track(tmp_path):
    async def scenario():
        lookup = LyricLookup()
        lookup.wait_first = asyncio.Event()
        app, _, _ = make_app(tmp_path, lyrics=lookup)
        async with app.run_test() as pilot:
            await app.workers.wait_for_complete()
            app.query_one("#tracks", DataTable).focus()
            await pilot.press("enter")
            await pilot.pause()
            app.query_one("#tracks", DataTable).move_cursor(row=1)
            await pilot.press("enter")
            lookup.wait_first.set()
            await app.workers.wait_for_complete()
            assert app.current_track == SECOND
            assert "Second song" in str(app.query_one("#lyrics", Static).render())
        await app.close()

    asyncio.run(scenario())


def test_karaoke_preserves_position_and_pause(tmp_path):
    async def scenario():
        app, player, _ = make_app(tmp_path)
        async with app.run_test() as pilot:
            await app.workers.wait_for_complete()
            app.query_one("#tracks", DataTable).focus()
            await pilot.press("enter")
            await app.workers.wait_for_complete()
            player.state = PlaybackState(position=19.5, duration=60, paused=True, idle=False)
            await pilot.press("k")
            await pilot.pause()
            await pilot.click("#confirm")
            await app.workers.wait_for_complete()
            assert player.loads[-1] == ("/stems/no_vocals.wav", 19.5, True)
            player.state = PlaybackState(position=24.5, duration=60, paused=False, idle=False)
            await pilot.press("k")
            await app.workers.wait_for_complete()
            assert player.loads[-1] == (LOCAL.location, 24.5, False)
        await app.close()

    asyncio.run(scenario())


def test_natural_eof_advances_queue_but_stop_does_not(tmp_path):
    async def scenario():
        app, player, db = make_app(tmp_path)
        db.save_queue([SECOND])
        async with app.run_test() as pilot:
            await app.workers.wait_for_complete()
            app.query_one("#tracks", DataTable).focus()
            await pilot.press("enter")
            await app.workers.wait_for_complete()
            player.state = PlaybackState(position=60, duration=60, ended=True, idle=True)
            app.poll_player()
            await app.workers.wait_for_complete()
            assert app.current_track == SECOND
            assert db.load_queue() == []
            db.save_queue([LOCAL])
            app.queue = db.load_queue()
            app._show_queue()
            await pilot.press("s")
            await app.workers.wait_for_complete()
            app.poll_player()
            await app.workers.wait_for_complete()
            assert app.current_track is None
            assert db.load_queue() == [LOCAL]
        await app.close()

    asyncio.run(scenario())


def test_old_eof_snapshot_cannot_override_new_track_request(tmp_path):
    class GatedPlayer(Player):
        def __init__(self):
            super().__init__()
            self.gate = False
            self.snapshot_started = asyncio.Event()
            self.snapshot_release = asyncio.Event()

        async def snapshot(self):
            state = self.state
            if self.gate:
                self.snapshot_started.set()
                await self.snapshot_release.wait()
            return state

    async def scenario():
        player = GatedPlayer()
        app, _, db = make_app(tmp_path, tracks=(LOCAL, SECOND, THIRD), player=player)
        db.save_queue([THIRD])
        async with app.run_test() as pilot:
            await app.workers.wait_for_complete()
            table = app.query_one("#tracks", DataTable)
            table.focus()
            await pilot.press("enter")
            await app.workers.wait_for_complete()
            player.state = PlaybackState(position=60, duration=60, ended=True, idle=True)
            player.gate = True
            app.poll_player()
            await asyncio.wait_for(player.snapshot_started.wait(), 1)
            table.move_cursor(row=1)
            await pilot.press("enter")
            player.snapshot_release.set()
            await app.workers.wait_for_complete()
            assert app.current_track == SECOND
            assert db.load_queue() == [THIRD]
        await app.close()

    asyncio.run(scenario())


def test_lyric_delay_is_persisted_per_track(tmp_path):
    async def scenario():
        app, _, db = make_app(tmp_path)
        async with app.run_test() as pilot:
            await app.workers.wait_for_complete()
            app.query_one("#tracks", DataTable).focus()
            await pilot.press("enter")
            await app.workers.wait_for_complete()
            app.action_delay_forward()
            assert db.get_delay(LOCAL.id) == 0.25
            assert db.get_delay(SECOND.id) == 0.0
        await app.close()

    asyncio.run(scenario())


def test_missing_mpv_does_not_close_browser(tmp_path):
    class BrokenPlayer(Player):
        async def load(self, location, start=0, paused=False):
            raise RuntimeError("Unable to start mpv: executable not found")

    async def scenario():
        app, _, _ = make_app(tmp_path, player=BrokenPlayer())
        async with app.run_test() as pilot:
            await app.workers.wait_for_complete()
            app.query_one("#tracks", DataTable).focus()
            await pilot.press("enter")
            await app.workers.wait_for_complete()
            assert app.current_track is None
            assert app.query_one("#tracks", DataTable).row_count == 2
            assert "mpv" in str(app.query_one("#status", Static).render())
        await app.close()

    asyncio.run(scenario())


def test_quit_cancels_pending_lyrics_and_closes_services(tmp_path):
    async def scenario():
        lookup = LyricLookup()
        lookup.wait_first = asyncio.Event()
        app, player, db = make_app(tmp_path, lyrics=lookup)
        async with app.run_test() as pilot:
            await app.workers.wait_for_complete()
            app.query_one("#tracks", DataTable).focus()
            await pilot.press("enter")
            for _ in range(100):
                if app.current_track == LOCAL:
                    break
                await asyncio.sleep(0.01)
            assert app.current_track == LOCAL
            await pilot.press("ctrl+q")
        assert player.closed
        assert lookup.closed
        with pytest.raises(sqlite3.ProgrammingError):
            db.load_queue()
        await app.close()

    asyncio.run(scenario())


def test_service_close_failure_still_closes_player_and_database(tmp_path):
    class BrokenStems(Stems):
        async def close(self):
            raise RuntimeError("stem shutdown failed")

    async def scenario():
        app, player, db = make_app(tmp_path)
        app.separator = BrokenStems()
        async with app.run_test():
            await app.workers.wait_for_complete()
        await app.close()
        assert player.closed
        with pytest.raises(sqlite3.ProgrammingError):
            db.load_queue()

    asyncio.run(scenario())
