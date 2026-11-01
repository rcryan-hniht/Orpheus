# Graph Report - Orpheus  (2026-11-02)

## Corpus Check
- 49 files · ~29,172 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 757 nodes · 1803 edges · 32 communities (19 shown, 13 thin omitted)
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 384 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `87750354`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- asyncio
- MpvPlayer
- HomeScreen
- Database
- DeezerProvider
- Xác minh TermMusic MVP
- install.sh
- OrpheusApp
- test_art.py
- 🎵 Orpheus
- test_phases_home_search.py
- orpheus
- NowPlayingScreen
- ORPHEUS Cyberpunk-Minimalist TUI Redesign — Design Specification
- 2026-11-01-orpheus-themes.md
- AlbumsModal
- SettingsModal
- .on_key
- ShortcutBar
- __main__.py
- MatrixRain
- AudioResolver
- AsciiTitle
- SearchScreen
- get_themes
- app.py
- updater.py
- SearchStatusBar
- ._get_selected_track_and_context
- ._populate_local_table
- test_visuals.py

## God Nodes (most connected - your core abstractions)
1. `Track` - 101 edges
2. `Database` - 57 edges
3. `SearchScreen` - 49 edges
4. `OrpheusApp` - 45 edges
5. `LyricsService` - 41 edges
6. `NowPlayingScreen` - 39 edges
7. `MpvPlayer` - 38 edges
8. `AlbumsModal` - 24 edges
9. `PlaybackState` - 24 edges
10. `HomeScreen` - 23 edges

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

## Communities (32 total, 13 thin omitted)

### Community 0 - "asyncio"
Cohesion: 0.09
Nodes (23): PlaybackState, make_app(), MockLyricsService, MockPlayer, MockProvider, Stems, test_app_initial_phase_is_home(), scenario() (+15 more)

### Community 1 - "MpvPlayer"
Cohesion: 0.08
Nodes (29): Global Constraints, Review Focus, Task 1: Update MpvPlayer options and timeout for yt-dlp streaming, Task 2: Update Track.playable and add Web Track Creation helper, Task 3: Integrate Web & YouTube playback and direct URL search in OrpheusApp, Task 4: Documentation, Verification, and Push, Web Audio Playback Implementation Plan, MpvPlayer (+21 more)

### Community 3 - "Database"
Cohesion: 0.08
Nodes (41): Task 6: User Albums / Playlists Store & Modal, AlbumStore, clean_song_title(), LyricsService, Lyrics, LyricsMatch, Track, Database (+33 more)

### Community 4 - "DeezerProvider"
Cohesion: 0.15
Nodes (5): DeezerProvider, test_deezer_provider_search(), test_deezer_provider_search_by_artist(), run(), run()

### Community 8 - "test_art.py"
Cohesion: 0.10
Nodes (18): compute_kitty_dimensions(), encode_kitty_graphics(), get_kitty_delete_command(), get_placeholder_art(), render_half_blocks(), supports_kitty_graphics(), AlbumArtWidget, test_compute_kitty_dimensions_preserves_aspect_ratio() (+10 more)

### Community 9 - "🎵 Orpheus"
Cohesion: 0.22
Nodes (8): 🛠️ CLI Options, Examples, ✨ Features, ⌨️ Keyboard Shortcuts, 📄 License & Contribution, 💻 Manual Installation (for Developers), 🎵 Orpheus, ⚡ Quick Install (One-Line Command)

### Community 10 - "test_phases_home_search.py"
Cohesion: 0.18
Nodes (5): rank_tracks_by_query(), test_rank_tracks_by_query_base_title_and_case_insensitive(), test_rank_tracks_by_query_exact_match_top(), test_search_screen_artist_query_and_enter_submission(), test_which_key_modal_dismiss()

### Community 12 - "NowPlayingScreen"
Cohesion: 0.05
Nodes (17): CavaVisualizer, format_progress_bar(), NowPlayingFooter, NowPlayingScreen, SyncedLyricsWidget, test_cava_visualizer_states(), test_format_progress_bar(), test_now_playing_action_find_and_quit() (+9 more)

### Community 13 - "ORPHEUS Cyberpunk-Minimalist TUI Redesign — Design Specification"
Cohesion: 0.14
Nodes (13): 1. Intent & Context, 2. Goals, Non-Goals & Anti-Goals, 3. Global Constraints & Standards, 4. Phase Breakdown & Architectural Design, 5. Glitch Transition Engine, 6. What Is Left to the Builder, Anti-Goals, Goals (+5 more)

### Community 16 - "SettingsModal"
Cohesion: 0.10
Nodes (5): SettingItem, SettingsModal, SettingsView, test_setting_item_change_value(), test_settings_modal_navigation()

### Community 18 - "ShortcutBar"
Cohesion: 0.24
Nodes (3): ShortcutBar, test_shortcut_bar_render_idle(), test_shortcut_bar_render_playing()

### Community 19 - "__main__.py"
Cohesion: 0.07
Nodes (22): main(), Separator, LicensedCatalogProvider, LocalProvider, _matches(), _safe_url(), YouTubeMetadataProvider, test_missing_separator_dependency_is_actionable() (+14 more)

### Community 20 - "MatrixRain"
Cohesion: 0.22
Nodes (3): MatrixColumn, MatrixRain, test_matrix_rain_step()

### Community 21 - "AudioResolver"
Cohesion: 0.06
Nodes (21): Global Constraints, ORPHEUS Cyberpunk-Minimalist TUI Redesign Implementation Plan, Review Focus, Task 1: Terminal Graphics Protocol Detection & Half-Block Art Engine, Task 2: Deezer Metadata Provider & YouTube yt-dlp Audio Resolver, Task 4: Glitch Transition Widget & Phase Transition Engine, Task 5: Reusable Settings Modal Component, Task 8: Phase 3 (Now Playing Screen) & Player Controls Integration (+13 more)

### Community 22 - "AsciiTitle"
Cohesion: 0.18
Nodes (6): Task 3: Matrix Rain Widget & ASCII Title Engine, Task 7: Phase 1 (Home Screen) & Phase 2 (Search Screen with Deezer + Local Split), AsciiTitle, test_ascii_title_pulse_renders_highlight_and_accent(), on_mount(), run()

### Community 24 - "get_themes"
Cohesion: 0.22
Nodes (5): get_themes(), on_mount(), test_presets_have_requested_names_and_modes(), test_home_screen_shortcuts_docked_at_bottom(), on_mount()

### Community 25 - "app.py"
Cohesion: 0.08
Nodes (14): active_line(), LyricLine, match_lyric_track(), normalize_lyric_match_text(), parse_lrc(), extract_artist_name(), _extract_base_title(), is_artist_query() (+6 more)

### Community 26 - "updater.py"
Cohesion: 0.10
Nodes (20): async_check_and_update(), find_repo_dir(), get_local_commit(), get_remote_commit(), get_remote_commit_async(), perform_update(), run_cli_update(), run_cli() (+12 more)

### Community 30 - "test_visuals.py"
Cohesion: 0.33
Nodes (3): get_title_lines(), test_ascii_title_render(), test_get_title_lines()

## Knowledge Gaps
- **1 isolated node(s):** `orpheus`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 213 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Track` connect `Database` to `asyncio`, `MpvPlayer`, `DeezerProvider`, `OrpheusApp`, `test_phases_home_search.py`, `NowPlayingScreen`, `AlbumsModal`, `__main__.py`, `AudioResolver`, `SearchScreen`, `app.py`, `._get_selected_track_and_context`?**
  _High betweenness centrality (0.246) - this node is a cross-community bridge._
- **Are the 41 inferred relationships involving `Track` (e.g. with `Task 2: Deezer Metadata Provider & YouTube yt-dlp Audio Resolver` and `Task 2: Update Track.playable and add Web Track Creation helper`) actually correct?**
  _`Track` has 41 INFERRED edges - model-reasoned connections that need verification._
- **What connects `orpheus` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `asyncio` be split into smaller, more focused modules?**
  _Cohesion score 0.08658536585365853 - nodes in this community are weakly interconnected._
- **Why does `OrpheusApp` connect `OrpheusApp` to `asyncio`, `MpvPlayer`, `HomeScreen`, `Database`, `DeezerProvider`, `NowPlayingScreen`, `SettingsModal`, `__main__.py`, `AudioResolver`, `SearchScreen`, `get_themes`, `app.py`, `._populate_local_table`?**
  _High betweenness centrality (0.139) - this node is a cross-community bridge._
- **Are the 25 inferred relationships involving `Database` (e.g. with `Task 6: User Albums / Playlists Store & Modal` and `AlbumStore`) actually correct?**
  _`Database` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Should `MpvPlayer` be split into smaller, more focused modules?**
  _Cohesion score 0.08013468013468013 - nodes in this community are weakly interconnected._