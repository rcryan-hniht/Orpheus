"""Textual interface for searching, queuing, and playing music."""

import asyncio
import logging
import webbrowser
from collections.abc import Callable
from pathlib import Path

from rich.text import Text
from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.screen import ModalScreen
from textual.widgets import Button, DataTable, Footer, Header, Input, Select, Static

from .lyrics import active_line, parse_lrc
from .models import Lyrics, LyricsMatch, PlaybackState, Track
from .themes import DEFAULT_THEME, PRESET_LABELS, get_themes

LOG = logging.getLogger(__name__)


def _clock(seconds: float) -> str:
    minutes, remaining = divmod(max(0, int(seconds)), 60)
    return f"{minutes}:{remaining:02d}"


class RightsScreen(ModalScreen[bool]):
    """Require explicit permission before creating local vocal stems."""

    CSS = """
    RightsScreen { align: center middle; }
    #rights-dialog {
        width: 100%; max-width: 60; height: auto; padding: 1 2;
        border: heavy $accent; background: $surface;
    }
    #rights-dialog Button { margin: 1 1 0 0; }
    """

    def compose(self) -> ComposeResult:
        with Vertical(id="rights-dialog"):
            yield Static(
                "Separate vocals only if you have the rights to process this local audio file."
            )
            with Horizontal():
                yield Button("I have the rights", id="confirm", variant="primary")
                yield Button("Cancel", id="cancel")

    @on(Button.Pressed, "#confirm")
    def confirm(self) -> None:
        self.dismiss(True)

    @on(Button.Pressed, "#cancel")
    def cancel(self) -> None:
        self.dismiss(False)


class LyricsPickerScreen(ModalScreen[LyricsMatch | None]):
    CSS = """
    LyricsPickerScreen { align: center middle; }
    #lyrics-dialog {
        width: 100%; max-width: 90; height: 75%; min-height: 12;
        padding: 1 2; border: heavy $accent; background: $surface;
    }
    #lyrics-query { height: 3; }
    #lyrics-results { height: 1fr; }
    #lyrics-search-status { height: 2; }
    """
    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def __init__(self, service, query: str):
        super().__init__()
        self.service = service
        self.initial_query = query
        self.matches: list[LyricsMatch] = []
        self._search_generation = 0

    def compose(self) -> ComposeResult:
        with Vertical(id="lyrics-dialog"):
            yield Static("Choose matching LRCLIB lyrics, or edit the search and press Enter.")
            yield Input(value=self.initial_query, id="lyrics-query")
            yield DataTable(id="lyrics-results", cursor_type="row")
            yield Static("Searching lyrics…", id="lyrics-search-status")
            yield Button("Cancel", id="lyrics-cancel")

    def on_mount(self) -> None:
        self.query_one("#lyrics-results", DataTable).add_columns(
            "Title", "Artist", "Album", "Duration"
        )
        self.query_one("#lyrics-query", Input).focus()
        self.search(self.initial_query)

    @on(Input.Submitted, "#lyrics-query")
    def on_query_submitted(self, event: Input.Submitted) -> None:
        self.search(event.value)

    @work(group="lyrics_candidates", exclusive=True)
    async def search(self, query: str) -> None:
        self._search_generation += 1
        generation = self._search_generation
        self.matches = []
        table = self.query_one("#lyrics-results", DataTable)
        table.clear()
        status = self.query_one("#lyrics-search-status", Static)
        status.update(Text("Searching LRCLIB…"))
        try:
            matches = await self.service.search(query)
        except Exception as exc:
            if generation == self._search_generation:
                LOG.warning("Lyrics candidate search failed (%s)", type(exc).__name__)
                status.update(
                    Text("Lyrics search failed. Edit the query and press Enter to retry.")
                )
            return
        if generation != self._search_generation:
            return
        self.matches = matches
        for index, match in enumerate(matches):
            duration = _clock(match.duration) if match.duration is not None else "—"
            table.add_row(match.title, match.artist, match.album, duration, key=str(index))
        status.update(Text(f"{len(matches)} match(es). Select one with Enter." if matches else
                           "No matches. Edit the search and press Enter again."))

    @on(DataTable.RowSelected, "#lyrics-results")
    def on_match_selected(self, event: DataTable.RowSelected) -> None:
        if 0 <= event.cursor_row < len(self.matches):
            self.dismiss(self.matches[event.cursor_row])

    @on(Button.Pressed, "#lyrics-cancel")
    def action_cancel(self) -> None:
        self.dismiss(None)


class OrpheusApp(App):
    TITLE = "Orpheus"
    CSS = """
    #search-row { height: 3; }
    #search { width: 1fr; }
    #source { width: 20; }
    #theme-row { height: 3; }
    #theme-label { width: 7; padding: 1 0 0 1; }
    #theme { width: 1fr; }
    #results-row { height: 2fr; }
    #tracks { width: 2fr; }
    #queue { width: 1fr; }
    #lyrics { height: 1fr; border: solid $accent; padding: 1; overflow: auto; }
    #attribution { height: 4; padding: 0 1; }
    #status { height: 2; padding: 0 1; }
    """
    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit", priority=True),
        Binding("e", "enqueue", "Queue"),
        Binding("delete", "remove_queue", "Remove"),
        Binding("n", "next_track", "Next"),
        Binding("space", "pause", "Pause"),
        Binding("s", "stop", "Stop"),
        Binding("left", "seek_back", "−5s", priority=True),
        Binding("right", "seek_forward", "+5s", priority=True),
        Binding("plus", "volume_up", "Vol+"),
        Binding("minus", "volume_down", "Vol−"),
        Binding("left_square_bracket", "delay_back", "Lyrics−", show=False),
        Binding("right_square_bracket", "delay_forward", "Lyrics+", show=False),
        Binding("r", "reload_lyrics", "Lyrics", show=False),
        Binding("k", "karaoke", "Karaoke"),
    ]

    def __init__(
        self,
        *,
        providers,
        player,
        database,
        lyrics,
        separator,
        music_dir: Path,
        theme: str | None = None,
        browser_opener: Callable[[str], bool] | None = None,
        auto_update: bool = True,
    ):
        super().__init__()
        self._auto_update = auto_update
        self.providers = providers
        self.player = player
        self.database = database
        self.lyrics_service = lyrics
        self.separator = separator
        self.music_dir = Path(music_dir)
        self.browser_opener = browser_opener if browser_opener is not None else webbrowser.open
        supported = {slug for slug, _ in PRESET_LABELS}
        saved = database.get_theme()
        self._initial_theme = (
            theme if theme in supported else saved if saved in supported else DEFAULT_THEME
        )
        self.results: list[Track] = []
        self.queue: list[Track] = []
        self.current_track: Track | None = None
        self.playback = PlaybackState()
        self.lyrics: Lyrics | None = None
        self.lyric_lines = []
        self.lyric_delay = 0.0
        self.stem: Path | None = None
        self.using_stem = False
        self._generation = 0
        self._search_generation = 0
        self._loading = False
        self._mpv_loaded = False
        self._karaoke_pending = False
        self._play_lock = asyncio.Lock()
        self._resources_closed = False

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal(id="search-row"):
            yield Input(placeholder="Search title, artist, or album; Enter to search", id="search")
            yield Select(
                [("YouTube Music" if name == "youtube" else name.title(), name)
                 for name in self.providers],
                value="local",
                allow_blank=False,
                id="source",
            )
        with Horizontal(id="theme-row"):
            yield Static("Theme", id="theme-label")
            yield Select(
                [(label, slug) for slug, label in PRESET_LABELS],
                value=self._initial_theme,
                allow_blank=True,
                prompt="Other Textual theme",
                id="theme",
            )
        with Horizontal(id="results-row"):
            yield DataTable(id="tracks", cursor_type="row")
            yield DataTable(id="queue", cursor_type="row")
        yield Static("Lyrics appear here when a track plays.", id="lyrics")
        yield Static("", id="attribution")
        yield Static("Ready", id="status")
        yield Footer()

    def on_mount(self) -> None:
        for theme in get_themes():
            self.register_theme(theme)
        self.watch(self, "theme", self._on_theme_change, init=False)
        self.theme = self._initial_theme
        self.database.set_theme(self._initial_theme)
        self.query_one("#tracks", DataTable).add_columns("Title", "Artist", "Source")
        self.query_one("#queue", DataTable).add_columns("Queue", "Artist")
        self.queue = self.database.load_queue()
        self._show_queue()
        self.query_one("#search", Input).focus()
        if not self.music_dir.is_dir():
            self._status(f"No music directory at {self.music_dir}. Pass --music-dir to choose one.")
        self.search("", "local")
        self.set_interval(0.5, self.poll_player)
        if self._auto_update:
            self._check_background_update()

    @work(group="auto_update", exclusive=True)
    async def _check_background_update(self) -> None:
        await asyncio.sleep(3.0)
        try:
            from .updater import async_check_and_update
            has_update, message = await async_check_and_update(self.database)
            if has_update and message:
                self.notify(message, title="Orpheus Update", severity="information", timeout=8.0)
        except Exception as exc:
            LOG.debug("Background update check encountered an error: %s", exc)

    def check_action(self, action: str, parameters: tuple[object, ...]) -> bool:
        if isinstance(self.focused, Input) and action != "quit":
            return False
        return True

    def _on_theme_change(self, theme: str) -> None:
        select = self.query_one("#theme", Select)
        if theme in dict(PRESET_LABELS):
            if select.value != theme:
                select.value = theme
            self.database.set_theme(theme)
        elif not select.is_blank:
            select.clear()

    @on(Select.Changed, "#theme")
    def on_theme_selected(self, event: Select.Changed) -> None:
        if event.value in dict(PRESET_LABELS) and self.theme != event.value:
            self.theme = event.value

    def _status(self, message: str) -> None:
        try:
            self.query_one("#status", Static).update(Text(message))
        except Exception:
            pass

    def _error(self, operation: str, exc: Exception) -> None:
        # HTTP exception strings can contain an API key in the request URL.
        LOG.warning("%s failed (%s)", operation, type(exc).__name__)
        detail = (
            str(exc)
            if operation in {"Playback", "Karaoke", "Lyrics"}
            or (operation == "Search" and isinstance(exc, ValueError))
            else type(exc).__name__
        )
        message = f"{operation} failed: {detail}"
        self._status(message)
        self.notify(message, severity="error")

    @on(Input.Submitted, "#search")
    def on_search_submitted(self, event: Input.Submitted) -> None:
        self.search(event.value.strip(), self.query_one("#source", Select).value)

    @on(Select.Changed, "#source")
    def on_source_changed(self, event: Select.Changed) -> None:
        if event.value in self.providers:
            self.search(self.query_one("#search", Input).value.strip(), event.value)

    @work(group="search", exclusive=True)
    async def search(self, query: str, source: str) -> None:
        self._search_generation += 1
        generation = self._search_generation
        if query.startswith(("http://", "https://")):
            from .sources import create_web_track

            track = create_web_track(query)
            if track is not None:
                self.results = [track]
                self._show_results()
                self._status(
                    f"Direct URL loaded: 1 track ({track.source}). "
                    "Press Enter to play or e to queue."
                )
                return
        if source == "youtube" and not query:
            self.results = []
            self._show_results()
            self._status("Enter a search term for YouTube metadata.")
            return
        self._status(f"Searching {source}…")
        try:
            tracks = await self.providers[source].search(query)
        except Exception as exc:
            if generation == self._search_generation:
                self._error("Search", exc)
            return
        if generation != self._search_generation:
            return
        self.results = tracks
        self._show_results()
        if source == "local" and not tracks and not self.music_dir.is_dir():
            self._status(f"No music directory at {self.music_dir}. Pass --music-dir to choose one.")
        elif source == "local" and not tracks and not query:
            self._status(f"No audio files found in {self.music_dir}.")
        else:
            self._status(
                f"{len(tracks)} track(s) in {source}."
                if tracks
                else f"No tracks found in {source}."
            )

    def _show_results(self) -> None:
        table = self.query_one("#tracks", DataTable)
        table.clear()
        for index, track in enumerate(self.results):
            table.add_row(track.title, track.artist, track.source, key=str(index))
        self._show_attribution(self.results[0] if self.results else None)

    def _show_queue(self) -> None:
        table = self.query_one("#queue", DataTable)
        table.clear()
        for index, track in enumerate(self.queue):
            table.add_row(track.title, track.artist, key=str(index))

    def _show_attribution(self, track: Track | None) -> None:
        if track is None:
            message = ""
        elif track.source == "youtube":
            message = f"YouTube Stream · {track.location}"
        elif track.source == "web":
            message = f"Web Stream · {track.location}"
        elif track.source == "licensed":
            message = f"{track.attribution} · {track.license} · {track.license_url}"
        else:
            message = f"Local file · {track.location}"
        try:
            self.query_one("#attribution", Static).update(Text(message))
        except Exception:
            pass

    @on(DataTable.RowHighlighted, "#tracks")
    def on_track_highlighted(self, event: DataTable.RowHighlighted) -> None:
        if 0 <= event.cursor_row < len(self.results):
            self._show_attribution(self.results[event.cursor_row])

    @on(DataTable.RowSelected)
    def on_row_selected(self, event: DataTable.RowSelected) -> None:
        if event.data_table.id == "tracks" and 0 <= event.cursor_row < len(self.results):
            self._request_track(self.results[event.cursor_row])
        elif event.data_table.id == "queue" and 0 <= event.cursor_row < len(self.queue):
            track = self.queue[event.cursor_row]
            self._request_track(track, queue_item=track)

    def _selected_result(self) -> Track | None:
        table = self.query_one("#tracks", DataTable)
        if self.focused is table and 0 <= table.cursor_row < len(self.results):
            return self.results[table.cursor_row]
        return None

    def action_enqueue(self) -> None:
        track = self._selected_result()
        if track is None:
            return
        if not track.playable:
            self.notify(
                "This track cannot play in the app queue.",
                severity="warning",
            )
            return
        self.queue.append(track)
        self.database.save_queue(self.queue)
        self._show_queue()
        self._status(f"Queued: {track.title}")

    def action_remove_queue(self) -> None:
        table = self.query_one("#queue", DataTable)
        if self.focused is table and 0 <= table.cursor_row < len(self.queue):
            del self.queue[table.cursor_row]
            self.database.save_queue(self.queue)
            self._show_queue()

    def _request_track(self, track: Track, queue_item: Track | None = None) -> None:
        if isinstance(self.screen, LyricsPickerScreen):
            self.screen.dismiss(None)
        if not track.playable:
            self.notify("This result cannot play in the app.", severity="warning")
            return
        self._generation += 1
        generation = self._generation
        self._loading = True
        self.current_track = None
        self.stem = None
        self.using_stem = False
        self.lyrics = None
        self.lyric_lines = []
        try:
            self.query_one("#lyrics", Static).update(Text("Loading lyrics…"))
        except Exception:
            pass
        self._status(f"Loading: {track.title}")
        self._load_track(track, generation, queue_item)

    @work(group="browser", exclusive=False)
    async def _open_youtube(self, track: Track, generation: int) -> None:
        try:
            opened = await asyncio.to_thread(self.browser_opener, track.location)
        except Exception as exc:
            LOG.warning("Browser open failed (%s)", type(exc).__name__)
            opened = False
        if generation != self._generation:
            return
        if not opened:
            self._loading = False
            self.notify("Could not open YouTube Music in your browser.", severity="error")
            if self.current_track is not None:
                self._update_playback()
            else:
                self._status("Could not open YouTube Music in your browser.")
            return
        async with self._play_lock:
            if generation != self._generation:
                return
            if self._mpv_loaded:
                try:
                    await self.player.stop()
                    self._mpv_loaded = False
                except Exception as exc:
                    if generation == self._generation:
                        LOG.warning("mpv stop before browser playback failed (%s)",
                                    type(exc).__name__)
                        self.notify(
                            "Browser opened, but mpv could not stop. Stop one source manually.",
                            severity="error",
                        )
                        self._loading = False
                    return
            if generation != self._generation:
                return
            self.current_track = track
            self.playback = PlaybackState()
            self.using_stem = False
            self.stem = None
            try:
                self.lyrics = self.lyrics_service.get_cached(track)
            except Exception as exc:
                LOG.warning("Cached lyrics lookup failed (%s)", type(exc).__name__)
                self.lyrics = None
            self.lyric_lines = []
            self._loading = False
            self._show_attribution(track)
            self._update_playback()
            if self.lyrics is not None:
                self._show_external_lyrics()
            else:
                self.query_one("#lyrics", Static).update(Text("Choose lyrics from LRCLIB…"))
        if self.lyrics is None:
            self._choose_external_lyrics(track, generation)

    @work(group="lyrics_choice", exclusive=True)
    async def _choose_external_lyrics(self, track: Track, generation: int) -> None:
        if generation != self._generation or self.current_track != track:
            return
        try:
            screen = LyricsPickerScreen(self.lyrics_service, track.title)
            match = await self.push_screen_wait(screen)
        except Exception as exc:
            if generation == self._generation:
                LOG.warning("Lyrics picker failed (%s)", type(exc).__name__)
                self.notify("Lyrics picker unavailable.", severity="error")
            return
        if match is None or generation != self._generation or self.current_track != track:
            return
        try:
            self.lyrics_service.cache_selection(track, match.lyrics)
        except Exception as exc:
            LOG.warning("Lyrics selection cache failed (%s)", type(exc).__name__)
            self.notify("Could not save lyrics choice; it may need selecting again.",
                        severity="warning")
        self.lyrics = match.lyrics
        if match.lyrics and match.lyrics.synced:
            self.lyric_lines = parse_lrc(match.lyrics.synced)
        else:
            self.lyric_lines = []
        self._update_lyrics()

    def _show_external_lyrics(self) -> None:
        lyrics = self.lyrics
        if lyrics is None:
            message = "No lyrics selected. Press r to search LRCLIB."
        elif lyrics.plain:
            message = lyrics.plain
        elif lyrics.synced:
            message = "\n".join(line.text for line in parse_lrc(lyrics.synced))
        elif lyrics.instrumental:
            message = "Instrumental track"
        else:
            message = "No lyrics in this match. Press r to search again."
        self.query_one("#lyrics", Static).update(Text(message))

    @work(group="playback", exclusive=False)
    async def _load_track(self, track: Track, generation: int, queue_item: Track | None) -> None:
        async with self._play_lock:
            if generation != self._generation:
                return
            try:
                await self.player.load(track.location)
                self._mpv_loaded = True
            except Exception as exc:
                if generation == self._generation:
                    self._error("Playback", exc)
                return
            finally:
                if generation == self._generation:
                    self._loading = False
            if generation != self._generation:
                return
            self.current_track = track
            self.lyric_delay = self.database.get_delay(track.id)
            self.playback = PlaybackState(idle=False)
            self._show_attribution(track)
            self._update_playback()
            if queue_item is not None:
                for index, item in enumerate(self.queue):
                    if item is queue_item:
                        del self.queue[index]
                        self.database.save_queue(self.queue)
                        self._show_queue()
                        break
            self._load_lyrics(track, generation)

    @work(group="lyrics", exclusive=True)
    async def _load_lyrics(self, track: Track, generation: int) -> None:
        try:
            lyrics = await self.lyrics_service.get(track)
        except Exception as exc:
            if generation == self._generation:
                self._error("Lyrics", exc)
                self.query_one("#lyrics", Static).update(
                    Text("Lyrics unavailable. Press r to retry.")
                )
            return
        if generation != self._generation or self.current_track != track:
            return
        self.lyrics = lyrics
        self.lyric_lines = parse_lrc(lyrics.synced) if lyrics and lyrics.synced else []
        self._update_lyrics()

    def _update_playback(self) -> None:
        if self.current_track is None:
            return
        state = self.playback
        mode = "karaoke" if self.using_stem else "original"
        playback = "paused" if state.paused else "playing"
        label = self.current_track.artist or self.current_track.source.capitalize()
        self._status(
            f"{label} — {self.current_track.title} · "
            f"{_clock(state.position)}/"
            f"{_clock(state.duration or self.current_track.duration or 0)} · "
            f"{playback} · {mode} · vol {state.volume:.0f}% · lyrics {self.lyric_delay:+.2f}s"
        )

    def _update_lyrics(self) -> None:
        if self.current_track is None:
            return
        if self.lyric_lines:
            index = active_line(self.lyric_lines, self.playback.position, self.lyric_delay)
            first = max(0, index - 2)
            last = min(len(self.lyric_lines), max(index + 4, 5))
            display = Text()
            for number in range(first, last):
                line = self.lyric_lines[number]
                display.append(
                    ("▶ " if number == index else "  ") + (line.text or "♪") + "\n",
                    style="bold" if number == index else "dim",
                )
            try:
                self.query_one("#lyrics", Static).update(display)
            except Exception:
                pass
        elif self.lyrics and self.lyrics.instrumental:
            try:
                self.query_one("#lyrics", Static).update(Text("Instrumental track"))
            except Exception:
                pass
        elif self.lyrics and self.lyrics.plain:
            try:
                self.query_one("#lyrics", Static).update(Text(self.lyrics.plain))
            except Exception:
                pass
        else:
            try:
                self.query_one("#lyrics", Static).update(Text("No lyrics found for this track."))
            except Exception:
                pass

    @work(group="poll", exclusive=True)
    async def poll_player(self) -> None:
        if self._loading or self.current_track is None or not self.current_track.playable:
            return
        async with self._play_lock:
            if self._loading or self.current_track is None or not self.current_track.playable:
                return
            generation = self._generation
            track = self.current_track
            try:
                state = await self.player.snapshot()
            except Exception as exc:
                if generation == self._generation and self.current_track is track:
                    self._error("Playback", exc)
                return
            if generation != self._generation or self.current_track is not track:
                return
            self.playback = state
            if state.ended:
                if self.queue:
                    self._request_track(self.queue[0], queue_item=self.queue[0])
                else:
                    self.current_track = None
                    self._status("Finished. Queue is empty.")
                return
            self._update_playback()
            self._update_lyrics()

    def action_next_track(self) -> None:
        if self.queue:
            self._request_track(self.queue[0], queue_item=self.queue[0])
        else:
            self.notify("Queue is empty.", severity="information")

    def action_pause(self) -> None:
        if self._browser_controls():
            return
        self._transport("pause", generation=self._generation)

    def action_stop(self) -> None:
        if self._browser_controls():
            return
        if self.current_track is None and not self._loading:
            return
        self._generation += 1
        self._loading = True
        self.current_track = None
        self._transport("stop", generation=self._generation)

    def action_seek_back(self) -> None:
        if self._browser_controls():
            return
        self._transport("seek", -5, self._generation)

    def action_seek_forward(self) -> None:
        if self._browser_controls():
            return
        self._transport("seek", 5, self._generation)

    def action_volume_up(self) -> None:
        if self._browser_controls():
            return
        self._transport("volume", 5, self._generation)

    def action_volume_down(self) -> None:
        if self._browser_controls():
            return
        self._transport("volume", -5, self._generation)

    def _browser_controls(self) -> bool:
        return False

    @work(group="transport", exclusive=False)
    async def _transport(self, operation: str, amount: float = 0, generation: int = 0) -> None:
        if operation != "stop" and (self.current_track is None or self._loading):
            return
        async with self._play_lock:
            if generation != self._generation:
                return
            try:
                if operation == "pause":
                    await self.player.toggle_pause()
                elif operation == "stop":
                    await self.player.stop()
                    self._mpv_loaded = False
                    self.playback = PlaybackState()
                    self.lyrics = None
                    self.lyric_lines = []
                    self.query_one("#lyrics", Static).update(
                        Text("Lyrics appear here when a track plays.")
                    )
                    self._status("Stopped")
                else:
                    state = await self.player.snapshot()
                    if operation == "seek":
                        await self.player.seek(
                            min(state.duration or float("inf"), max(0, state.position + amount))
                        )
                    else:
                        await self.player.set_volume(state.volume + amount)
                if operation != "stop":
                    self.playback = await self.player.snapshot()
                    self._update_playback()
                    self._update_lyrics()
            except Exception as exc:
                self._error("Playback", exc)
            finally:
                if operation == "stop" and generation == self._generation:
                    self._loading = False

    def action_delay_back(self) -> None:
        self._change_delay(-0.25)

    def action_delay_forward(self) -> None:
        self._change_delay(0.25)

    def _change_delay(self, amount: float) -> None:
        if self.current_track is None:
            return
        self.lyric_delay = round(self.lyric_delay + amount, 2)
        self.database.set_delay(self.current_track.id, self.lyric_delay)
        self._update_playback()
        self._update_lyrics()

    def action_reload_lyrics(self) -> None:
        if self.current_track is not None:
            self._choose_external_lyrics(self.current_track, self._generation)

    @work(group="karaoke_prompt", exclusive=True)
    async def action_karaoke(self) -> None:
        track = self.current_track
        if track is None:
            return
        if self.using_stem:
            self._loading = True
            self._switch_audio(track.location, self._generation, False)
            return
        if not track.is_local:
            self.notify("Karaoke requires a local track.", severity="warning")
            return
        if self._karaoke_pending:
            return
        self._karaoke_pending = True
        generation = self._generation
        try:
            if await self.push_screen_wait(RightsScreen()):
                self._prepare_karaoke(track, generation)
            else:
                self._karaoke_pending = False
        except Exception as exc:
            self._karaoke_pending = False
            self._error("Karaoke", exc)

    @work(group="karaoke", exclusive=True)
    async def _prepare_karaoke(self, track: Track, generation: int) -> None:
        try:
            if generation != self._generation or self.current_track != track:
                return
            self._status("Separating vocals… playback continues.")
            stem = await self.separator.prepare(track, rights_confirmed=True)
            if generation != self._generation or self.current_track != track:
                return
            self.stem = stem
            self._loading = True
            self._switch_audio(str(stem), generation, True)
        except Exception as exc:
            if generation == self._generation:
                self._error("Karaoke", exc)
        finally:
            self._karaoke_pending = False

    @work(group="playback", exclusive=False)
    async def _switch_audio(self, location: str, generation: int, karaoke: bool) -> None:
        async with self._play_lock:
            if generation != self._generation or self.current_track is None:
                return
            try:
                state = await self.player.snapshot()
                if generation != self._generation:
                    return
                await self.player.load(location, start=state.position, paused=state.paused)
                if generation == self._generation:
                    self.using_stem = karaoke
                    self.playback = state
                    self._update_playback()
            except Exception as exc:
                if generation == self._generation:
                    self._error("Karaoke", exc)
            finally:
                if generation == self._generation:
                    self._loading = False

    async def close(self) -> None:
        if self._resources_closed:
            return
        self._resources_closed = True
        workers = list(self.workers)
        self.workers.cancel_all()
        await asyncio.gather(*(worker.wait() for worker in workers), return_exceptions=True)
        closers = [self.separator.close(), self.lyrics_service.close(), self.player.close()]
        closers.extend(
            provider.close() for provider in self.providers.values() if hasattr(provider, "close")
        )
        for result in await asyncio.gather(*closers, return_exceptions=True):
            if isinstance(result, BaseException):
                LOG.warning("Service close failed (%s)", type(result).__name__)
        try:
            self.database.close()
        except Exception as exc:
            LOG.warning("Database close failed (%s)", type(exc).__name__)

    async def action_quit(self) -> None:
        await self.close()
        self.exit()

