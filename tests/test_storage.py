from orpheus.models import Track
from orpheus.storage import Database


def test_queue_and_delay_survive_reopen(tmp_path):
    path = tmp_path / "music.sqlite"
    track = Track(id="file-1", title="Song", location="/music/song.mp3", artist="A")
    db = Database(path)
    db.save_queue([track])
    db.set_delay(track.id, 1.25)
    db.close()

    db = Database(path)
    assert db.load_queue() == [track]
    assert db.get_delay(track.id) == 1.25
    assert db.get_delay("other") == 0.0
    db.close()


def test_queue_replacement_clears_old_entries(tmp_path):
    db = Database(tmp_path / "music.sqlite")
    db.save_queue([Track("a", "A", "/a")])
    db.save_queue([])
    assert db.load_queue() == []
    db.close()


def test_theme_setting_migrates_existing_database_without_losing_music_data(tmp_path):
    path = tmp_path / "music.sqlite"
    track = Track("local:old", "Old song", "/music/old.mp3")
    db = Database(path)
    db.save_queue([track])
    db.set_delay(track.id, 0.5)
    db.connection.execute("INSERT INTO lyrics_cache VALUES (?, ?, ?)", (track.id, None, 1000))
    db.connection.execute("DROP TABLE settings")
    db.connection.commit()
    db.close()

    db = Database(path)
    assert db.get_theme() is None
    db.set_theme("catppuccin-latte")
    db.close()

    db = Database(path)
    assert db.get_theme() == "catppuccin-latte"
    assert db.load_queue() == [track]
    assert db.get_delay(track.id) == 0.5
    assert db.connection.execute("SELECT track_id FROM lyrics_cache").fetchone() == (track.id,)
    db.close()
