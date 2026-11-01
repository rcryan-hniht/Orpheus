# Graph Report - Orpheus  (2026-11-02)

## Corpus Check
- 51 files · ~33,867 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 860 nodes · 2047 edges · 36 communities (28 shown, 8 thin omitted)
- Extraction: 78% EXTRACTED · 22% INFERRED · 0% AMBIGUOUS · INFERRED: 451 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a3122fc8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- CavaVisualizer
- MpvPlayer
- HomeScreen
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
- AlbumNameModal
- glitch.py
- test_app.py
- updater.py
- ORPHEUS Cyberpunk-Minimalist TUI Redesign — Design Specification
- SearchStatusBar
- .on_key
- now_playing.py
- test_phases_home_search.py
- test_cli.py
- ._get_selected_track_and_context

## God Nodes (most connected - your core abstractions)
1. `Track` - 107 edges
2. `SearchScreen` - 65 edges
3. `Database` - 58 edges
4. `OrpheusApp` - 45 edges
5. `NowPlayingScreen` - 45 edges
6. `LyricsService` - 41 edges
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

## Communities (36 total, 8 thin omitted)

### Community 0 - "CavaVisualizer"
Cohesion: 0.07
Nodes (10): CavaReader, CavaVisualizer, NowPlayingFooter, test_cava_reader_binary_read_loop(), test_cava_reader_init(), test_cava_reader_set_bars(), test_cava_reader_start_and_stop_cleanup(), test_cava_visualizer_reads_cava_reader() (+2 more)

### Community 1 - "MpvPlayer"
Cohesion: 0.09
Nodes (27): Global Constraints, Review Focus, Task 1: Update MpvPlayer options and timeout for yt-dlp streaming, Task 2: Update Track.playable and add Web Track Creation helper, Task 3: Integrate Web & YouTube playback and direct URL search in OrpheusApp, Task 4: Documentation, Verification, and Push, Web Audio Playback Implementation Plan, MpvPlayer (+19 more)

### Community 2 - "HomeScreen"
Cohesion: 0.12
Nodes (7): Global Constraints, ORPHEUS Cyberpunk-Minimalist TUI Redesign Implementation Plan, HomeScreen, get_themes(), test_presets_have_requested_names_and_modes(), test_home_screen_shortcuts_docked_at_bottom(), on_mount()

### Community 3 - "Database"
Cohesion: 0.07
Nodes (55): clean_song_title(), LyricsService, match_lyric_track(), Lyrics, LyricsMatch, Track, Separator, Database (+47 more)

### Community 4 - "SearchScreen"
Cohesion: 0.14
Nodes (5): SearchScreen, test_search_screen_action_quit_and_focus_search(), test_search_screen_action_stop(), test_search_screen_albums_and_split(), test_search_screen_split_toggle()

### Community 7 - "OrpheusApp"
Cohesion: 0.09
Nodes (3): OrpheusApp, WhichKeyModal, test_which_key_modal_dismiss()

### Community 8 - "test_art.py"
Cohesion: 0.10
Nodes (18): compute_kitty_dimensions(), encode_kitty_graphics(), get_kitty_delete_command(), get_placeholder_art(), render_half_blocks(), supports_kitty_graphics(), AlbumArtWidget, test_compute_kitty_dimensions_preserves_aspect_ratio() (+10 more)

### Community 9 - "🎵 Orpheus"
Cohesion: 0.22
Nodes (8): 🛠️ CLI Options, Examples, ✨ Features, ⌨️ Keyboard Shortcuts, 📄 License & Contribution, 💻 Manual Installation (for Developers), 🎵 Orpheus, ⚡ Quick Install

### Community 10 - "resolver.py"
Cohesion: 0.05
Nodes (27): normalize_lyric_match_text(), artist_name_matches(), AudioResolver, DeezerProvider, extract_artist_name(), _extract_base_title(), _fold_ascii(), is_artist_query() (+19 more)

### Community 12 - "NowPlayingScreen"
Cohesion: 0.05
Nodes (20): PlaybackState, format_progress_bar(), NowPlayingScreen, SyncedLyricsWidget, MockPlayer, test_app_playlist_load_and_queue_navigation(), scenario(), test_app_poll_player_album_vs_standalone() (+12 more)

### Community 13 - "._populate_albums_table"
Cohesion: 0.19
Nodes (4): on_dismiss(), on_dismiss(), on_confirm_delete(), on_dismiss()

### Community 15 - "AlbumsModal"
Cohesion: 0.07
Nodes (9): Task 6: User Albums / Playlists Store & Modal, AlbumsModal, AlbumStore, AlbumsView, test_album_and_track_queue_ordering(), test_album_store_crud(), test_albums_modal_colon_key_and_creation(), notify() (+1 more)

### Community 16 - "SettingsModal"
Cohesion: 0.10
Nodes (6): SettingGroup, SettingItem, SettingsModal, SettingsView, test_setting_item_change_value(), test_settings_modal_navigation()

### Community 17 - "test_visuals.py"
Cohesion: 0.31
Nodes (3): get_title_lines(), test_ascii_title_render(), test_get_title_lines()

### Community 18 - "ShortcutBar"
Cohesion: 0.24
Nodes (3): ShortcutBar, test_shortcut_bar_render_idle(), test_shortcut_bar_render_playing()

### Community 19 - "__main__.py"
Cohesion: 0.08
Nodes (15): main(), create_web_track(), LicensedCatalogProvider, LocalProvider, _matches(), _safe_url(), YouTubeMetadataProvider, test_catalog_rejects_non_audio_or_extraction_urls() (+7 more)

### Community 20 - "MatrixRain"
Cohesion: 0.22
Nodes (3): Task 3: Matrix Rain Widget & ASCII Title Engine, MatrixRain, test_matrix_rain_step()

### Community 21 - "GlitchOverlay"
Cohesion: 0.15
Nodes (10): Review Focus, Task 1: Terminal Graphics Protocol Detection & Half-Block Art Engine, Task 2: Deezer Metadata Provider & YouTube yt-dlp Audio Resolver, Task 4: Glitch Transition Widget & Phase Transition Engine, Task 5: Reusable Settings Modal Component, Task 7: Phase 1 (Home Screen) & Phase 2 (Search Screen with Deezer + Local Split), Task 8: Phase 3 (Now Playing Screen) & Player Controls Integration, Task 9: App Controller Phase Orchestration & E2E System Tests (+2 more)

### Community 22 - "AsciiTitle"
Cohesion: 0.18
Nodes (4): AsciiTitle, test_ascii_title_pulse_renders_highlight_and_accent(), on_mount(), run()

### Community 23 - "AlbumNameModal"
Cohesion: 0.12
Nodes (4): AlbumNameModal, ConfirmModal, test_confirm_modal_and_album_name_modal(), on_mount()

### Community 24 - "glitch.py"
Cohesion: 0.23
Nodes (4): generate_glitch_frame(), MatrixColumn, test_generate_glitch_frame_contains_glitch_chars(), test_generate_glitch_frame_dimensions()

### Community 25 - "test_app.py"
Cohesion: 0.12
Nodes (10): make_app(), MockLyricsService, MockProvider, Stems, test_app_initial_phase_is_home(), scenario(), test_app_play_track_transitions_to_now_playing(), scenario() (+2 more)

### Community 26 - "updater.py"
Cohesion: 0.12
Nodes (14): async_check_and_update(), find_repo_dir(), get_local_commit(), get_remote_commit(), get_remote_commit_async(), perform_update(), run_cli_update(), test_find_repo_dir() (+6 more)

### Community 27 - "ORPHEUS Cyberpunk-Minimalist TUI Redesign — Design Specification"
Cohesion: 0.14
Nodes (13): 1. Intent & Context, 2. Goals, Non-Goals & Anti-Goals, 3. Global Constraints & Standards, 4. Phase Breakdown & Architectural Design, 5. Glitch Transition Engine, 6. What Is Left to the Builder, Anti-Goals, Goals (+5 more)

### Community 28 - "SearchStatusBar"
Cohesion: 0.18
Nodes (3): SearchStatusBar, test_search_screen_album_pane_shortcuts_and_status_bar(), test_search_status_bar_render()

### Community 31 - "now_playing.py"
Cohesion: 0.38
Nodes (4): active_line(), LyricLine, parse_lrc(), test_lrc_multiple_timestamps_offset_and_delay()

### Community 32 - "test_phases_home_search.py"
Cohesion: 0.14
Nodes (9): test_rank_tracks_by_query_base_title_and_case_insensitive(), test_rank_tracks_by_query_exact_match_top(), test_search_screen_action_delete_item_album_and_track(), push_screen(), test_search_screen_artist_query_and_enter_submission(), on_mount(), test_search_screen_down_arrow_routing_and_focus(), on_mount() (+1 more)

### Community 33 - "test_cli.py"
Cohesion: 0.46
Nodes (6): run_cli(), test_explicit_missing_music_directory_is_explained(), test_help_works_without_loading_textual(), test_theme_flag_rejects_unknown_preset(), test_version_flag(), test_youtube_requires_api_key()

## Knowledge Gaps
- **1 isolated node(s):** `orpheus`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 240 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Track` connect `Database` to `CavaVisualizer`, `MpvPlayer`, `models.py`, `._get_selected_track_and_context`, `SearchScreen`, `test_phases_home_search.py`, `OrpheusApp`, `resolver.py`, `NowPlayingScreen`, `AlbumsModal`, `__main__.py`, `GlitchOverlay`, `SearchStatusBar`, `app.py`, `.on_key`, `now_playing.py`?**
  _High betweenness centrality (0.253) - this node is a cross-community bridge._
- **Are the 46 inferred relationships involving `Track` (e.g. with `Task 2: Deezer Metadata Provider & YouTube yt-dlp Audio Resolver` and `Task 2: Update Track.playable and add Web Track Creation helper`) actually correct?**
  _`Track` has 46 INFERRED edges - model-reasoned connections that need verification._
- **What connects `orpheus` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `CavaVisualizer` be split into smaller, more focused modules?**
  _Cohesion score 0.07446808510638298 - nodes in this community are weakly interconnected._
- **Why does `SearchScreen` connect `SearchScreen` to `test_phases_home_search.py`, `HomeScreen`, `Database`, `._get_selected_track_and_context`, `OrpheusApp`, `resolver.py`, `._populate_albums_table`, `AlbumsModal`, `GlitchOverlay`, `AlbumNameModal`, `ORPHEUS Cyberpunk-Minimalist TUI Redesign — Design Specification`, `SearchStatusBar`, `app.py`, `.on_key`?**
  _High betweenness centrality (0.152) - this node is a cross-community bridge._
- **Are the 19 inferred relationships involving `SearchScreen` (e.g. with `ORPHEUS Cyberpunk-Minimalist TUI Redesign Implementation Plan` and `Task 9: App Controller Phase Orchestration & E2E System Tests`) actually correct?**
  _`SearchScreen` has 19 INFERRED edges - model-reasoned connections that need verification._
- **Should `MpvPlayer` be split into smaller, more focused modules?**
  _Cohesion score 0.08597285067873303 - nodes in this community are weakly interconnected._