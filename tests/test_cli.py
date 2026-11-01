import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_cli(*arguments):
    return subprocess.run(
        [sys.executable, "-m", "orpheus", *arguments],
        cwd=ROOT,
        env={**os.environ, "PYTHONPATH": str(ROOT / "src")},
        capture_output=True,
        text=True,
        check=False,
    )


def test_help_works_without_loading_textual():
    result = run_cli("--help")
    assert result.returncode == 0
    assert "--music-dir" in result.stdout
    assert "--youtube" in result.stdout
    assert "--theme" in result.stdout
    assert "--update" in result.stdout
    assert "--version" in result.stdout

    result_short = run_cli("-h")
    assert result_short.returncode == 0
    assert "--music-dir" in result_short.stdout


def test_version_flag():
    result = run_cli("--version")
    assert result.returncode == 0
    assert "0.1.0" in result.stdout or "0.1.0" in result.stderr

    result_v = run_cli("-v")
    assert result_v.returncode == 0
    assert "0.1.0" in result_v.stdout or "0.1.0" in result_v.stderr


def test_theme_flag_rejects_unknown_preset(tmp_path):
    result = run_cli("--music-dir", str(tmp_path), "--theme", "unknown")
    assert result.returncode != 0
    assert "invalid choice" in result.stderr
    assert "github-light-contrast" in result.stderr


def test_explicit_missing_music_directory_is_explained(tmp_path):
    result = run_cli("--music-dir", str(tmp_path / "missing"))
    assert result.returncode != 0
    assert "music directory" in result.stderr.lower()


def test_youtube_requires_api_key(tmp_path, monkeypatch):
    monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
    result = run_cli("--music-dir", str(tmp_path), "--youtube")
    assert result.returncode != 0
    assert "YOUTUBE_API_KEY" in result.stderr
