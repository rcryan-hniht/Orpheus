# Graph Report - Orpheus  (2026-11-01)

## Corpus Check
- 25 files · ~11,236 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 342 nodes · 872 edges · 15 communities (9 shown, 6 thin omitted)
- Extraction: 82% EXTRACTED · 18% INFERRED · 0% AMBIGUOUS · INFERRED: 154 edges (avg confidence: 0.9)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- lyrics.py
- MpvPlayer
- OrpheusApp
- Database
- Track
- Xác minh TermMusic MVP
- on
- test_cli.py
- app.py
- TermMusic
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

### Community 0 - "lyrics.py"
Cohesion: 0.11
Nodes (8): active_line(), LyricLine, parse_lrc(), test_lrc_multiple_timestamps_offset_and_delay(), test_catalog_rejects_non_audio_or_extraction_urls(), test_catalog_rejects_nonfinite_duration(), test_licensed_catalog_requires_license_and_safe_https_url(), test_local_search_recurses_and_skips_invalid_audio()

### Community 1 - "MpvPlayer"
Cohesion: 0.12
Nodes (19): MpvPlayer, optional(), FakeWriter, test_ipc_routes_events_and_replies_by_request_id(), run(), test_ipc_surfaces_command_errors_and_disconnects(), run(), test_missing_mpv_reports_clear_error() (+11 more)

### Community 3 - "Database"
Cohesion: 0.14
Nodes (22): LyricsService, Lyrics, LyricsMatch, Database, test_lrclib_network_error_uses_stale_cache(), run(), test_lrclib_rejects_malformed_lyric_fields(), run() (+14 more)

### Community 4 - "Track"
Cohesion: 0.09
Nodes (20): TermMusic implementation plan, main(), Track, Separator, LicensedCatalogProvider, LocalProvider, _matches(), _safe_url() (+12 more)

### Community 6 - "on"
Cohesion: 0.12
Nodes (3): _clock(), LyricsPickerScreen, RightsScreen

### Community 7 - "test_cli.py"
Cohesion: 0.43
Nodes (5): run_cli(), test_explicit_missing_music_directory_is_explained(), test_help_works_without_loading_textual(), test_theme_flag_rejects_unknown_preset(), test_youtube_requires_api_key()

### Community 8 - "app.py"
Cohesion: 0.09
Nodes (11): get_themes(), Provider, Stems, make_app(), test_five_presets_have_requested_names_and_modes(), test_saved_theme_restored_and_cli_override_persisted(), scenario(), test_theme_selection_persists_without_interrupting_playback() (+3 more)

### Community 9 - "TermMusic"
Cohesion: 0.20
Nodes (8): Cài đặt trên Ubuntu, Cấu hình agent, Dữ liệu, logging và quyền riêng tư, Giao diện và phím tắt, Karaoke tùy chọn, Nguồn trực tuyến có giấy phép, Orpheus, Phát triển và kiểm thử

### Community 13 - "test_app.py"
Cohesion: 0.06
Nodes (34): PlaybackState, LyricLookup, make_app(), Player, test_failed_browser_open_keeps_local_playing(), scenario(), test_karaoke_preserves_position_and_pause(), scenario() (+26 more)

## Knowledge Gaps
- **1 isolated node(s):** `orpheus`
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 69 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **6 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `OrpheusApp` connect `OrpheusApp` to `Database`, `Track`, `on`, `app.py`, `test_app.py`?**
  _High betweenness centrality (0.240) - this node is a cross-community bridge._
- **Are the 5 inferred relationships involving `OrpheusApp` (e.g. with `Lyrics` and `PlaybackState`) actually correct?**
  _`OrpheusApp` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `orpheus` to the rest of the system?**
  _1 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `lyrics.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1140819964349376 - nodes in this community are weakly interconnected._
- **Why does `Track` connect `Track` to `lyrics.py`, `OrpheusApp`, `Database`, `app.py`, `TermMusic`?**
  _High betweenness centrality (0.227) - this node is a cross-community bridge._
- **Are the 20 inferred relationships involving `Track` (e.g. with `TermMusic implementation plan` and `OrpheusApp`) actually correct?**
  _`Track` has 20 INFERRED edges - model-reasoned connections that need verification._
- **Should `MpvPlayer` be split into smaller, more focused modules?**
  _Cohesion score 0.12195121951219512 - nodes in this community are weakly interconnected._