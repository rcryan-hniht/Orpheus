# Graph Report - Orpheus  (2026-11-02)

## Corpus Check
- 48 files · ~24,679 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 682 nodes · 1611 edges · 26 communities (22 shown, 4 thin omitted)
- Extraction: 79% EXTRACTED · 21% INFERRED · 0% AMBIGUOUS · INFERRED: 337 edges (avg confidence: 0.91)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `cb8a7bf0`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- updater.py
- MpvPlayer
- OrpheusApp
- Database
- test_themes.py
- Xác minh TermMusic MVP
- install.sh
- models.py
- test_art.py
- 🎵 Orpheus
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
- lyrics.py
- Review Focus

## God Nodes (most connected - your core abstractions)
1. `Track` - 92 edges
2. `Database` - 54 edges
3. `OrpheusApp` - 44 edges
4. `LyricsService` - 39 edges
5. `MpvPlayer` - 38 edges
6. `SearchScreen` - 36 edges
7. `NowPlayingScreen` - 34 edges
8. `HomeScreen` - 22 edges
9. `AlbumsModal` - 20 edges
10. `Lyrics` - 20 edges

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

## Communities (26 total, 4 thin omitted)

### Community 0 - "updater.py"
Cohesion: 0.10
Nodes (20): async_check_and_update(), find_repo_dir(), get_local_commit(), get_remote_commit(), get_remote_commit_async(), perform_update(), run_cli_update(), run_cli() (+12 more)

### Community 1 - "MpvPlayer"
Cohesion: 0.09
Nodes (27): Global Constraints, Review Focus, Task 1: Update MpvPlayer options and timeout for yt-dlp streaming, Task 2: Update Track.playable and add Web Track Creation helper, Task 3: Integrate Web & YouTube playback and direct URL search in OrpheusApp, Task 4: Documentation, Verification, and Push, Web Audio Playback Implementation Plan, MpvPlayer (+19 more)

### Community 2 - "OrpheusApp"
Cohesion: 0.08
Nodes (4): OrpheusApp, DeezerProvider, test_deezer_provider_search(), run()

### Community 3 - "Database"
Cohesion: 0.08
Nodes (39): Task 8: Phase 3 (Now Playing Screen) & Player Controls Integration, LyricsService, Lyrics, LyricsMatch, Track, AudioResolver, Database, test_fetch_lyricfind_rejects_unmatched_song() (+31 more)

### Community 4 - "test_themes.py"
Cohesion: 0.18
Nodes (10): get_themes(), Stems, make_app(), test_presets_have_requested_names_and_modes(), test_saved_theme_restored_and_cli_override_persisted(), scenario(), test_theme_selection_persists_without_interrupting_playback(), scenario() (+2 more)

### Community 7 - "models.py"
Cohesion: 0.09
Nodes (13): PlaybackState, make_app(), MockLyricsService, MockPlayer, MockProvider, test_app_initial_phase_is_home(), scenario(), test_app_play_track_transitions_to_now_playing() (+5 more)

### Community 8 - "test_art.py"
Cohesion: 0.07
Nodes (19): encode_kitty_graphics(), get_kitty_delete_command(), get_placeholder_art(), render_half_blocks(), supports_kitty_graphics(), AlbumArtWidget, NowPlayingFooter, SettingGroup (+11 more)

### Community 9 - "🎵 Orpheus"
Cohesion: 0.22
Nodes (8): 🛠️ CLI Options, Examples, ✨ Features, ⌨️ Keyboard Shortcuts, 📄 License & Contribution, 💻 Manual Installation (for Developers), 🎵 Orpheus, ⚡ Quick Install (One-Line Command)

### Community 12 - "NowPlayingScreen"
Cohesion: 0.11
Nodes (7): format_progress_bar(), NowPlayingScreen, test_format_progress_bar(), test_now_playing_action_find_and_quit(), test_now_playing_actions_await_app_methods(), test_now_playing_double_tap_seek(), test_now_playing_repeat_cycling()

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
Cohesion: 0.24
Nodes (3): Task 4: Glitch Transition Widget & Phase Transition Engine, GlitchOverlay, test_glitch_overlay_lifecycle()

### Community 18 - "HomeScreen"
Cohesion: 0.15
Nodes (3): HomeScreen, test_home_screen_shortcuts_docked_at_bottom(), on_mount()

### Community 19 - "__main__.py"
Cohesion: 0.06
Nodes (24): main(), Separator, create_web_track(), LicensedCatalogProvider, LocalProvider, _matches(), _safe_url(), YouTubeMetadataProvider (+16 more)

### Community 20 - "MatrixRain"
Cohesion: 0.20
Nodes (4): Task 7: Phase 1 (Home Screen) & Phase 2 (Search Screen with Deezer + Local Split), MatrixColumn, MatrixRain, test_matrix_rain_step()

### Community 21 - "matrix.py"
Cohesion: 0.31
Nodes (3): get_title_lines(), test_ascii_title_render(), test_get_title_lines()

### Community 22 - "AsciiTitle"
Cohesion: 0.21
Nodes (4): AsciiTitle, test_ascii_title_pulse_renders_highlight_and_accent(), on_mount(), run()

### Community 23 - "SearchScreen"
Cohesion: 0.05
Nodes (9): ShortcutBar, SearchScreen, SearchStatusBar, test_search_screen_action_quit_and_focus_search(), test_search_screen_playlist_context(), test_search_screen_split_toggle(), test_search_status_bar_render(), test_shortcut_bar_render_idle() (+1 more)

### Community 24 - "generate_glitch_frame"
Cohesion: 0.27
Nodes (3): generate_glitch_frame(), test_generate_glitch_frame_contains_glitch_chars(), test_generate_glitch_frame_dimensions()

### Community 25 - "lyrics.py"
Cohesion: 0.09
Nodes (17): active_line(), clean_song_title(), LyricLine, match_lyric_track(), normalize_lyric_match_text(), parse_lrc(), SyncedLyricsWidget, _extract_base_title() (+9 more)

### Community 30 - "Review Focus"
Cohesion: 0.22
Nodes (8): Global Constraints, ORPHEUS Cyberpunk-Minimalist TUI Redesign Implementation Plan, Review Focus, Task 1: Terminal Graphics Protocol Detection & Half-Block Art Engine, Task 2: Deezer Metadata Provider & YouTube yt-dlp Audio Resolver, Task 3: Matrix Rain Widget & ASCII Title Engine, Task 5: Reusable Settings Modal Component, Task 9: App Controller Phase Orchestration & E2E System Tests

## Knowledge Gaps
- **1 isolated node(s):** `orpheus`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 192 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **4 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Track` connect `Database` to `MpvPlayer`, `OrpheusApp`, `models.py`, `test_art.py`, `NowPlayingScreen`, `AlbumsModal`, `__main__.py`, `SearchScreen`, `lyrics.py`, `Review Focus`?**
  _High betweenness centrality (0.233) - this node is a cross-community bridge._
- **Are the 37 inferred relationships involving `Track` (e.g. with `Task 2: Deezer Metadata Provider & YouTube yt-dlp Audio Resolver` and `Task 2: Update Track.playable and add Web Track Creation helper`) actually correct?**
  _`Track` has 37 INFERRED edges - model-reasoned connections that need verification._
- **What connects `orpheus` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `updater.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09716599190283401 - nodes in this community are weakly interconnected._
- **Why does `OrpheusApp` connect `OrpheusApp` to `MpvPlayer`, `Database`, `test_themes.py`, `models.py`, `test_art.py`, `NowPlayingScreen`, `AlbumsModal`, `SettingsModal`, `HomeScreen`, `__main__.py`, `SearchScreen`, `Review Focus`?**
  _High betweenness centrality (0.145) - this node is a cross-community bridge._
- **Are the 23 inferred relationships involving `Database` (e.g. with `Task 6: User Albums / Playlists Store & Modal` and `AlbumStore`) actually correct?**
  _`Database` has 23 INFERRED edges - model-reasoned connections that need verification._
- **Should `MpvPlayer` be split into smaller, more focused modules?**
  _Cohesion score 0.08597285067873303 - nodes in this community are weakly interconnected._