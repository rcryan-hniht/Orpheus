# Graph Report - Orpheus  (2026-11-02)

## Corpus Check
- 51 files · ~36,254 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 2 file(s) not represented in the graph (top: (none) 1, .lock 1)

## Summary
- 895 nodes · 2159 edges · 31 communities (23 shown, 8 thin omitted)
- Extraction: 78% EXTRACTED · 22% INFERRED · 0% AMBIGUOUS · INFERRED: 474 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f6ad7532`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- CavaReader
- MpvPlayer
- .on_key
- Database
- SearchScreen
- Xác minh TermMusic MVP
- install.sh
- OrpheusApp
- test_art.py
- 🎵 Orpheus
- resolver.py
- orpheus
- NowPlayingScreen
- ._populate_albums_table
- 2026-11-01-orpheus-themes.md
- AlbumsModal
- SettingsModal
- test_visuals.py
- ShortcutBar
- __main__.py
- MatrixRain
- GlitchOverlay
- AsciiTitle
- .render
- glitch.py
- app.py
- test_themes.py
- SearchStatusBar
- .safe_app
- updater.py
- test_phases_home_search.py

## God Nodes (most connected - your core abstractions)
1. `Track` - 116 edges
2. `SearchScreen` - 67 edges
3. `Database` - 58 edges
4. `NowPlayingScreen` - 49 edges
5. `OrpheusApp` - 46 edges
6. `LyricsService` - 41 edges
7. `MpvPlayer` - 38 edges
8. `PlaybackState` - 37 edges
9. `HomeScreen` - 30 edges
10. `AlbumsModal` - 24 edges

## Surprising Connections (you probably didn't know these)
- `Task 5: Reusable Settings Modal Component` --references--> `SettingsModal`  [INFERRED]
  docs/superpowers/plans/2026-11-01-orpheus-ui-redesign.md → src/orpheus/settings.py
- `Task 6: User Albums / Playlists Store & Modal` --references--> `AlbumsModal`  [INFERRED]
  docs/superpowers/plans/2026-11-01-orpheus-ui-redesign.md → src/orpheus/albums.py
- `Task 7: Phase 1 (Home Screen) & Phase 2 (Search Screen with Deezer + Local Split)` --references--> `AlbumsModal`  [INFERRED]
  docs/superpowers/plans/2026-11-01-orpheus-ui-redesign.md → src/orpheus/albums.py
- `Task 9: App Controller Phase Orchestration & E2E System Tests` --references--> `OrpheusApp`  [INFERRED]
  docs/superpowers/plans/2026-11-01-orpheus-ui-redesign.md → src/orpheus/app.py
- `Web Audio Playback Implementation Plan` --references--> `OrpheusApp`  [INFERRED]
  docs/superpowers/plans/2026-11-01-web-audio-playback.md → src/orpheus/app.py

## Import Cycles
- None detected.

## Communities (31 total, 8 thin omitted)

### Community 0 - "CavaReader"
Cohesion: 0.08
Nodes (10): CavaReader, CavaVisualizer, NowPlayingFooter, test_cava_reader_binary_read_loop(), test_cava_reader_init(), test_cava_reader_set_bars(), test_cava_reader_start_and_stop_cleanup(), test_cava_visualizer_reads_cava_reader() (+2 more)

### Community 1 - "MpvPlayer"
Cohesion: 0.09
Nodes (27): Global Constraints, Review Focus, Task 1: Update MpvPlayer options and timeout for yt-dlp streaming, Task 2: Update Track.playable and add Web Track Creation helper, Task 3: Integrate Web & YouTube playback and direct URL search in OrpheusApp, Task 4: Documentation, Verification, and Push, Web Audio Playback Implementation Plan, MpvPlayer (+19 more)

### Community 3 - "Database"
Cohesion: 0.07
Nodes (44): Task 6: User Albums / Playlists Store & Modal, AlbumStore, clean_song_title(), LyricsService, match_lyric_track(), Lyrics, LyricsMatch, Track (+36 more)

### Community 7 - "OrpheusApp"
Cohesion: 0.09
Nodes (3): OrpheusApp, WhichKeyModal, test_which_key_modal_dismiss()

### Community 8 - "test_art.py"
Cohesion: 0.10
Nodes (18): compute_kitty_dimensions(), encode_kitty_graphics(), get_kitty_delete_command(), get_placeholder_art(), render_half_blocks(), supports_kitty_graphics(), AlbumArtWidget, test_compute_kitty_dimensions_preserves_aspect_ratio() (+10 more)

### Community 9 - "🎵 Orpheus"
Cohesion: 0.22
Nodes (8): 🛠️ CLI Options, Examples, ✨ Features, ⌨️ Keyboard Shortcuts, 📄 License & Contribution, 💻 Manual Installation (for Developers), 🎵 Orpheus, ⚡ Quick Install (One-Line Command)

### Community 10 - "resolver.py"
Cohesion: 0.05
Nodes (29): normalize_lyric_match_text(), artist_name_matches(), AudioResolver, DeezerProvider, extract_artist_name(), _extract_base_title(), _fold_ascii(), is_artist_query() (+21 more)

### Community 12 - "NowPlayingScreen"
Cohesion: 0.06
Nodes (16): format_progress_bar(), NowPlayingScreen, SyncedLyricsWidget, test_format_progress_bar(), test_now_playing_action_find_and_quit(), test_now_playing_action_stop(), test_now_playing_actions_await_app_methods(), test_now_playing_compose_includes_cava_and_no_vol() (+8 more)

### Community 13 - "._populate_albums_table"
Cohesion: 0.23
Nodes (4): on_dismiss(), on_dismiss(), on_confirm_delete(), on_dismiss()

### Community 15 - "AlbumsModal"
Cohesion: 0.06
Nodes (9): AlbumNameModal, AlbumsModal, AlbumsView, ConfirmModal, test_albums_modal_colon_key_and_creation(), notify(), on_mount(), test_confirm_modal_and_album_name_modal() (+1 more)

### Community 16 - "SettingsModal"
Cohesion: 0.10
Nodes (6): Task 9: App Controller Phase Orchestration & E2E System Tests, SettingItem, SettingsModal, SettingsView, test_setting_item_change_value(), test_settings_modal_navigation()

### Community 17 - "test_visuals.py"
Cohesion: 0.24
Nodes (4): get_title_lines(), test_ascii_title_render(), test_get_title_lines(), test_matrix_rain_theme_synchronization()

### Community 18 - "ShortcutBar"
Cohesion: 0.22
Nodes (3): ShortcutBar, test_shortcut_bar_render_idle(), test_shortcut_bar_render_playing()

### Community 19 - "__main__.py"
Cohesion: 0.07
Nodes (24): main(), Separator, create_web_track(), LicensedCatalogProvider, LocalProvider, _matches(), _safe_url(), YouTubeMetadataProvider (+16 more)

### Community 20 - "MatrixRain"
Cohesion: 0.24
Nodes (3): MatrixColumn, MatrixRain, test_matrix_rain_set_enabled()

### Community 21 - "GlitchOverlay"
Cohesion: 0.15
Nodes (10): Review Focus, Task 1: Terminal Graphics Protocol Detection & Half-Block Art Engine, Task 2: Deezer Metadata Provider & YouTube yt-dlp Audio Resolver, Task 3: Matrix Rain Widget & ASCII Title Engine, Task 4: Glitch Transition Widget & Phase Transition Engine, Task 5: Reusable Settings Modal Component, Task 7: Phase 1 (Home Screen) & Phase 2 (Search Screen with Deezer + Local Split), Task 8: Phase 3 (Now Playing Screen) & Player Controls Integration (+2 more)

### Community 22 - "AsciiTitle"
Cohesion: 0.21
Nodes (4): AsciiTitle, test_ascii_title_pulse_renders_highlight_and_accent(), on_mount(), run()

### Community 24 - "glitch.py"
Cohesion: 0.31
Nodes (3): generate_glitch_frame(), test_generate_glitch_frame_contains_glitch_chars(), test_generate_glitch_frame_dimensions()

### Community 25 - "app.py"
Cohesion: 0.06
Nodes (29): active_line(), LyricLine, parse_lrc(), _interpolate_color(), _rgb_to_hex(), PlaybackState, HomePlayingWidget, SettingGroup (+21 more)

### Community 27 - "test_themes.py"
Cohesion: 0.05
Nodes (29): Global Constraints, ORPHEUS Cyberpunk-Minimalist TUI Redesign Implementation Plan, 1. Intent & Context, 2. Goals, Non-Goals & Anti-Goals, 3. Global Constraints & Standards, 4. Phase Breakdown & Architectural Design, 5. Glitch Transition Engine, 6. What Is Left to the Builder (+21 more)

### Community 28 - "SearchStatusBar"
Cohesion: 0.18
Nodes (3): SearchStatusBar, test_search_screen_album_pane_shortcuts_and_status_bar(), test_search_status_bar_render()

### Community 31 - "updater.py"
Cohesion: 0.10
Nodes (20): async_check_and_update(), find_repo_dir(), get_local_commit(), get_remote_commit(), get_remote_commit_async(), perform_update(), run_cli_update(), run_cli() (+12 more)

### Community 32 - "test_phases_home_search.py"
Cohesion: 0.11
Nodes (14): on_mount(), test_search_screen_action_delete_item_album_and_track(), push_screen(), test_search_screen_albums_and_split(), test_search_screen_artist_query_and_enter_submission(), __init__(), on_mount(), test_search_screen_down_arrow_routing_and_focus() (+6 more)

## Knowledge Gaps
- **1 isolated node(s):** `orpheus`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 241 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Track` connect `Database` to `test_phases_home_search.py`, `MpvPlayer`, `SearchScreen`, `OrpheusApp`, `resolver.py`, `NowPlayingScreen`, `AlbumsModal`, `__main__.py`, `GlitchOverlay`, `app.py`, `test_themes.py`, `SearchStatusBar`, `.safe_app`?**
  _High betweenness centrality (0.285) - this node is a cross-community bridge._
- **Are the 52 inferred relationships involving `Track` (e.g. with `Task 2: Deezer Metadata Provider & YouTube yt-dlp Audio Resolver` and `Task 2: Update Track.playable and add Web Track Creation helper`) actually correct?**
  _`Track` has 52 INFERRED edges - model-reasoned connections that need verification._
- **What connects `orpheus` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `CavaReader` be split into smaller, more focused modules?**
  _Cohesion score 0.07729468599033816 - nodes in this community are weakly interconnected._
- **Why does `SearchScreen` connect `SearchScreen` to `test_phases_home_search.py`, `.on_key`, `Database`, `OrpheusApp`, `resolver.py`, `._populate_albums_table`, `AlbumsModal`, `SettingsModal`, `app.py`, `test_themes.py`, `SearchStatusBar`, `.safe_app`?**
  _High betweenness centrality (0.145) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `SearchScreen` (e.g. with `ORPHEUS Cyberpunk-Minimalist TUI Redesign Implementation Plan` and `Task 9: App Controller Phase Orchestration & E2E System Tests`) actually correct?**
  _`SearchScreen` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Should `MpvPlayer` be split into smaller, more focused modules?**
  _Cohesion score 0.08597285067873303 - nodes in this community are weakly interconnected._