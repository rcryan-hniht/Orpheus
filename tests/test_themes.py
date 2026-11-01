import asyncio

import pytest
from test_app import LOCAL, LyricLookup, Player, Provider, Stems

from orpheus.app import OrpheusApp
from orpheus.storage import Database
from orpheus.themes import DEFAULT_THEME, PRESET_LABELS, get_themes

pytest.importorskip("textual")


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


def test_presets_have_requested_names_and_modes():
    assert DEFAULT_THEME == "oasis-starlight"
    assert PRESET_LABELS == (
        ("oasis-starlight", "Oasis Starlight (Light)"),
        ("oasis-abyss", "Oasis Abyss (Dark)"),
        ("catppuccin-latte", "Catppuccin Latte"),
        ("catppuccin-frappe", "Catppuccin Frappé"),
        ("catppuccin-macchiato", "Catppuccin Macchiato"),
        ("catppuccin-mocha", "Catppuccin Mocha"),
        ("flexoki-light", "Flexoki Light"),
        ("flexoki-dark", "Flexoki Dark"),
        ("github-light", "GitHub Light"),
        ("github-dark", "GitHub Dark"),
        ("github-light-contrast", "GitHub Light Contrast"),
        ("github-dark-contrast", "GitHub Dark Contrast"),
        ("blackmetal", "BlackMetal"),
        ("sequoia-light-monochrome", "Sequoia Light Monochrome"),
    )
    assert [(theme.name, theme.dark) for theme in get_themes()] == [
        ("oasis-starlight", False),
        ("oasis-abyss", True),
        ("catppuccin-latte", False),
        ("catppuccin-frappe", True),
        ("catppuccin-macchiato", True),
        ("catppuccin-mocha", True),
        ("flexoki-light", False),
        ("flexoki-dark", True),
        ("github-light", False),
        ("github-dark", True),
        ("github-light-contrast", False),
        ("github-dark-contrast", True),
        ("blackmetal", True),
        ("sequoia-light-monochrome", False),
    ]


def test_theme_selection_persists_without_interrupting_playback(tmp_path):
    async def scenario():
        app, db = make_app(tmp_path)
        async with app.run_test() as pilot:
            assert app.theme == DEFAULT_THEME
            app.theme = "catppuccin-latte"
            await pilot.pause()
            assert app.theme == "catppuccin-latte"
            assert db.get_theme() == "catppuccin-latte"
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
        await app.close()

        app, db = make_app(tmp_path, theme="github-dark-contrast")
        async with app.run_test():
            assert app.theme == "github-dark-contrast"
            assert db.get_theme() == "github-dark-contrast"
        await app.close()

    asyncio.run(scenario())


def test_blackmetal_preset_matches_ghostty():
    themes = {t.name: t for t in get_themes()}
    assert "blackmetal" in themes
    bm = themes["blackmetal"]
    assert bm.dark is True
    assert bm.background == "#000000"
    assert bm.foreground == "#c1c1c1"
    assert bm.primary == "#486e6f"
    assert bm.secondary == "#a06666"
    assert bm.accent == "#dd9999"


def test_unknown_saved_theme_falls_back(tmp_path):
    async def scenario():
        db = Database(tmp_path / "music.sqlite")
        db.set_theme("removed-preset")
        db.close()
        app, db = make_app(tmp_path)
        async with app.run_test():
            assert app.theme == DEFAULT_THEME
        await app.close()

    asyncio.run(scenario())
