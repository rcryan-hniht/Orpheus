from __future__ import annotations

import base64
import io
import os

from PIL import Image


def supports_kitty_graphics() -> bool:
    """Return True if current terminal environment supports Kitty Graphics Protocol."""
    term = os.environ.get("TERM", "").lower()
    if term == "dumb":
        return False
    if os.environ.get("KITTY_WINDOW_ID"):
        return True
    if os.environ.get("GHOSTTY_RESOURCES_DIR"):
        return True
    if os.environ.get("TERM_PROGRAM") in ("ghostty", "kitty"):
        return True
    if "kitty" in term or "ghostty" in term:
        return True
    return False


def compute_kitty_dimensions(
    image_bytes: bytes | None, max_cols: int = 28, max_rows: int = 14
) -> tuple[int, int]:
    """Calculate (cols, rows) that preserves the image's true aspect ratio in the terminal.

    In standard monospace terminal fonts, a character cell is approximately 1:2 aspect ratio
    (width = 0.5 * height). For a square image (aspect 1.0), cols = 2 * rows.
    """
    if not image_bytes:
        return max_cols, max_rows

    try:
        img = Image.open(io.BytesIO(image_bytes))
        w, h = img.size
        aspect = (w / h) if h > 0 else 1.0
    except Exception:
        aspect = 1.0

    target_rows = max_rows
    target_cols = int(round(2 * target_rows * aspect))
    if target_cols > max_cols:
        target_cols = max_cols
        target_rows = max(4, int(round(target_cols / (2 * aspect))))
    elif target_cols < 8:
        target_cols = 8
        target_rows = max(4, int(round(target_cols / (2 * aspect))))

    return target_cols, target_rows


def encode_kitty_graphics(image_bytes: bytes, cols: int = 28, rows: int = 14) -> str:
    """Encode an image into Kitty Graphics Protocol escape sequences scaled to cols x rows."""
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        pixel_w = max(10, cols * 12)
        pixel_h = max(10, rows * 24)
        img.thumbnail((pixel_w, pixel_h), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        png_bytes = buf.getvalue()
    except Exception:
        png_bytes = image_bytes

    b64 = base64.b64encode(png_bytes).decode("ascii")
    chunks = [b64[i : i + 4096] for i in range(0, len(b64), 4096)]
    if not chunks:
        return ""

    out: list[str] = []
    for i, chunk in enumerate(chunks):
        is_last = i == len(chunks) - 1
        m = 0 if is_last else 1
        if i == 0:
            out.append(f"\033_Ga=T,f=100,t=d,c={cols},r={rows},z=1,m={m};{chunk}\033\\")
        else:
            out.append(f"\033_Gm={m};{chunk}\033\\")
    return "".join(out)


def get_kitty_delete_command() -> str:
    """Return Kitty Graphics Protocol escape sequence to delete all placed images."""
    return "\033_Ga=d,d=a\033\\"


def render_half_blocks(image_bytes: bytes, max_width: int = 28, max_height: int = 14) -> str:
    """Render image downsampled to 24-bit ANSI half-block (▀▄) characters.

    Each character cell represents two vertical pixels (top=foreground, bottom=background).
    """
    try:
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception:
        return get_placeholder_art(max_width, max_height)

    # Each terminal cell is 1 char wide and 2 vertical half-blocks tall
    target_pixel_height = max_height * 2
    w_ratio = max_width / img.width
    h_ratio = target_pixel_height / img.height
    scale = min(w_ratio, h_ratio, 1.0)

    new_w = max(1, int(img.width * scale))
    new_h = max(2, int(img.height * scale))
    # Make sure height is even
    if new_h % 2 != 0:
        new_h += 1

    img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    pixels = img.load()

    lines: list[str] = []
    for y in range(0, new_h, 2):
        line_parts: list[str] = []
        for x in range(new_w):
            r1, g1, b1 = pixels[x, y]
            if y + 1 < new_h:
                r2, g2, b2 = pixels[x, y + 1]
            else:
                r2, g2, b2 = 0, 0, 0
            # ▀ with fg = top pixel, bg = bottom pixel
            line_parts.append(f"\033[38;2;{r1};{g1};{b1}m\033[48;2;{r2};{g2};{b2}m▀\033[0m")
        lines.append("".join(line_parts))

    return "\n".join(lines)


def get_placeholder_art(max_width: int = 30, max_height: int = 15) -> str:
    """Generate a clean minimalist ASCII cassette/album placeholder."""
    w = max(20, min(max_width, 36))
    h = max(8, min(max_height, 14))

    top = "┌" + "─" * (w - 2) + "┐"
    bottom = "└" + "─" * (w - 2) + "┘"
    inner_w = w - 2

    lines = [top]
    center_y = h // 2
    for y in range(1, h - 1):
        if y == center_y - 1:
            line_content = "──[ CASSETTE ]──".center(inner_w)
        elif y == center_y:
            line_content = "(O)   ORPHEUS   (O)".center(inner_w)
        elif y == center_y + 1:
            line_content = "──[   ♪ ♫ ♪  ]──".center(inner_w)
        else:
            line_content = " " * inner_w
        lines.append("│" + line_content + "│")
    lines.append(bottom)
    return "\n".join(lines)
