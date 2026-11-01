from orpheus.phases.home import ShortcutBar
from orpheus.phases.search import SearchScreen


def test_shortcut_bar_render_idle():
    bar = ShortcutBar(is_playing=False)
    rendered = bar.render_text()
    assert "[S]" in rendered
    assert "[f]" in rendered
    assert "[q]" in rendered
    assert "[p]" not in rendered
    assert "[s]" not in rendered


def test_shortcut_bar_render_playing():
    bar = ShortcutBar(is_playing=True)
    rendered = bar.render_text()
    assert "[p]" in rendered
    assert "[s]" in rendered
    assert "[S]" in rendered
    assert "[f]" in rendered
    assert "[q]" in rendered


def test_search_screen_split_toggle():
    screen = SearchScreen()
    assert screen.split_view is False
    screen.action_toggle_split()
    assert screen.split_view is True
    screen.action_toggle_split()
    assert screen.split_view is False
