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
    assert "[?]" in rendered
    assert "[p]" in rendered
    assert "[s]" not in rendered  # Hidden from footer, available in which key
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
    assert "[?]" in rendered
    assert "Which key" in rendered
    assert "[Alt+l]" not in rendered
    assert "[Alt+h]" not in rendered
    assert "[p]" not in rendered
    assert "[a]" in rendered
    assert "[Enter]" in rendered
    assert "[f]" in rendered
    assert "[S]" in rendered
    assert "[q]" in rendered
    assert "[Esc]" in rendered

    # When playing
    class DummyApp:
        current_track = Track("1", "Song", "/path")

    bar._app = DummyApp()
    rendered_playing = bar.render().plain
    assert "[p]" in rendered_playing
    assert "Playing" in rendered_playing


def test_search_screen_albums_and_split():
    screen = SearchScreen()
    # Albums split is True by default for two-pane layout: MY ALBUM and SEARCH
    assert screen.albums_split is True
    assert screen.local_split is False

    # Toggle albums split (Alt+h)
    screen.action_toggle_albums_split()
    assert screen.albums_split is False

    # Toggle back on
    screen.action_toggle_albums_split()
    assert screen.albums_split is True

    # Toggle local split (Alt+l)
    screen.action_toggle_split()
    assert screen.local_split is True
    assert screen.split_view is True

    # Toggle off local split
    screen.action_toggle_split()
    assert screen.local_split is False
    assert screen.split_view is False


def test_which_key_modal_dismiss():
    from orpheus.which_key import WhichKeyModal

    modal = WhichKeyModal()
    dismissed = False

    def fake_dismiss(res):
        nonlocal dismissed
        dismissed = True

    modal.dismiss = fake_dismiss
    modal.action_dismiss_modal()
    assert dismissed is True


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


def test_search_screen_artist_query_and_enter_submission():
    from unittest.mock import AsyncMock

    from textual.app import App
    from textual.widgets import Input

    target_track = Track("dz-11", "Trần Duy Hưng", "https://deezer.com/11", artist="Dangrangto")

    class DummyProvider:
        def __init__(self):
            self.search_by_artist = AsyncMock(return_value=[target_track])
            self.search = AsyncMock(return_value=[])

    provider = DummyProvider()
    screen = SearchScreen(deezer_provider=provider)

    class TestApp(App):
        def on_mount(self):
            self.push_screen(screen)

    import asyncio

    played_tracks = []

    class MockApp(TestApp):
        def load_playlist_and_play(self, track, queue, history):
            played_tracks.append((track, queue, history))

    async def run():
        app = MockApp()
        async with app.run_test(size=(100, 30)) as pilot:
            await pilot.pause()
            inp = screen.query_one("#search-input", Input)
            inp.value = "@artist DangRangTo"

            # Submit input (simulates pressing Enter on search bar)
            await screen.on_input_submitted(Input.Submitted(inp, value="@artist DangRangTo"))
            await pilot.pause()

            # Verify provider search_by_artist was called
            provider.search_by_artist.assert_awaited_once_with("DangRangTo", limit=30)
            # Verify immediate transition to play top track
            assert len(played_tracks) == 1
            assert played_tracks[0][0] == target_track

    asyncio.run(run())


def test_search_screen_action_stop():
    screen = SearchScreen()
    stopped = False

    class DummyApp:
        def action_stop(self):
            nonlocal stopped
            stopped = True

    screen._app = DummyApp()
    # When input does not have focus, action_stop calls app.action_stop
    screen.action_stop()
    assert stopped is True


def test_search_screen_action_now_playing():
    screen = SearchScreen()
    switched_to = None

    class DummyApp:
        current_track = Track("t1", "Test", "/path")

        def switch_phase(self, phase):
            nonlocal switched_to
            switched_to = phase

    screen._app = DummyApp()
    screen.action_now_playing()
    assert switched_to == "now_playing"

    # When input has focus but empty, still switches to now_playing
    class DummyInput:
        has_focus = True
        value = ""

    screen.query_one = lambda sel, cls=None: DummyInput()
    switched_to = None
    screen._app.current_track = Track("t1", "Test", "/path")
    screen.action_now_playing()
    assert switched_to == "now_playing"

    # When input has focus and value is typed, does not switch (preserves typing)
    DummyInput.value = "pop"
    switched_to = None
    screen.action_now_playing()
    assert switched_to is None

    # If current_track is None, does nothing
    DummyInput.value = ""
    switched_to = None
    screen._app.current_track = None
    screen.action_now_playing()
    assert switched_to is None


def test_search_screen_action_delete_item_album_and_track():
    from unittest.mock import MagicMock

    screen = SearchScreen()
    mock_store = MagicMock()
    mock_notify = MagicMock()

    class DummyApp:
        album_store = mock_store
        queue = [Track("t1", "Track 1", "/1"), Track("t2", "Track 2", "/2")]
        notify = mock_notify

    screen._app = DummyApp()

    # Case 1: In #albums-table pane
    screen._active_pane = "albums"
    screen.albums_split = True

    class DummyAlbumsTable:
        cursor_row = 0
        row_count = 1

        def coordinate_to_cell_key(self, coord):
            class CellKey:
                class RowKey:
                    value = "album:MyFavs"

                row_key = RowKey()

            return CellKey()

    screen.query_one = lambda sel, cls=None: DummyAlbumsTable()
    screen._populate_albums_table = MagicMock()
    screen.action_delete_item()
    mock_store.delete_album.assert_called_once_with("MyFavs")
    mock_notify.assert_called_with(
        "Deleted album 'MyFavs'", title="Album Deleted", timeout=3.0, markup=False
    )

    # Case 2: In #online-table with an album open
    screen._active_pane = "online"
    screen.current_selected_album = "Rock"
    screen._online_results = [Track("t1", "Track 1", "/1"), Track("t2", "Track 2", "/2")]
    mock_store.get_album_tracks.return_value = [Track("t2", "Track 2", "/2")]

    class DummyTracksTable:
        cursor_row = 0
        row_count = 1

        def coordinate_to_cell_key(self, coord):
            class CellKey:
                class RowKey:
                    value = "t1"

                row_key = RowKey()

            return CellKey()

        def clear(self):
            pass

        def add_row(self, *args, **kwargs):
            pass

    dummy_header = MagicMock()
    screen.query_one = lambda sel, cls=None: dummy_header if "header" in sel else DummyTracksTable()
    screen.action_delete_item()
    mock_store.remove_track.assert_called_once_with("Rock", "t1")
    assert len(screen._app.queue) == 1
    assert screen._app.queue[0].id == "t2"
    mock_notify.assert_called_with(
        "Removed 'Track 1' from album 'Rock'",
        title="Album Updated",
        timeout=3.0,
        markup=False,
    )


def test_search_screen_down_arrow_routing_and_focus():
    import asyncio

    from textual.app import App
    from textual.widgets import DataTable, Input

    class TestApp(App):
        def on_mount(self):
            self.push_screen(SearchScreen())

    async def run():
        app = TestApp()
        async with app.run_test(size=(100, 30)) as pilot:
            await pilot.pause()
            screen = app.screen
            inp = screen.query_one("#search-input", Input)

            # 1. On entry, search box is focused
            assert inp.has_focus is True

            # 2. Down arrow with empty search -> focus goes to My album (albums-table)
            await pilot.press("down")
            await pilot.pause()
            albums_tbl = screen.query_one("#albums-table", DataTable)
            assert albums_tbl.has_focus is True

            # 3. Press Up to return to search box
            await pilot.press("up")
            await pilot.pause()
            assert inp.has_focus is True

            # 4. If search results are present, Down arrow goes to SEARCH pane
            inp.value = "Huong Ly"
            screen._online_results = [Track("1", "Song A", "loc", artist="Huong Ly")]
            online_tbl = screen.query_one("#online-table", DataTable)
            online_tbl.add_row("Song A", "Huong Ly", "Alb", "3:00", key="1")
            screen.current_selected_album = None

            await pilot.press("down")
            await pilot.pause()
            assert online_tbl.has_focus is True

    asyncio.run(run())
