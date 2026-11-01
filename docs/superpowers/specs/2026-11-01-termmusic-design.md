# TermMusic MVP design

The requested product is a Python/Textual terminal music player for Ubuntu Wayland,
using mpv JSON IPC, local music and explicitly licensed online audio, timed LRCLIB
lyrics, and optional rights-confirmed local Demucs karaoke. No cover artwork or
YouTube audio extraction is included.

Use one Python process and one mpv subprocess. A separate server and a plugin
framework add deployment work without helping this MVP. Source providers share
an asynchronous `search(query)` interface; the catalog provider accepts a JSON
list with HTTPS URLs and explicit license attribution. YouTube search is an
optional metadata provider, whose results cannot be played or separated.

`models`, `sources`, `player`, `storage`, `lyrics`, and `separation` contain backend
logic. `app` owns the Textual UI and queue policy; `__main__` owns arguments,
XDG paths, and logging. SQLite stores queue snapshots, lyric caches and per-track
delay. No user account, remote service, or database server is needed.

Search, track list, queue, lyrics, playback status and keyboard shortcuts are
visible together. Work happens asynchronously. A track generation counter rejects
stale lyrics or separation results. Only real EOF advances the queue. mpv uses a
private Unix socket, one reader, request IDs, finite waits and no shell or video.

Positive lyric delay means displaying a line later. Demucs only accepts local
tracks after explicit rights confirmation. Cache complete stems; preserve the
latest position and paused state when changing versions. Shutdown cancels workers
and closes mpv, HTTP clients and SQLite.

Defaults chosen for this implementation: user-maintained licensed catalog rather
than an unauthenticated third-party music service; optional YouTube API key from
the environment; Demucs as an external command to keep its PyTorch environment
separate from the lightweight player.

Verification covers source validation, IPC replies/events/timeouts, SQLite
persistence, lyrics and delay, separation authorization/cache/failure, headless
Textual interaction, and a real mpv run against a generated WAV with null audio.
Heavy model inference and audible output require a suitable local environment.
