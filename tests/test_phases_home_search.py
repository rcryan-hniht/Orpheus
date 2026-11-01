from orpheus.models import Track
from orpheus.phases.home import ShortcutBar
from orpheus.phases.search import SearchScreen, SearchStatusBar


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


def test_search_status_bar_render():
    bar = SearchStatusBar()
    rendered = bar.render().plain
    assert "[Alt+l]" in rendered
    assert "[a]" in rendered
    assert "[Enter]" in rendered
    assert "[f]" in rendered
    assert "[S]" in rendered
    assert "[q]" in rendered
    assert "[Esc]" in rendered


def test_rank_tracks_by_query_exact_match_top():
    from orpheus.resolver import rank_tracks_by_query

    t1 = Track("1", "Như Một Người Dưng (Jerk Drill x Synth Club)", "l1", artist="Bảo Ngọc")
    t2 = Track("2", "Như Một Người Rưng", "l2", artist="OSAD")
    t3 = Track("3", "Như Một Giấc Mơ", "l3", artist="Mỹ Tâm")
    tracks = [t1, t2, t3]

    ranked = rank_tracks_by_query(tracks, "Như Một Người Rưng")
    assert ranked[0].id == "2"
    assert ranked[0].title == "Như Một Người Rưng"


def test_rank_tracks_by_query_base_title_and_case_insensitive():
    from orpheus.resolver import rank_tracks_by_query

    t1 = Track("1", "Song Title (Remix 2026)", "l1", artist="Artist A")
    t2 = Track("2", "Other Song", "l2", artist="Artist B")
    t3 = Track("3", "Song Title", "l3", artist="Artist C")
    tracks = [t1, t2, t3]

    ranked = rank_tracks_by_query(tracks, "song title")
    assert ranked[0].id == "3"  # Exact match
    assert ranked[1].id == "1"  # Base title match


def test_search_screen_action_quit_and_focus_search():
    screen = SearchScreen()
    exited = False

    class DummyApp:
        def exit(self):
            nonlocal exited
            exited = True

    screen._app = DummyApp()
    screen.action_quit()
    assert exited is True


def test_search_screen_playlist_context():
    tracks = [
        Track("track:1", "Song 1", "https://example.com/1", artist="Artist A"),
        Track("track:2", "Song 2", "https://example.com/2", artist="Artist B"),
        Track("track:3", "Song 3", "https://example.com/3", artist="Artist C"),
    ]
    screen = SearchScreen(local_tracks=tracks)
    screen._online_results = tracks

    # Simulate online selection at index 1
    class DummyTable:
        cursor_row = 1
        row_count = 3

        def coordinate_to_cell_key(self, coord):
            class DummyCellKey:
                class DummyRowKey:
                    value = "track:2"

                row_key = DummyRowKey()

            return DummyCellKey()

    screen.query_one = lambda sel, cls=None: DummyTable() if "table" in sel else None
    selected, queue, history = screen._get_selected_track_and_context()

    assert selected == tracks[1]
    assert queue == [tracks[2]]
    assert history == [tracks[0]]
