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


@pytest.fixture
def scrollable_diff_data() -> DiffData:
    """DiffData with enough lines per file to make scrolling testable.

    Contains 4 files, each with multiple hunks and 30+ lines so that
    scroll operations (j/k, Ctrl+D/U, G) produce measurable offset changes.
    """

    def _make_lines(count: int, start: int = 1) -> list[DiffLine]:
        lines: list[DiffLine] = []
        for i in range(count):
            lineno = start + i
            lines.append(
                DiffLine(
                    type="context",
                    content=f"line {lineno} of code here with some padding text",
                    old_lineno=lineno,
                    new_lineno=lineno,
                )
            )
        return lines

    def _make_mixed_hunk(header: str, ctx: int, adds: int, removes: int, start: int = 1) -> DiffHunk:
        lines: list[DiffLine] = []
        lineno = start
        for i in range(ctx):
            lines.append(DiffLine(type="context", content=f"context line {lineno}", old_lineno=lineno, new_lineno=lineno))
            lineno += 1
        for i in range(removes):
            lines.append(DiffLine(type="remove", content=f"removed line {lineno}", old_lineno=lineno, new_lineno=None))
            lineno += 1
        new_lineno = lineno
        for i in range(adds):
            lines.append(DiffLine(type="add", content=f"added line {new_lineno}", old_lineno=None, new_lineno=new_lineno))
            new_lineno += 1
        return DiffHunk(header=header, lines=lines)

    return DiffData(
        files=[
            DiffFile(
                path="src/alpha.py",
                old_path=None,
                status="modified",
                hunks=[
                    DiffHunk(header="@@ -1,20 +1,20 @@", lines=_make_lines(20, start=1)),
                    _make_mixed_hunk("@@ -25,15 +25,18 @@", ctx=5, adds=8, removes=3, start=25),
                ],
                added_lines=8,
                removed_lines=3,
            ),
            DiffFile(
                path="src/beta.py",
                old_path=None,
                status="added",
                hunks=[
                    DiffHunk(
                        header="@@ -0,0 +1,40 @@",
                        lines=[
                            DiffLine(type="add", content=f"new line {i}", old_lineno=None, new_lineno=i)
                            for i in range(1, 41)
                        ],
                    ),
                ],
                added_lines=40,
                removed_lines=0,
            ),
            DiffFile(
                path="src/gamma.py",
                old_path=None,
                status="modified",
                hunks=[
                    _make_mixed_hunk("@@ -1,10 +1,12 @@", ctx=4, adds=6, removes=2, start=1),
                    _make_mixed_hunk("@@ -50,10 +52,14 @@", ctx=3, adds=8, removes=2, start=50),
                    DiffHunk(header="@@ -80,5 +84,5 @@", lines=_make_lines(10, start=80)),
                ],
                added_lines=14,
                removed_lines=4,
            ),
            DiffFile(
                path="src/delta.py",
                old_path="src/old_delta.py",
                status="renamed",
                hunks=[
                    DiffHunk(header="@@ -1,30 +1,35 @@", lines=_make_lines(30, start=1)),
                    _make_mixed_hunk("@@ -35,5 +40,10 @@", ctx=3, adds=5, removes=2, start=35),
                ],
                added_lines=5,
                removed_lines=2,
            ),
        ],
        base_ref="abc123",
        head_ref="def456",
    )
