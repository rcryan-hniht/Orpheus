import asyncio
from unittest.mock import MagicMock, patch

import httpx

from orpheus.storage import Database
from orpheus.updater import (
    async_check_and_update,
    find_repo_dir,
    get_local_commit,
    get_remote_commit,
    get_remote_commit_async,
    perform_update,
)


def test_find_repo_dir():
    repo_dir = find_repo_dir()
    assert repo_dir is not None
    assert (repo_dir / "pyproject.toml").is_file()


def test_get_local_commit():
    commit = get_local_commit()
    assert commit is not None
    assert len(commit) == 40


def test_get_remote_commit_success():
    fake_response = MagicMock()
    fake_response.status_code = 200
    fake_response.json.return_value = {
        "sha": "1234567890abcdef1234567890abcdef12345678",
        "commit": {"message": "feat: new cool feature\n\nDetailed description"},
    }
    client = MagicMock(spec=httpx.Client)
    client.get.return_value = fake_response

    result = get_remote_commit(client)
    assert result == ("1234567890abcdef1234567890abcdef12345678", "feat: new cool feature")


def test_get_remote_commit_failure():
    client = MagicMock(spec=httpx.Client)
    client.get.side_effect = httpx.ConnectError("Network offline")

    result = get_remote_commit(client)
    assert result is None


def test_get_remote_commit_async_success():
    async def run():
        fake_response = MagicMock()
        fake_response.status_code = 200
        fake_response.json.return_value = {
            "sha": "abcdef1234567890abcdef1234567890abcdef12",
            "commit": {"message": "fix: resolve bug"},
        }
        client = MagicMock(spec=httpx.AsyncClient)
        client.get = MagicMock(return_value=fake_response)

        async def fake_get(*args, **kwargs):
            return fake_response

        client.get = fake_get

        result = await get_remote_commit_async(client)
        assert result == ("abcdef1234567890abcdef1234567890abcdef12", "fix: resolve bug")

    asyncio.run(run())


def test_perform_update_rejects_dirty_repo(tmp_path):
    # Create fake git repo with uncommitted file
    fake_git = tmp_path / ".git"
    fake_git.mkdir()
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text('name = "orpheus"')

    with patch("subprocess.run") as mock_run:
        status_mock = MagicMock()
        status_mock.stdout = " M modified_file.py\n"
        mock_run.return_value = status_mock

        success, msg = perform_update(tmp_path)
        assert not success
        assert "uncommitted" in msg.lower()


def test_async_check_and_update_respects_interval(tmp_path):
    async def run():
        db = Database(tmp_path / "test.sqlite")
        db.set_setting("last_update_check", str(10000000000.0))  # Far future

        updated, message = await async_check_and_update(db, auto_apply=False)
        assert not updated
        assert message is None
        db.close()

    asyncio.run(run())
