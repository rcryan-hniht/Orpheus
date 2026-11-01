import asyncio
import json
import tempfile
from pathlib import Path

from .models import PlaybackState


class MpvPlayer:
    def __init__(self, executable: str = "mpv", extra_args: list[str] | None = None):
        self.executable = executable
        self.extra_args = extra_args or []
        self._directory: tempfile.TemporaryDirectory | None = None
        self._process: asyncio.subprocess.Process | None = None
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._reader_task: asyncio.Task | None = None
        self._pending: dict[int, asyncio.Future] = {}
        self._next_id = 0
        self._file_loaded = asyncio.Event()
        self._load_lock = asyncio.Lock()
        self._disconnected = False
        self._ended = False
        self._manually_stopped = False

    async def start(self) -> None:
        if self._process is not None:
            return
        self._directory = tempfile.TemporaryDirectory(prefix="orpheus-mpv-")
        socket = str(Path(self._directory.name) / "ipc.sock")
        try:
            self._process = await asyncio.create_subprocess_exec(
                self.executable,
                "--no-config",
                "--no-terminal",
                "--no-video",
                "--ytdl=yes",
                "--ytdl-format=bestaudio/best",
                "--slang=vi,vie,en,eng",
                "--alang=vi,vie,en,eng",
                "--load-scripts=no",
                "--network-timeout=15",
                "--idle=yes",
                f"--input-ipc-server={socket}",
                *self.extra_args,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            loop = asyncio.get_running_loop()
            deadline = loop.time() + 5
            while True:
                if self._process.returncode is not None:
                    raise RuntimeError("mpv exited before its control socket was ready")
                try:
                    self._reader, self._writer = await asyncio.open_unix_connection(socket)
                    break
                except (FileNotFoundError, ConnectionRefusedError):
                    if loop.time() >= deadline:
                        raise RuntimeError("mpv did not start its control socket")
                    await asyncio.sleep(0.05)
            self._reader_task = asyncio.create_task(self._read_messages())
        except (OSError, RuntimeError) as exc:
            await self.close()
            raise RuntimeError(f"Unable to start mpv: {exc}") from exc

    async def _read_messages(self) -> None:
        try:
            while True:
                line = await self._reader.readline()
                if not line:
                    break
                try:
                    message = json.loads(line)
                except (ValueError, UnicodeDecodeError):
                    continue
                request_id = message.get("request_id")
                if request_id in self._pending:
                    future = self._pending.pop(request_id)
                    if not future.done():
                        future.set_result(message)
                event = message.get("event")
                if event == "file-loaded":
                    self._ended = False
                    self._file_loaded.set()
                elif (
                    event == "end-file"
                    and message.get("reason") == "eof"
                    and not self._manually_stopped
                ):
                    self._ended = True
        except (OSError, ConnectionError) as exc:
            error = RuntimeError(f"mpv connection failed: {exc}")
        except asyncio.CancelledError:
            error = RuntimeError("mpv connection closed")
        else:
            error = RuntimeError("mpv disconnected")
        finally:
            self._disconnected = True
            self._file_loaded.set()
            for future in self._pending.values():
                if not future.done():
                    future.set_exception(error)
            self._pending.clear()

    async def _command(self, *parts):
        if self._disconnected:
            raise RuntimeError("mpv disconnected")
        if self._writer is None:
            raise RuntimeError("mpv is not connected")
        self._next_id += 1
        request_id = self._next_id
        future = asyncio.get_running_loop().create_future()
        self._pending[request_id] = future
        try:
            self._writer.write(
                (json.dumps({"command": list(parts), "request_id": request_id}) + "\n").encode()
            )
            await asyncio.wait_for(self._writer.drain(), 4)
            reply = await asyncio.wait_for(future, 4)
        except (OSError, TimeoutError) as exc:
            raise RuntimeError(f"mpv command timed out or failed: {parts[0]}") from exc
        finally:
            self._pending.pop(request_id, None)
        if reply.get("error") != "success":
            raise RuntimeError(f"mpv {parts[0]} failed: {reply.get('error', 'unknown error')}")
        return reply.get("data")

    async def load(self, location: str, start: float = 0, paused: bool = False) -> None:
        if not location:
            raise ValueError("A playback location is required")
        async with self._load_lock:
            await self.start()
            self._file_loaded.clear()
            self._ended = False
            self._manually_stopped = False
            await self._command("set_property", "pause", True)
            await self._command("loadfile", location, "replace")
            try:
                await asyncio.wait_for(self._file_loaded.wait(), 20)
            except TimeoutError as exc:
                raise RuntimeError("mpv could not load the track") from exc
            if self._disconnected:
                raise RuntimeError("mpv disconnected while loading the track")
            if start:
                await self.seek(start)
            await self._command("set_property", "pause", paused)

    async def toggle_pause(self) -> None:
        paused = await self._command("get_property", "pause")
        await self._command("set_property", "pause", not paused)

    async def seek(self, seconds: float) -> None:
        await self._command("seek", max(0.0, seconds), "absolute+exact")

    async def set_volume(self, value: float) -> None:
        await self._command("set_property", "volume", max(0.0, min(100.0, value)))

    async def stop(self) -> None:
        self._manually_stopped = True
        self._ended = False
        await self._command("stop")

    async def snapshot(self) -> PlaybackState:
        async def optional(name: str):
            try:
                return await self._command("get_property", name)
            except RuntimeError as exc:
                if "property unavailable" in str(exc):
                    return None
                raise

        idle = await self._command("get_property", "idle-active")
        position, duration, paused, volume = await asyncio.gather(
            *(optional(name) for name in ("time-pos", "duration", "pause", "volume"))
        )
        return PlaybackState(
            position=float(position or 0),
            duration=float(duration or 0),
            paused=bool(paused),
            idle=bool(idle),
            volume=float(volume or 0),
            ended=self._ended,
        )

    async def close(self) -> None:
        if self._writer is not None:
            self._writer.close()
            try:
                await self._writer.wait_closed()
            except OSError:
                pass
            self._writer = None
        if self._reader_task is not None:
            self._reader_task.cancel()
            try:
                await self._reader_task
            except asyncio.CancelledError:
                pass
            self._reader_task = None
        if self._process is not None:
            if self._process.returncode is None:
                self._process.terminate()
                try:
                    await asyncio.wait_for(self._process.wait(), 2)
                except TimeoutError:
                    self._process.kill()
                    await self._process.wait()
            self._process = None
        if self._directory is not None:
            self._directory.cleanup()
            self._directory = None
