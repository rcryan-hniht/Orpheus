from __future__ import annotations

import logging
import os
import shutil
import subprocess
import tempfile
import threading

logger = logging.getLogger(__name__)


class CavaReader:
    """Reads real-time audio FFT spectrum data directly from the system cava daemon."""

    def __init__(self, num_bars: int = 32, framerate: int = 60, sensitivity: int = 150) -> None:
        self.num_bars = num_bars
        self.framerate = framerate
        self.sensitivity = sensitivity
        self.available = bool(shutil.which("cava"))
        self._proc: subprocess.Popen[bytes] | None = None
        self._conf_path: str | None = None
        self._thread: threading.Thread | None = None
        self._running = False
        self._lock = threading.Lock()
        self._latest_bars: list[float] = [0.0] * num_bars

    @property
    def is_running(self) -> bool:
        with self._lock:
            return self._running and self._proc is not None and self._proc.poll() is None

    def start(self) -> bool:
        """Start cava subprocess and begin reading raw 8-bit frequency bar magnitudes."""
        if not self.available:
            return False

        with self._lock:
            if self._proc is not None and self._proc.poll() is None:
                # Already running
                return True

        # Stop any dead process first
        self.stop()

        # Build cava config using pulse audio capture (PipeWire / PulseAudio monitor)
        conf_content = (
            f"[general]\n"
            f"framerate = {self.framerate}\n"
            f"bars = {self.num_bars}\n"
            f"autosens = 1\n"
            f"sensitivity = {self.sensitivity}\n"
            f"lower_cutoff_freq = 50\n"
            f"higher_cutoff_freq = 10000\n\n"
            f"[input]\n"
            f"method = pulse\n"
            f"source = auto\n\n"
            f"[output]\n"
            f"method = raw\n"
            f"raw_target = /dev/stdout\n"
            f"data_format = binary\n"
            f"bit_format = 8bit\n"
            f"channels = mono\n"
            f"mono_option = average\n\n"
            f"[smoothing]\n"
            f"monstercat = 1\n"
            f"waves = 0\n"
            f"noise_reduction = 75\n"
        )

        try:
            with tempfile.NamedTemporaryFile("w", delete=False) as f:
                f.write(conf_content)
                conf_path = f.name

            proc = subprocess.Popen(
                ["cava", "-p", conf_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
            )
            with self._lock:
                self._conf_path = conf_path
                self._proc = proc
                self._running = True

            self._thread = threading.Thread(target=self._read_loop, daemon=True)
            self._thread.start()
            return True
        except Exception as exc:
            logger.warning("Failed to start cava subprocess: %s", exc)
            self.stop()
            return False

    def _read_loop(self) -> None:
        """Continuously reads num_bars bytes per frame from cava stdout using a byte buffer."""
        buf = bytearray()
        while self._running:
            proc = self._proc
            if not proc or not proc.stdout:
                break
            try:
                chunk = proc.stdout.read(self.num_bars)
                if not chunk:
                    break
                buf.extend(chunk)
                while len(buf) >= self.num_bars:
                    frame = buf[: self.num_bars]
                    buf = buf[self.num_bars :]
                    # Each byte is an unsigned 8-bit integer 0..255 representing FFT bar height
                    bars = [b / 255.0 for b in frame]
                    with self._lock:
                        self._latest_bars = bars
            except Exception:
                break
        self._running = False

    def get_bars(self) -> list[float]:
        """Return a copy of the latest normalized frequency magnitudes (each 0.0 to 1.0)."""
        with self._lock:
            return list(self._latest_bars)

    def set_bars(self, bars: list[float]) -> None:
        """Manually override bar values (useful for tests and visual mock previews)."""
        with self._lock:
            if len(bars) >= self.num_bars:
                self._latest_bars = list(bars[: self.num_bars])
            else:
                self._latest_bars = list(bars) + [0.0] * (self.num_bars - len(bars))

    def stop(self) -> None:
        """Gracefully stop cava process and clean up temporary configuration files."""
        self._running = False
        with self._lock:
            proc = self._proc
            self._proc = None
            conf_path = self._conf_path
            self._conf_path = None

        if proc:
            try:
                proc.terminate()
                proc.wait(timeout=0.3)
            except Exception:
                try:
                    proc.kill()
                    proc.wait(timeout=0.2)
                except Exception:
                    pass

        if conf_path and os.path.exists(conf_path):
            try:
                os.remove(conf_path)
            except Exception:
                pass

    def __del__(self) -> None:
        self.stop()
