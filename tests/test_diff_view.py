"""Tests for the DiffView widget."""

from __future__ import annotations

import asyncio

from textual.app import App, ComposeResult
from textual.widgets import Static

from prview.models import DiffData, DiffFile, DiffLine
from prview.widgets.diff_view import DiffView


class DiffViewTestApp(App):
    def compose(self) -> ComposeResult:
        yield DiffView()


def test_show_file_renders(sample_diff_data: DiffData) -> None:
    """show_file() should populate the view with non-empty content."""
    diff_file = sample_diff_data.files[1]

    async def run() -> None:
        async with DiffViewTestApp().run_test() as pilot:
            diff_view = pilot.app.query_one(DiffView)
            diff_view.show_file(diff_file)
            await pilot.pause()
            statics = diff_view.query(Static)
            assert len(statics) > 0

    asyncio.run(run())


def test_hunk_header_present(sample_diff_data: DiffData) -> None:
    """Hunk header text should appear in the built content."""
    diff_file = sample_diff_data.files[1]
    content = DiffView._build_content(diff_file)
    plain = content.plain
    assert "@@ -10,7 +10,7 @@ class Foo:" in plain
    assert "@@ -25,6 +25,8 @@ class Foo:" in plain


def test_line_numbers(sample_diff_data: DiffData) -> None:
    """Line numbers should render correctly for context, add, and remove lines."""
    diff_file = sample_diff_data.files[1]
    content = DiffView._build_content(diff_file)
    plain = content.plain

    # Context line: both line numbers present
    assert "   10 |    10 |" in plain
    # Remove line: old lineno present, new lineno blank
    assert "   11 |       | -" in plain
    # Add line: old lineno blank, new lineno present
    assert "      |    11 | +" in plain


def test_clear(sample_diff_data: DiffData) -> None:
    """clear() should empty the view."""
    diff_file = sample_diff_data.files[0]

    async def run() -> None:
        async with DiffViewTestApp().run_test() as pilot:
            diff_view = pilot.app.query_one(DiffView)
            diff_view.show_file(diff_file)
            await pilot.pause()
            assert len(diff_view.query(Static)) > 0

            diff_view.clear()
            await pilot.pause()
            assert len(diff_view.query(Static)) == 0

    asyncio.run(run())


def test_color_coding() -> None:
    """Added lines should have green style, removed lines red style."""
    add_line = DiffLine(type="add", content="new code", old_lineno=None, new_lineno=5)
    remove_line = DiffLine(type="remove", content="old code", old_lineno=5, new_lineno=None)
    context_line = DiffLine(type="context", content="unchanged", old_lineno=5, new_lineno=5)

    add_text = DiffView._render_line(add_line)
    remove_text = DiffView._render_line(remove_line)
    context_text = DiffView._render_line(context_line)

    assert "green" in str(add_text.style)
    assert "red" in str(remove_text.style)
    assert "green" not in str(context_text.style or "")
