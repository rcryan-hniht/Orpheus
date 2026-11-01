import asyncio

import pytest

pytest.importorskip("textual")

from test_app import LOCAL, LyricLookup, Player, Provider, Stems
from textual.widgets import DataTable, Select

from orpheus.app import OrpheusApp
from orpheus.storage import Database
from orpheus.themes import DEFAULT_THEME, PRESET_LABELS, get_themes


def make_app(tmp_path, theme=None):
    db = Database(tmp_path / "music.sqlite")
    app = OrpheusApp(
        providers={"local": Provider([LOCAL])},
        player=Player(),
        database=db,
        lyrics=LyricLookup(),
        separator=Stems(),
        music_dir=tmp_path,
        theme=theme,
    )
    return app, db


def test_five_presets_have_requested_names_and_modes():
    assert DEFAULT_THEME == "github-light-contrast"
    assert PRESET_LABELS == (
        ("blackmetal", "BlackMetal"),
        ("sequoia-light-monochrome", "Sequoia Light Monochrome"),
        ("catppuccin-latte", "Catppuccin Latte"),
        ("github-dark-contrast", "GitHub Dark Contrast"),
        ("github-light-contrast", "GitHub Light Contrast"),
    )
    assert [(theme.name, theme.dark) for theme in get_themes()] == [
        ("blackmetal", True),
        ("sequoia-light-monochrome", False),
        ("catppuccin-latte", False),
        ("github-dark-contrast", True),
        ("github-light-contrast", False),
    ]


def test_theme_selection_persists_without_interrupting_playback(tmp_path):
    async def scenario():
        app, db = make_app(tmp_path)
        async with app.run_test() as pilot:
            await app.workers.wait_for_complete()
            assert app.theme == DEFAULT_THEME
            table = app.query_one("#tracks", DataTable)
            table.focus()
            await pilot.press("enter")
            await app.workers.wait_for_complete()
            playing = app.current_track
            app.query_one("#theme", Select).value = "catppuccin-latte"
            await pilot.pause()
            assert app.theme == "catppuccin-latte"
            assert db.get_theme() == "catppuccin-latte"
            assert app.current_track == playing
            assert app.queue == []
        await app.close()

    asyncio.run(scenario())


def test_saved_theme_restored_and_cli_override_persisted(tmp_path):
    async def scenario():
        db = Database(tmp_path / "music.sqlite")
        db.set_theme("blackmetal")
        db.close()
        app, db = make_app(tmp_path)
        async with app.run_test():
            assert app.theme == "blackmetal"
            assert app.query_one("#theme", Select).value == "blackmetal"
        await app.close()

        app, db = make_app(tmp_path, theme="github-dark-contrast")
        async with app.run_test():
            assert app.theme == "github-dark-contrast"
            assert db.get_theme() == "github-dark-contrast"
        await app.close()

    asyncio.run(scenario())


def test_unknown_saved_theme_falls_back_and_palette_changes_sync_selector(tmp_path):
    async def scenario():
        db = Database(tmp_path / "music.sqlite")
        db.set_theme("removed-preset")
        db.close()
        app, db = make_app(tmp_path)
        async with app.run_test() as pilot:
            assert app.theme == DEFAULT_THEME
            app.theme = "sequoia-light-monochrome"
            await pilot.pause()
            assert app.query_one("#theme", Select).value == app.theme
            assert db.get_theme() == app.theme
            app.theme = "textual-dark"
            await pilot.pause()
            assert app.query_one("#theme", Select).is_blank
        await app.close()

    asyncio.run(scenario())
