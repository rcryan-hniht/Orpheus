from orpheus.albums import AlbumStore
from orpheus.models import Track
from orpheus.storage import Database


def test_album_store_crud(tmp_path):
    db = Database(tmp_path / "music.sqlite")
    store = AlbumStore(db)

    # Empty initially
    assert store.list_albums() == []

    # Create album
    store.create_album("Cyber Hits")
    assert store.list_albums() == ["Cyber Hits"]

    # Add track
    t1 = Track(id="1", title="Resonance", location="/res.mp3", artist="HOME")
    store.add_track("Cyber Hits", t1)
    tracks = store.get_album_tracks("Cyber Hits")
    assert len(tracks) == 1
    assert tracks[0].title == "Resonance"

    # Rename album
    store.rename_album("Cyber Hits", "Synth Legends")
    assert store.list_albums() == ["Synth Legends"]
    tracks2 = store.get_album_tracks("Synth Legends")
    assert len(tracks2) == 1

    # Remove track
    t2 = Track(id="2", title="Macintosh Plus", location="/mac.mp3", artist="Vektroid")
    store.add_track("Synth Legends", t2)
    assert len(store.get_album_tracks("Synth Legends")) == 2
    store.remove_track("Synth Legends", "1")
    tracks3 = store.get_album_tracks("Synth Legends")
    assert len(tracks3) == 1
    assert tracks3[0].id == "2"

    # Delete album
    store.delete_album("Synth Legends")
    assert store.list_albums() == []
    assert store.get_album_tracks("Synth Legends") == []

    db.close()


def test_album_and_track_queue_ordering(tmp_path):
    db = Database(tmp_path / "queue_test.sqlite")
    store = AlbumStore(db)

    # 1. Test album creation queue order (FIFO)
    store.create_album("Zeta")
    store.create_album("Beta")
    store.create_album("Alpha")
    assert store.list_albums() == ["Zeta", "Beta", "Alpha"]

    # 2. Test track addition queue order (FIFO)
    t_z = Track(id="tz", title="Zeta Track", location="/z.mp3")
    t_a = Track(id="ta", title="Alpha Track", location="/a.mp3")
    t_m = Track(id="tm", title="Mid Track", location="/m.mp3")

    store.add_track("Beta", t_z)
    store.add_track("Beta", t_a)
    store.add_track("Beta", t_m)

    tracks = store.get_album_tracks("Beta")
    assert [t.id for t in tracks] == ["tz", "ta", "tm"]
    assert [t.title for t in tracks] == ["Zeta Track", "Alpha Track", "Mid Track"]

    # Re-adding an existing track queues it at the end
    store.add_track("Beta", t_z)
    tracks_after = store.get_album_tracks("Beta")
    assert [t.id for t in tracks_after] == ["ta", "tm", "tz"]

    db.close()


def test_albums_modal_colon_key_and_creation(tmp_path):
    import asyncio

    from textual.app import App
    from textual.widgets import Input

    from orpheus.albums import AlbumsModal
    from orpheus.themes import get_themes

    db = Database(tmp_path / "albums_modal.sqlite")
    store = AlbumStore(db)
    track = Track(
        id="t100", title="Test Track", location="https://example.com/audio", artist="Tester"
    )

    notifications = []

    class TestApp(App):
        def notify(self, message, **kwargs):
            notifications.append((message, kwargs))
            super().notify(message, **kwargs)

        def on_mount(self):
            for t in get_themes():
                self.register_theme(t)
            self.theme = "oasis-starlight"
            self.push_screen(AlbumsModal(store=store, target_track=track))

    async def run():
        app = TestApp()
        async with app.run_test(size=(80, 24)) as pilot:
            await pilot.pause()
            modal = app.screen
            assert isinstance(modal, AlbumsModal)

            # Test colon key triggers create_mode
            await pilot.press("colon")
            await pilot.pause()
            assert modal.mode == "create"
            inp = modal.query_one(Input)
            assert inp.display is True
            assert inp.has_focus is True

            # Type album name and press Enter to confirm
            await pilot.press("V", "i", "e", "t", "N", "a", "m", "enter")
            await pilot.pause()

            # Verify album created in store and track added
            assert "VietNam" in store.list_albums()
            album_tracks = store.get_album_tracks("VietNam")
            assert len(album_tracks) == 1
            assert album_tracks[0].title == "Test Track"
            assert any("VietNam" in msg and "Test Track" in msg for msg, _ in notifications)

    asyncio.run(run())
    db.close()


def test_confirm_modal_and_album_name_modal():
    import asyncio

    from textual.app import App
    from textual.widgets import Button, Input

    from orpheus.albums import AlbumNameModal, ConfirmModal
    from orpheus.themes import get_themes

    # Test 1: ConfirmModal dismissals
    dismiss_results = []

    class ConfirmApp(App):
        def on_mount(self):
            for t in get_themes():
                self.register_theme(t)
            self.theme = "oasis-starlight"
            self.push_screen(
                ConfirmModal(title="Delete Album", message="Are you sure?"),
                callback=lambda res: dismiss_results.append(res),
            )

    async def run_confirm_yes():
        app = ConfirmApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("y")
            await pilot.pause()
            assert dismiss_results == [True]

    asyncio.run(run_confirm_yes())

    dismiss_results.clear()

    async def run_confirm_no():
        app = ConfirmApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("n")
            await pilot.pause()
            assert dismiss_results == [False]

    asyncio.run(run_confirm_no())

    dismiss_results.clear()

    async def run_confirm_button():
        app = ConfirmApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            btn = app.screen.query_one("#confirm-yes", Button)
            btn.press()
            await pilot.pause()
            assert dismiss_results == [True]

    asyncio.run(run_confirm_button())

    # Test 2: AlbumNameModal dismissals
    input_results = []

    class NameApp(App):
        def on_mount(self):
            for t in get_themes():
                self.register_theme(t)
            self.theme = "oasis-starlight"
            self.push_screen(
                AlbumNameModal(title="Create Album", initial_value="Synth"),
                callback=lambda res: input_results.append(res),
            )

    async def run_name_submit():
        app = NameApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            inp = app.screen.query_one("#album-name-input", Input)
            assert inp.has_focus is True
            assert inp.value == "Synth"
            await pilot.press("w", "a", "v", "e", "enter")
            await pilot.pause()
            assert input_results == ["Synthwave"]

    asyncio.run(run_name_submit())

    input_results.clear()

    async def run_name_cancel():
        app = NameApp()
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("escape")
            await pilot.pause()
            assert input_results == [None]

    asyncio.run(run_name_cancel())
