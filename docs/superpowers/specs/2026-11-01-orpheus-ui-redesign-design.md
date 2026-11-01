# ORPHEUS Cyberpunk-Minimalist TUI Redesign — Design Specification

## 1. Intent & Context

**Orpheus** is evolving from a traditional multi-pane terminal music player into an immersive, cyberpunk-minimalist terminal music experience (TUI). The redesign replaces the cluttered multi-widget layout with three distinct operational phases (**Home**, **Search**, **Now Playing**), unified by a **Glitch Transition**, a **Matrix Rain** animated canvas, intelligent **Deezer + yt-dlp Audio Resolution**, and adaptive **Album Art Rendering** (native Kitty Graphics Protocol for Ghostty/Kitty, with an ANSI half-block fallback for other terminals).

---

## 2. Goals, Non-Goals & Anti-Goals

### Goals
- **3 Distinct App Phases**:
  1. **Home**: Full-screen Matrix rain background, central large 3D-shaded ASCII "ORPHEUS" title (`░▒▓`), and a dynamic shortcut bar (`[S] Settings`, `[f] Find`, `[q] Quit`, plus `[p] Playing` and `[s] Stop` when music is active).
  2. **Search**: Online Deezer search by default (metadata, album art URL, related tracks, debounced 400ms). `[Alt+l]` toggles a 50/50 split pane with the local library sliding in from the right. `[a]` manages user custom albums (create, modify, delete, add).
  3. **Now Playing**: 2-column layout. Left: auto-detected Kitty Graphics Protocol album art (Ghostty/Kitty) or ANSI half-block (`▀▄`) fallback, slim progress bar `━━━●────`, time `-m:ss`, volume, controls, and Demucs karaoke toggle `[k]`. Right: large synchronized lyrics via LRCLIB with intro dots `...` and active line highlighting.
- **Glitch Transition**: 200–300ms cyberpunk visual glitch effect (horizontal character tears, block noise `█ ▓ ▒ ░ # @ %`, accent color flickers) across phase switches.
- **Controls & Navigation**:
  - `→` / `←`: Seek forward / backward 5s.
  - Double-tap `→→` / `←←` (within 350ms): Seek forward / backward 10s.
  - `Shift + →` / `Shift + ←`: Next / Previous track in queue.
  - `[r]`: Toggle repeat mode (`Repeat: Off / Track / All`).
  - `[k]`: Toggle Demucs AI vocal removal / karaoke mode.
  - `[space]`: Play / Pause toggle.
  - `[p]`: Open / return to Now Playing from Home (when audio active).
  - `[s]`: Stop playback (Home only, visible when audio is active).
  - `[esc]`: Return to Home with glitch transition (playback continues uninterrupted in background).
- **Settings Modal (`[S]`)**: Floating centered box with clean borders `┌─┐│└┘`, groups `── Group ──`, `◀ Value ▶` toggles/steppers, live preview on colorscheme and Matrix rain, Enter to save, Esc to cancel.
- **Audio Resolver**:
  - Deezer metadata drives a background `yt-dlp` query (`{artist} - {title} audio`), selecting the best audio stream matching track duration within ±5s, prioritizing YouTube "Topic" or official artist channels, and excluding live/cover/remix when the original is not.
  - Duration Tolerance (Builder's Call): If no match within ±5s, relaxes threshold up to ±15s strictly for official "Topic" channels.
  - Fallback: If YouTube resolution fails (network error, no candidate), automatically falls back to Jamendo API (`api.jamendo.com/v3.0/tracks`). If both fail, displays "Can't play this track" in status bar and advances to the next track.
  - Prefetch: Pre-resolves next track 20s before current track ends.
  - Now Playing Async Lifecycle: Now Playing opens immediately via Glitch showing album cover and "Resolving audio..." without blocking UI; playback begins as soon as stream URL is handed to mpv.

### Non-Goals
- Video playback or graphical windows (no browser, no external GUI popups).
- Graphical mouse-first interfaces (all interactions are fully keyboard-driven).
- Mascot graphics, circular logos, or watermark overlays.

### Anti-Goals
- Blocking the Textual UI event loop during network requests (Deezer, LRCLIB, yt-dlp, or cover art downloading).
- Crashing on terminals with limited capabilities (fallback to pure ANSI text gracefully).
- Breaking existing CLI options (`--version`, `--update`, `--music-dir`, `--no-auto-update`).

---

## 3. Global Constraints & Standards

- **Language**: All UI labels, status messages, error logs, help prompts, and commit messages MUST be in **English**.
- **Terminal Compatibility**: Fully responsive down to minimum standard terminal dimension **80 columns × 24 rows**.
- **No Access Bypasses**: Strictly follow sandboxing rules; never execute `rm -rf`.
- **Formatting**: Zero errors in `ruff check src tests`.
- **Knowledge Graph**: Run `graphify update .` after changes.

---

## 4. Phase Breakdown & Architectural Design

### Phase 1: Home
- **MatrixRain Widget**:
  - Renders random falling characters (Katakana `ｦ-ﾝ`, digits `0-9`, symbols).
  - Columns operate at 15–25% active density.
  - Head character is brightest accent/white; tail fades to dark green / theme tone.
  - Respects screen resizing dynamically.
- **AsciiTitle Widget**:
  - Big block ASCII "ORPHEUS" (5–7 lines high) centered horizontally and vertically.
  - Block characters `█ ▀ ▄` with depth gradient `░ ▒ ▓`.
  - Configurable animation: `None`, `Wave`, `Pulse` (brightness sweep across characters).
  - Accent color reflects active colorscheme.
- **Dynamic Shortcut Bar**:
  - Centered 2–3 rows below title.
  - Brackets `[ ]` in accent color, labels in muted text.
  - Idle state: `[S] Settings    [f] Find    [q] Quit`
  - Active audio state (playing/paused): `[p] Playing    [s] Stop    [S] Settings    [f] Find    [q] Quit`

### Phase 2: Search (Find)
- Activated via `[f]`.
- Top: Search input bar `Search: [________________]` with 400ms debounce.
- Layout:
  - **Single Pane (Default)**: Full-width Online results table powered by Deezer API (Track title, Artist, Album, Duration). Below it, Related Artists & Top Tracks group.
  - **Split Pane (`[Alt+l]`)**: Screen splits 50/50 horizontally. Left pane shows Online (Deezer); right pane slides in displaying Local audio library files (`~/Music`). Pressing `[Alt+l]` again toggles back to single pane.
- **Album / Playlist Management (`[a]`)**:
  - Pressing `[a]` on any highlighted track opens the "My Albums" modal dialog.
  - `↑` / `↓` navigates existing user albums.
  - If no albums exist (or selecting `[+ New Album]`): press `Enter` to prompt for album name and create it.
  - `[m]`: Modify / rename the selected album name.
  - `[d]`: Delete the selected album (with confirmation prompt).
  - Pressing `Enter` on an existing album adds the highlighted song to that album.
- **Navigation & Focus (Builder's Call)**:
  - Pressing `Down` arrow moves focus from search `Input` to results table.
  - When split pane is active, `Tab` / `Shift+Tab` or `Left` / `Right` switches focus between Online and Local panes.
  - Pressing `Esc` when search input has text clears the text; pressing `Esc` when input is empty transitions back to previous screen (Home) via Glitch.
- Hitting **Enter** on a track initiates audio resolution and transitions via Glitch into Now Playing.

### Phase 3: Now Playing
- **Left Column**:
  - **Album Art**:
    - Query terminal capabilities (`TERM_PROGRAM == "ghostty"`, `KITTY_WINDOW_ID`, `GHOSTTY_RESOURCES_DIR`, or terminal escape query).
    - If Ghostty / Kitty detected: render high-resolution image using Kitty Graphics Protocol escape sequences (`\033_G...`).
    - If unsupported terminal: downsample image to half-block Unicode characters (`▀▄`, identical to `chafa` output) with 24-bit ANSI color.
    - Placeholder: Minimalist ASCII vinyl/cassette placeholder if loading or offline.
  - **Track Info**: Track title, Artist, Album name.
  - **Slim Progress Bar**: `━━━●────` with elapsed time (`mm:ss`) on left, remaining time (`-mm:ss`) on right.
  - **Playback State & Controls**: `⏮ ⏯ ⏭`, volume indicator, repeat mode badge (`[Repeat: Track]`), and karaoke badge (`[Karaoke: On/Off]`).
  - **Demucs AI Karaoke (`[k]`)**: Toggles instrumental track vs original audio for local/compatible songs.
- **Right Column**:
  - **Lyrics View**: Powered by LRCLIB.
  - If synchronized lyrics exist (`syncedLyrics`): large typography, active sung line highlighted in bold theme accent, past/future lines dimmed, auto-scrolling with intro indicator `...`.
  - If plain lyrics only: static scrollable text without auto-sync.
- **Footer**:
  - Dimmed shortcuts: `[space] play/pause  →/← seek  Shift+→/← next/prev  [r] repeat  [k] karaoke  [esc] back`

---

## 5. Glitch Transition Engine

- Triggered upon switching between Home, Search, and Now Playing.
- Duration: 200–300ms (~6 to 9 frames at 30fps).
- Mechanics:
  1. Captures terminal buffer snapshot.
  2. Applies horizontal scanline offsets (random rows shifted left/right by 2–8 characters).
  3. Replaces random segments with block glyphs (`█ ▓ ▒ ░ # % & / \ < >`).
  4. Flashes theme accent colors.
  5. Clears and reveals the destination phase seamlessly.

---

## 6. What Is Left to the Builder

- Internal state machine structuring the 3 phases within Textual (`HomeScreen`, `SearchScreen`, `NowPlayingScreen` or a single root with reactive phase states).
- Detection logic for double-tap arrow keys (`last_tap_time` threshold <= 350ms).
- Fallback caching for Deezer cover images in `~/.cache/orpheus/covers/`.
- Local SQLite persistence for theme settings, repeat mode, and matrix animation options.
