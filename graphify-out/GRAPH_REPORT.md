# Graph Report - Orpheus  (2026-11-01)

## Corpus Check
- 48 files · ~20,898 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 583 nodes · 1365 edges · 28 communities (20 shown, 8 thin omitted)
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 280 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e14b274e`
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
- httpx
- test_art.py
- 🎵 Orpheus
- SearchScreen
- orpheus
- NowPlayingScreen
- sources.py
- 2026-11-01-orpheus-themes.md
- AlbumsModal
- SettingsModal
- GlitchOverlay
- updater.py
- __main__.py
- MatrixRain
- ShortcutBar
- test_sources.py
- HomeScreen
- AsciiTitle
- YouTubeMetadataProvider
- generate_glitch_frame
- test_cli.py

## God Nodes (most connected - your core abstractions)
1. `Track` - 78 edges
2. `Database` - 48 edges
3. `OrpheusApp` - 41 edges
4. `MpvPlayer` - 38 edges
5. `LyricsService` - 31 edges
6. `NowPlayingScreen` - 29 edges
7. `SearchScreen` - 26 edges
8. `AlbumsModal` - 20 edges
9. `HomeScreen` - 20 edges
10. `SettingsModal` - 19 edges

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

## Communities (28 total, 8 thin omitted)

### Community 0 - "app.py"
Cohesion: 0.14
Nodes (7): active_line(), LyricLine, parse_lrc(), SettingGroup, get_title_lines(), test_lrc_multiple_timestamps_offset_and_delay(), test_get_title_lines()

### Community 1 - "MpvPlayer"
Cohesion: 0.08
Nodes (27): Global Constraints, Review Focus, Task 1: Update MpvPlayer options and timeout for yt-dlp streaming, Task 2: Update Track.playable and add Web Track Creation helper, Task 3: Integrate Web & YouTube playback and direct URL search in OrpheusApp, Task 4: Documentation, Verification, and Push, Web Audio Playback Implementation Plan, MpvPlayer (+19 more)

### Community 2 - "OrpheusApp"
Cohesion: 0.10
Nodes (3): OrpheusApp, get_themes(), test_five_presets_have_requested_names_and_modes()

### Community 3 - "Database"
Cohesion: 0.07
Nodes (41): LyricsService, Lyrics, LyricsMatch, Database, make_app(), MockLyricsService, MockProvider, Stems (+33 more)

### Community 4 - "Track"
Cohesion: 0.09
Nodes (21): Task 2: Deezer Metadata Provider & YouTube yt-dlp Audio Resolver, Track, AudioResolver, DeezerProvider, Separator, _matches(), _safe_url(), test_audio_resolver_fallback_to_jamendo_when_yt_fails() (+13 more)

### Community 7 - "httpx"
Cohesion: 0.16
Nodes (9): get_remote_commit(), get_remote_commit_async(), test_find_repo_dir(), test_get_local_commit(), test_get_remote_commit_async_success(), run(), test_get_remote_commit_failure(), test_get_remote_commit_success() (+1 more)

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
Cohesion: 0.11
Nodes (7): PlaybackState, format_progress_bar(), NowPlayingScreen, MockPlayer, test_format_progress_bar(), test_now_playing_double_tap_seek(), test_now_playing_repeat_cycling()

### Community 15 - "AlbumsModal"
Cohesion: 0.10
Nodes (5): Task 6: User Albums / Playlists Store & Modal, AlbumsModal, AlbumStore, AlbumsView, test_album_store_crud()

### Community 16 - "SettingsModal"
Cohesion: 0.10
Nodes (6): Task 5: Reusable Settings Modal Component, SettingItem, SettingsModal, SettingsView, test_setting_item_change_value(), test_settings_modal_navigation()

### Community 17 - "GlitchOverlay"
Cohesion: 0.17
Nodes (9): Review Focus, Task 1: Terminal Graphics Protocol Detection & Half-Block Art Engine, Task 3: Matrix Rain Widget & ASCII Title Engine, Task 4: Glitch Transition Widget & Phase Transition Engine, Task 7: Phase 1 (Home Screen) & Phase 2 (Search Screen with Deezer + Local Split), Task 8: Phase 3 (Now Playing Screen) & Player Controls Integration, Task 9: App Controller Phase Orchestration & E2E System Tests, GlitchOverlay (+1 more)

### Community 18 - "updater.py"
Cohesion: 0.28
Nodes (5): async_check_and_update(), find_repo_dir(), get_local_commit(), perform_update(), run_cli_update()

### Community 20 - "MatrixRain"
Cohesion: 0.22
Nodes (3): MatrixColumn, MatrixRain, test_matrix_rain_step()

### Community 21 - "ShortcutBar"
Cohesion: 0.24
Nodes (3): ShortcutBar, test_shortcut_bar_render_idle(), test_shortcut_bar_render_playing()

### Community 22 - "test_sources.py"
Cohesion: 0.35
Nodes (5): LicensedCatalogProvider, test_catalog_rejects_non_audio_or_extraction_urls(), test_catalog_rejects_nonfinite_duration(), test_licensed_catalog_requires_license_and_safe_https_url(), test_local_search_recurses_and_skips_invalid_audio()

### Community 25 - "YouTubeMetadataProvider"
Cohesion: 0.32
Nodes (4): YouTubeMetadataProvider, test_youtube_provider_returns_metadata_only(), reply(), run()

### Community 26 - "generate_glitch_frame"
Cohesion: 0.33
Nodes (3): generate_glitch_frame(), test_generate_glitch_frame_contains_glitch_chars(), test_generate_glitch_frame_dimensions()

### Community 27 - "test_cli.py"
Cohesion: 0.52
Nodes (6): run_cli(), test_explicit_missing_music_directory_is_explained(), test_help_works_without_loading_textual(), test_theme_flag_rejects_unknown_preset(), test_version_flag(), test_youtube_requires_api_key()

## Knowledge Gaps
- **1 isolated node(s):** `orpheus`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 164 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Track` connect `Track` to `app.py`, `MpvPlayer`, `OrpheusApp`, `Database`, `SearchScreen`, `NowPlayingScreen`, `sources.py`, `AlbumsModal`, `__main__.py`, `test_sources.py`, `YouTubeMetadataProvider`?**
  _High betweenness centrality (0.218) - this node is a cross-community bridge._
- **Are the 30 inferred relationships involving `Track` (e.g. with `Task 2: Deezer Metadata Provider & YouTube yt-dlp Audio Resolver` and `Task 2: Update Track.playable and add Web Track Creation helper`) actually correct?**
  _`Track` has 30 INFERRED edges - model-reasoned connections that need verification._
- **What connects `orpheus` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14082503556187767 - nodes in this community are weakly interconnected._
- **Why does `OrpheusApp` connect `OrpheusApp` to `app.py`, `MpvPlayer`, `Database`, `Track`, `SearchScreen`, `NowPlayingScreen`, `AlbumsModal`, `SettingsModal`, `GlitchOverlay`, `__main__.py`, `HomeScreen`?**
  _High betweenness centrality (0.159) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `Database` (e.g. with `Task 6: User Albums / Playlists Store & Modal` and `AlbumStore`) actually correct?**
  _`Database` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Should `MpvPlayer` be split into smaller, more focused modules?**
  _Cohesion score 0.08345428156748912 - nodes in this community are weakly interconnected._