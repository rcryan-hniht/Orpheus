import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, patch

from orpheus.app import OrpheusApp
from orpheus.models import Lyrics, PlaybackState, Track
from orpheus.storage import Database

LOCAL = Track("local:one", "First song", "/music/first.mp3", artist="Alice", duration=180)
SECOND = Track("local:two", "Second song", "/music/second.mp3", artist="Bob", duration=210)


class MockProvider:
    def __init__(self, tracks):
        self.tracks = tracks

    async def search(self, query=""):
        return [t for t in self.tracks if query.casefold() in t.title.casefold()]


Provider = MockProvider


class MockPlayer:
    def __init__(self):
        self.loads = []
        self.state = PlaybackState(position=10, duration=180, paused=False, idle=False)
        self.closed = False
        self.stops = 0

    async def load(self, location, start=0, paused=False):
        self.loads.append((location, start, paused))
        self.state = PlaybackState(position=start, duration=180, paused=paused, idle=False)

    async def snapshot(self):
        return self.state

    async def toggle_pause(self):
        self.state = PlaybackState(
            position=self.state.position, duration=180, paused=not self.state.paused, idle=False
        )

    async def seek(self, seconds):
        self.state = PlaybackState(
            position=seconds, duration=180, paused=self.state.paused, idle=False
        )

    async def stop(self):
        self.stops += 1
        self.state = PlaybackState()

    async def close(self):
        self.closed = True


Player = MockPlayer


class MockLyricsService:
    def __init__(self):
        self.closed = False

    async def get(self, track):
        return Lyrics(plain="Hello world", synced="[00:05.00]Hello world")

    async def close(self):
        self.closed = True


LyricLookup = MockLyricsService


class Stems:
    async def prepare(self, track, rights_confirmed=False):
        return Path("/stems/no_vocals.wav")

    async def close(self):
        pass


def make_app(tmp_path):
    db = Database(tmp_path / "orpheus.sqlite")
    player = MockPlayer()
    lyrics = MockLyricsService()
    app = OrpheusApp(
        providers={"local": MockProvider([LOCAL, SECOND])},
        player=player,
        database=db,
        lyrics=lyrics,
        music_dir=tmp_path,
        auto_update=False,
    )
    return app, player, db


def test_app_initial_phase_is_home(tmp_path):
    async def scenario():
        app, player, db = make_app(tmp_path)
        async with app.run_test() as pilot:
            assert app.screen.__class__.__name__ == "HomeScreen"
            # Press 'f' to go to search
            await pilot.press("f")
            await asyncio.sleep(0.3)
            assert app.screen.__class__.__name__ == "SearchScreen"
        await app.close()

    asyncio.run(scenario())


def test_app_play_track_transitions_to_now_playing(tmp_path):
    async def scenario():
        app, player, db = make_app(tmp_path)
        with patch.object(
            app.audio_resolver,
            "resolve_stream_url",
            new=AsyncMock(return_value=("/music/first.mp3", "local")),
        ):
            async with app.run_test() as pilot:
                # Trigger playback
                app.play_resolved_track(LOCAL)
                await asyncio.sleep(0.3)
                assert app.screen.__class__.__name__ == "NowPlayingScreen"
                assert app.current_track == LOCAL
                assert len(player.loads) == 1
                assert player.loads[0][0] == "/music/first.mp3"

                # Press escape to return to Home with background playback
                await pilot.press("escape")
                await asyncio.sleep(0.3)
                assert app.screen.__class__.__name__ == "HomeScreen"
                assert app.home_screen.query_one("#home-shortcuts").is_playing is True

                # Press 's' to stop playback
                await pilot.press("s")
                await asyncio.sleep(0.1)
                assert player.stops == 1
                assert app.home_screen.query_one("#home-shortcuts").is_playing is False
        await app.close()

    asyncio.run(scenario())


def test_app_settings_modal_open_and_close(tmp_path):
    async def scenario():
        app, player, db = make_app(tmp_path)
        async with app.run_test() as pilot:
            await pilot.press("S")
            await asyncio.sleep(0.1)
            assert app.screen.__class__.__name__ == "SettingsModal"
            await pilot.press("escape")
            await asyncio.sleep(0.1)
            assert app.screen.__class__.__name__ == "HomeScreen"
        await app.close()

    asyncio.run(scenario())


def test_app_playlist_load_and_queue_navigation(tmp_path):
    async def scenario():
        app, player, db = make_app(tmp_path)
        with patch.object(
            app.audio_resolver,
            "resolve_stream_url",
            new=AsyncMock(return_value=("/music/song.mp3", "local")),
        ):
            async with app.run_test():
                # Load playlist with track 1, queue track 2
                app.load_playlist_and_play(LOCAL, queue=[SECOND], history=[])
                await asyncio.sleep(0.2)
                assert app.current_track == LOCAL
                assert app.queue == [SECOND]

                # Advance to next track
                await app.action_next()
                await asyncio.sleep(0.2)
                assert app.current_track == SECOND
                assert len(app.history) >= 1
                assert app.history[-1] == LOCAL

                # Advance back to prev track (seek < 3s)
                app.playback = PlaybackState(position=1.0, duration=180.0)
                await app.action_prev()
                await asyncio.sleep(0.2)
                assert app.current_track == LOCAL
        await app.close()

    asyncio.run(scenario())


def test_app_poll_player_album_vs_standalone(tmp_path):
    async def scenario():
        app, player, db = make_app(tmp_path)
        with patch.object(
            app.audio_resolver,
            "resolve_stream_url",
            new=AsyncMock(return_value=("/music/song.mp3", "local")),
        ):
            async with app.run_test():
                # Case 1: Standalone track with no album -> stops when ended
                app.play_resolved_track(LOCAL)
                await asyncio.sleep(0.1)
                assert app.current_album is None
                assert app.queue == []

                # Simulate track ended in player snapshot
                player.state = PlaybackState(ended=True, position=180.0, duration=180.0)
                await app.poll_player()
                assert player.stops >= 1
                assert app.current_track is None

                # Case 2: In album -> advances to next track in album
                app.load_playlist_and_play(LOCAL, queue=[SECOND], album="My Album")
                await asyncio.sleep(0.1)
                assert app.current_album == "My Album"
                assert app.queue == [SECOND]

                player.state = PlaybackState(ended=True, position=180.0, duration=180.0)
                await app.poll_player()
                # Should have transitioned to SECOND
                assert app.current_track == SECOND
        await app.close()

    asyncio.run(scenario())


def test_app_single_track_album_no_seek_stop_and_space_replay(tmp_path):
    async def scenario():
        app, player, db = make_app(tmp_path)
        with patch.object(
            app.audio_resolver,
            "resolve_stream_url",
            new=AsyncMock(return_value=("/music/song.mp3", "local")),
        ):
            async with app.run_test():
                # 1. Load a single-track album
                app.load_playlist_and_play(LOCAL, queue=[], album="Solo Album")
                await asyncio.sleep(0.1)
                assert app.is_single_track_album() is True

                initial_pos = player.state.position
                # 2. Seeking has no effect on single-track album
                await app.action_seek(15.0)
                assert player.state.position == initial_pos

                # 3. Next / Prev has no effect
                await app.action_next()
                assert app.current_track == LOCAL
                await app.action_prev()
                assert app.current_track == LOCAL

                # 4. When song ends, it stops
                player.state = PlaybackState(ended=True, position=180.0, duration=180.0)
                await app.poll_player()
                assert player.stops >= 1
                assert app.current_track is None
                assert app.last_played_track == LOCAL

                # 5. Pressing space replays the track from start
                await app.action_toggle_pause()
                await asyncio.sleep(0.1)
                assert app.current_track == LOCAL

                # 6. While active, space toggles pause
                await app.action_toggle_pause()
                assert player.state.paused is True
        await app.close()

    asyncio.run(scenario())
