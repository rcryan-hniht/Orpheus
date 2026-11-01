# Graph Report - Orpheus  (2026-11-02)

## Corpus Check
- 48 files · ~26,777 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 713 nodes · 1695 edges · 29 communities (19 shown, 10 thin omitted)
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 362 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `dd92926c`
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
- matrix.py
- AsciiTitle
- SearchScreen
- SearchStatusBar
- app.py
- test_phases_home_search.py
- ._get_selected_track_and_context

## God Nodes (most connected - your core abstractions)
1. `Track` - 99 edges
2. `Database` - 56 edges
3. `OrpheusApp` - 43 edges
4. `LyricsService` - 41 edges
5. `SearchScreen` - 38 edges
6. `MpvPlayer` - 38 edges
7. `NowPlayingScreen` - 36 edges
8. `HomeScreen` - 22 edges
9. `PlaybackState` - 21 edges
10. `DeezerProvider` - 21 edges

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

## Communities (29 total, 10 thin omitted)

### Community 0 - "updater.py"
Cohesion: 0.09
Nodes (20): async_check_and_update(), find_repo_dir(), get_local_commit(), get_remote_commit(), get_remote_commit_async(), perform_update(), run_cli_update(), run_cli() (+12 more)

### Community 1 - "MpvPlayer"
Cohesion: 0.08
Nodes (29): Global Constraints, Review Focus, Task 1: Update MpvPlayer options and timeout for yt-dlp streaming, Task 2: Update Track.playable and add Web Track Creation helper, Task 3: Integrate Web & YouTube playback and direct URL search in OrpheusApp, Task 4: Documentation, Verification, and Push, Web Audio Playback Implementation Plan, MpvPlayer (+21 more)

### Community 2 - "HomeScreen"
Cohesion: 0.12
Nodes (7): Global Constraints, ORPHEUS Cyberpunk-Minimalist TUI Redesign Implementation Plan, HomeScreen, get_themes(), test_presets_have_requested_names_and_modes(), test_home_screen_shortcuts_docked_at_bottom(), on_mount()

### Community 3 - "Database"
Cohesion: 0.10
Nodes (39): clean_song_title(), LyricsService, match_lyric_track(), Lyrics, LyricsMatch, Track, Database, test_clean_song_title() (+31 more)

### Community 4 - "AudioResolver"
Cohesion: 0.06
Nodes (20): normalize_lyric_match_text(), AudioResolver, DeezerProvider, extract_artist_name(), _extract_base_title(), is_artist_query(), _normalize_for_match(), rank_tracks_by_query() (+12 more)

### Community 8 - "test_art.py"
Cohesion: 0.06
Nodes (22): encode_kitty_graphics(), get_kitty_delete_command(), get_placeholder_art(), render_half_blocks(), supports_kitty_graphics(), AlbumArtWidget, CavaVisualizer, NowPlayingFooter (+14 more)

### Community 9 - "🎵 Orpheus"
Cohesion: 0.22
Nodes (8): 🛠️ CLI Options, Examples, ✨ Features, ⌨️ Keyboard Shortcuts, 📄 License & Contribution, 💻 Manual Installation (for Developers), 🎵 Orpheus, ⚡ Quick Install (One-Line Command)

### Community 10 - "glitch.py"
Cohesion: 0.31
Nodes (3): generate_glitch_frame(), test_generate_glitch_frame_contains_glitch_chars(), test_generate_glitch_frame_dimensions()

### Community 12 - "NowPlayingScreen"
Cohesion: 0.08
Nodes (14): PlaybackState, format_progress_bar(), NowPlayingScreen, MockPlayer, test_app_playlist_load_and_queue_navigation(), scenario(), test_format_progress_bar(), test_now_playing_action_find_and_quit() (+6 more)

### Community 13 - "ORPHEUS Cyberpunk-Minimalist TUI Redesign — Design Specification"
Cohesion: 0.14
Nodes (13): 1. Intent & Context, 2. Goals, Non-Goals & Anti-Goals, 3. Global Constraints & Standards, 4. Phase Breakdown & Architectural Design, 5. Glitch Transition Engine, 6. What Is Left to the Builder, Anti-Goals, Goals (+5 more)

### Community 15 - "AlbumsModal"
Cohesion: 0.09
Nodes (5): Task 6: User Albums / Playlists Store & Modal, AlbumsModal, AlbumStore, AlbumsView, test_album_store_crud()

### Community 16 - "SettingsModal"
Cohesion: 0.10
Nodes (5): SettingItem, SettingsModal, SettingsView, test_setting_item_change_value(), test_settings_modal_navigation()

### Community 17 - "GlitchOverlay"
Cohesion: 0.15
Nodes (10): Review Focus, Task 1: Terminal Graphics Protocol Detection & Half-Block Art Engine, Task 2: Deezer Metadata Provider & YouTube yt-dlp Audio Resolver, Task 3: Matrix Rain Widget & ASCII Title Engine, Task 4: Glitch Transition Widget & Phase Transition Engine, Task 5: Reusable Settings Modal Component, Task 8: Phase 3 (Now Playing Screen) & Player Controls Integration, Task 9: App Controller Phase Orchestration & E2E System Tests (+2 more)

### Community 18 - "ShortcutBar"
Cohesion: 0.24
Nodes (3): ShortcutBar, test_shortcut_bar_render_idle(), test_shortcut_bar_render_playing()

### Community 19 - "asyncio"
Cohesion: 0.05
Nodes (30): main(), Separator, LicensedCatalogProvider, LocalProvider, _matches(), _safe_url(), YouTubeMetadataProvider, Stems (+22 more)

### Community 20 - "MatrixRain"
Cohesion: 0.20
Nodes (4): Task 7: Phase 1 (Home Screen) & Phase 2 (Search Screen with Deezer + Local Split), MatrixColumn, MatrixRain, test_matrix_rain_step()

### Community 22 - "AsciiTitle"
Cohesion: 0.16
Nodes (5): AsciiTitle, test_ascii_title_pulse_renders_highlight_and_accent(), on_mount(), run(), test_ascii_title_render()

### Community 25 - "app.py"
Cohesion: 0.09
Nodes (14): active_line(), LyricLine, parse_lrc(), SettingGroup, make_app(), MockLyricsService, MockProvider, test_app_initial_phase_is_home() (+6 more)

### Community 26 - "test_phases_home_search.py"
Cohesion: 0.20
Nodes (4): test_rank_tracks_by_query_base_title_and_case_insensitive(), test_rank_tracks_by_query_exact_match_top(), test_search_screen_artist_query_and_enter_submission(), test_search_screen_split_toggle()

## Knowledge Gaps
- **1 isolated node(s):** `orpheus`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 203 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Track` connect `Database` to `MpvPlayer`, `AudioResolver`, `OrpheusApp`, `NowPlayingScreen`, `AlbumsModal`, `GlitchOverlay`, `asyncio`, `SearchScreen`, `app.py`, `test_phases_home_search.py`, `._get_selected_track_and_context`?**
  _High betweenness centrality (0.247) - this node is a cross-community bridge._
- **Are the 40 inferred relationships involving `Track` (e.g. with `Task 2: Deezer Metadata Provider & YouTube yt-dlp Audio Resolver` and `Task 2: Update Track.playable and add Web Track Creation helper`) actually correct?**
  _`Track` has 40 INFERRED edges - model-reasoned connections that need verification._
- **What connects `orpheus` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `updater.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09146341463414634 - nodes in this community are weakly interconnected._
- **Why does `OrpheusApp` connect `OrpheusApp` to `MpvPlayer`, `HomeScreen`, `Database`, `AudioResolver`, `NowPlayingScreen`, `AlbumsModal`, `SettingsModal`, `GlitchOverlay`, `asyncio`, `SearchScreen`, `app.py`?**
  _High betweenness centrality (0.131) - this node is a cross-community bridge._
- **Are the 24 inferred relationships involving `Database` (e.g. with `Task 6: User Albums / Playlists Store & Modal` and `AlbumStore`) actually correct?**
  _`Database` has 24 INFERRED edges - model-reasoned connections that need verification._
- **Should `MpvPlayer` be split into smaller, more focused modules?**
  _Cohesion score 0.08013468013468013 - nodes in this community are weakly interconnected._