from orpheus.glitch import GlitchOverlay, generate_glitch_frame


def test_generate_glitch_frame_dimensions():
    frame = generate_glitch_frame(width=80, height=24, intensity=0.5)
    assert len(frame) == 24
    for line in frame:
        assert len(line) == 80


def test_generate_glitch_frame_contains_glitch_chars():
    frame = generate_glitch_frame(width=80, height=24, intensity=0.8)
    combined = "".join(frame)
    assert any(c in combined for c in "█▓▒░#%&/\\<>")


def test_glitch_overlay_lifecycle():
    called = []

    def on_complete():
        called.append(True)

    overlay = GlitchOverlay(duration_seconds=0.1, on_complete=on_complete)
    assert overlay.is_active is True
    # Step all frames
    overlay.finish()
    assert overlay.is_active is False
    assert len(called) == 1
