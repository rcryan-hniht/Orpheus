# Graph Report - Orpheus  (2026-11-01)

## Corpus Check
- 28 files · ~12,424 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 380 nodes · 968 edges · 18 communities (13 shown, 5 thin omitted)
- Extraction: 84% EXTRACTED · 16% INFERRED · 0% AMBIGUOUS · INFERRED: 158 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `b8f4b650`
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
- app.py
- 🎵 Orpheus
- 2026-11-01-termmusic-design.md
- orpheus
- PlaybackState
- test_app.py
- 2026-11-01-orpheus-themes.md
- LyricLookup
- test_old_eof_snapshot_cannot_override_new_track_request
- test_stale_browser_open_does_not_replace_new_local_track

## God Nodes (most connected - your core abstractions)
1. `OrpheusApp` - 56 edges
2. `Track` - 55 edges
3. `Database` - 43 edges
4. `MpvPlayer` - 29 edges
5. `LyricsService` - 27 edges
6. `PlaybackState` - 23 edges
7. `make_app()` - 21 edges
8. `Separator` - 16 edges
9. `main()` - 15 edges
10. `Lyrics` - 15 edges

## Surprising Connections (you probably didn't know these)
- `TermMusic implementation plan` --references--> `Track`  [INFERRED]
  docs/superpowers/plans/2026-11-01-termmusic.md → src/orpheus/models.py
- `make_app()` --uses--> `OrpheusApp`  [INFERRED]
  tests/test_app.py → src/orpheus/app.py
- `make_app()` --uses--> `OrpheusApp`  [INFERRED]
  tests/test_themes.py → src/orpheus/app.py
- `test_lrclib_network_error_uses_stale_cache()` --uses--> `Track`  [INFERRED]
  tests/test_lyrics.py → src/orpheus/models.py
- `test_lrclib_rejects_malformed_lyric_fields()` --uses--> `Track`  [INFERRED]
  tests/test_lyrics.py → src/orpheus/models.py

## Import Cycles
- None detected.

## Communities (18 total, 5 thin omitted)

### Community 0 - "app.py"
Cohesion: 0.12
Nodes (6): active_line(), LyricLine, parse_lrc(), get_themes(), test_lrc_multiple_timestamps_offset_and_delay(), test_five_presets_have_requested_names_and_modes()

### Community 1 - "MpvPlayer"
Cohesion: 0.12
Nodes (19): MpvPlayer, optional(), FakeWriter, test_ipc_routes_events_and_replies_by_request_id(), run(), test_ipc_surfaces_command_errors_and_disconnects(), run(), test_missing_mpv_reports_clear_error() (+11 more)

### Community 2 - "OrpheusApp"
Cohesion: 0.07
Nodes (4): _clock(), LyricsPickerScreen, OrpheusApp, RightsScreen

### Community 3 - "Database"
Cohesion: 0.12
Nodes (26): LyricsService, Lyrics, LyricsMatch, Database, test_youtube_lyrics_require_choice_and_cached_choice_skips_picker(), scenario(), test_lrclib_network_error_uses_stale_cache(), run() (+18 more)

### Community 4 - "Track"
Cohesion: 0.08
Nodes (23): TermMusic implementation plan, Track, Separator, LicensedCatalogProvider, LocalProvider, _matches(), _safe_url(), YouTubeMetadataProvider (+15 more)

### Community 7 - "updater.py"
Cohesion: 0.07
Nodes (21): main(), async_check_and_update(), find_repo_dir(), get_local_commit(), get_remote_commit(), get_remote_commit_async(), perform_update(), run_cli_update() (+13 more)

### Community 8 - "app.py"
Cohesion: 0.18
Nodes (9): Provider, Stems, make_app(), test_saved_theme_restored_and_cli_override_persisted(), scenario(), test_theme_selection_persists_without_interrupting_playback(), scenario(), test_unknown_saved_theme_falls_back_and_palette_changes_sync_selector() (+1 more)

### Community 9 - "🎵 Orpheus"
Cohesion: 0.22
Nodes (8): 🛠️ CLI Options, Examples, ✨ Features, ⌨️ Keyboard Shortcuts, 📄 License & Contribution, 💻 Manual Installation (for Developers), 🎵 Orpheus, ⚡ Quick Install (One-Line Command)

### Community 12 - "PlaybackState"
Cohesion: 0.19
Nodes (6): PlaybackState, Player, test_karaoke_preserves_position_and_pause(), scenario(), test_natural_eof_advances_queue_but_stop_does_not(), scenario()

### Community 13 - "test_app.py"
Cohesion: 0.14
Nodes (15): make_app(), test_failed_browser_open_keeps_local_playing(), scenario(), test_lyric_delay_is_persisted_per_track(), scenario(), test_missing_mpv_does_not_close_browser(), scenario(), test_search_input_keeps_spaces_and_shortcut_letters() (+7 more)

### Community 15 - "LyricLookup"
Cohesion: 0.20
Nodes (5): LyricLookup, test_late_lyrics_cannot_replace_new_track(), scenario(), test_quit_cancels_pending_lyrics_and_closes_services(), scenario()

### Community 16 - "test_old_eof_snapshot_cannot_override_new_track_request"
Cohesion: 0.40
Nodes (3): test_old_eof_snapshot_cannot_override_new_track_request(), __init__(), scenario()

### Community 17 - "test_stale_browser_open_does_not_replace_new_local_track"
Cohesion: 0.67
Nodes (3): test_stale_browser_open_does_not_replace_new_local_track(), opener(), scenario()

## Knowledge Gaps
- **1 isolated node(s):** `orpheus`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 82 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **5 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `OrpheusApp` connect `OrpheusApp` to `app.py`, `Database`, `Track`, `updater.py`, `app.py`, `PlaybackState`, `test_app.py`?**
  _High betweenness centrality (0.214) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `OrpheusApp` (e.g. with `Lyrics` and `PlaybackState`) actually correct?**
  _`OrpheusApp` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `orpheus` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12121212121212122 - nodes in this community are weakly interconnected._
- **Why does `Track` connect `Track` to `app.py`, `OrpheusApp`, `Database`, `test_app.py`?**
  _High betweenness centrality (0.161) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `Track` (e.g. with `TermMusic implementation plan` and `OrpheusApp`) actually correct?**
  _`Track` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Should `MpvPlayer` be split into smaller, more focused modules?**
  _Cohesion score 0.11962833914053426 - nodes in this community are weakly interconnected._