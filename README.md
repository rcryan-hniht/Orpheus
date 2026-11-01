# 🎵 Orpheus

**Orpheus** is a modern, lightweight terminal music player for Linux (Wayland & X11) and macOS, built with Python and Textual. Audio is played smoothly via the mpv JSON IPC engine without video windows or bloat.

---

## ⚡ Quick Install (One-Line Command)

Run this single command in your terminal to automatically install Orpheus:

```bash
curl -fsSL https://raw.githubusercontent.com/rcryan-hniht/Orpheus/main/install.sh | bash
```

Once installed, simply launch the app from any terminal window:

```bash
orpheus
```

*(Requirements: Python 3.11+ and `mpv`. If `mpv` is not installed, install it with `sudo apt install mpv` on Ubuntu/Debian or `brew install mpv` on macOS).*

---

## ✨ Features

- **🎧 Local-First Audio Playback**: Recursively scans and indexes your music library (`~/Music` or customized via `--music-dir`). Supports MP3, FLAC, Ogg, WAV, M4A, OPUS, and more. Fast metadata tag extraction (title, artist, album, duration) using `mutagen`.
- **⚡ mpv Engine via JSON IPC**: High-performance audio playback via background Unix socket IPC. Zero UI lag, no video windows, direct output to PipeWire or PulseAudio.
- **📜 Real-Time Synced Lyrics**: Automatic lookup and smooth synchronized scrolling lyrics from [LRCLIB](https://lrclib.net). Falls back to plain text lyrics and caches results locally in SQLite for 30 days.
- **⏱️ Live Lyric Delay Tuning**: Adjust lyric timing on the fly using `[` and `]` (±0.25s). Timing offsets are persistently remembered per song in the local database.
- **📋 Persistent Playback Queue**: Enqueue tracks (`e`), delete items (`Delete`), and enjoy seamless auto-advance when songs end. Queues survive app restarts.
- **🎤 Optional Karaoke Separation (Demucs)**: Generate local instrumental/vocal stems with Demucs (`k`). Preserves playback position and pause state when toggling between original and instrumental tracks.
- **🎨 Built-in Color Themes**: Switch instantly between 5 presets (`github-dark-contrast`, `blackmetal`, `catppuccin-latte`, `sequoia-light-monochrome`, `github-light-contrast`) via in-app dropdown or `--theme` CLI flag.
- **🔄 Automatic Background Updates**: Checks for updates quietly in the background and notifies you when an update is ready.
- **🌐 Licensed Catalog & YouTube Search**:
  - Play licensed HTTPS audio catalogs via `--catalog examples/catalog.json`.
  - Search metadata via YouTube Data API v3 (`--youtube`).

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
| :--- | :--- |
| **Enter** | Play selected track |
| **`e`** | Enqueue selected track |
| **Tab** / **Shift+Tab** | Navigate focus between panels (Search, Track List, Queue, Lyrics) |
| **Delete** | Remove selected item from queue |
| **Space** | Pause / Resume playback |
| **`s`** / **`n`** | Stop playback / Next track in queue |
| **`←`** / **`→`** | Seek backward / forward 5 seconds |
| **`-`** / **`+`** | Volume down / up |
| **`[`** / **`]`** | Decrease / increase lyric delay by 0.25s |
| **`r`** | Reload lyrics from cache or LRCLIB |
| **`k`** | Toggle Karaoke (Instrumental) / Original track |
| **Ctrl+Q** | Quit Orpheus |

---

## 🛠️ CLI Options

```text
usage: orpheus [-h] [-v] [--update] [--no-auto-update] [--music-dir MUSIC_DIR]
               [--catalog CATALOG] [--data-dir DATA_DIR]
               [--cache-dir CACHE_DIR] [--mpv MPV] [--demucs DEMUCS]
               [--youtube]
               [--theme {blackmetal,sequoia-light-monochrome,catppuccin-latte,github-dark-contrast,github-light-contrast}]

options:
  -h, --help            Show this help message and exit
  -v, --version         Show program's version number and exit
  --update              Check for updates and upgrade Orpheus to the latest version
  --no-auto-update      Disable background automatic update checking
  --music-dir MUSIC_DIR Local music folder (default: ~/Music)
  --catalog CATALOG     Licensed catalog JSON file
  --data-dir DATA_DIR   SQLite database and log folder
  --cache-dir CACHE_DIR Vocal stem cache folder
  --mpv MPV             mpv executable path (default: mpv)
  --demucs DEMUCS       Demucs executable path (default: demucs)
  --youtube             Enable YouTube metadata search (requires YOUTUBE_API_KEY)
  --theme THEME         Select color theme preset
```

### Examples

```bash
# Check version
orpheus -v

# Self-update to latest release
orpheus --update

# Specify custom music folder
orpheus --music-dir "$HOME/Music/Favorites"

# Launch with sample licensed catalog
orpheus --catalog examples/catalog.json

# Launch with a specific theme
orpheus --theme github-dark-contrast
```

---

## 💻 Manual Installation (for Developers)

```bash
git clone https://github.com/rcryan-hniht/Orpheus.git
cd Orpheus

python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'

# Run tests and linter
pytest
ruff check src tests

# Run Orpheus locally
python -m orpheus --catalog examples/catalog.json
```

---

## 📄 License & Contribution

Orpheus is open-source software. Issues, contributions, and pull requests are warmly welcomed!
