# Graph Report - Orpheus  (2026-11-01)

## Corpus Check
- 26 files · ~11,231 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 343 nodes · 871 edges · 15 communities (9 shown, 6 thin omitted)
- Extraction: 82% EXTRACTED · 18% INFERRED · 0% AMBIGUOUS · INFERRED: 153 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `9143440c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Track
- MpvPlayer
- OrpheusApp
- Database
- Track
- Xác minh TermMusic MVP
- install.sh
- test_cli.py
- app.py
- 🎵 Orpheus
- 2026-11-01-termmusic-design.md
- orpheus
- test_app.py
- 2026-11-01-orpheus-themes.md

## God Nodes (most connected - your core abstractions)
1. `OrpheusApp` - 55 edges
2. `Track` - 55 edges
3. `Database` - 38 edges
4. `MpvPlayer` - 29 edges
5. `LyricsService` - 27 edges
6. `PlaybackState` - 23 edges
7. `make_app()` - 21 edges
8. `Separator` - 16 edges
9. `Lyrics` - 15 edges
10. `LyricLookup` - 14 edges

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

## Communities (15 total, 6 thin omitted)

### Community 0 - "Track"
Cohesion: 0.25
Nodes (11): TermMusic implementation plan, Track, Separator, test_missing_separator_dependency_is_actionable(), run(), test_separator_caches_only_complete_outputs(), run(), test_separator_does_not_cache_partial_output() (+3 more)

### Community 1 - "MpvPlayer"
Cohesion: 0.12
Nodes (19): MpvPlayer, optional(), FakeWriter, test_ipc_routes_events_and_replies_by_request_id(), run(), test_ipc_surfaces_command_errors_and_disconnects(), run(), test_missing_mpv_reports_clear_error() (+11 more)

### Community 2 - "OrpheusApp"
Cohesion: 0.07
Nodes (4): _clock(), LyricsPickerScreen, OrpheusApp, RightsScreen

### Community 3 - "Database"
Cohesion: 0.11
Nodes (26): active_line(), LyricLine, LyricsService, parse_lrc(), Lyrics, LyricsMatch, Database, test_lrc_multiple_timestamps_offset_and_delay() (+18 more)

### Community 4 - "Track"
Cohesion: 0.08
Nodes (13): main(), LicensedCatalogProvider, LocalProvider, _matches(), _safe_url(), YouTubeMetadataProvider, test_catalog_rejects_non_audio_or_extraction_urls(), test_catalog_rejects_nonfinite_duration() (+5 more)

### Community 7 - "test_cli.py"
Cohesion: 0.21
Nodes (5): run_cli(), test_explicit_missing_music_directory_is_explained(), test_help_works_without_loading_textual(), test_theme_flag_rejects_unknown_preset(), test_youtube_requires_api_key()

### Community 8 - "app.py"
Cohesion: 0.09
Nodes (11): get_themes(), Provider, Stems, make_app(), test_five_presets_have_requested_names_and_modes(), test_saved_theme_restored_and_cli_override_persisted(), scenario(), test_theme_selection_persists_without_interrupting_playback() (+3 more)

### Community 9 - "🎵 Orpheus"
Cohesion: 0.25
Nodes (7): 📄 Bản quyền & Đóng góp, ⚡ Cài đặt nhanh (1 dòng lệnh), 💻 Cài đặt thủ công dành cho lập trình viên, 🎵 Orpheus, ⌨️ Phím tắt điều khiển (Shortcuts), ✨ Tính năng nổi bật (Features), 🛠️ Tùy chọn dòng lệnh (CLI Options)

### Community 13 - "test_app.py"
Cohesion: 0.06
Nodes (34): PlaybackState, LyricLookup, make_app(), Player, test_failed_browser_open_keeps_local_playing(), scenario(), test_karaoke_preserves_position_and_pause(), scenario() (+26 more)

## Knowledge Gaps
- **1 isolated node(s):** `orpheus`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 71 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `OrpheusApp` connect `OrpheusApp` to `Track`, `Database`, `Track`, `app.py`, `test_app.py`?**
  _High betweenness centrality (0.230) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `OrpheusApp` (e.g. with `Lyrics` and `PlaybackState`) actually correct?**
  _`OrpheusApp` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `orpheus` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `MpvPlayer` be split into smaller, more focused modules?**
  _Cohesion score 0.11962833914053426 - nodes in this community are weakly interconnected._
- **Why does `Track` connect `Track` to `OrpheusApp`, `Database`, `Track`, `test_cli.py`, `app.py`?**
  _High betweenness centrality (0.184) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `Track` (e.g. with `TermMusic implementation plan` and `OrpheusApp`) actually correct?**
  _`Track` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Should `OrpheusApp` be split into smaller, more focused modules?**
  _Cohesion score 0.07075873827791987 - nodes in this community are weakly interconnected._