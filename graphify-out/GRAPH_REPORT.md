# Graph Report - Orpheus  (2026-11-02)

## Corpus Check
- 48 files · ~22,485 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 628 nodes · 1473 edges · 24 communities (19 shown, 5 thin omitted)
- Extraction: 80% EXTRACTED · 20% INFERRED · 0% AMBIGUOUS · INFERRED: 295 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4e48a7ad`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- PlaybackState
- MpvPlayer
- OrpheusApp
- Database
- Track
- Xác minh TermMusic MVP
- install.sh
- app.py
- test_art.py
- 🎵 Orpheus
- SearchScreen
- orpheus
- NowPlayingScreen
- ORPHEUS Cyberpunk-Minimalist TUI Redesign — Design Specification
- 2026-11-01-orpheus-themes.md
- AlbumsModal
- SettingsModal
- GlitchOverlay
- HomeScreen
- __main__.py
- MatrixRain
- matrix.py
- AsciiTitle
- generate_glitch_frame

## God Nodes (most connected - your core abstractions)
1. `Track` - 81 edges
2. `Database` - 48 edges
3. `OrpheusApp` - 43 edges
4. `MpvPlayer` - 38 edges
5. `SearchScreen` - 32 edges
6. `LyricsService` - 31 edges
7. `NowPlayingScreen` - 31 edges
8. `AlbumsModal` - 20 edges
9. `HomeScreen` - 20 edges
10. `PlaybackState` - 19 edges

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

## Communities (24 total, 5 thin omitted)

### Community 0 - "PlaybackState"
Cohesion: 0.10
Nodes (13): PlaybackState, make_app(), MockLyricsService, MockPlayer, MockProvider, test_app_initial_phase_is_home(), scenario(), test_app_play_track_transitions_to_now_playing() (+5 more)

### Community 1 - "MpvPlayer"
Cohesion: 0.09
Nodes (27): Global Constraints, Review Focus, Task 1: Update MpvPlayer options and timeout for yt-dlp streaming, Task 2: Update Track.playable and add Web Track Creation helper, Task 3: Integrate Web & YouTube playback and direct URL search in OrpheusApp, Task 4: Documentation, Verification, and Push, Web Audio Playback Implementation Plan, MpvPlayer (+19 more)

### Community 2 - "OrpheusApp"
Cohesion: 0.09
Nodes (4): OrpheusApp, DeezerProvider, test_deezer_provider_search(), run()

### Community 3 - "Database"
Cohesion: 0.10
Nodes (32): LyricsService, Lyrics, LyricsMatch, Database, Stems, test_lrclib_network_error_uses_stale_cache(), run(), test_lrclib_rejects_malformed_lyric_fields() (+24 more)

### Community 4 - "Track"
Cohesion: 0.15
Nodes (15): Track, AudioResolver, Separator, test_audio_resolver_fallback_to_jamendo_when_yt_fails(), run(), test_audio_resolver_selects_closest_duration(), run(), test_missing_separator_dependency_is_actionable() (+7 more)

### Community 7 - "app.py"
Cohesion: 0.07
Nodes (19): active_line(), LyricLine, parse_lrc(), SettingGroup, async_check_and_update(), find_repo_dir(), get_local_commit(), get_remote_commit() (+11 more)

### Community 8 - "test_art.py"
Cohesion: 0.07
Nodes (18): encode_kitty_graphics(), get_kitty_delete_command(), get_placeholder_art(), render_half_blocks(), supports_kitty_graphics(), AlbumArtWidget, NowPlayingFooter, SyncedLyricsWidget (+10 more)

### Community 9 - "🎵 Orpheus"
Cohesion: 0.22
Nodes (8): 🛠️ CLI Options, Examples, ✨ Features, ⌨️ Keyboard Shortcuts, 📄 License & Contribution, 💻 Manual Installation (for Developers), 🎵 Orpheus, ⚡ Quick Install (One-Line Command)

### Community 10 - "SearchScreen"
Cohesion: 0.06
Nodes (8): ShortcutBar, SearchScreen, SearchStatusBar, test_search_screen_playlist_context(), test_search_screen_split_toggle(), test_search_status_bar_render(), test_shortcut_bar_render_idle(), test_shortcut_bar_render_playing()

### Community 12 - "NowPlayingScreen"
Cohesion: 0.10
Nodes (8): format_progress_bar(), NowPlayingScreen, get_themes(), test_format_progress_bar(), test_now_playing_actions_await_app_methods(), test_now_playing_double_tap_seek(), test_now_playing_repeat_cycling(), test_presets_have_requested_names_and_modes()

### Community 13 - "ORPHEUS Cyberpunk-Minimalist TUI Redesign — Design Specification"
Cohesion: 0.14
Nodes (13): 1. Intent & Context, 2. Goals, Non-Goals & Anti-Goals, 3. Global Constraints & Standards, 4. Phase Breakdown & Architectural Design, 5. Glitch Transition Engine, 6. What Is Left to the Builder, Anti-Goals, Goals (+5 more)

### Community 15 - "AlbumsModal"
Cohesion: 0.10
Nodes (5): Task 6: User Albums / Playlists Store & Modal, AlbumsModal, AlbumStore, AlbumsView, test_album_store_crud()

### Community 16 - "SettingsModal"
Cohesion: 0.10
Nodes (5): SettingItem, SettingsModal, SettingsView, test_setting_item_change_value(), test_settings_modal_navigation()

### Community 17 - "GlitchOverlay"
Cohesion: 0.15
Nodes (10): Review Focus, Task 1: Terminal Graphics Protocol Detection & Half-Block Art Engine, Task 2: Deezer Metadata Provider & YouTube yt-dlp Audio Resolver, Task 4: Glitch Transition Widget & Phase Transition Engine, Task 5: Reusable Settings Modal Component, Task 7: Phase 1 (Home Screen) & Phase 2 (Search Screen with Deezer + Local Split), Task 8: Phase 3 (Now Playing Screen) & Player Controls Integration, Task 9: App Controller Phase Orchestration & E2E System Tests (+2 more)

### Community 18 - "HomeScreen"
Cohesion: 0.14
Nodes (3): Global Constraints, ORPHEUS Cyberpunk-Minimalist TUI Redesign Implementation Plan, HomeScreen

### Community 19 - "__main__.py"
Cohesion: 0.07
Nodes (21): main(), create_web_track(), LicensedCatalogProvider, LocalProvider, _matches(), _safe_url(), YouTubeMetadataProvider, run_cli() (+13 more)

### Community 20 - "MatrixRain"
Cohesion: 0.22
Nodes (3): Task 3: Matrix Rain Widget & ASCII Title Engine, MatrixRain, test_matrix_rain_step()

### Community 21 - "matrix.py"
Cohesion: 0.27
Nodes (3): MatrixColumn, get_title_lines(), test_get_title_lines()

### Community 24 - "generate_glitch_frame"
Cohesion: 0.31
Nodes (3): generate_glitch_frame(), test_generate_glitch_frame_contains_glitch_chars(), test_generate_glitch_frame_dimensions()

## Knowledge Gaps
- **1 isolated node(s):** `orpheus`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 180 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Track` connect `Track` to `PlaybackState`, `MpvPlayer`, `OrpheusApp`, `Database`, `app.py`, `SearchScreen`, `NowPlayingScreen`, `AlbumsModal`, `GlitchOverlay`, `__main__.py`?**
  _High betweenness centrality (0.218) - this node is a cross-community bridge._
- **Are the 31 inferred relationships involving `Track` (e.g. with `Task 2: Deezer Metadata Provider & YouTube yt-dlp Audio Resolver` and `Task 2: Update Track.playable and add Web Track Creation helper`) actually correct?**
  _`Track` has 31 INFERRED edges - model-reasoned connections that need verification._
- **What connects `orpheus` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `PlaybackState` be split into smaller, more focused modules?**
  _Cohesion score 0.09846153846153846 - nodes in this community are weakly interconnected._
- **Why does `OrpheusApp` connect `OrpheusApp` to `PlaybackState`, `MpvPlayer`, `Database`, `Track`, `app.py`, `SearchScreen`, `NowPlayingScreen`, `AlbumsModal`, `SettingsModal`, `GlitchOverlay`, `HomeScreen`, `__main__.py`?**
  _High betweenness centrality (0.151) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `Database` (e.g. with `Task 6: User Albums / Playlists Store & Modal` and `AlbumStore`) actually correct?**
  _`Database` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Should `MpvPlayer` be split into smaller, more focused modules?**
  _Cohesion score 0.08597285067873303 - nodes in this community are weakly interconnected._