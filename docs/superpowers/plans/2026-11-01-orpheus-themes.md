# Orpheus themes and YouTube Music plan

The user's latest requests authorize five theme presets, renaming the application
to Orpheus, GitHub Light Contrast as the default, and installing project agent
configuration. They explicitly selected official YouTube Music browser playback
with LRCLIB lyrics, retaining the prohibition on audio extraction.

1. Add native Textual presets with stable names, a theme selector, `--theme`, and
   additive SQLite settings. Test restoration, CLI override, invalid saved values,
   all five presets and existing playback/queue behavior with real Textual.
2. Install `.agents/*.toml` and `.codex/config.toml` using the user's exact model
   roles. Preserve existing files; validate TOML and relative config paths.
3. Add LRCLIB search candidates and cache confirmed selections. Keep YouTube
   results excluded from mpv, queues and Demucs; use official Music watch URLs.
4. Add official-browser launch from YouTube Music results and a lyrics chooser.
   Show external playback clearly; lyrics are text because no browser playback
   timeline is exposed to this TUI. Browser failure must leave local playback
   usable. Test opening, guards, selection/cache and stale-result handling.
5. Rename Python package, project metadata, CLI, current documentation and test
   imports to Orpheus after parallel source edits finish. Preserve existing data
   through a documented legacy-directory fallback rather than moving user files.
6. Run the complete suite, lint, package build and native theme rendering; obtain
   Sol 6.1 xhigh review, address concrete findings, then update Graphify.

File ownership: Sol TUI owns themes/app/storage/CLI and theme tests first; Sol
backend owns metadata provider/LRCLIB/models and their tests. The parent integrates
the rename and documentation. Browser UI follows themes sequentially to avoid
overlapping app edits. Luna verifies official APIs/palettes; reviewer reads the
integrated change. Existing playback, rights confirmation and metadata boundaries
remain binding.
