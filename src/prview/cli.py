"""Command-line interface for prview.

Uses os.dup2 to restore fd 0 to /dev/tty after reading piped stdin,
so that Textual can interact with the terminal normally.
"""

from __future__ import annotations

import argparse
import os
import sys


def _read_piped_stdin() -> str | None:
    """Read diff text from piped stdin if available, then restore tty on fd 0.

    Returns the piped text, or None if stdin is a terminal (no pipe).
    If stdin is piped, we must restore fd 0 to /dev/tty so Textual
    can read keyboard input. See spike/FINDINGS.md for details.
    """
    if sys.stdin.isatty():
        return None

    # Check if there's actually piped data (stdin might just not be a tty
    # in environments like CI or IDE terminals)
    import select
    if not select.select([sys.stdin], [], [], 0.0)[0]:
        # No data waiting on stdin — treat as non-piped
        return None

    diff_text = sys.stdin.buffer.read().decode()

    # Restore fd 0 to /dev/tty so Textual can use the terminal
    try:
        tty_fd = os.open("/dev/tty", os.O_RDONLY)
        os.dup2(tty_fd, 0)
        os.close(tty_fd)
        sys.stdin.close()
        sys.stdin = os.fdopen(0, "r")
    except OSError:
        # /dev/tty not available (e.g. CI, containers) — Textual may not
        # work interactively, but at least we won't crash here
        pass

    return diff_text


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="prview",
        description="Interactive terminal diff browser",
    )
    parser.add_argument(
        "range",
        nargs="?",
        default=None,
        help="Git revision range (e.g. HEAD~3, main..feature)",
    )
    parser.add_argument(
        "--staged",
        action="store_true",
        help="Show staged (cached) changes",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    # Step 1: Handle piped stdin BEFORE importing Textual
    diff_text = _read_piped_stdin()

    args = _parse_args(argv)

    # Step 2: Get diff text from git if nothing was piped
    if diff_text is None:
        from prview.git import get_diff, get_staged_diff

        if args.staged:
            diff_text = get_staged_diff()
        elif args.range:
            diff_text = get_diff([args.range])
        else:
            diff_text = get_diff()

    # Step 3: Parse and launch
    from prview.diff_parser import parse
    from prview.state import ReviewState
    from prview.app import DiffnavApp

    diff_data = parse(diff_text)
    if not diff_data.files:
        print("No changes to display.")
        return

    review_state = ReviewState()
    app = DiffnavApp(diff_data, review_state)
    app.run()
