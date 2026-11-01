# ORPHEUS Cyberpunk-Minimalist TUI Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** Redesign ORPHEUS into a cyberpunk-minimalist terminal music player with 3 distinct operational phases (Home, Search, Now Playing), unified by a Glitch Transition engine, Matrix rain, Deezer+yt-dlp audio resolver, adaptive Kitty/half-block album art, and interactive album management.

**Architecture:** A 3-phase Textual application (`HomeScreen`, `SearchScreen`, `NowPlayingScreen`) interconnected by a 200–300ms `GlitchTransition`. Background tasks resolve Deezer metadata to `yt-dlp` audio streams and LRCLIB synchronized lyrics without blocking the UI event loop. Terminal detection routes high-res graphics to Kitty/Ghostty or falls back to ANSI 24-bit half-blocks (`▀▄`).

**Tech Stack:** Python 3.11+, Textual 8.x, mpv IPC JSON, yt-dlp, httpx, Pillow (PIL), mutagen, SQLite.

**Spec:** [`docs/superpowers/specs/2026-11-01-orpheus-ui-redesign-design.md`](file:///home/killua/Projects/Orpheus/docs/superpowers/specs/2026-11-01-orpheus-ui-redesign-design.md)

## Global Constraints

- Language: All UI labels, status messages, error logs, help prompts, and commit messages MUST be in English.
- Terminal Compatibility: Fully responsive down to minimum standard terminal dimension 80 columns × 24 rows.
- No Access Bypasses: Strictly follow sandboxing rules; never execute `rm -rf`.
- Formatting: Zero errors in `ruff check src tests`.
- Knowledge Graph: Run `graphify update .` after changes.
- Existing CLI Flags: Retain `--version`, `--update`, `--music-dir`, and `--no-auto-update`.

## Review Focus

1. **Terminal protocol detection false-positives**: If a terminal reports `TERM_PROGRAM=ghostty` inside a tmux session that does not support passthrough, Kitty graphics escape sequences can print raw garbage characters. Ensure half-block fallback or safe escape querying is available.
2. **Audio resolver timeout under slow networks**: If `yt-dlp` stream extraction hangs or takes >15s, Now Playing must not freeze; it should show "Resolving audio..." with a cancelable/skippable state and fallback to Jamendo or next track.
3. **Double-tap seek race condition**: If right/left arrow is tapped twice rapidly, seeking ±10s must not desync mpv's playback position or cause playback glitches.
4. **Search split pane resizing**: When switching between single pane and `[Alt+l]` split pane on small terminals (80x24), the layout must not overflow or clip results.
5. **Album dialog input focus**: When creating a new album via `Enter` in the `[a]` dialog, typing text into the album name input must not trigger background search or transport shortcuts.

---

### Task 1: Terminal Graphics Protocol Detection & Half-Block Art Engine

**Files:**
- Create: `src/orpheus/art.py`
- Test: `tests/test_art.py`

**Interfaces:**
- Consumes: Pillow `Image`, terminal environment variables (`TERM_PROGRAM`, `KITTY_WINDOW_ID`, `GHOSTTY_RESOURCES_DIR`).
- Produces:
  - `supports_kitty_graphics() -> bool`
  - `encode_kitty_graphics(image_bytes: bytes) -> str`
  - `render_half_blocks(image_bytes: bytes, max_width: int, max_height: int) -> str`
  - `get_placeholder_art(max_width: int, max_height: int) -> str`

- [x] **Step 1: Write failing tests for art rendering & detection**

Create `tests/test_art.py`:
```python
from unittest.mock import patch
from orpheus.art import supports_kitty_graphics, render_half_blocks, get_placeholder_art

def test_supports_kitty_graphics_ghostty():
    with patch.dict("os.environ", {"TERM_PROGRAM": "ghostty"}, clear=True):
        assert supports_kitty_graphics() is True

def test_supports_kitty_graphics_kitty():
    with patch.dict("os.environ", {"KITTY_WINDOW_ID": "1"}, clear=True):
        assert supports_kitty_graphics() is True

def test_supports_kitty_graphics_other():
    with patch.dict("os.environ", {"TERM": "xterm-256color"}, clear=True):
        assert supports_kitty_graphics() is False

def test_placeholder_art_returns_ascii():
    art = get_placeholder_art(20, 10)
    assert len(art) > 0
    assert "ORPHEUS" in art or "♪" in art or "─" in art
```

- [x] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_art.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'orpheus.art'`

- [x] **Step 3: Implement `src/orpheus/art.py`**

Implement terminal graphics detection, Kitty escape sequence generator (`\033_G...`), 24-bit ANSI half-block renderer using Pillow downsampling with `▀` (foreground=top pixel RGB, background=bottom pixel RGB), and an ASCII vinyl/cassette placeholder.

- [x] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_art.py -v`
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add src/orpheus/art.py tests/test_art.py
git commit -m "feat(art): add terminal graphics detection and half-block art renderer"
```

---

### Task 2: Deezer Metadata Provider & YouTube yt-dlp Audio Resolver

**Files:**
- Create: `src/orpheus/resolver.py`
- Test: `tests/test_resolver.py`

**Interfaces:**
- Consumes: `Track` from `src/orpheus/models.py`, `httpx.AsyncClient`.
- Produces:
  - `class DeezerProvider`: `search(query: str) -> list[Track]`, `get_related(artist_id: str) -> list[Track]`
  - `class AudioResolver`: `resolve_stream_url(track: Track) -> tuple[str, str]` (stream_url, source_name) with ±5s duration tolerance, relaxing up to ±15s for Topic channels.

- [x] **Step 1: Write failing tests for Deezer provider and AudioResolver**

Create `tests/test_resolver.py` testing Deezer JSON search parsing, duration scoring, channel prioritization (Topic/Official), and Jamendo fallback.

- [x] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_resolver.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'orpheus.resolver'`

- [x] **Step 3: Implement `src/orpheus/resolver.py`**

Implement `DeezerProvider` using `https://api.deezer.com/search` and `AudioResolver` utilizing `yt-dlp --dump-json --flat-playlist` matching, duration scoring (±5s strict, ±15s Topic), and fallback.

- [x] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_resolver.py -v`
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add src/orpheus/resolver.py tests/test_resolver.py
git commit -m "feat(resolver): implement deezer metadata provider and yt-dlp audio stream resolver"
```

---

### Task 3: Matrix Rain Widget & ASCII Title Engine

**Files:**
- Create: `src/orpheus/matrix.py`
- Create: `src/orpheus/title.py`
- Test: `tests/test_visuals.py`

**Interfaces:**
- Consumes: Textual `Widget`, `renderables`.
- Produces:
  - `class MatrixRain(Widget)`: reactive falling Katakana/digits/symbols with tail fade and density control.
  - `class AsciiTitle(Widget)`: 3D block-pixel "ORPHEUS" (`█ ▀ ▄ ░ ▒ ▓`) with animations (`None`, `Wave`, `Pulse`).

- [x] **Step 1: Write failing tests for MatrixRain and AsciiTitle**

Create `tests/test_visuals.py` verifying character generation, frame stepping, title animation state, and color styling.

- [x] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_visuals.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [x] **Step 3: Implement `src/orpheus/matrix.py` and `src/orpheus/title.py`**

Build `MatrixRain` widget with dynamic column allocation (15-25% density) and `AsciiTitle` with block font, shading, and periodic brightness sweep animations.

- [x] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_visuals.py -v`
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add src/orpheus/matrix.py src/orpheus/title.py tests/test_visuals.py
git commit -m "feat(visuals): add MatrixRain canvas and AsciiTitle 3D block widgets"
```

---

### Task 4: Glitch Transition Widget & Phase Transition Engine

**Files:**
- Create: `src/orpheus/glitch.py`
- Test: `tests/test_glitch.py`

**Interfaces:**
- Consumes: Textual `Widget`, screen dimensions.
- Produces:
  - `class GlitchOverlay(Widget)`: 200–300ms overlay applying horizontal scanline character displacement, random glyph blocks (`█ ▓ ▒ ░ # % &`), accent color flashing, and phase completion callback.

- [x] **Step 1: Write failing tests for GlitchOverlay**

Create `tests/test_glitch.py` testing glitch frame generation, duration lifecycle, character corruption mechanics, and completion callback.

- [x] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_glitch.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'orpheus.glitch'`

- [x] **Step 3: Implement `src/orpheus/glitch.py`**

Implement `GlitchOverlay` capturing the terminal buffer or generating structured cyberpunk horizontal tear noise over 6–9 frames (~250ms).

- [x] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_glitch.py -v`
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add src/orpheus/glitch.py tests/test_glitch.py
git commit -m "feat(glitch): implement cyberpunk glitch transition engine"
```

---

### Task 5: Reusable Settings Modal Component

**Files:**
- Create: `src/orpheus/settings.py`
- Test: `tests/test_settings.py`

**Interfaces:**
- Consumes: Textual `ModalScreen`.
- Produces:
  - `class SettingsModal(ModalScreen)`: centered floating box with `┌─┐│└┘` borders, `── Group ──` headers, `◀ Value ▶` selectors, live preview callbacks, and `Enter`/`Esc` key bindings.

- [x] **Step 1: Write failing tests for SettingsModal**

Create `tests/test_settings.py` testing item navigation with `↑/↓`, value changing with `←/→`, live preview triggers, Enter to save, and Esc to discard.

- [x] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_settings.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'orpheus.settings'`

- [x] **Step 3: Implement `src/orpheus/settings.py`**

Implement `SettingsModal` supporting select, toggle, and numeric settings with custom styling and callbacks.

- [x] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_settings.py -v`
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add src/orpheus/settings.py tests/test_settings.py
git commit -m "feat(settings): add reusable cyberpunk settings modal with live preview"
```

---

### Task 6: User Albums / Playlists Store & Modal

**Files:**
- Create: `src/orpheus/albums.py`
- Modify: `src/orpheus/storage.py`
- Test: `tests/test_albums.py`

**Interfaces:**
- Consumes: `Database` from `src/orpheus/storage.py`.
- Produces:
  - `class AlbumStore`: `create_album(name)`, `rename_album(old, new)`, `delete_album(name)`, `add_track(album_name, track)`, `list_albums()`, `get_album_tracks(name)`.
  - `class AlbumsModal(ModalScreen)`: interactive UI handling `[a]` dialog with `↑/↓`, `Enter` (add or create), `[m]` (modify/rename), `[d]` (delete).

- [x] **Step 1: Write failing tests for AlbumStore and AlbumsModal**

Create `tests/test_albums.py` testing SQLite CRUD for user albums and modal navigation events.

- [x] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_albums.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'orpheus.albums'`

- [x] **Step 3: Implement `src/orpheus/albums.py` and extend `src/orpheus/storage.py`**

Add SQLite schema for albums and album tracks; implement `AlbumStore` and `AlbumsModal`.

- [x] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_albums.py -v`
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add src/orpheus/albums.py src/orpheus/storage.py tests/test_albums.py
git commit -m "feat(albums): implement custom user albums storage and interactive management modal"
```

---

### Task 7: Phase 1 (Home Screen) & Phase 2 (Search Screen with Deezer + Local Split)

**Files:**
- Create: `src/orpheus/phases/home.py`
- Create: `src/orpheus/phases/search.py`
- Test: `tests/test_phases_home_search.py`

**Interfaces:**
- Consumes: `MatrixRain`, `AsciiTitle`, `DeezerProvider`, `AlbumsModal`, `GlitchOverlay`.
- Produces:
  - `class HomeScreen(Screen)`: Home phase with dynamic shortcut bar (`[S] Settings  [f] Find  [q] Quit`, plus `[p] Playing` and `[s] Stop` when music is active).
  - `class SearchScreen(Screen)`: Search phase with 400ms debounce, Online Deezer results, `[Alt+l]` 50/50 split pane for Local library, `[a]` album assignment, and Enter to play.

- [x] **Step 1: Write failing tests for HomeScreen and SearchScreen**

Create `tests/test_phases_home_search.py` testing Home shortcut bar reactivity when audio is idle vs playing, Search query debouncing, split pane toggle `[Alt+l]`, and album modal triggering via `[a]`.

- [x] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_phases_home_search.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [x] **Step 3: Implement `src/orpheus/phases/home.py` and `src/orpheus/phases/search.py`**

Implement Home and Search screens adhering to layout, focus handling (`↓` to results, `Tab` between split panes), and shortcut bars.

- [x] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_phases_home_search.py -v`
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add src/orpheus/phases/home.py src/orpheus/phases/search.py tests/test_phases_home_search.py
git commit -m "feat(phases): implement Home screen and Search screen with Deezer and local split pane"
```

---

### Task 8: Phase 3 (Now Playing Screen) & Player Controls Integration

**Files:**
- Create: `src/orpheus/phases/now_playing.py`
- Modify: `src/orpheus/player.py`
- Test: `tests/test_phase_now_playing.py`

**Interfaces:**
- Consumes: `art.py`, `LyricsService`, `MpvPlayer`, `AudioResolver`, `GlitchOverlay`.
- Produces:
  - `class NowPlayingScreen(Screen)`:
    - Left column: Adaptive album art (Kitty protocol or half-block), track info, slim progress bar `━━━●────`, elapsed/remaining time, volume, repeat badge (`[Repeat: Track]`), karaoke badge (`[Karaoke: On/Off]`).
    - Right column: Synchronized LRCLIB lyrics with `...` intro, active line highlighting, plain lyrics fallback.
    - Footer shortcuts: `[space] play/pause  →/← seek  Shift+→/← next/prev  [r] repeat  [k] karaoke  [esc] back`.
    - Double-tap arrow key detection (`<= 350ms`) for ±10s seeking.
    - Background prefetch 20s before song end.

- [x] **Step 1: Write failing tests for NowPlayingScreen**

Create `tests/test_phase_now_playing.py` testing single-tap vs double-tap seek detection, synchronized lyrics scrolling, repeat mode cycling, karaoke toggle, and esc transition to Home.

- [x] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_phase_now_playing.py -v`
Expected: FAIL with `ModuleNotFoundError`

- [x] **Step 3: Implement `src/orpheus/phases/now_playing.py`**

Implement Now Playing screen with 2-column layout, lyrics syncing, double-tap seek handling, and Demucs karaoke toggle.

- [x] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_phase_now_playing.py -v`
Expected: PASS

- [x] **Step 5: Commit**

```bash
git add src/orpheus/phases/now_playing.py tests/test_phase_now_playing.py
git commit -m "feat(phases): implement Now Playing screen with synced lyrics, album art, and advanced transport controls"
```

---

### Task 9: App Controller Phase Orchestration & E2E System Tests

**Files:**
- Modify: `src/orpheus/app.py`
- Modify: `src/orpheus/__main__.py`
- Test: `tests/test_app.py`
- Test: `tests/test_cli.py`

**Interfaces:**
- Consumes: All phases (`HomeScreen`, `SearchScreen`, `NowPlayingScreen`), `SettingsModal`, `GlitchOverlay`.
- Produces:
  - Unified `OrpheusApp` orchestrating the 3 phases via Glitch transitions while preserving CLI arguments and continuous background audio playback.

- [x] **Step 1: Write failing e2e tests for phase transitions in `tests/test_app.py`**

Update `tests/test_app.py` to test navigating Home -> Search -> Now Playing -> Home with background playback, `[s]` Stop on Home, and `[p]` Playing return.

- [x] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_app.py -v`
Expected: FAIL matching new phase architecture expectations

- [x] **Step 3: Update `src/orpheus/app.py` and `src/orpheus/__main__.py`**

Refactor `OrpheusApp` to host the 3 screen phases with Glitch transitions, wire settings modal, and preserve background audio when returning to Home.

- [x] **Step 4: Run full test suite & linter to verify 100% pass**

Run: `pytest`
Expected: 100% PASS
Run: `ruff check src tests`
Expected: Zero errors
Run: `graphify update .`

- [x] **Step 5: Commit & Push**

```bash
git add src/ tests/ docs/
git commit -m "feat(app): orchestrate 3-phase TUI with glitch transitions, album art, and deezer resolver"
git push origin main
```
