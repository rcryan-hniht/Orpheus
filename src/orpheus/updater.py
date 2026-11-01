"""Automatic update and version checking mechanism for Orpheus."""

import asyncio
import logging
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING

import httpx

if TYPE_CHECKING:
    from .storage import Database

LOG = logging.getLogger("orpheus.updater")

GITHUB_REPO = "rcryan-hniht/Orpheus"
COMMITS_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/commits/main"
UPDATE_CHECK_INTERVAL_SECONDS = 6 * 3600  # Check at most once every 6 hours in the background


def find_repo_dir() -> Path | None:
    """Find the root of the Orpheus Git repository if installed via git."""
    candidates = [
        Path(__file__).resolve().parents[2],
        Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "orpheus/app",
        Path.cwd(),
    ]
    for candidate in candidates:
        if (candidate / ".git").is_dir() and (candidate / "pyproject.toml").is_file():
            try:
                content = (candidate / "pyproject.toml").read_text(encoding="utf-8")
                if 'name = "orpheus"' in content:
                    return candidate
            except OSError:
                continue
    return None


def get_local_commit(repo_dir: Path | None = None) -> str | None:
    """Get the current local git commit hash, if available."""
    target_dir = repo_dir or find_repo_dir()
    if not target_dir or not shutil.which("git"):
        return None
    try:
        result = subprocess.run(
            ["git", "-C", str(target_dir), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        pass
    return None


def get_remote_commit(client: httpx.Client | None = None) -> tuple[str, str] | None:
    """Fetch the latest commit hash and summary from GitHub main branch."""
    headers = {
        "User-Agent": "Orpheus-Updater/0.1.0",
        "Accept": "application/vnd.github.v3+json",
    }
    close_client = False
    if client is None:
        client = httpx.Client(timeout=10, headers=headers)
        close_client = True
    try:
        response = client.get(COMMITS_API_URL)
        if response.status_code == 200:
            data = response.json()
            sha = data.get("sha", "")
            message = data.get("commit", {}).get("message", "").splitlines()[0]
            if sha:
                return sha, message
    except Exception as exc:
        LOG.debug("Failed to fetch latest commit from GitHub: %s", exc)
    finally:
        if close_client:
            client.close()
    return None


async def get_remote_commit_async(
    client: httpx.AsyncClient | None = None,
) -> tuple[str, str] | None:
    """Async variant to fetch the latest commit hash from GitHub."""
    headers = {
        "User-Agent": "Orpheus-Updater/0.1.0",
        "Accept": "application/vnd.github.v3+json",
    }
    close_client = False
    if client is None:
        client = httpx.AsyncClient(timeout=10, headers=headers)
        close_client = True
    try:
        response = await client.get(COMMITS_API_URL)
        if response.status_code == 200:
            data = response.json()
            sha = data.get("sha", "")
            message = data.get("commit", {}).get("message", "").splitlines()[0]
            if sha:
                return sha, message
    except Exception as exc:
        LOG.debug("Async update check failed: %s", exc)
    finally:
        if close_client:
            await client.aclose()
    return None


def perform_update(repo_dir: Path | None = None) -> tuple[bool, str]:
    """Pull the latest code and reinstall the package. Returns (success, message)."""
    target_dir = repo_dir or find_repo_dir()

    if target_dir and (target_dir / ".git").is_dir() and shutil.which("git"):
        # Check for uncommitted local changes
        status = subprocess.run(
            ["git", "-C", str(target_dir), "status", "--porcelain"],
            capture_output=True,
            text=True,
            check=False,
        )
        if status.stdout.strip():
            return False, "Cannot auto-update: repository has uncommitted local modifications."

        # Pull or fetch & reset
        pull = subprocess.run(
            ["git", "-C", str(target_dir), "pull", "--ff-only", "origin", "main"],
            capture_output=True,
            text=True,
            check=False,
        )
        if pull.returncode != 0:
            fetch = subprocess.run(
                ["git", "-C", str(target_dir), "fetch", "--depth=1", "origin", "main"],
                capture_output=True,
                text=True,
                check=False,
            )
            reset = subprocess.run(
                ["git", "-C", str(target_dir), "reset", "--hard", "origin/main"],
                capture_output=True,
                text=True,
                check=False,
            )
            if fetch.returncode != 0 or reset.returncode != 0:
                return False, f"Git update failed: {pull.stderr.strip() or reset.stderr.strip()}"

        # Reinstall package in current python environment
        pip_cmd = [sys.executable, "-m", "pip", "install", str(target_dir), "--quiet"]
        pip_run = subprocess.run(pip_cmd, capture_output=True, text=True, check=False)
        if pip_run.returncode != 0:
            return False, f"Pip installation failed: {pip_run.stderr.strip()}"

        new_sha = get_local_commit(target_dir) or "latest"
        return True, f"Successfully updated Orpheus to commit {new_sha[:7]}."

    # Fallback: pip install directly from GitHub repository
    pip_cmd = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--upgrade",
        f"git+https://github.com/{GITHUB_REPO}.git",
        "--quiet",
    ]
    pip_run = subprocess.run(pip_cmd, capture_output=True, text=True, check=False)
    if pip_run.returncode == 0:
        return True, "Successfully upgraded Orpheus to the latest version via pip."
    return False, f"Update failed: {pip_run.stderr.strip() or 'Unknown error'}"


def run_cli_update() -> int:
    """Entry point for the `--update` CLI flag."""
    print("Checking for updates from GitHub...")
    repo_dir = find_repo_dir()
    local_sha = get_local_commit(repo_dir)

    remote = get_remote_commit()
    if remote is None:
        print("❌ Could not connect to GitHub. Please check your internet connection.")
        return 1

    remote_sha, remote_msg = remote
    if local_sha and local_sha == remote_sha:
        print(f"✨ Orpheus is already up to date (commit {local_sha[:7]}).")
        return 0

    print(f"📦 New version found: {remote_sha[:7]} - {remote_msg}")
    print("⬇️  Downloading and applying update...")
    success, message = perform_update(repo_dir)
    if success:
        print(f"✨ {message}")
        print("🚀 You can now restart Orpheus to use the latest version.")
        return 0
    else:
        print(f"❌ {message}")
        return 1


async def async_check_and_update(
    db: "Database | None" = None,
    auto_apply: bool = True,
    force: bool = False,
) -> tuple[bool, str | None]:
    """Background check for updates in Textual app.

    Returns (has_update_or_updated, notification_message).
    """
    now = time.time()
    if db is not None and not force:
        last_check_str = db.get_setting("last_update_check")
        if last_check_str:
            try:
                last_check = float(last_check_str)
                if now - last_check < UPDATE_CHECK_INTERVAL_SECONDS:
                    return False, None
            except ValueError:
                pass

    remote = await get_remote_commit_async()
    if remote is None:
        return False, None

    remote_sha, _ = remote
    repo_dir = find_repo_dir()
    local_sha = get_local_commit(repo_dir)

    if db is not None:
        db.set_setting("last_update_check", str(now))

    if local_sha and local_sha == remote_sha:
        return False, None

    if auto_apply:
        success, message = await asyncio.to_thread(perform_update, repo_dir)
        if success:
            return True, f"Orpheus updated to {remote_sha[:7]}! Restart app to apply."
        return True, f"New version available ({remote_sha[:7]}). Run 'orpheus --update' to apply."

    return True, f"New version available ({remote_sha[:7]}). Run 'orpheus --update' to apply."
