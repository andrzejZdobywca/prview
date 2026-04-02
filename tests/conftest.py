"""Shared pytest fixtures for prview tests."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from prview.models import DiffData, DiffFile, DiffHunk, DiffLine

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixtures_dir() -> Path:
    return FIXTURES_DIR


@pytest.fixture
def sample_diff_text(fixtures_dir: Path) -> str:
    """Raw text of the sample.diff fixture."""
    return (fixtures_dir / "sample.diff").read_text()


@pytest.fixture
def sample_diff_data() -> DiffData:
    """Hand-constructed DiffData for use in widget tests without depending on diff_parser."""
    return DiffData(
        files=[
            DiffFile(
                path="src/new_file.py",
                old_path=None,
                status="added",
                hunks=[
                    DiffHunk(
                        header="@@ -0,0 +1,3 @@",
                        lines=[
                            DiffLine(type="add", content="def hello():", old_lineno=None, new_lineno=1),
                            DiffLine(type="add", content='    return "hello"', old_lineno=None, new_lineno=2),
                            DiffLine(type="add", content="", old_lineno=None, new_lineno=3),
                        ],
                    )
                ],
                added_lines=3,
                removed_lines=0,
            ),
            DiffFile(
                path="src/existing.py",
                old_path=None,
                status="modified",
                hunks=[
                    DiffHunk(
                        header="@@ -10,7 +10,7 @@ class Foo:",
                        lines=[
                            DiffLine(type="context", content="    def bar(self):", old_lineno=10, new_lineno=10),
                            DiffLine(type="remove", content="        return 1", old_lineno=11, new_lineno=None),
                            DiffLine(type="add", content="        return 2", old_lineno=None, new_lineno=11),
                            DiffLine(type="context", content="", old_lineno=12, new_lineno=12),
                        ],
                    ),
                    DiffHunk(
                        header="@@ -25,6 +25,8 @@ class Foo:",
                        lines=[
                            DiffLine(type="context", content="    def baz(self):", old_lineno=25, new_lineno=25),
                            DiffLine(type="context", content="        pass", old_lineno=26, new_lineno=26),
                            DiffLine(type="add", content="", old_lineno=None, new_lineno=27),
                            DiffLine(type="add", content="    def qux(self):", old_lineno=None, new_lineno=28),
                        ],
                    ),
                ],
                added_lines=3,
                removed_lines=1,
            ),
            DiffFile(
                path="old_module.py",
                old_path=None,
                status="deleted",
                hunks=[
                    DiffHunk(
                        header="@@ -1,5 +0,0 @@",
                        lines=[
                            DiffLine(type="remove", content="# old module", old_lineno=1, new_lineno=None),
                            DiffLine(type="remove", content="def old_func():", old_lineno=2, new_lineno=None),
                            DiffLine(type="remove", content="    pass", old_lineno=3, new_lineno=None),
                        ],
                    )
                ],
                added_lines=0,
                removed_lines=3,
            ),
            DiffFile(
                path="src/renamed.py",
                old_path="src/old_name.py",
                status="renamed",
                hunks=[
                    DiffHunk(
                        header="@@ -1,3 +1,4 @@",
                        lines=[
                            DiffLine(type="context", content="def func():", old_lineno=1, new_lineno=1),
                            DiffLine(type="remove", content="    return 1", old_lineno=2, new_lineno=None),
                            DiffLine(type="add", content="    return 2", old_lineno=None, new_lineno=2),
                            DiffLine(type="add", content="", old_lineno=None, new_lineno=3),
                            DiffLine(type="context", content="", old_lineno=3, new_lineno=4),
                        ],
                    )
                ],
                added_lines=2,
                removed_lines=1,
            ),
        ],
        base_ref=None,
        head_ref=None,
    )
