# Graph Report - Orpheus  (2026-11-02)

## Corpus Check
- 51 files · ~32,482 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 823 nodes · 1963 edges · 33 communities (23 shown, 10 thin omitted)
- Extraction: 78% EXTRACTED · 22% INFERRED · 0% AMBIGUOUS · INFERRED: 436 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `19edcc03`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- CavaVisualizer
- MpvPlayer
- HomeScreen
- Database
- test_phases_home_search.py
- Xác minh TermMusic MVP
- install.sh
- OrpheusApp
- test_art.py
- 🎵 Orpheus
- resolver.py
- orpheus
- NowPlayingScreen
- SearchScreen
- 2026-11-01-orpheus-themes.md
- AlbumsModal
- SettingsModal
- test_visuals.py
- ShortcutBar
- __main__.py
- MatrixRain
- GlitchOverlay
- AsciiTitle
- .safe_app
- glitch.py
- app.py
- updater.py
- ORPHEUS Cyberpunk-Minimalist TUI Redesign — Design Specification
- SearchStatusBar
- ._do_search
- test_search_screen_action_delete_item_album_and_track
- test_search_screen_artist_query_and_enter_submission

## God Nodes (most connected - your core abstractions)
1. `Track` - 107 edges
2. `Database` - 58 edges
3. `SearchScreen` - 55 edges
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

## Communities (33 total, 10 thin omitted)

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
Cohesion: 0.10
Nodes (39): clean_song_title(), LyricsService, match_lyric_track(), Lyrics, LyricsMatch, Track, Database, test_clean_song_title() (+31 more)

### Community 4 - "test_phases_home_search.py"
Cohesion: 0.16
Nodes (7): test_search_screen_action_stop(), test_search_screen_albums_and_split(), test_search_screen_down_arrow_routing_and_focus(), on_mount(), run(), test_search_screen_playlist_context(), test_search_screen_split_toggle()

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
Cohesion: 0.06
Nodes (26): normalize_lyric_match_text(), artist_name_matches(), AudioResolver, DeezerProvider, _extract_base_title(), _fold_ascii(), normalize_artist(), _normalize_for_match() (+18 more)

### Community 12 - "NowPlayingScreen"
Cohesion: 0.05
Nodes (20): PlaybackState, format_progress_bar(), NowPlayingScreen, SyncedLyricsWidget, MockPlayer, test_app_playlist_load_and_queue_navigation(), scenario(), test_app_poll_player_album_vs_standalone() (+12 more)

### Community 15 - "AlbumsModal"
Cohesion: 0.07
Nodes (9): Task 6: User Albums / Playlists Store & Modal, AlbumsModal, AlbumStore, AlbumsView, test_album_and_track_queue_ordering(), test_album_store_crud(), test_albums_modal_colon_key_and_creation(), notify() (+1 more)

### Community 16 - "SettingsModal"
Cohesion: 0.10
Nodes (5): SettingItem, SettingsModal, SettingsView, test_setting_item_change_value(), test_settings_modal_navigation()

### Community 17 - "test_visuals.py"
Cohesion: 0.27
Nodes (3): get_title_lines(), test_ascii_title_render(), test_get_title_lines()

### Community 18 - "ShortcutBar"
Cohesion: 0.20
Nodes (3): ShortcutBar, test_shortcut_bar_render_idle(), test_shortcut_bar_render_playing()

### Community 19 - "__main__.py"
Cohesion: 0.07
Nodes (24): main(), Separator, create_web_track(), LicensedCatalogProvider, LocalProvider, _matches(), _safe_url(), YouTubeMetadataProvider (+16 more)

### Community 20 - "MatrixRain"
Cohesion: 0.20
Nodes (4): Task 7: Phase 1 (Home Screen) & Phase 2 (Search Screen with Deezer + Local Split), MatrixColumn, MatrixRain, test_matrix_rain_step()

### Community 21 - "GlitchOverlay"
Cohesion: 0.15
Nodes (10): Review Focus, Task 1: Terminal Graphics Protocol Detection & Half-Block Art Engine, Task 2: Deezer Metadata Provider & YouTube yt-dlp Audio Resolver, Task 3: Matrix Rain Widget & ASCII Title Engine, Task 4: Glitch Transition Widget & Phase Transition Engine, Task 5: Reusable Settings Modal Component, Task 8: Phase 3 (Now Playing Screen) & Player Controls Integration, Task 9: App Controller Phase Orchestration & E2E System Tests (+2 more)

### Community 22 - "AsciiTitle"
Cohesion: 0.21
Nodes (4): AsciiTitle, test_ascii_title_pulse_renders_highlight_and_accent(), on_mount(), run()

### Community 24 - "glitch.py"
Cohesion: 0.31
Nodes (3): generate_glitch_frame(), test_generate_glitch_frame_contains_glitch_chars(), test_generate_glitch_frame_dimensions()

### Community 25 - "app.py"
Cohesion: 0.07
Nodes (22): active_line(), LyricLine, parse_lrc(), SettingGroup, make_app(), MockLyricsService, MockProvider, Stems (+14 more)

### Community 26 - "updater.py"
Cohesion: 0.10
Nodes (20): async_check_and_update(), find_repo_dir(), get_local_commit(), get_remote_commit(), get_remote_commit_async(), perform_update(), run_cli_update(), run_cli() (+12 more)

### Community 27 - "ORPHEUS Cyberpunk-Minimalist TUI Redesign — Design Specification"
Cohesion: 0.14
Nodes (13): 1. Intent & Context, 2. Goals, Non-Goals & Anti-Goals, 3. Global Constraints & Standards, 4. Phase Breakdown & Architectural Design, 5. Glitch Transition Engine, 6. What Is Left to the Builder, Anti-Goals, Goals (+5 more)

### Community 29 - "._do_search"
Cohesion: 0.28
Nodes (3): extract_artist_name(), is_artist_query(), test_artist_query_parsing()

## Knowledge Gaps
- **1 isolated node(s):** `orpheus`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 227 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Track` connect `Database` to `test_search_screen_artist_query_and_enter_submission`, `MpvPlayer`, `test_phases_home_search.py`, `OrpheusApp`, `resolver.py`, `NowPlayingScreen`, `SearchScreen`, `AlbumsModal`, `__main__.py`, `GlitchOverlay`, `.safe_app`, `app.py`, `SearchStatusBar`, `test_search_screen_action_delete_item_album_and_track`?**
  _High betweenness centrality (0.260) - this node is a cross-community bridge._
- **Are the 46 inferred relationships involving `Track` (e.g. with `Task 2: Deezer Metadata Provider & YouTube yt-dlp Audio Resolver` and `Task 2: Update Track.playable and add Web Track Creation helper`) actually correct?**
  _`Track` has 46 INFERRED edges - model-reasoned connections that need verification._
- **What connects `orpheus` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `CavaVisualizer` be split into smaller, more focused modules?**
  _Cohesion score 0.0726950354609929 - nodes in this community are weakly interconnected._
- **Why does `OrpheusApp` connect `OrpheusApp` to `MpvPlayer`, `HomeScreen`, `Database`, `resolver.py`, `NowPlayingScreen`, `SearchScreen`, `AlbumsModal`, `SettingsModal`, `__main__.py`, `GlitchOverlay`, `app.py`?**
  _High betweenness centrality (0.128) - this node is a cross-community bridge._
- **Are the 26 inferred relationships involving `Database` (e.g. with `Task 6: User Albums / Playlists Store & Modal` and `AlbumStore`) actually correct?**
  _`Database` has 26 INFERRED edges - model-reasoned connections that need verification._
- **Should `MpvPlayer` be split into smaller, more focused modules?**
  _Cohesion score 0.08597285067873303 - nodes in this community are weakly interconnected._