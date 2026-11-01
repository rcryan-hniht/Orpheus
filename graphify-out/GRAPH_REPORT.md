# Graph Report - Orpheus  (2026-11-01)

## Corpus Check
- 48 files · ~21,133 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 588 nodes · 1375 edges · 24 communities (18 shown, 6 thin omitted)
- Extraction: 80% EXTRACTED · 20% INFERRED · 0% AMBIGUOUS · INFERRED: 281 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5eb47449`
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
- test_themes.py
- 2026-11-01-orpheus-themes.md
- AlbumsModal
- SettingsModal
- GlitchOverlay
- __main__.py
- MatrixRain
- ShortcutBar
- HomeScreen
- AsciiTitle
- generate_glitch_frame

## God Nodes (most connected - your core abstractions)
1. `Track` - 78 edges
2. `Database` - 48 edges
3. `OrpheusApp` - 41 edges
4. `MpvPlayer` - 38 edges
5. `LyricsService` - 31 edges
6. `NowPlayingScreen` - 30 edges
7. `SearchScreen` - 27 edges
8. `AlbumsModal` - 20 edges
9. `HomeScreen` - 20 edges
10. `SettingsModal` - 19 edges

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

## Communities (24 total, 6 thin omitted)

### Community 0 - "app.py"
Cohesion: 0.08
Nodes (16): active_line(), LyricLine, parse_lrc(), SettingGroup, get_title_lines(), make_app(), MockLyricsService, MockProvider (+8 more)

### Community 1 - "MpvPlayer"
Cohesion: 0.09
Nodes (27): Global Constraints, Review Focus, Task 1: Update MpvPlayer options and timeout for yt-dlp streaming, Task 2: Update Track.playable and add Web Track Creation helper, Task 3: Integrate Web & YouTube playback and direct URL search in OrpheusApp, Task 4: Documentation, Verification, and Push, Web Audio Playback Implementation Plan, MpvPlayer (+19 more)

### Community 2 - "OrpheusApp"
Cohesion: 0.09
Nodes (4): OrpheusApp, DeezerProvider, test_deezer_provider_search(), run()

### Community 3 - "Database"
Cohesion: 0.12
Nodes (24): LyricsService, Lyrics, LyricsMatch, Database, test_lrclib_network_error_uses_stale_cache(), run(), test_lrclib_rejects_malformed_lyric_fields(), run() (+16 more)

### Community 4 - "Track"
Cohesion: 0.14
Nodes (16): Task 2: Deezer Metadata Provider & YouTube yt-dlp Audio Resolver, Track, AudioResolver, Separator, test_audio_resolver_fallback_to_jamendo_when_yt_fails(), run(), test_audio_resolver_selects_closest_duration(), run() (+8 more)

### Community 7 - "updater.py"
Cohesion: 0.10
Nodes (20): async_check_and_update(), find_repo_dir(), get_local_commit(), get_remote_commit(), get_remote_commit_async(), perform_update(), run_cli_update(), run_cli() (+12 more)

### Community 8 - "test_art.py"
Cohesion: 0.08
Nodes (13): encode_kitty_graphics(), get_placeholder_art(), render_half_blocks(), supports_kitty_graphics(), AlbumArtWidget, SyncedLyricsWidget, test_encode_kitty_graphics_escapes(), test_placeholder_art_returns_ascii() (+5 more)

### Community 9 - "🎵 Orpheus"
Cohesion: 0.22
Nodes (8): 🛠️ CLI Options, Examples, ✨ Features, ⌨️ Keyboard Shortcuts, 📄 License & Contribution, 💻 Manual Installation (for Developers), 🎵 Orpheus, ⚡ Quick Install (One-Line Command)

### Community 10 - "SearchScreen"
Cohesion: 0.06
Nodes (17): Global Constraints, ORPHEUS Cyberpunk-Minimalist TUI Redesign Implementation Plan, 1. Intent & Context, 2. Goals, Non-Goals & Anti-Goals, 3. Global Constraints & Standards, 4. Phase Breakdown & Architectural Design, 5. Glitch Transition Engine, 6. What Is Left to the Builder (+9 more)

### Community 12 - "NowPlayingScreen"
Cohesion: 0.10
Nodes (8): PlaybackState, format_progress_bar(), NowPlayingScreen, MockPlayer, test_format_progress_bar(), test_now_playing_actions_await_app_methods(), test_now_playing_double_tap_seek(), test_now_playing_repeat_cycling()

### Community 13 - "test_themes.py"
Cohesion: 0.17
Nodes (10): get_themes(), Stems, make_app(), test_five_presets_have_requested_names_and_modes(), test_saved_theme_restored_and_cli_override_persisted(), scenario(), test_theme_selection_persists_without_interrupting_playback(), scenario() (+2 more)

### Community 15 - "AlbumsModal"
Cohesion: 0.10
Nodes (5): Task 6: User Albums / Playlists Store & Modal, AlbumsModal, AlbumStore, AlbumsView, test_album_store_crud()

### Community 16 - "SettingsModal"
Cohesion: 0.11
Nodes (5): SettingItem, SettingsModal, SettingsView, test_setting_item_change_value(), test_settings_modal_navigation()

### Community 17 - "GlitchOverlay"
Cohesion: 0.17
Nodes (9): Review Focus, Task 1: Terminal Graphics Protocol Detection & Half-Block Art Engine, Task 3: Matrix Rain Widget & ASCII Title Engine, Task 4: Glitch Transition Widget & Phase Transition Engine, Task 5: Reusable Settings Modal Component, Task 7: Phase 1 (Home Screen) & Phase 2 (Search Screen with Deezer + Local Split), Task 8: Phase 3 (Now Playing Screen) & Player Controls Integration, Task 9: App Controller Phase Orchestration & E2E System Tests (+1 more)

### Community 19 - "__main__.py"
Cohesion: 0.08
Nodes (15): main(), create_web_track(), LicensedCatalogProvider, LocalProvider, _matches(), _safe_url(), YouTubeMetadataProvider, test_catalog_rejects_non_audio_or_extraction_urls() (+7 more)

### Community 20 - "MatrixRain"
Cohesion: 0.22
Nodes (3): MatrixColumn, MatrixRain, test_matrix_rain_step()

### Community 21 - "ShortcutBar"
Cohesion: 0.24
Nodes (3): ShortcutBar, test_shortcut_bar_render_idle(), test_shortcut_bar_render_playing()

### Community 26 - "generate_glitch_frame"
Cohesion: 0.25
Nodes (4): generate_glitch_frame(), test_generate_glitch_frame_contains_glitch_chars(), test_generate_glitch_frame_dimensions(), test_glitch_overlay_lifecycle()

## Knowledge Gaps
- **1 isolated node(s):** `orpheus`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 167 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Track` connect `Track` to `app.py`, `MpvPlayer`, `OrpheusApp`, `Database`, `SearchScreen`, `NowPlayingScreen`, `AlbumsModal`, `__main__.py`?**
  _High betweenness centrality (0.220) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `Track` (e.g. with `Task 2: Deezer Metadata Provider & YouTube yt-dlp Audio Resolver` and `Task 2: Update Track.playable and add Web Track Creation helper`) actually correct?**
  _`Track` has 30 INFERRED edges - model-reasoned connections that need verification._
- **What connects `orpheus` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08166969147005444 - nodes in this community are weakly interconnected._
- **Why does `OrpheusApp` connect `OrpheusApp` to `app.py`, `MpvPlayer`, `Database`, `Track`, `SearchScreen`, `NowPlayingScreen`, `test_themes.py`, `AlbumsModal`, `SettingsModal`, `GlitchOverlay`, `__main__.py`, `HomeScreen`?**
  _High betweenness centrality (0.159) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `Database` (e.g. with `Task 6: User Albums / Playlists Store & Modal` and `AlbumStore`) actually correct?**
  _`Database` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Should `MpvPlayer` be split into smaller, more focused modules?**
  _Cohesion score 0.08521870286576169 - nodes in this community are weakly interconnected._