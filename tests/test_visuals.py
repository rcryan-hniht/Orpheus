from orpheus.matrix import MatrixRain
from orpheus.title import AsciiTitle, get_title_lines


def test_get_title_lines():
    lines = get_title_lines(style="pulse", frame=0, accent_color="cyan")
    assert len(lines) >= 5
    # Should contain block glyphs
    combined = "".join(lines)
    assert "█" in combined or "▀" in combined or "▄" in combined or "▓" in combined


def test_matrix_rain_step():
    matrix = MatrixRain(density=0.2)
    matrix.setup_columns(width=40, height=20)
    assert len(matrix.columns) == 40
    # Step forward a frame
    matrix.step()
    # At least some columns should have characters
    assert any(len(col.tail) > 0 for col in matrix.columns)


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


def test_ascii_title_light_theme_palette():
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
            _, highlight, _, _ = title._get_palette()
            # Must NOT use white highlight on light theme
            assert "#ffffff" not in highlight.lower()

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
