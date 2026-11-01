# Graph Report - Orpheus  (2026-11-02)

## Corpus Check
- 48 files · ~27,089 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 719 nodes · 1710 edges · 31 communities (21 shown, 10 thin omitted)
- Extraction: 78% EXTRACTED · 22% INFERRED · 0% AMBIGUOUS · INFERRED: 368 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ef57be2c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- updater.py
- MpvPlayer
- HomeScreen
- Database
- AudioResolver
- Xác minh TermMusic MVP
- install.sh
- OrpheusApp
- test_art.py
- 🎵 Orpheus
- glitch.py
- orpheus
- NowPlayingScreen
- ORPHEUS Cyberpunk-Minimalist TUI Redesign — Design Specification
- 2026-11-01-orpheus-themes.md
- AlbumsModal
- SettingsModal
- GlitchOverlay
- ShortcutBar
- asyncio
- MatrixRain
- asyncio
- AsciiTitle
- SearchScreen
- SearchStatusBar
- app.py
- test_search_screen_artist_query_and_enter_submission
- ._get_selected_track_and_context
- Review Focus

## God Nodes (most connected - your core abstractions)
1. `Track` - 100 edges
2. `Database` - 57 edges
3. `OrpheusApp` - 43 edges
4. `LyricsService` - 41 edges
5. `SearchScreen` - 38 edges
6. `MpvPlayer` - 38 edges
7. `NowPlayingScreen` - 36 edges
8. `AlbumsModal` - 24 edges
9. `HomeScreen` - 22 edges
10. `PlaybackState` - 21 edges

## Surprising Connections (you probably didn't know these)
- `Task 4: Glitch Transition Widget & Phase Transition Engine` --references--> `GlitchOverlay`  [INFERRED]
  docs/superpowers/plans/2026-11-01-orpheus-ui-redesign.md → src/orpheus/glitch.py
- `Task 5: Reusable Settings Modal Component` --references--> `SettingsModal`  [INFERRED]
  docs/superpowers/plans/2026-11-01-orpheus-ui-redesign.md → src/orpheus/settings.py
- `Task 7: Phase 1 (Home Screen) & Phase 2 (Search Screen with Deezer + Local Split)` --references--> `AlbumsModal`  [INFERRED]
  docs/superpowers/plans/2026-11-01-orpheus-ui-redesign.md → src/orpheus/albums.py
- `Task 9: App Controller Phase Orchestration & E2E System Tests` --references--> `OrpheusApp`  [INFERRED]
  docs/superpowers/plans/2026-11-01-orpheus-ui-redesign.md → src/orpheus/app.py
- `Web Audio Playback Implementation Plan` --references--> `OrpheusApp`  [INFERRED]
  docs/superpowers/plans/2026-11-01-web-audio-playback.md → src/orpheus/app.py

## Import Cycles
- None detected.

## Communities (31 total, 10 thin omitted)

### Community 0 - "updater.py"
Cohesion: 0.12
Nodes (14): async_check_and_update(), find_repo_dir(), get_local_commit(), get_remote_commit(), get_remote_commit_async(), perform_update(), run_cli_update(), test_find_repo_dir() (+6 more)

### Community 1 - "MpvPlayer"
Cohesion: 0.09
Nodes (27): Global Constraints, Review Focus, Task 1: Update MpvPlayer options and timeout for yt-dlp streaming, Task 2: Update Track.playable and add Web Track Creation helper, Task 3: Integrate Web & YouTube playback and direct URL search in OrpheusApp, Task 4: Documentation, Verification, and Push, Web Audio Playback Implementation Plan, MpvPlayer (+19 more)

### Community 2 - "HomeScreen"
Cohesion: 0.14
Nodes (6): HomeScreen, get_themes(), on_mount(), test_presets_have_requested_names_and_modes(), test_home_screen_shortcuts_docked_at_bottom(), on_mount()

### Community 3 - "Database"
Cohesion: 0.10
Nodes (38): clean_song_title(), LyricsService, Lyrics, LyricsMatch, Track, Database, test_albums_modal_colon_key_and_creation(), test_clean_song_title() (+30 more)

### Community 4 - "AudioResolver"
Cohesion: 0.05
Nodes (25): Task 8: Phase 3 (Now Playing Screen) & Player Controls Integration, match_lyric_track(), normalize_lyric_match_text(), AudioResolver, DeezerProvider, extract_artist_name(), _extract_base_title(), is_artist_query() (+17 more)

### Community 8 - "test_art.py"
Cohesion: 0.11
Nodes (16): encode_kitty_graphics(), get_kitty_delete_command(), get_placeholder_art(), render_half_blocks(), supports_kitty_graphics(), AlbumArtWidget, test_encode_kitty_graphics_escapes(), test_get_kitty_delete_command() (+8 more)

### Community 9 - "🎵 Orpheus"
Cohesion: 0.22
Nodes (8): 🛠️ CLI Options, Examples, ✨ Features, ⌨️ Keyboard Shortcuts, 📄 License & Contribution, 💻 Manual Installation (for Developers), 🎵 Orpheus, ⚡ Quick Install (One-Line Command)

### Community 10 - "glitch.py"
Cohesion: 0.33
Nodes (3): generate_glitch_frame(), test_generate_glitch_frame_contains_glitch_chars(), test_generate_glitch_frame_dimensions()

### Community 12 - "NowPlayingScreen"
Cohesion: 0.06
Nodes (16): CavaVisualizer, format_progress_bar(), NowPlayingFooter, NowPlayingScreen, SyncedLyricsWidget, test_cava_visualizer_states(), test_format_progress_bar(), test_now_playing_action_find_and_quit() (+8 more)

### Community 13 - "ORPHEUS Cyberpunk-Minimalist TUI Redesign — Design Specification"
Cohesion: 0.14
Nodes (13): 1. Intent & Context, 2. Goals, Non-Goals & Anti-Goals, 3. Global Constraints & Standards, 4. Phase Breakdown & Architectural Design, 5. Glitch Transition Engine, 6. What Is Left to the Builder, Anti-Goals, Goals (+5 more)

### Community 15 - "AlbumsModal"
Cohesion: 0.08
Nodes (5): Task 6: User Albums / Playlists Store & Modal, AlbumsModal, AlbumStore, AlbumsView, test_album_store_crud()

### Community 16 - "SettingsModal"
Cohesion: 0.10
Nodes (5): SettingItem, SettingsModal, SettingsView, test_setting_item_change_value(), test_settings_modal_navigation()

### Community 17 - "GlitchOverlay"
Cohesion: 0.24
Nodes (3): Task 7: Phase 1 (Home Screen) & Phase 2 (Search Screen with Deezer + Local Split), GlitchOverlay, test_glitch_overlay_lifecycle()

### Community 18 - "ShortcutBar"
Cohesion: 0.23
Nodes (3): ShortcutBar, test_shortcut_bar_render_idle(), test_shortcut_bar_render_playing()

### Community 19 - "asyncio"
Cohesion: 0.07
Nodes (21): main(), create_web_track(), LicensedCatalogProvider, LocalProvider, _matches(), _safe_url(), YouTubeMetadataProvider, run_cli() (+13 more)

### Community 20 - "MatrixRain"
Cohesion: 0.18
Nodes (3): MatrixColumn, MatrixRain, test_matrix_rain_step()

### Community 21 - "asyncio"
Cohesion: 0.06
Nodes (30): PlaybackState, Separator, make_app(), MockLyricsService, MockPlayer, MockProvider, Stems, test_app_initial_phase_is_home() (+22 more)

### Community 22 - "AsciiTitle"
Cohesion: 0.19
Nodes (5): AsciiTitle, test_ascii_title_pulse_renders_highlight_and_accent(), on_mount(), run(), test_ascii_title_render()

### Community 23 - "SearchScreen"
Cohesion: 0.17
Nodes (3): SearchScreen, test_search_screen_action_quit_and_focus_search(), test_search_screen_split_toggle()

### Community 25 - "app.py"
Cohesion: 0.12
Nodes (7): active_line(), LyricLine, parse_lrc(), SettingGroup, get_title_lines(), test_lrc_multiple_timestamps_offset_and_delay(), test_get_title_lines()

### Community 29 - "Review Focus"
Cohesion: 0.20
Nodes (9): Global Constraints, ORPHEUS Cyberpunk-Minimalist TUI Redesign Implementation Plan, Review Focus, Task 1: Terminal Graphics Protocol Detection & Half-Block Art Engine, Task 2: Deezer Metadata Provider & YouTube yt-dlp Audio Resolver, Task 3: Matrix Rain Widget & ASCII Title Engine, Task 4: Glitch Transition Widget & Phase Transition Engine, Task 5: Reusable Settings Modal Component (+1 more)

## Knowledge Gaps
- **1 isolated node(s):** `orpheus`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 205 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Track` connect `Database` to `MpvPlayer`, `AudioResolver`, `OrpheusApp`, `NowPlayingScreen`, `AlbumsModal`, `asyncio`, `asyncio`, `SearchScreen`, `app.py`, `test_search_screen_artist_query_and_enter_submission`, `._get_selected_track_and_context`, `Review Focus`?**
  _High betweenness centrality (0.249) - this node is a cross-community bridge._
- **Are the 41 inferred relationships involving `Track` (e.g. with `Task 2: Deezer Metadata Provider & YouTube yt-dlp Audio Resolver` and `Task 2: Update Track.playable and add Web Track Creation helper`) actually correct?**
  _`Track` has 41 INFERRED edges - model-reasoned connections that need verification._
- **What connects `orpheus` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `updater.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11895161290322581 - nodes in this community are weakly interconnected._
- **Why does `OrpheusApp` connect `OrpheusApp` to `MpvPlayer`, `HomeScreen`, `Database`, `AudioResolver`, `NowPlayingScreen`, `AlbumsModal`, `SettingsModal`, `asyncio`, `asyncio`, `SearchScreen`, `app.py`, `Review Focus`, `._do_search`?**
  _High betweenness centrality (0.130) - this node is a cross-community bridge._
- **Are the 25 inferred relationships involving `Database` (e.g. with `Task 6: User Albums / Playlists Store & Modal` and `AlbumStore`) actually correct?**
  _`Database` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Should `MpvPlayer` be split into smaller, more focused modules?**
  _Cohesion score 0.08597285067873303 - nodes in this community are weakly interconnected._