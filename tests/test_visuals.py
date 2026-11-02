from orpheus.matrix import MatrixRain
from orpheus.title import AsciiTitle, get_title_lines


def test_get_title_lines():
    lines = get_title_lines(style="pulse", frame=0, accent_color="cyan")
    assert len(lines) >= 5
    # Should contain block glyphs
    combined = "".join(lines)
    assert "█" in combined or "▀" in combined or "▄" in combined or "▓" in combined


def test_matrix_rain_theme_synchronization():
    from unittest.mock import MagicMock

    from orpheus.matrix import MatrixRain

    matrix = MatrixRain(density=1.0)
    matrix.setup_columns(width=10, height=10)

    # Mock dark theme (e.g. Black Metal)
    dummy_dark_theme = MagicMock()
    dummy_dark_theme.dark = True
    dummy_dark_theme.accent = "#dd9999"
    dummy_dark_theme.background = "#000000"

    dummy_app = MagicMock()
    dummy_app.current_theme = dummy_dark_theme
    matrix._app = dummy_app

    # Ensure a column has a tail
    col = matrix.columns[0]
    col.active = True
    col.head_y = 5.0
    col.tail = [(5, "ｱ"), (4, "ｲ"), (3, "ｳ"), (1, "ｴ")]

    rendered = matrix.render()
    # Check that spans contain theme styles
    styles = [str(span.style) for span in rendered.spans]
    assert any("bold #ffffff" in s for s in styles)  # Head
    assert any("#dd9999" in s for s in styles)  # Upper tail

    # Mock light theme
    dummy_light_theme = MagicMock()
    dummy_light_theme.dark = False
    dummy_light_theme.accent = "#0550ae"
    dummy_light_theme.background = "#ffffff"
    dummy_app.current_theme = dummy_light_theme

    rendered_light = matrix.render()
    light_styles = [str(span.style) for span in rendered_light.spans]
    assert any("bold #000000" in s for s in light_styles)  # Head on light theme
    assert any("#0550ae" in s for s in light_styles)  # Upper tail on light theme


def test_matrix_rain_set_enabled():
    matrix = MatrixRain(density=0.2, enabled=False)
    assert matrix.enabled is False
    assert matrix._timer is None

    matrix.set_enabled(True)
    assert matrix.enabled is True

    matrix.set_enabled(False)
    assert matrix.enabled is False


def test_matrix_rain_uses_pure_japanese_katakana():
    from orpheus.matrix import KATAKANA

    # Must contain Japanese Katakana
    assert "ｱ" in KATAKANA and "ﾜ" in KATAKANA
    # Must NOT contain ugly math and punctuation symbols
    for bad_char in ":*+<>~=#$%&\\/":
        assert bad_char not in KATAKANA


def test_ascii_title_render():
    title = AsciiTitle(animation="wave", accent_color="blue")
    text = title.render_frame(width=80)
    assert len(text) > 0
    assert "█" in text or "▒" in text or "▓" in text


def test_ascii_title_pulse_renders_highlight_and_accent():
    from textual.app import App

    from orpheus.themes import get_themes

    class DummyApp(App):
        def on_mount(self):
            for t in get_themes():
                self.register_theme(t)
            self.theme = "github-light-contrast"

    import asyncio

    async def run():
        app = DummyApp()
        async with app.run_test() as pilot:
            title = AsciiTitle(animation="pulse")
            app.screen.mount(title)
            await pilot.pause()
            rendered = title.render()
            assert len(rendered.plain) > 0
            # Ensure title renders stylized spans
            assert len(rendered.spans) > 0

    asyncio.run(run())


def test_home_screen_shortcuts_docked_at_bottom():
    from textual.app import App

    from orpheus.phases.home import HomeScreen
    from orpheus.themes import get_themes

    class DummyApp(App):
        def on_mount(self):
            for t in get_themes():
                self.register_theme(t)
            self.theme = "github-light-contrast"
            self.push_screen(HomeScreen())

    import asyncio

    async def run():
        app = DummyApp()
        async with app.run_test(size=(120, 35)) as pilot:
            await pilot.pause()
            screen = app.screen
            title = screen.query_one("#home-title")
            shortcuts = screen.query_one("#home-shortcuts")
            # Title should be vertically centered around y=13
            assert 10 <= title.region.y <= 16
            # Shortcuts should be at bottom (y >= 30 out of 35)
            assert shortcuts.region.y >= 30

    asyncio.run(run())
