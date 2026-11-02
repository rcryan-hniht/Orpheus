# Graph Report - Orpheus  (2026-11-02)

## Corpus Check
- 51 files · ~36,311 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 2 file(s) not represented in the graph (top: (none) 1, .lock 1)

## Summary
- 896 nodes · 2161 edges · 43 communities (35 shown, 8 thin omitted)
- Extraction: 78% EXTRACTED · 22% INFERRED · 0% AMBIGUOUS · INFERRED: 474 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `7ef4faa7`
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
- now_playing.py
- AlbumNameModal
- asyncio
- SearchStatusBar
- PlaybackState
- httpx
- updater.py
- test_phases_home_search.py
- ORPHEUS Cyberpunk-Minimalist TUI Redesign — Design Specification
- HomeScreen
- sources.py
- HomePlayingWidget
- Review Focus
- make_app
- test_sources.py
- YouTubeMetadataProvider
- test_cli.py
- MockLyricsService

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

## Communities (43 total, 8 thin omitted)

### Community 0 - "CavaReader"
Cohesion: 0.08
Nodes (10): CavaReader, CavaVisualizer, NowPlayingFooter, test_cava_reader_binary_read_loop(), test_cava_reader_init(), test_cava_reader_set_bars(), test_cava_reader_start_and_stop_cleanup(), test_cava_visualizer_reads_cava_reader() (+2 more)

### Community 1 - "MpvPlayer"
Cohesion: 0.09
Nodes (27): Global Constraints, Review Focus, Task 1: Update MpvPlayer options and timeout for yt-dlp streaming, Task 2: Update Track.playable and add Web Track Creation helper, Task 3: Integrate Web & YouTube playback and direct URL search in OrpheusApp, Task 4: Documentation, Verification, and Push, Web Audio Playback Implementation Plan, MpvPlayer (+19 more)

### Community 3 - "Database"
Cohesion: 0.09
Nodes (40): clean_song_title(), LyricsService, match_lyric_track(), Lyrics, LyricsMatch, Track, Database, test_clean_song_title() (+32 more)

### Community 4 - "SearchScreen"
Cohesion: 0.15
Nodes (4): SearchScreen, test_search_screen_action_quit_and_focus_search(), test_search_screen_albums_and_split(), test_search_screen_split_toggle()

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
Cohesion: 0.16
Nodes (4): on_dismiss(), on_dismiss(), on_confirm_delete(), on_dismiss()

### Community 15 - "AlbumsModal"
Cohesion: 0.07
Nodes (9): Task 6: User Albums / Playlists Store & Modal, AlbumsModal, AlbumStore, AlbumsView, test_album_and_track_queue_ordering(), test_album_store_crud(), test_albums_modal_colon_key_and_creation(), notify() (+1 more)

### Community 16 - "SettingsModal"
Cohesion: 0.10
Nodes (5): SettingItem, SettingsModal, SettingsView, test_setting_item_change_value(), test_settings_modal_navigation()

### Community 17 - "test_visuals.py"
Cohesion: 0.27
Nodes (4): get_title_lines(), test_ascii_title_render(), test_get_title_lines(), test_matrix_rain_theme_synchronization()

### Community 18 - "ShortcutBar"
Cohesion: 0.31
Nodes (3): ShortcutBar, test_shortcut_bar_render_idle(), test_shortcut_bar_render_playing()

### Community 19 - "__main__.py"
Cohesion: 0.17
Nodes (3): main(), LicensedCatalogProvider, LocalProvider

### Community 20 - "MatrixRain"
Cohesion: 0.22
Nodes (4): Task 7: Phase 1 (Home Screen) & Phase 2 (Search Screen with Deezer + Local Split), MatrixColumn, MatrixRain, test_matrix_rain_set_enabled()

### Community 21 - "GlitchOverlay"
Cohesion: 0.24
Nodes (3): Task 8: Phase 3 (Now Playing Screen) & Player Controls Integration, GlitchOverlay, test_glitch_overlay_lifecycle()

### Community 22 - "AsciiTitle"
Cohesion: 0.21
Nodes (4): AsciiTitle, test_ascii_title_pulse_renders_highlight_and_accent(), on_mount(), run()

### Community 24 - "glitch.py"
Cohesion: 0.27
Nodes (3): generate_glitch_frame(), test_generate_glitch_frame_contains_glitch_chars(), test_generate_glitch_frame_dimensions()

### Community 25 - "now_playing.py"
Cohesion: 0.16
Nodes (7): active_line(), LyricLine, parse_lrc(), _interpolate_color(), _rgb_to_hex(), SettingGroup, test_lrc_multiple_timestamps_offset_and_delay()

### Community 26 - "AlbumNameModal"
Cohesion: 0.12
Nodes (4): AlbumNameModal, ConfirmModal, test_confirm_modal_and_album_name_modal(), on_mount()

### Community 27 - "asyncio"
Cohesion: 0.09
Nodes (25): Separator, get_themes(), Stems, test_app_play_track_transitions_to_now_playing(), scenario(), test_app_settings_modal_open_and_close(), scenario(), test_missing_separator_dependency_is_actionable() (+17 more)

### Community 28 - "SearchStatusBar"
Cohesion: 0.18
Nodes (3): SearchStatusBar, test_search_screen_album_pane_shortcuts_and_status_bar(), test_search_status_bar_render()

### Community 29 - "PlaybackState"
Cohesion: 0.19
Nodes (8): PlaybackState, MockPlayer, test_app_playlist_load_and_queue_navigation(), scenario(), test_app_single_track_album_no_seek_stop_and_space_replay(), scenario(), test_home_screen_now_playing_widget(), run()

### Community 30 - "httpx"
Cohesion: 0.19
Nodes (6): get_remote_commit(), get_remote_commit_async(), test_get_remote_commit_async_success(), run(), test_get_remote_commit_failure(), test_get_remote_commit_success()

### Community 31 - "updater.py"
Cohesion: 0.20
Nodes (8): async_check_and_update(), find_repo_dir(), get_local_commit(), perform_update(), run_cli_update(), test_find_repo_dir(), test_get_local_commit(), test_perform_update_rejects_dirty_repo()

### Community 32 - "test_phases_home_search.py"
Cohesion: 0.11
Nodes (13): on_mount(), test_search_screen_action_delete_item_album_and_track(), push_screen(), test_search_screen_artist_query_and_enter_submission(), __init__(), on_mount(), test_search_screen_down_arrow_routing_and_focus(), on_mount() (+5 more)

### Community 33 - "ORPHEUS Cyberpunk-Minimalist TUI Redesign — Design Specification"
Cohesion: 0.14
Nodes (13): 1. Intent & Context, 2. Goals, Non-Goals & Anti-Goals, 3. Global Constraints & Standards, 4. Phase Breakdown & Architectural Design, 5. Glitch Transition Engine, 6. What Is Left to the Builder, Anti-Goals, Goals (+5 more)

### Community 34 - "HomeScreen"
Cohesion: 0.15
Nodes (3): HomeScreen, test_home_screen_shortcuts_docked_at_bottom(), on_mount()

### Community 35 - "sources.py"
Cohesion: 0.22
Nodes (4): create_web_track(), _matches(), _safe_url(), test_create_web_track_and_playability()

### Community 37 - "Review Focus"
Cohesion: 0.20
Nodes (9): Global Constraints, ORPHEUS Cyberpunk-Minimalist TUI Redesign Implementation Plan, Review Focus, Task 1: Terminal Graphics Protocol Detection & Half-Block Art Engine, Task 2: Deezer Metadata Provider & YouTube yt-dlp Audio Resolver, Task 3: Matrix Rain Widget & ASCII Title Engine, Task 4: Glitch Transition Widget & Phase Transition Engine, Task 5: Reusable Settings Modal Component (+1 more)

### Community 38 - "make_app"
Cohesion: 0.20
Nodes (8): make_app(), MockProvider, test_app_initial_phase_is_home(), scenario(), test_app_loading_notification_on_track_play(), scenario(), test_app_poll_player_album_vs_standalone(), scenario()

### Community 39 - "test_sources.py"
Cohesion: 0.42
Nodes (4): test_catalog_rejects_non_audio_or_extraction_urls(), test_catalog_rejects_nonfinite_duration(), test_licensed_catalog_requires_license_and_safe_https_url(), test_local_search_recurses_and_skips_invalid_audio()

### Community 40 - "YouTubeMetadataProvider"
Cohesion: 0.32
Nodes (4): YouTubeMetadataProvider, test_youtube_provider_returns_metadata_only(), reply(), run()

### Community 41 - "test_cli.py"
Cohesion: 0.46
Nodes (6): run_cli(), test_explicit_missing_music_directory_is_explained(), test_help_works_without_loading_textual(), test_theme_flag_rejects_unknown_preset(), test_version_flag(), test_youtube_requires_api_key()

## Knowledge Gaps
- **1 isolated node(s):** `orpheus`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 241 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Track` connect `Database` to `CavaReader`, `MpvPlayer`, `.on_key`, `SearchScreen`, `OrpheusApp`, `resolver.py`, `NowPlayingScreen`, `AlbumsModal`, `__main__.py`, `now_playing.py`, `asyncio`, `SearchStatusBar`, `PlaybackState`, `test_phases_home_search.py`, `HomeScreen`, `sources.py`, `HomePlayingWidget`, `Review Focus`, `YouTubeMetadataProvider`?**
  _High betweenness centrality (0.284) - this node is a cross-community bridge._
- **Are the 52 inferred relationships involving `Track` (e.g. with `Task 2: Deezer Metadata Provider & YouTube yt-dlp Audio Resolver` and `Task 2: Update Track.playable and add Web Track Creation helper`) actually correct?**
  _`Track` has 52 INFERRED edges - model-reasoned connections that need verification._
- **What connects `orpheus` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `CavaReader` be split into smaller, more focused modules?**
  _Cohesion score 0.07585568917668825 - nodes in this community are weakly interconnected._
- **Why does `SearchScreen` connect `SearchScreen` to `test_phases_home_search.py`, `ORPHEUS Cyberpunk-Minimalist TUI Redesign — Design Specification`, `.on_key`, `Database`, `Review Focus`, `OrpheusApp`, `resolver.py`, `._populate_albums_table`, `AlbumsModal`, `now_playing.py`, `AlbumNameModal`, `asyncio`, `SearchStatusBar`?**
  _High betweenness centrality (0.145) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `SearchScreen` (e.g. with `ORPHEUS Cyberpunk-Minimalist TUI Redesign Implementation Plan` and `Task 9: App Controller Phase Orchestration & E2E System Tests`) actually correct?**
  _`SearchScreen` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Should `MpvPlayer` be split into smaller, more focused modules?**
  _Cohesion score 0.08597285067873303 - nodes in this community are weakly interconnected._