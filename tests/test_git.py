from unittest.mock import patch, MagicMock
import pytest

from prview.git import get_diff, get_staged_diff, get_repo_root, get_pr_diff, GitError


def _mock_result(stdout="", stderr="", returncode=0):
    mock = MagicMock()
    mock.stdout = stdout
    mock.stderr = stderr
    mock.returncode = returncode
    return mock


@patch("prview.git.subprocess.run")
def test_get_diff_no_args(mock_run):
    mock_run.return_value = _mock_result(stdout="diff output\n")
    result = get_diff()
    mock_run.assert_called_once_with(["git", "diff"], capture_output=True, text=True)
    assert result == "diff output"


@patch("prview.git.subprocess.run")
def test_get_diff_with_args(mock_run):
    mock_run.return_value = _mock_result(stdout="diff output\n")
    result = get_diff(["main..feature"])
    mock_run.assert_called_once_with(
        ["git", "diff", "main..feature"], capture_output=True, text=True
    )
    assert result == "diff output"


@patch("prview.git.subprocess.run")
def test_get_diff_error(mock_run):
    mock_run.return_value = _mock_result(stderr="fatal: bad revision", returncode=1)
    with pytest.raises(GitError, match="fatal: bad revision"):
        get_diff(["bad..ref"])


@patch("prview.git.subprocess.run")
def test_get_staged_diff(mock_run):
    mock_run.return_value = _mock_result(stdout="staged diff\n")
    result = get_staged_diff()
    mock_run.assert_called_once_with(
        ["git", "diff", "--cached"], capture_output=True, text=True
    )
    assert result == "staged diff"


@patch("prview.git.subprocess.run")
def test_get_repo_root_success(mock_run):
    mock_run.return_value = _mock_result(stdout="/home/user/repo\n")
    result = get_repo_root()
    assert result == "/home/user/repo"


@patch("prview.git.subprocess.run")
def test_get_repo_root_not_repo(mock_run):
    mock_run.return_value = _mock_result(
        stderr="fatal: not a git repository", returncode=128
    )
    result = get_repo_root()
    assert result is None


@patch("prview.git.subprocess.run")
def test_get_pr_diff(mock_run):
    mock_run.return_value = _mock_result(stdout="pr diff content\n")
    result = get_pr_diff(123)
    mock_run.assert_called_once_with(
        ["gh", "pr", "diff", "123"], capture_output=True, text=True
    )
    assert result == "pr diff content"
