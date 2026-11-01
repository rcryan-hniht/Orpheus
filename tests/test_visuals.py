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


def test_ascii_title_render():
    title = AsciiTitle(animation="wave", accent_color="blue")
    text = title.render_frame(width=80)
    assert len(text) > 0
    assert "█" in text or "▒" in text or "▓" in text
