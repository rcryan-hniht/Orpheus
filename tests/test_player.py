import asyncio
import json
import shutil
import socket
import wave

import pytest

from orpheus.player import MpvPlayer


class FakeWriter:
    def __init__(self, reader, replies=None):
        self.reader = reader
        self.replies = replies or {}
        self.commands = []

    def write(self, data):
        message = json.loads(data)
        self.commands.append(message["command"])
        self.reader.feed_data(b'{"event":"file-loaded"}\n')
        error, value = self.replies.get(message["command"][-1], ("success", 42))
        reply = {"request_id": message["request_id"], "error": error, "data": value}
        self.reader.feed_data((json.dumps(reply) + "\n").encode())

    async def drain(self):
        pass

    def close(self):
        pass

    async def wait_closed(self):
        pass


def test_ipc_routes_events_and_replies_by_request_id():
    async def run():
        player = MpvPlayer()
        player._reader = asyncio.StreamReader()
        player._writer = FakeWriter(player._reader)
        player._reader_task = asyncio.create_task(player._read_messages())
        try:
            assert await player._command("get_property", "duration") == 42
            assert player._file_loaded.is_set()
            assert player._writer.commands == [["get_property", "duration"]]
            player._reader.feed_eof()
            await player._reader_task
            with pytest.raises(RuntimeError, match="disconnected"):
                await player._command("get_property", "duration")
        finally:
            await player.close()

    asyncio.run(run())


def test_ipc_surfaces_command_errors_and_disconnects():
    async def run():
        player = MpvPlayer()
        player._reader = asyncio.StreamReader()
        player._writer = FakeWriter(player._reader, {"pause": ("property unavailable", None)})
        player._reader_task = asyncio.create_task(player._read_messages())
        try:
            with pytest.raises(RuntimeError, match="property unavailable"):
                await player._command("get_property", "pause")
            player._reader.feed_eof()
            await player._reader_task
            with pytest.raises(RuntimeError, match="disconnected"):
                await player._command("get_property", "pause")
        finally:
            await player.close()

    asyncio.run(run())


def test_snapshot_handles_unavailable_idle_properties():
    async def run():
        player = MpvPlayer()
        player._reader = asyncio.StreamReader()
        player._writer = FakeWriter(
            player._reader,
            {
                "idle-active": ("success", True),
                "time-pos": ("property unavailable", None),
                "duration": ("property unavailable", None),
                "pause": ("success", False),
                "volume": ("success", 60),
            },
        )
        player._reader_task = asyncio.create_task(player._read_messages())
        try:
            state = await player.snapshot()
            assert state.idle and state.position == 0 and state.duration == 0
            assert state.volume == 60
        finally:
            await player.close()

    asyncio.run(run())


def test_stop_does_not_report_racing_eof_as_natural_end():
    class RacingWriter(FakeWriter):
        def write(self, data):
            if json.loads(data)["command"] == ["stop"]:
                self.reader.feed_data(b'{"event":"end-file","reason":"eof"}\n')
            super().write(data)

    async def run():
        player = MpvPlayer()
        player._reader = asyncio.StreamReader()
        player._writer = RacingWriter(player._reader)
        player._reader_task = asyncio.create_task(player._read_messages())
        try:
            await player.stop()
            assert not player._ended
            player._reader.feed_data(b'{"event":"end-file","reason":"eof"}\n')
            await asyncio.sleep(0)
            assert not player._ended
        finally:
            await player.close()

    asyncio.run(run())


def test_new_file_load_clears_outgoing_eof_but_reports_its_own_eof():
    class SwitchingWriter(FakeWriter):
        def write(self, data):
            message = json.loads(data)
            command = message["command"]
            if command == ["set_property", "pause", True] and not getattr(
                self, "sent_old_eof", False
            ):
                self.sent_old_eof = True
                self.reader.feed_data(b'{"event":"end-file","reason":"eof"}\n')
            elif command[0] == "loadfile":
                self.reader.feed_data(b'{"event":"file-loaded"}\n')
            values = {
                "idle-active": False,
                "time-pos": 0,
                "duration": 10,
                "pause": True,
                "volume": 100,
            }
            reply = {
                "request_id": message["request_id"],
                "error": "success",
                "data": values.get(command[-1]),
            }
            self.reader.feed_data((json.dumps(reply) + "\n").encode())

    async def run():
        player = MpvPlayer()
        player._reader = asyncio.StreamReader()
        player._writer = SwitchingWriter(player._reader)
        player._reader_task = asyncio.create_task(player._read_messages())

        async def already_started():
            pass

        player.start = already_started
        try:
            await player.load("/tmp/new.wav", paused=True)
            assert not (await player.snapshot()).ended
            player._reader.feed_data(b'{"event":"end-file","reason":"eof"}\n')
            await asyncio.sleep(0)
            assert (await player.snapshot()).ended
        finally:
            await player.close()

    asyncio.run(run())


def _unix_sockets_available():
    try:
        with socket.socket(socket.AF_UNIX) as server:
            with socket.socket(socket.AF_UNIX) as client:
                server.bind("\0orpheus-test")
                server.listen()
                client.connect("\0orpheus-test")
        return True
    except PermissionError:
        return False


@pytest.mark.skipif(
    not shutil.which("mpv") or not _unix_sockets_available(),
    reason="mpv or Unix sockets unavailable",
)
def test_mpv_load_seek_pause_and_stop(tmp_path):
    song = tmp_path / "tone.wav"
    with wave.open(str(song), "wb") as sound:
        sound.setnchannels(1)
        sound.setsampwidth(2)
        sound.setframerate(8000)
        sound.writeframes(b"\0\0" * 8000 * 8)

    async def run():
        player = MpvPlayer(extra_args=["--ao=null"])
        try:
            await player.start()
            await player.load(str(song), start=2, paused=True)
            state = await player.snapshot()
            assert state.paused
            assert 1.5 <= state.position <= 2.5
            assert state.duration == pytest.approx(8, abs=0.1)
            assert not state.idle
            await player.seek(4)
            assert (await player.snapshot()).position == pytest.approx(4, abs=0.2)
            await player.stop()
            state = await player.snapshot()
            assert state.idle and not state.ended
        finally:
            await player.close()

    asyncio.run(run())


def test_missing_mpv_reports_clear_error():
    async def run():
        player = MpvPlayer(executable="/missing/mpv")
        with pytest.raises(RuntimeError, match="mpv"):
            await player.start()
        await player.close()

    asyncio.run(run())
