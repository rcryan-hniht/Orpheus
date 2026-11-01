import time

from orpheus.phases.now_playing import NowPlayingScreen, format_progress_bar


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
