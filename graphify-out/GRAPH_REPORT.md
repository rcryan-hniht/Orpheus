# Graph Report - Orpheus  (2026-11-02)

## Corpus Check
- 48 files · ~22,135 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 619 nodes · 1443 edges · 25 communities (16 shown, 9 thin omitted)
- Extraction: 80% EXTRACTED · 20% INFERRED · 0% AMBIGUOUS · INFERRED: 295 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b712ec0f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- app.py
- MpvPlayer
- OrpheusApp
- Database
- Track
- Xác minh TermMusic MVP
- install.sh
- updater.py
- test_art.py
- 🎵 Orpheus
- SearchScreen
- orpheus
- NowPlayingScreen
- ORPHEUS Cyberpunk-Minimalist TUI Redesign — Design Specification
- 2026-11-01-orpheus-themes.md
- AlbumsModal
- SettingsModal
- DeezerProvider
- SearchStatusBar
- __main__.py
- HomeScreen
- ShortcutBar
- ._get_selected_track_and_context
- 4. Phase Breakdown & Architectural Design

## God Nodes (most connected - your core abstractions)
1. `Track` - 81 edges
2. `Database` - 48 edges
3. `OrpheusApp` - 43 edges
4. `MpvPlayer` - 38 edges
5. `LyricsService` - 31 edges
6. `SearchScreen` - 31 edges
7. `NowPlayingScreen` - 30 edges
8. `AlbumsModal` - 20 edges
9. `HomeScreen` - 20 edges
10. `PlaybackState` - 19 edges

## Surprising Connections (you probably didn't know these)
- `Task 7: Phase 1 (Home Screen) & Phase 2 (Search Screen with Deezer + Local Split)` --references--> `AlbumsModal`  [INFERRED]
  docs/superpowers/plans/2026-11-01-orpheus-ui-redesign.md → src/orpheus/albums.py
- `Task 9: App Controller Phase Orchestration & E2E System Tests` --references--> `OrpheusApp`  [INFERRED]
  docs/superpowers/plans/2026-11-01-orpheus-ui-redesign.md → src/orpheus/app.py
- `Web Audio Playback Implementation Plan` --references--> `OrpheusApp`  [INFERRED]
  docs/superpowers/plans/2026-11-01-web-audio-playback.md → src/orpheus/app.py
- `Task 4: Glitch Transition Widget & Phase Transition Engine` --references--> `GlitchOverlay`  [INFERRED]
  docs/superpowers/plans/2026-11-01-orpheus-ui-redesign.md → src/orpheus/glitch.py
- `Task 8: Phase 3 (Now Playing Screen) & Player Controls Integration` --references--> `LyricsService`  [INFERRED]
  docs/superpowers/plans/2026-11-01-orpheus-ui-redesign.md → src/orpheus/lyrics.py

## Import Cycles
- None detected.

## Communities (25 total, 9 thin omitted)

### Community 0 - "app.py"
Cohesion: 0.09
Nodes (12): SettingGroup, get_title_lines(), make_app(), MockLyricsService, MockProvider, test_app_initial_phase_is_home(), scenario(), test_app_play_track_transitions_to_now_playing() (+4 more)

### Community 1 - "MpvPlayer"
Cohesion: 0.09
Nodes (27): Global Constraints, Review Focus, Task 1: Update MpvPlayer options and timeout for yt-dlp streaming, Task 2: Update Track.playable and add Web Track Creation helper, Task 3: Integrate Web & YouTube playback and direct URL search in OrpheusApp, Task 4: Documentation, Verification, and Push, Web Audio Playback Implementation Plan, MpvPlayer (+19 more)

### Community 3 - "Database"
Cohesion: 0.08
Nodes (36): active_line(), LyricLine, LyricsService, parse_lrc(), Lyrics, LyricsMatch, Database, Stems (+28 more)

### Community 4 - "Track"
Cohesion: 0.14
Nodes (15): Track, AudioResolver, Separator, test_audio_resolver_fallback_to_jamendo_when_yt_fails(), run(), test_audio_resolver_selects_closest_duration(), run(), test_missing_separator_dependency_is_actionable() (+7 more)

### Community 7 - "updater.py"
Cohesion: 0.10
Nodes (20): async_check_and_update(), find_repo_dir(), get_local_commit(), get_remote_commit(), get_remote_commit_async(), perform_update(), run_cli_update(), run_cli() (+12 more)

### Community 8 - "test_art.py"
Cohesion: 0.07
Nodes (16): encode_kitty_graphics(), get_placeholder_art(), render_half_blocks(), supports_kitty_graphics(), AlbumArtWidget, NowPlayingFooter, SyncedLyricsWidget, test_encode_kitty_graphics_escapes() (+8 more)

### Community 9 - "🎵 Orpheus"
Cohesion: 0.22
Nodes (8): 🛠️ CLI Options, Examples, ✨ Features, ⌨️ Keyboard Shortcuts, 📄 License & Contribution, 💻 Manual Installation (for Developers), 🎵 Orpheus, ⚡ Quick Install (One-Line Command)

### Community 12 - "NowPlayingScreen"
Cohesion: 0.08
Nodes (10): PlaybackState, format_progress_bar(), NowPlayingScreen, MockPlayer, test_app_playlist_load_and_queue_navigation(), scenario(), test_format_progress_bar(), test_now_playing_actions_await_app_methods() (+2 more)

### Community 13 - "ORPHEUS Cyberpunk-Minimalist TUI Redesign — Design Specification"
Cohesion: 0.20
Nodes (9): 1. Intent & Context, 2. Goals, Non-Goals & Anti-Goals, 3. Global Constraints & Standards, 5. Glitch Transition Engine, 6. What Is Left to the Builder, Anti-Goals, Goals, Non-Goals (+1 more)

### Community 15 - "AlbumsModal"
Cohesion: 0.10
Nodes (5): Task 6: User Albums / Playlists Store & Modal, AlbumsModal, AlbumStore, AlbumsView, test_album_store_crud()

### Community 16 - "SettingsModal"
Cohesion: 0.10
Nodes (6): Task 5: Reusable Settings Modal Component, SettingItem, SettingsModal, SettingsView, test_setting_item_change_value(), test_settings_modal_navigation()

### Community 17 - "DeezerProvider"
Cohesion: 0.09
Nodes (15): Review Focus, Task 1: Terminal Graphics Protocol Detection & Half-Block Art Engine, Task 2: Deezer Metadata Provider & YouTube yt-dlp Audio Resolver, Task 4: Glitch Transition Widget & Phase Transition Engine, Task 7: Phase 1 (Home Screen) & Phase 2 (Search Screen with Deezer + Local Split), Task 8: Phase 3 (Now Playing Screen) & Player Controls Integration, Task 9: App Controller Phase Orchestration & E2E System Tests, generate_glitch_frame() (+7 more)

### Community 19 - "__main__.py"
Cohesion: 0.08
Nodes (15): main(), create_web_track(), LicensedCatalogProvider, LocalProvider, _matches(), _safe_url(), YouTubeMetadataProvider, test_catalog_rejects_non_audio_or_extraction_urls() (+7 more)

### Community 20 - "HomeScreen"
Cohesion: 0.06
Nodes (11): Global Constraints, ORPHEUS Cyberpunk-Minimalist TUI Redesign Implementation Plan, Task 3: Matrix Rain Widget & ASCII Title Engine, MatrixColumn, MatrixRain, HomeScreen, get_themes(), AsciiTitle (+3 more)

### Community 21 - "ShortcutBar"
Cohesion: 0.24
Nodes (3): ShortcutBar, test_shortcut_bar_render_idle(), test_shortcut_bar_render_playing()

### Community 24 - "4. Phase Breakdown & Architectural Design"
Cohesion: 0.50
Nodes (4): 4. Phase Breakdown & Architectural Design, Phase 1: Home, Phase 2: Search (Find), Phase 3: Now Playing

## Knowledge Gaps
- **1 isolated node(s):** `orpheus`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 177 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Track` connect `Track` to `app.py`, `MpvPlayer`, `OrpheusApp`, `Database`, `SearchScreen`, `NowPlayingScreen`, `AlbumsModal`, `DeezerProvider`, `__main__.py`, `._get_selected_track_and_context`?**
  _High betweenness centrality (0.222) - this node is a cross-community bridge._
- **Are the 31 inferred relationships involving `Track` (e.g. with `Task 2: Deezer Metadata Provider & YouTube yt-dlp Audio Resolver` and `Task 2: Update Track.playable and add Web Track Creation helper`) actually correct?**
  _`Track` has 31 INFERRED edges - model-reasoned connections that need verification._
- **What connects `orpheus` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08525506638714186 - nodes in this community are weakly interconnected._
- **Why does `OrpheusApp` connect `OrpheusApp` to `app.py`, `MpvPlayer`, `Database`, `Track`, `SearchScreen`, `NowPlayingScreen`, `AlbumsModal`, `SettingsModal`, `DeezerProvider`, `__main__.py`, `HomeScreen`?**
  _High betweenness centrality (0.154) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `Database` (e.g. with `Task 6: User Albums / Playlists Store & Modal` and `AlbumStore`) actually correct?**
  _`Database` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Should `MpvPlayer` be split into smaller, more focused modules?**
  _Cohesion score 0.08597285067873303 - nodes in this community are weakly interconnected._