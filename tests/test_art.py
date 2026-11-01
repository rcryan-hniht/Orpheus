import io
from unittest.mock import patch

from PIL import Image

from orpheus.art import (
    encode_kitty_graphics,
    get_placeholder_art,
    render_half_blocks,
    supports_kitty_graphics,
)


def test_supports_kitty_graphics_ghostty():
    with patch.dict("os.environ", {"TERM_PROGRAM": "ghostty"}, clear=True):
        assert supports_kitty_graphics() is True


def test_supports_kitty_graphics_kitty():
    with patch.dict("os.environ", {"KITTY_WINDOW_ID": "1"}, clear=True):
        assert supports_kitty_graphics() is True


def test_supports_kitty_graphics_resources():
    with patch.dict("os.environ", {"GHOSTTY_RESOURCES_DIR": "/usr/share/ghostty"}, clear=True):
        assert supports_kitty_graphics() is True


def test_supports_kitty_graphics_other():
    with patch.dict("os.environ", {"TERM": "xterm-256color"}, clear=True):
        assert supports_kitty_graphics() is False


def test_placeholder_art_returns_ascii():
    art = get_placeholder_art(20, 10)
    assert len(art) > 0
    assert "ORPHEUS" in art or "♪" in art or "─" in art or "┌" in art


def test_encode_kitty_graphics_escapes():
    img = Image.new("RGB", (10, 10), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    raw = buf.getvalue()

    seq = encode_kitty_graphics(raw)
    assert seq.startswith("\033_G")
    assert seq.endswith("\033\\")
    assert "a=T,f=100" in seq or "m=0" in seq


def test_render_half_blocks_produces_unicode_blocks():
    img = Image.new("RGB", (4, 4), color=(0, 255, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    raw = buf.getvalue()

    rendered = render_half_blocks(raw, max_width=4, max_height=4)
    assert "▀" in rendered
    assert "\033[38;2;" in rendered or "\033[48;2;" in rendered
