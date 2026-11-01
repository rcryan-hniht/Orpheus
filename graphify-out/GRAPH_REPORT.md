# Graph Report - Orpheus  (2026-11-01)

## Corpus Check
- 31 files · ~14,502 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 405 nodes · 1008 edges · 20 communities (14 shown, 6 thin omitted)
- Extraction: 82% EXTRACTED · 18% INFERRED · 0% AMBIGUOUS · INFERRED: 181 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `50664803`
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
- Track
- prompt.md
- progress.md

## God Nodes (most connected - your core abstractions)
1. `OrpheusApp` - 57 edges
2. `Track` - 57 edges
3. `Database` - 43 edges
4. `MpvPlayer` - 34 edges
5. `LyricsService` - 27 edges
6. `PlaybackState` - 23 edges
7. `make_app()` - 21 edges
8. `Separator` - 16 edges
9. `main()` - 15 edges
10. `Lyrics` - 15 edges

## Surprising Connections (you probably didn't know these)
- `TermMusic implementation plan` --references--> `Track`  [INFERRED]
  docs/superpowers/plans/2026-11-01-termmusic.md → src/orpheus/models.py
- `Task 2: Update Track.playable and add Web Track Creation helper` --references--> `Track`  [INFERRED]
  docs/superpowers/plans/2026-11-01-web-audio-playback.md → src/orpheus/models.py
- `Task 3: Integrate Web & YouTube playback and direct URL search in OrpheusApp` --references--> `MpvPlayer`  [INFERRED]
  docs/superpowers/plans/2026-11-01-web-audio-playback.md → src/orpheus/player.py
- `Web Audio Playback Implementation Plan` --references--> `MpvPlayer`  [INFERRED]
  docs/superpowers/plans/2026-11-01-web-audio-playback.md → src/orpheus/player.py
- `Task 2: Update Track.playable and add Web Track Creation helper` --references--> `create_web_track()`  [INFERRED]
  docs/superpowers/plans/2026-11-01-web-audio-playback.md → src/orpheus/sources.py

## Import Cycles
- None detected.

## Communities (20 total, 6 thin omitted)

### Community 0 - "app.py"
Cohesion: 0.08
Nodes (5): _clock(), LyricsPickerScreen, RightsScreen, get_themes(), test_five_presets_have_requested_names_and_modes()

### Community 1 - "MpvPlayer"
Cohesion: 0.11
Nodes (21): Task 1: Update MpvPlayer options and timeout for yt-dlp streaming, MpvPlayer, optional(), FakeWriter, test_ipc_routes_events_and_replies_by_request_id(), run(), test_ipc_surfaces_command_errors_and_disconnects(), run() (+13 more)

### Community 2 - "OrpheusApp"
Cohesion: 0.09
Nodes (8): Global Constraints, Review Focus, Task 2: Update Track.playable and add Web Track Creation helper, Task 3: Integrate Web & YouTube playback and direct URL search in OrpheusApp, Task 4: Documentation, Verification, and Push, Web Audio Playback Implementation Plan, OrpheusApp, parse_lrc()

### Community 3 - "Database"
Cohesion: 0.10
Nodes (28): active_line(), LyricLine, LyricsService, Lyrics, LyricsMatch, Database, test_lyrics_reload_opens_picker_and_caches_choice(), test_lrc_multiple_timestamps_offset_and_delay() (+20 more)

### Community 4 - "Track"
Cohesion: 0.09
Nodes (13): create_web_track(), LicensedCatalogProvider, _matches(), _safe_url(), YouTubeMetadataProvider, test_catalog_rejects_non_audio_or_extraction_urls(), test_catalog_rejects_nonfinite_duration(), test_create_web_track_and_playability() (+5 more)

### Community 7 - "updater.py"
Cohesion: 0.07
Nodes (22): main(), LocalProvider, async_check_and_update(), find_repo_dir(), get_local_commit(), get_remote_commit(), get_remote_commit_async(), perform_update() (+14 more)

### Community 8 - "app.py"
Cohesion: 0.18
Nodes (9): Provider, Stems, make_app(), test_saved_theme_restored_and_cli_override_persisted(), scenario(), test_theme_selection_persists_without_interrupting_playback(), scenario(), test_unknown_saved_theme_falls_back_and_palette_changes_sync_selector() (+1 more)

### Community 9 - "🎵 Orpheus"
Cohesion: 0.22
Nodes (8): 🛠️ CLI Options, Examples, ✨ Features, ⌨️ Keyboard Shortcuts, 📄 License & Contribution, 💻 Manual Installation (for Developers), 🎵 Orpheus, ⚡ Quick Install (One-Line Command)

### Community 12 - "PlaybackState"
Cohesion: 0.18
Nodes (7): PlaybackState, Player, test_karaoke_preserves_position_and_pause(), scenario(), test_natural_eof_advances_queue_but_stop_does_not(), scenario(), load()

### Community 13 - "test_app.py"
Cohesion: 0.13
Nodes (17): make_app(), test_direct_url_search_plays_and_queues(), scenario(), test_lyric_delay_is_persisted_per_track(), scenario(), test_missing_mpv_does_not_close_browser(), scenario(), test_search_input_keeps_spaces_and_shortcut_letters() (+9 more)

### Community 15 - "LyricLookup"
Cohesion: 0.20
Nodes (6): LyricLookup, test_late_lyrics_cannot_replace_new_track(), scenario(), scenario(), test_quit_cancels_pending_lyrics_and_closes_services(), scenario()

### Community 16 - "test_old_eof_snapshot_cannot_override_new_track_request"
Cohesion: 0.33
Nodes (4): test_old_eof_snapshot_cannot_override_new_track_request(), __init__(), scenario(), __init__()

### Community 17 - "Track"
Cohesion: 0.27
Nodes (11): TermMusic implementation plan, Track, Separator, test_missing_separator_dependency_is_actionable(), run(), test_separator_caches_only_complete_outputs(), run(), test_separator_does_not_cache_partial_output() (+3 more)

### Community 18 - "prompt.md"
Cohesion: 0.22
Nodes (8): 1. Màn hình khởi động (Home), 2. Hiệu ứng nền Matrix, 3. Chữ ORPHEUS, 4. Settings (hộp thoại nổi), 5. Find ([f]), 6. Màn hình Now Playing (terminal), 7. Phong cách chung, 8. Yêu cầu đầu ra

## Knowledge Gaps
- **1 isolated node(s):** `orpheus`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 99 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `OrpheusApp` connect `OrpheusApp` to `app.py`, `Database`, `updater.py`, `app.py`, `PlaybackState`, `test_app.py`, `Track`?**
  _High betweenness centrality (0.198) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `OrpheusApp` (e.g. with `Web Audio Playback Implementation Plan` and `Lyrics`) actually correct?**
  _`OrpheusApp` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `orpheus` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `app.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07765151515151515 - nodes in this community are weakly interconnected._
- **Why does `Track` connect `Track` to `app.py`, `OrpheusApp`, `Database`, `Track`, `updater.py`?**
  _High betweenness centrality (0.153) - this node is a cross-community bridge._
- **Are the 21 inferred relationships involving `Track` (e.g. with `TermMusic implementation plan` and `Task 2: Update Track.playable and add Web Track Creation helper`) actually correct?**
  _`Track` has 21 INFERRED edges - model-reasoned connections that need verification._
- **Should `MpvPlayer` be split into smaller, more focused modules?**
  _Cohesion score 0.10570824524312897 - nodes in this community are weakly interconnected._