"""Command-line entry point for the terminal player."""

import argparse
import asyncio
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

from .themes import PRESET_LABELS


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Play local music in your terminal")
    parser.add_argument("--music-dir", type=Path, help="local music folder (default: ~/Music)")
    parser.add_argument("--catalog", type=Path, help="licensed catalog JSON file")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "orpheus",
        help="SQLite database and log folder",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache")) / "orpheus",
        help="vocal stem cache folder",
    )
    parser.add_argument("--mpv", default="mpv", help="mpv executable")
    parser.add_argument("--demucs", default="demucs", help="Demucs executable")
    parser.add_argument("--youtube", action="store_true", help="enable YouTube metadata search")
    parser.add_argument(
        "--theme", choices=[slug for slug, _ in PRESET_LABELS], help="color theme preset"
    )
    args = parser.parse_args(argv)

    music_dir = (args.music_dir or Path.home() / "Music").expanduser()
    if args.music_dir is not None and not music_dir.is_dir():
        parser.error(f"Music directory does not exist: {music_dir}")
    if args.catalog and not args.catalog.expanduser().is_file():
        parser.error(f"Catalog file does not exist: {args.catalog}")
    if args.youtube and not os.environ.get("YOUTUBE_API_KEY"):
        parser.error("--youtube requires YOUTUBE_API_KEY")

    try:
        from .app import OrpheusApp
    except ModuleNotFoundError as exc:
        if exc.name == "textual":
            parser.exit(2, "Textual is missing. Install Orpheus dependencies first.\n")
        raise

    from .lyrics import LyricsService
    from .player import MpvPlayer
    from .separation import Separator
    from .sources import LicensedCatalogProvider, LocalProvider, YouTubeMetadataProvider
    from .storage import Database

    data_dir = args.data_dir.expanduser()
    cache_dir = args.cache_dir.expanduser()
    data_dir.mkdir(parents=True, exist_ok=True)
    cache_dir.mkdir(parents=True, exist_ok=True)
    log = logging.getLogger("orpheus")
    log.setLevel(logging.WARNING)
    log.addHandler(
        RotatingFileHandler(data_dir / "orpheus.log", maxBytes=1_000_000, backupCount=2)
    )

    database = Database(data_dir / "orpheus.sqlite")
    providers = {"local": LocalProvider(music_dir)}
    if args.catalog:
        providers["catalog"] = LicensedCatalogProvider(args.catalog.expanduser())
    if args.youtube:
        providers["youtube"] = YouTubeMetadataProvider(os.environ["YOUTUBE_API_KEY"])
    app = OrpheusApp(
        providers=providers,
        player=MpvPlayer(args.mpv),
        database=database,
        lyrics=LyricsService(database),
        separator=Separator(cache_dir, args.demucs),
        music_dir=music_dir,
        theme=args.theme,
    )

    async def run() -> None:
        try:
            await app.run_async()
        finally:
            await app.close()

    asyncio.run(run())


if __name__ == "__main__":
    main()
