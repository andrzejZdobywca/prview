import subprocess
from pathlib import Path


class GitError(Exception):
    """Raised when a git command fails."""
    pass


def get_diff(args: list[str] | None = None) -> str:
    """Run `git diff` with optional args, return raw diff text."""
    cmd = ["git", "diff"]
    if args:
        cmd.extend(args)
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise GitError(result.stderr.strip())
    return result.stdout.strip()


def get_staged_diff() -> str:
    """Return diff of staged changes. Shorthand for get_diff(["--cached"])."""
    return get_diff(["--cached"])


def get_repo_root() -> str | None:
    """Return the git repo root path, or None if not in a repo."""
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def get_pr_diff(pr_number: int) -> str:
    """Fetch PR diff via `gh pr diff`. Raises GitError if gh CLI not available."""
    result = subprocess.run(
        ["gh", "pr", "diff", str(pr_number)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise GitError(result.stderr.strip())
    return result.stdout.strip()


def get_current_branch() -> str | None:
    """Return the current branch name, or None if detached HEAD."""
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    branch = result.stdout.strip()
    return None if branch == "HEAD" else branch
