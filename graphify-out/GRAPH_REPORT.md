# Graph Report - Orpheus  (2026-11-02)

## Corpus Check
- 48 files · ~23,915 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 665 nodes · 1569 edges · 30 communities (21 shown, 9 thin omitted)
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 324 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `95f89ee4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- updater.py
- MpvPlayer
- OrpheusApp
- Database
- Track
- Xác minh TermMusic MVP
- install.sh
- app.py
- test_art.py
- 🎵 Orpheus
- ShortcutBar
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
- SearchScreen
- generate_glitch_frame
- resolver.py
- SearchStatusBar
- test_phases_home_search.py
- ._get_selected_track_and_context

## God Nodes (most connected - your core abstractions)
1. `Track` - 89 edges
2. `Database` - 52 edges
3. `OrpheusApp` - 43 edges
4. `MpvPlayer` - 38 edges
5. `LyricsService` - 36 edges
6. `SearchScreen` - 36 edges
7. `NowPlayingScreen` - 34 edges
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

## Communities (30 total, 9 thin omitted)

### Community 0 - "updater.py"
Cohesion: 0.09
Nodes (20): async_check_and_update(), find_repo_dir(), get_local_commit(), get_remote_commit(), get_remote_commit_async(), perform_update(), run_cli_update(), run_cli() (+12 more)

### Community 1 - "MpvPlayer"
Cohesion: 0.09
Nodes (27): Global Constraints, Review Focus, Task 1: Update MpvPlayer options and timeout for yt-dlp streaming, Task 2: Update Track.playable and add Web Track Creation helper, Task 3: Integrate Web & YouTube playback and direct URL search in OrpheusApp, Task 4: Documentation, Verification, and Push, Web Audio Playback Implementation Plan, MpvPlayer (+19 more)

### Community 3 - "Database"
Cohesion: 0.09
Nodes (38): LyricsService, match_lyric_track(), Lyrics, LyricsMatch, Database, test_fetch_lyricfind_rejects_unmatched_song(), run(), test_fetch_lyricfind_successful_match() (+30 more)

### Community 4 - "Track"
Cohesion: 0.09
Nodes (18): Track, AudioResolver, DeezerProvider, Separator, test_audio_resolver_fallback_to_jamendo_when_yt_fails(), run(), test_audio_resolver_selects_closest_duration(), run() (+10 more)

### Community 7 - "app.py"
Cohesion: 0.06
Nodes (20): active_line(), LyricLine, parse_lrc(), PlaybackState, get_themes(), make_app(), MockLyricsService, MockPlayer (+12 more)

### Community 8 - "test_art.py"
Cohesion: 0.11
Nodes (15): encode_kitty_graphics(), get_kitty_delete_command(), get_placeholder_art(), render_half_blocks(), supports_kitty_graphics(), AlbumArtWidget, test_encode_kitty_graphics_escapes(), test_get_kitty_delete_command() (+7 more)

### Community 9 - "🎵 Orpheus"
Cohesion: 0.22
Nodes (8): 🛠️ CLI Options, Examples, ✨ Features, ⌨️ Keyboard Shortcuts, 📄 License & Contribution, 💻 Manual Installation (for Developers), 🎵 Orpheus, ⚡ Quick Install (One-Line Command)

### Community 10 - "ShortcutBar"
Cohesion: 0.24
Nodes (3): ShortcutBar, test_shortcut_bar_render_idle(), test_shortcut_bar_render_playing()

### Community 12 - "NowPlayingScreen"
Cohesion: 0.07
Nodes (11): format_progress_bar(), NowPlayingFooter, NowPlayingScreen, SyncedLyricsWidget, test_format_progress_bar(), test_now_playing_action_find_and_quit(), test_now_playing_actions_await_app_methods(), test_now_playing_double_tap_seek() (+3 more)

### Community 13 - "ORPHEUS Cyberpunk-Minimalist TUI Redesign — Design Specification"
Cohesion: 0.14
Nodes (13): 1. Intent & Context, 2. Goals, Non-Goals & Anti-Goals, 3. Global Constraints & Standards, 4. Phase Breakdown & Architectural Design, 5. Glitch Transition Engine, 6. What Is Left to the Builder, Anti-Goals, Goals (+5 more)

### Community 15 - "AlbumsModal"
Cohesion: 0.10
Nodes (5): Task 6: User Albums / Playlists Store & Modal, AlbumsModal, AlbumStore, AlbumsView, test_album_store_crud()

### Community 16 - "SettingsModal"
Cohesion: 0.10
Nodes (6): SettingGroup, SettingItem, SettingsModal, SettingsView, test_setting_item_change_value(), test_settings_modal_navigation()

### Community 17 - "GlitchOverlay"
Cohesion: 0.14
Nodes (11): Review Focus, Task 1: Terminal Graphics Protocol Detection & Half-Block Art Engine, Task 2: Deezer Metadata Provider & YouTube yt-dlp Audio Resolver, Task 3: Matrix Rain Widget & ASCII Title Engine, Task 4: Glitch Transition Widget & Phase Transition Engine, Task 5: Reusable Settings Modal Component, Task 7: Phase 1 (Home Screen) & Phase 2 (Search Screen with Deezer + Local Split), Task 8: Phase 3 (Now Playing Screen) & Player Controls Integration (+3 more)

### Community 18 - "HomeScreen"
Cohesion: 0.17
Nodes (3): Global Constraints, ORPHEUS Cyberpunk-Minimalist TUI Redesign Implementation Plan, HomeScreen

### Community 19 - "__main__.py"
Cohesion: 0.08
Nodes (15): main(), create_web_track(), LicensedCatalogProvider, LocalProvider, _matches(), _safe_url(), YouTubeMetadataProvider, test_catalog_rejects_non_audio_or_extraction_urls() (+7 more)

### Community 20 - "MatrixRain"
Cohesion: 0.22
Nodes (3): MatrixColumn, MatrixRain, test_matrix_rain_step()

### Community 21 - "matrix.py"
Cohesion: 0.31
Nodes (3): get_title_lines(), test_ascii_title_render(), test_get_title_lines()

### Community 23 - "SearchScreen"
Cohesion: 0.16
Nodes (3): SearchScreen, test_search_screen_action_quit_and_focus_search(), test_search_screen_split_toggle()

### Community 24 - "generate_glitch_frame"
Cohesion: 0.27
Nodes (3): generate_glitch_frame(), test_generate_glitch_frame_contains_glitch_chars(), test_generate_glitch_frame_dimensions()

### Community 25 - "resolver.py"
Cohesion: 0.33
Nodes (4): normalize_lyric_match_text(), _extract_base_title(), _normalize_for_match(), score_track()

### Community 27 - "test_phases_home_search.py"
Cohesion: 0.29
Nodes (3): rank_tracks_by_query(), test_rank_tracks_by_query_base_title_and_case_insensitive(), test_rank_tracks_by_query_exact_match_top()

## Knowledge Gaps
- **1 isolated node(s):** `orpheus`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 190 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Track` connect `Track` to `MpvPlayer`, `OrpheusApp`, `Database`, `app.py`, `NowPlayingScreen`, `AlbumsModal`, `GlitchOverlay`, `__main__.py`, `SearchScreen`, `resolver.py`, `test_phases_home_search.py`, `._get_selected_track_and_context`?**
  _High betweenness centrality (0.233) - this node is a cross-community bridge._
- **Are the 36 inferred relationships involving `Track` (e.g. with `Task 2: Deezer Metadata Provider & YouTube yt-dlp Audio Resolver` and `Task 2: Update Track.playable and add Web Track Creation helper`) actually correct?**
  _`Track` has 36 INFERRED edges - model-reasoned connections that need verification._
- **What connects `orpheus` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `updater.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09146341463414634 - nodes in this community are weakly interconnected._
- **Why does `OrpheusApp` connect `OrpheusApp` to `MpvPlayer`, `Database`, `Track`, `app.py`, `NowPlayingScreen`, `AlbumsModal`, `SettingsModal`, `GlitchOverlay`, `HomeScreen`, `__main__.py`, `SearchScreen`?**
  _High betweenness centrality (0.144) - this node is a cross-community bridge._
- **Are the 22 inferred relationships involving `Database` (e.g. with `Task 6: User Albums / Playlists Store & Modal` and `AlbumStore`) actually correct?**
  _`Database` has 22 INFERRED edges - model-reasoned connections that need verification._
- **Should `MpvPlayer` be split into smaller, more focused modules?**
  _Cohesion score 0.08597285067873303 - nodes in this community are weakly interconnected._