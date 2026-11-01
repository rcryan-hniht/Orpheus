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

    # Delete album
    store.delete_album("Synth Legends")
    assert store.list_albums() == []
    assert store.get_album_tracks("Synth Legends") == []

    db.close()
