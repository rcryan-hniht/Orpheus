import time
from unittest.mock import AsyncMock

from orpheus.phases.now_playing import (
    AlbumArtWidget,
    NowPlayingFooter,
    NowPlayingScreen,
    format_progress_bar,
)


def test_format_progress_bar():
    bar = format_progress_bar(position=30, duration=100, width=20)
    assert "●" in bar
    assert "━" in bar
    assert "─" in bar


def test_now_playing_repeat_cycling():
    screen = NowPlayingScreen()
    assert screen.repeat_mode == "off"
    screen.action_toggle_repeat()
    assert screen.repeat_mode == "track"
    screen.action_toggle_repeat()
    assert screen.repeat_mode == "all"
    screen.action_toggle_repeat()
    assert screen.repeat_mode == "off"


def test_now_playing_double_tap_seek():
    screen = NowPlayingScreen()
    # First tap
    t1 = time.monotonic()
    delta1 = screen.calc_seek_delta(direction="forward", now=t1)
    assert delta1 == 5.0

    # Rapid second tap within 200ms
    t2 = t1 + 0.2
    delta2 = screen.calc_seek_delta(direction="forward", now=t2)
    assert delta2 == 10.0

    # Slow third tap after 500ms
    t3 = t2 + 0.5
    delta3 = screen.calc_seek_delta(direction="forward", now=t3)
    assert delta3 == 5.0


def test_now_playing_footer_render():
    footer = NowPlayingFooter()
    rendered = footer.render().plain
    assert "[space]" in rendered
    assert "Seek" in rendered
    assert "[r]" in rendered
    assert "[k]" in rendered
    assert "[f]" in rendered
    assert "[S]" in rendered
    assert "[q]" in rendered
    assert "[Esc]" in rendered


def test_now_playing_action_find_and_quit():
    screen = NowPlayingScreen()
    switched = ""
    exited = False

    class DummyApp:
        def switch_phase(self, phase):
            nonlocal switched
            switched = phase

        def exit(self):
            nonlocal exited
            exited = True

    screen._app = DummyApp()
    screen.action_find()
    assert switched == "search"
    screen.action_quit()
    assert exited is True


def test_synced_lyrics_widget_loading_and_empty():
    from orpheus.phases.now_playing import SyncedLyricsWidget

    w = SyncedLyricsWidget()
    w.set_loading(True)
    assert "Loading lyrics" in w.render().plain
    w.set_lyrics(None)
    assert "No lyrics available" in w.render().plain


def test_album_art_widget_render_half_blocks():
    art = AlbumArtWidget()
    # Default placeholder when no cover
    rendered = art.render()
    assert len(rendered.plain) > 0
    assert "ORPHEUS" in rendered.plain or "CASSETTE" in rendered.plain


def test_album_art_kitty_centering_calculation():
    from unittest.mock import PropertyMock, patch

    from textual.geometry import Region

    art = AlbumArtWidget()
    art._raw_bytes = b"fake-png-bytes"
    art._is_mounted = True
    written = []
    art._write_terminal = lambda data: written.append(data)

    mock_region = Region(x=0, y=0, width=44, height=20)

    import orpheus.phases.now_playing as np_mod

    orig_supports = np_mod.supports_kitty_graphics
    orig_encode = np_mod.encode_kitty_graphics
    try:
        np_mod.supports_kitty_graphics = lambda: True
        np_mod.encode_kitty_graphics = lambda b, cols, rows: "KITTY_PAYLOAD"
        mock_reg = PropertyMock(return_value=mock_region)
        with patch.object(AlbumArtWidget, "region", new_callable=lambda: mock_reg):
            art._draw_kitty()
        assert len(written) == 1
        # Escape sequence should contain column 7: \033[1;7H
        assert "\033[1;7H" in written[0]
    finally:
        np_mod.supports_kitty_graphics = orig_supports
        np_mod.encode_kitty_graphics = orig_encode


def test_now_playing_actions_await_app_methods():
    import asyncio

    class FakeApp:
        def __init__(self):
            self.action_toggle_pause = AsyncMock()
            self.action_seek = AsyncMock()
            self.action_next = AsyncMock()
            self.action_prev = AsyncMock()
            self.action_karaoke = AsyncMock()

    fake_app = FakeApp()
    screen = NowPlayingScreen()
    screen._app = fake_app

    async def run():
        await screen.action_toggle_playback()
        fake_app.action_toggle_pause.assert_awaited_once()

        await screen.action_seek_forward()
        fake_app.action_seek.assert_awaited_once_with(5.0)

        await screen.action_next_track()
        fake_app.action_next.assert_awaited_once()

        await screen.action_prev_track()
        fake_app.action_prev.assert_awaited_once()

        await screen.action_toggle_karaoke()
        fake_app.action_karaoke.assert_awaited_once()

    asyncio.run(run())
