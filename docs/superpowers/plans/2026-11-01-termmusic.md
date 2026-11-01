# TermMusic implementation plan

The user's request authorizes implementation and testing of this MVP. Astra
reviewed architecture; Sol 6.0 xhigh implements/tests the backend; the parent
integrates the TUI; Luna checks official references; Sol 6.1 xhigh reviews code.

1. **Sources and persistence** — Define `Track` and playback/lyrics models in
   `src/termmusic/models.py`. Implement local, licensed catalog and metadata-only
   YouTube providers in `sources.py`. Add SQLite queue, delay and lyrics cache in
   `storage.py`. First test recursive discovery, validation and database reopening.
2. **Playback** — Implement `player.py` with a private mpv socket and async request
   routing. First test interleaved replies, errors, disconnection and position/pause
   preservation. Run real mpv against generated PCM audio with `--ao=null`.
3. **Lyrics and karaoke** — Implement `lyrics.py` LRC parsing, LRCLIB retrieval,
   positive/negative caching and offset semantics. Implement `separation.py` local
   rights validation, subprocess execution, complete cache publication and cleanup.
   Test network responses and fake Demucs processes without model downloads.
4. **TUI and CLI** — Implement `app.py` and `__main__.py`: search, track list,
   persistent queue, playback actions, timed/plain lyrics, delay, rights confirmation
   and version switching. First add headless behavior tests with injected dependencies.
   Confirm metadata-only entries cannot enter playback and stale jobs cannot
   overwrite current playback/lyrics.
5. **Delivery** — Add virtualenv packaging, Ubuntu instructions, catalog schema and
   examples, agent configuration and logging. Run pytest, Ruff, CLI help and TUI
   smoke checks. Review with Sol 6.1 xhigh; fix material issues and rerun checks.

Only `AGENTS.md` existed initially. Preserve it. `.agents`, `.codex` and `.git`
are read-only host mounts: attempt authorized writes safely, and deliver an
installable configuration bundle if these mounts prevent creating files.
