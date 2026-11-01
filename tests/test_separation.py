import asyncio

import pytest

from orpheus.models import Track
from orpheus.separation import Separator


def test_separator_requires_local_track_and_rights(tmp_path):
    async def run():
        separator = Separator(tmp_path / "cache", command="/missing/demucs")
        local = Track("1", "Song", str(tmp_path / "song.wav"))
        with pytest.raises(ValueError, match="rights"):
            await separator.prepare(local)
        remote = Track("2", "Song", "https://example.org/song.mp3", source="licensed")
        with pytest.raises(ValueError, match="local"):
            await separator.prepare(remote, rights_confirmed=True)
        await separator.close()

    asyncio.run(run())


def test_separator_caches_only_complete_outputs(tmp_path):
    audio = tmp_path / "song.wav"
    audio.write_bytes(b"audio fixture")
    fake = tmp_path / "demucs"
    fake.write_text("""#!/usr/bin/env python3
import pathlib, sys
root = pathlib.Path(sys.argv[sys.argv.index('-o') + 1])
out = root / 'htdemucs' / pathlib.Path(sys.argv[-1]).stem
out.mkdir(parents=True)
(out / 'vocals.wav').write_bytes(b'voice')
(out / 'no_vocals.wav').write_bytes(b'music')
""")
    fake.chmod(0o755)

    async def run():
        separator = Separator(tmp_path / "cache", command=str(fake))
        track = Track("1", "Song", str(audio))
        first, second = await asyncio.gather(
            separator.prepare(track, rights_confirmed=True),
            separator.prepare(track, rights_confirmed=True),
        )
        assert first == second
        assert first.read_bytes() == b"music"
        assert (first.parent / "vocals.wav").read_bytes() == b"voice"
        fake.unlink()
        assert await separator.prepare(track, rights_confirmed=True) == first
        await separator.close()

    asyncio.run(run())


def test_missing_separator_dependency_is_actionable(tmp_path):
    audio = tmp_path / "song.wav"
    audio.write_bytes(b"audio fixture")

    async def run():
        separator = Separator(tmp_path / "cache", command="/missing/demucs")
        with pytest.raises(RuntimeError, match="Demucs"):
            await separator.prepare(Track("1", "Song", str(audio)), rights_confirmed=True)
        await separator.close()

    asyncio.run(run())


def test_separator_does_not_cache_partial_output(tmp_path):
    audio = tmp_path / "song.wav"
    audio.write_bytes(b"audio fixture")
    fake = tmp_path / "demucs"
    fake.write_text("""#!/usr/bin/env python3
import pathlib, sys
root = pathlib.Path(sys.argv[sys.argv.index('-o') + 1])
out = root / 'htdemucs' / pathlib.Path(sys.argv[-1]).stem
out.mkdir(parents=True)
(out / 'vocals.wav').write_bytes(b'voice')
""")
    fake.chmod(0o755)

    async def run():
        cache = tmp_path / "cache"
        separator = Separator(cache, command=str(fake))
        with pytest.raises(RuntimeError, match="both vocal stems"):
            await separator.prepare(Track("1", "Song", str(audio)), rights_confirmed=True)
        assert list(cache.iterdir()) == []
        await separator.close()

    asyncio.run(run())
