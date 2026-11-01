# Web Audio Playback Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enable native playback of web audio streams (YouTube, direct HTTP/HTTPS audio URLs, SoundCloud/Bandcamp streams) via mpv with yt-dlp integration directly inside Orpheus terminal player, and support pasting direct URLs to play or enqueue.

**Architecture:** Configure `MpvPlayer` with `--ytdl=yes`, `--ytdl-format=bestaudio/best`, `--slang=vi,vie,en,eng`, and `--alang=vi,vie,en,eng` with an increased load timeout (20s) for stream extraction. Extend `Track.playable` to include `"youtube"` and `"web"`. Remove browser-launching delegation in `OrpheusApp`, routing YouTube and Web tracks directly through `_load_track` to mpv. Add URL detection and `create_web_track` utility in `sources.py` allowing direct HTTP/HTTPS URLs (and YouTube URLs) entered into the search box to be immediately populated in the results table for playback or queueing.

**Tech Stack:** Python 3.14, Textual, mpv (with yt-dlp IPC), httpx, pytest, pytest-asyncio/anyio.

**Spec:** Direct requirements from user request ("hướng 2 , và 1 nếu có thể" — native yt-dlp/mpv audio streaming and direct URL search/enqueue support).

## Global Constraints

- All notifications, CLI outputs, error messages, help strings, UI labels, and commit messages MUST be in English.
- No bypassing permissions, access controls, or sandbox boundaries; no `rm -rf`.
- Always run `graphify update .` after code changes.
- Maintain formatting and lint standards with `ruff check src tests`.

## Review Focus

1. Slow stream extraction causing timeout on `load`: mpv timeout must be at least 20s.
2. Incompatible URL schemes (e.g., `javascript:`, local `file://` pasted in search): must only accept `http://` or `https://`.
3. Transport actions (seek, pause, volume) when playing YouTube stream: must operate without raising browser warnings.
4. Enqueueing YouTube and Web stream tracks: must be allowed and persistable in queue database.
5. Synced/plain lyrics lookup for web streams: must gracefully handle missing metadata without crashing.

---

### Task 1: Update MpvPlayer options and timeout for yt-dlp streaming

**Files:**
- Modify: `src/orpheus/player.py:32-45`
- Modify: `src/orpheus/player.py:135-139`
- Modify: `tests/test_player.py`

**Interfaces:**
- Consumes: `MpvPlayer` class
- Produces: `MpvPlayer.start` spawning mpv with `--ytdl=yes`, `--ytdl-format=bestaudio/best`, `--slang=vi,vie,en,eng`, `--alang=vi,vie,en,eng`, `MpvPlayer.load` with 20s timeout.

- [ ] **Step 1: Write the failing test**

In `tests/test_player.py`:
```python
def test_mpv_player_ytdl_and_lang_flags_configured():
    # Verify player start uses --ytdl=yes, --ytdl-format=bestaudio/best, --slang=vi,vie,en,eng, --alang=vi,vie,en,eng
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_player.py -k test_mpv_player_ytdl_and_lang_flags_configured -v`
Expected: FAIL

- [ ] **Step 3: Implement player changes in `src/orpheus/player.py`**

Replace `--ytdl=no` with `--ytdl=yes`, `--ytdl-format=bestaudio/best`, `--slang=vi,vie,en,eng`, `--alang=vi,vie,en,eng` in `create_subprocess_exec`.
Increase `asyncio.wait_for(self._file_loaded.wait(), 20)` in `load()`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_player.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/orpheus/player.py tests/test_player.py
git commit -m "feat(player): enable yt-dlp audio streaming in mpv with extended timeout"
```

---

### Task 2: Update Track.playable and add Web Track Creation helper

**Files:**
- Modify: `src/orpheus/models.py:21-24`
- Modify: `src/orpheus/sources.py`
- Test: `tests/test_sources.py`

**Interfaces:**
- Consumes: `Track` dataclass
- Produces:
  - `Track.playable`: returns `True` for `self.source in {"local", "licensed", "youtube", "web"}`
  - `create_web_track(url: str) -> Track`: constructs a `Track` with `source="youtube"` if YouTube domain, else `source="web"`

- [ ] **Step 1: Write the failing test**

In `tests/test_sources.py`:
```python
def test_create_web_track_and_playability():
    # Test YouTube URL and generic web audio URL
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_sources.py -k test_create_web_track_and_playability -v`
Expected: FAIL

- [ ] **Step 3: Implement `Track.playable` and `create_web_track`**

In `src/orpheus/models.py`:
Update `Track.playable` to include `"youtube"` and `"web"`.
In `src/orpheus/sources.py`:
Implement `create_web_track(url: str) -> Track | None`.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_sources.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/orpheus/models.py src/orpheus/sources.py tests/test_sources.py
git commit -m "feat(sources): support web tracks and mark youtube/web as playable"
```

---

### Task 3: Integrate Web & YouTube playback and direct URL search in OrpheusApp

**Files:**
- Modify: `src/orpheus/app.py`
- Test: `tests/test_app.py`

**Interfaces:**
- Consumes: `create_web_track`, `Track.playable`, `MpvPlayer`
- Produces: Direct URL handling in `search()`, native playback of `youtube` and `web` tracks in `_load_track`, enabled enqueueing and playback controls for YouTube/web tracks.

- [ ] **Step 1: Write failing test in `tests/test_app.py`**

Test URL paste in search producing track, playing YouTube track loading into `player.load()`, and enqueueing web/youtube track.

- [ ] **Step 2: Run test to verify it fails**

Run: `pytest tests/test_app.py -k test_web_url_and_youtube_playback -v`
Expected: FAIL

- [ ] **Step 3: Implement app logic changes in `src/orpheus/app.py`**

- In `search()`: check if `query.startswith(("http://", "https://"))`, create web track and display in results table.
- In `_request_track()`: remove browser-opening delegation; allow `youtube` tracks to load via `_load_track()`.
- In `action_enqueue()`: allow enqueueing `youtube` and `web` tracks.
- In `_browser_controls()`: return `False` so player controls work for streaming tracks.
- In `_update_playback()`: format status string for YouTube and web tracks.
- In `_show_attribution()`: format attribution string for YouTube and web tracks.

- [ ] **Step 4: Run test to verify it passes**

Run: `pytest tests/test_app.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/orpheus/app.py tests/test_app.py
git commit -m "feat(app): support direct URL search and native youtube/web playback"
```

---

### Task 4: Documentation, Verification, and Push

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update README.md**

Add documentation on streaming YouTube and direct audio URLs, noting `yt-dlp` requirement.

- [ ] **Step 2: Run full verification suite**

Run `ruff check src tests` and `pytest`.

- [ ] **Step 3: Update code graph**

Run `graphify update .`.

- [ ] **Step 4: Commit and push to main**

```bash
git add README.md graphify-out/
git commit -m "docs: document web audio and youtube streaming features"
git push origin main
```
