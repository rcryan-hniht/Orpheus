import asyncio
import hashlib
import os
import shutil
import tempfile
from pathlib import Path

from .models import Track


class Separator:
    def __init__(self, cache_dir: Path, command: str = "demucs"):
        self.cache_dir = Path(cache_dir)
        self.command = command
        self._jobs: dict[str, asyncio.Task[Path]] = {}
        self._limit = asyncio.Semaphore(1)

    async def prepare(self, track: Track, rights_confirmed: bool = False) -> Path:
        if not track.is_local:
            raise ValueError("Vocal separation requires a local track")
        if not rights_confirmed:
            raise ValueError("Confirm your rights to separate this track")
        source = Path(track.location)
        if not source.is_file():
            raise ValueError("Local audio file is missing")
        stat = source.stat()
        # shortcut: metadata keys cache; hash bytes if timestamp spoofing matters.
        fingerprint = f"htdemucs:{source.resolve()}:{stat.st_size}:{stat.st_mtime_ns}"
        key = hashlib.sha256(fingerprint.encode()).hexdigest()
        output = self.cache_dir / key / "htdemucs" / source.stem
        if (output / "vocals.wav").is_file() and (output / "no_vocals.wav").is_file():
            return output / "no_vocals.wav"
        if key not in self._jobs:
            task = asyncio.create_task(self._run(source, key))
            self._jobs[key] = task
            task.add_done_callback(lambda _: self._jobs.pop(key, None))
        return await asyncio.shield(self._jobs[key])

    async def _run(self, source: Path, key: str) -> Path:
        async with self._limit:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            temporary = Path(tempfile.mkdtemp(prefix="demucs-", dir=self.cache_dir))
            process = None
            try:
                try:
                    process = await asyncio.create_subprocess_exec(
                        self.command,
                        "--two-stems=vocals",
                        "-n",
                        "htdemucs",
                        "-o",
                        str(temporary),
                        str(source),
                        stdout=asyncio.subprocess.PIPE,
                        stderr=asyncio.subprocess.PIPE,
                    )
                except FileNotFoundError as exc:
                    raise RuntimeError(
                        "Demucs is not installed. Install it to separate vocals"
                    ) from exc
                _, stderr = await process.communicate()
                if process.returncode:
                    detail = stderr.decode(errors="replace").strip().splitlines()[-1:] or [
                        "unknown error"
                    ]
                    raise RuntimeError(f"Demucs failed: {detail[0]}")
                output = temporary / "htdemucs" / source.stem
                if (
                    not (output / "vocals.wav").is_file()
                    or not (output / "no_vocals.wav").is_file()
                ):
                    raise RuntimeError("Demucs did not produce both vocal stems")
                destination = self.cache_dir / key
                if destination.exists():
                    shutil.rmtree(destination)
                os.replace(temporary, destination)
                return destination / "htdemucs" / source.stem / "no_vocals.wav"
            finally:
                if process is not None and process.returncode is None:
                    process.kill()
                    await process.wait()
                if temporary.exists():
                    shutil.rmtree(temporary)

    async def close(self) -> None:
        tasks = list(self._jobs.values())
        for task in tasks:
            task.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
