# Graph Report - Orpheus  (2026-11-02)

## Corpus Check
- 49 files · ~30,847 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 781 nodes · 1862 edges · 31 communities (25 shown, 6 thin omitted)
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 396 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `be45ccde`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- CavaVisualizer
- MpvPlayer
- HomeScreen
- Database
- resolver.py
- Xác minh TermMusic MVP
- install.sh
- OrpheusApp
- test_art.py
- 🎵 Orpheus
- updater.py
- orpheus
- NowPlayingScreen
- ORPHEUS Cyberpunk-Minimalist TUI Redesign — Design Specification
- 2026-11-01-orpheus-themes.md
- AlbumsModal
- SettingsModal
- test_visuals.py
- ShortcutBar
- __main__.py
- MatrixRain
- GlitchOverlay
- AsciiTitle
- SearchScreen
- glitch.py
- app.py
- httpx
- sources.py
- YouTubeMetadataProvider
- test_cli.py
- ORPHEUS Cyberpunk-Minimalist TUI Redesign Implementation Plan

## God Nodes (most connected - your core abstractions)
1. `Track` - 104 edges
2. `Database` - 57 edges
3. `SearchScreen` - 53 edges
4. `OrpheusApp` - 45 edges
5. `LyricsService` - 41 edges
6. `NowPlayingScreen` - 40 edges
7. `MpvPlayer` - 38 edges
8. `AlbumsModal` - 24 edges
9. `PlaybackState` - 24 edges
10. `HomeScreen` - 23 edges

## Surprising Connections (you probably didn't know these)
- `Task 5: Reusable Settings Modal Component` --references--> `SettingsModal`  [INFERRED]
  docs/superpowers/plans/2026-11-01-orpheus-ui-redesign.md → src/orpheus/settings.py
- `Task 7: Phase 1 (Home Screen) & Phase 2 (Search Screen with Deezer + Local Split)` --references--> `AlbumsModal`  [INFERRED]
  docs/superpowers/plans/2026-11-01-orpheus-ui-redesign.md → src/orpheus/albums.py
- `Task 9: App Controller Phase Orchestration & E2E System Tests` --references--> `OrpheusApp`  [INFERRED]
  docs/superpowers/plans/2026-11-01-orpheus-ui-redesign.md → src/orpheus/app.py
- `Web Audio Playback Implementation Plan` --references--> `OrpheusApp`  [INFERRED]
  docs/superpowers/plans/2026-11-01-web-audio-playback.md → src/orpheus/app.py
- `Task 4: Glitch Transition Widget & Phase Transition Engine` --references--> `GlitchOverlay`  [INFERRED]
  docs/superpowers/plans/2026-11-01-orpheus-ui-redesign.md → src/orpheus/glitch.py

## Import Cycles
- None detected.

## Communities (31 total, 6 thin omitted)

### Community 0 - "CavaVisualizer"
Cohesion: 0.11
Nodes (6): CavaVisualizer, NowPlayingFooter, SyncedLyricsWidget, test_cava_visualizer_states(), test_now_playing_footer_render(), test_synced_lyrics_widget_loading_and_empty()

### Community 1 - "MpvPlayer"
Cohesion: 0.08
Nodes (29): Global Constraints, Review Focus, Task 1: Update MpvPlayer options and timeout for yt-dlp streaming, Task 2: Update Track.playable and add Web Track Creation helper, Task 3: Integrate Web & YouTube playback and direct URL search in OrpheusApp, Task 4: Documentation, Verification, and Push, Web Audio Playback Implementation Plan, MpvPlayer (+21 more)

### Community 2 - "HomeScreen"
Cohesion: 0.14
Nodes (5): HomeScreen, get_themes(), test_presets_have_requested_names_and_modes(), test_home_screen_shortcuts_docked_at_bottom(), on_mount()

### Community 3 - "Database"
Cohesion: 0.07
Nodes (50): clean_song_title(), LyricsService, Lyrics, LyricsMatch, Track, Separator, Database, test_clean_song_title() (+42 more)

### Community 4 - "resolver.py"
Cohesion: 0.05
Nodes (31): match_lyric_track(), normalize_lyric_match_text(), artist_name_matches(), AudioResolver, DeezerProvider, extract_artist_name(), _extract_base_title(), _fold_ascii() (+23 more)

### Community 7 - "OrpheusApp"
Cohesion: 0.09
Nodes (3): OrpheusApp, WhichKeyModal, test_which_key_modal_dismiss()

### Community 8 - "test_art.py"
Cohesion: 0.10
Nodes (18): compute_kitty_dimensions(), encode_kitty_graphics(), get_kitty_delete_command(), get_placeholder_art(), render_half_blocks(), supports_kitty_graphics(), AlbumArtWidget, test_compute_kitty_dimensions_preserves_aspect_ratio() (+10 more)

### Community 9 - "🎵 Orpheus"
Cohesion: 0.22
Nodes (8): 🛠️ CLI Options, Examples, ✨ Features, ⌨️ Keyboard Shortcuts, 📄 License & Contribution, 💻 Manual Installation (for Developers), 🎵 Orpheus, ⚡ Quick Install (One-Line Command)

### Community 10 - "updater.py"
Cohesion: 0.24
Nodes (5): async_check_and_update(), find_repo_dir(), get_local_commit(), perform_update(), run_cli_update()

### Community 12 - "NowPlayingScreen"
Cohesion: 0.06
Nodes (17): PlaybackState, format_progress_bar(), NowPlayingScreen, MockPlayer, test_app_playlist_load_and_queue_navigation(), scenario(), test_app_poll_player_album_vs_standalone(), scenario() (+9 more)

### Community 13 - "ORPHEUS Cyberpunk-Minimalist TUI Redesign — Design Specification"
Cohesion: 0.14
Nodes (13): 1. Intent & Context, 2. Goals, Non-Goals & Anti-Goals, 3. Global Constraints & Standards, 4. Phase Breakdown & Architectural Design, 5. Glitch Transition Engine, 6. What Is Left to the Builder, Anti-Goals, Goals (+5 more)

### Community 15 - "AlbumsModal"
Cohesion: 0.08
Nodes (8): Task 6: User Albums / Playlists Store & Modal, AlbumsModal, AlbumStore, AlbumsView, test_album_store_crud(), test_albums_modal_colon_key_and_creation(), notify(), on_mount()

### Community 16 - "SettingsModal"
Cohesion: 0.10
Nodes (5): SettingItem, SettingsModal, SettingsView, test_setting_item_change_value(), test_settings_modal_navigation()

### Community 17 - "test_visuals.py"
Cohesion: 0.27
Nodes (3): get_title_lines(), test_ascii_title_render(), test_get_title_lines()

### Community 18 - "ShortcutBar"
Cohesion: 0.24
Nodes (3): ShortcutBar, test_shortcut_bar_render_idle(), test_shortcut_bar_render_playing()

### Community 19 - "__main__.py"
Cohesion: 0.17
Nodes (3): main(), LicensedCatalogProvider, LocalProvider

### Community 20 - "MatrixRain"
Cohesion: 0.20
Nodes (4): Task 7: Phase 1 (Home Screen) & Phase 2 (Search Screen with Deezer + Local Split), MatrixColumn, MatrixRain, test_matrix_rain_step()

### Community 21 - "GlitchOverlay"
Cohesion: 0.15
Nodes (10): Review Focus, Task 1: Terminal Graphics Protocol Detection & Half-Block Art Engine, Task 2: Deezer Metadata Provider & YouTube yt-dlp Audio Resolver, Task 3: Matrix Rain Widget & ASCII Title Engine, Task 4: Glitch Transition Widget & Phase Transition Engine, Task 5: Reusable Settings Modal Component, Task 8: Phase 3 (Now Playing Screen) & Player Controls Integration, Task 9: App Controller Phase Orchestration & E2E System Tests (+2 more)

### Community 22 - "AsciiTitle"
Cohesion: 0.18
Nodes (4): AsciiTitle, test_ascii_title_pulse_renders_highlight_and_accent(), on_mount(), run()

### Community 23 - "SearchScreen"
Cohesion: 0.05
Nodes (12): SearchScreen, on_dismiss(), SearchStatusBar, test_search_screen_action_delete_item_album_and_track(), test_search_screen_action_now_playing(), test_search_screen_action_quit_and_focus_search(), test_search_screen_action_stop(), test_search_screen_albums_and_three_pane_split() (+4 more)

### Community 24 - "glitch.py"
Cohesion: 0.31
Nodes (3): generate_glitch_frame(), test_generate_glitch_frame_contains_glitch_chars(), test_generate_glitch_frame_dimensions()

### Community 25 - "app.py"
Cohesion: 0.07
Nodes (22): active_line(), LyricLine, parse_lrc(), SettingGroup, make_app(), MockLyricsService, MockProvider, Stems (+14 more)

### Community 26 - "httpx"
Cohesion: 0.15
Nodes (9): get_remote_commit(), get_remote_commit_async(), test_find_repo_dir(), test_get_local_commit(), test_get_remote_commit_async_success(), run(), test_get_remote_commit_failure(), test_get_remote_commit_success() (+1 more)

### Community 28 - "YouTubeMetadataProvider"
Cohesion: 0.32
Nodes (4): YouTubeMetadataProvider, test_youtube_provider_returns_metadata_only(), reply(), run()

### Community 29 - "test_cli.py"
Cohesion: 0.46
Nodes (6): run_cli(), test_explicit_missing_music_directory_is_explained(), test_help_works_without_loading_textual(), test_theme_flag_rejects_unknown_preset(), test_version_flag(), test_youtube_requires_api_key()

## Knowledge Gaps
- **1 isolated node(s):** `orpheus`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 220 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Track` connect `Database` to `MpvPlayer`, `resolver.py`, `OrpheusApp`, `NowPlayingScreen`, `AlbumsModal`, `__main__.py`, `GlitchOverlay`, `SearchScreen`, `app.py`, `sources.py`, `YouTubeMetadataProvider`?**
  _High betweenness centrality (0.256) - this node is a cross-community bridge._
- **Are the 44 inferred relationships involving `Track` (e.g. with `Task 2: Deezer Metadata Provider & YouTube yt-dlp Audio Resolver` and `Task 2: Update Track.playable and add Web Track Creation helper`) actually correct?**
  _`Track` has 44 INFERRED edges - model-reasoned connections that need verification._
- **What connects `orpheus` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `CavaVisualizer` be split into smaller, more focused modules?**
  _Cohesion score 0.11375661375661375 - nodes in this community are weakly interconnected._
- **Why does `OrpheusApp` connect `OrpheusApp` to `MpvPlayer`, `HomeScreen`, `Database`, `resolver.py`, `NowPlayingScreen`, `AlbumsModal`, `SettingsModal`, `__main__.py`, `GlitchOverlay`, `SearchScreen`, `app.py`?**
  _High betweenness centrality (0.136) - this node is a cross-community bridge._
- **Are the 25 inferred relationships involving `Database` (e.g. with `Task 6: User Albums / Playlists Store & Modal` and `AlbumStore`) actually correct?**
  _`Database` has 25 INFERRED edges - model-reasoned connections that need verification._
- **Should `MpvPlayer` be split into smaller, more focused modules?**
  _Cohesion score 0.08013468013468013 - nodes in this community are weakly interconnected._