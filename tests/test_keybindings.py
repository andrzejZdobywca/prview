"""Tests for the new keybinding scheme.

Expected behavior after the feature is implemented:
- Arrow Up/Down always navigate the file list (global, focus-independent)
- Vim keys (j/k/G/Ctrl+D/Ctrl+U) control the diff view scroll
- DiffView gets auto-focused on mount so vim keys work immediately
- n/p file navigation continues to work
"""

from __future__ import annotations

import asyncio

import pytest

from prview.models import DiffData
from tests.user_simulator import UserSimulator


# ======================================================================
# Arrow key file navigation (global)
# ======================================================================


def test_arrow_down_navigates_to_next_file(scrollable_diff_data: DiffData) -> None:
    """Arrow Down should move the file list cursor to the next file."""

    async def run() -> None:
        async with UserSimulator.from_diff_data(scrollable_diff_data) as sim:
            initial_file = sim.get_current_file()
            assert initial_file == "src/alpha.py", "First file should be selected on startup"

            await sim.navigate_file_down()
            assert sim.get_current_file() == "src/beta.py"

    asyncio.run(run())


def test_arrow_up_navigates_to_previous_file(scrollable_diff_data: DiffData) -> None:
    """Arrow Up should move the file list cursor to the previous file."""

    async def run() -> None:
        async with UserSimulator.from_diff_data(scrollable_diff_data) as sim:
            # Move down first, then back up
            await sim.navigate_file_down()
            assert sim.get_current_file() == "src/beta.py"

            await sim.navigate_file_up()
            assert sim.get_current_file() == "src/alpha.py"

    asyncio.run(run())


def test_arrow_navigation_wraps_or_stops_at_boundaries(scrollable_diff_data: DiffData) -> None:
    """Arrow keys should stop (not wrap) at the first and last file."""

    async def run() -> None:
        async with UserSimulator.from_diff_data(scrollable_diff_data) as sim:
            # At the top already — pressing up should stay on the first file
            await sim.navigate_file_up()
            assert sim.get_current_file() == "src/alpha.py"

            # Navigate to the last file
            for _ in range(sim.get_file_count() - 1):
                await sim.navigate_file_down()
            assert sim.get_current_file() == "src/delta.py"

            # Pressing down at the end should stay on the last file
            await sim.navigate_file_down()
            assert sim.get_current_file() == "src/delta.py"

    asyncio.run(run())


def test_arrow_keys_work_when_diff_focused(scrollable_diff_data: DiffData) -> None:
    """Arrow keys should still navigate the file list even when the DiffView has focus.

    This is the key behavioral change: arrow keys are global file-list
    navigation regardless of which widget currently has focus.
    """

    async def run() -> None:
        async with UserSimulator.from_diff_data(scrollable_diff_data) as sim:
            # After the feature, DiffView should have focus on start
            # (or we can explicitly focus it)
            focused = sim.get_focused_widget_id()
            # Ensure diff-view is focused (it should be auto-focused)
            if focused != "diff-view":
                await sim.toggle_focus()
            assert sim.get_focused_widget_id() == "diff-view"

            # Arrow Down should still navigate the file list
            initial_file = sim.get_current_file()
            await sim.navigate_file_down()
            new_file = sim.get_current_file()
            assert new_file != initial_file, (
                "Arrow Down should change the selected file even when DiffView is focused"
            )

    asyncio.run(run())


# ======================================================================
# Vim diff scrolling
# ======================================================================


def test_j_scrolls_diff_down(scrollable_diff_data: DiffData) -> None:
    """Pressing ``j`` should scroll the diff content downward."""

    async def run() -> None:
        async with UserSimulator.from_diff_data(scrollable_diff_data) as sim:
            initial_pos = sim.get_diff_scroll_position()
            await sim.scroll_diff_down()
            new_pos = sim.get_diff_scroll_position()
            assert new_pos > initial_pos, (
                f"j should scroll down: {initial_pos} -> {new_pos}"
            )

    asyncio.run(run())


def test_k_scrolls_diff_up(scrollable_diff_data: DiffData) -> None:
    """Pressing ``k`` should scroll the diff content upward."""

    async def run() -> None:
        async with UserSimulator.from_diff_data(scrollable_diff_data) as sim:
            # First scroll down so we have room to scroll up
            for _ in range(5):
                await sim.scroll_diff_down()
            pos_after_down = sim.get_diff_scroll_position()
            assert pos_after_down > 0, "Should have scrolled down first"

            await sim.scroll_diff_up()
            pos_after_up = sim.get_diff_scroll_position()
            assert pos_after_up < pos_after_down, (
                f"k should scroll up: {pos_after_down} -> {pos_after_up}"
            )

    asyncio.run(run())


def test_G_scrolls_to_bottom(scrollable_diff_data: DiffData) -> None:
    """Pressing ``G`` (Shift+G) should scroll the diff to the very bottom."""

    async def run() -> None:
        async with UserSimulator.from_diff_data(scrollable_diff_data) as sim:
            initial_pos = sim.get_diff_scroll_position()
            await sim.scroll_diff_to_bottom()
            bottom_pos = sim.get_diff_scroll_position()
            assert bottom_pos > initial_pos, (
                f"G should scroll to bottom: {initial_pos} -> {bottom_pos}"
            )
            # The position should be at or near max_scroll_y
            diff_view = sim._app.query_one("#diff-view")
            assert bottom_pos >= diff_view.max_scroll_y * 0.9, (
                "G should scroll to (near) the very bottom of the diff"
            )

    asyncio.run(run())


def test_ctrl_d_scrolls_half_page_down(scrollable_diff_data: DiffData) -> None:
    """Ctrl+D should scroll the diff down by approximately half a page."""

    async def run() -> None:
        async with UserSimulator.from_diff_data(scrollable_diff_data) as sim:
            initial_pos = sim.get_diff_scroll_position()
            await sim.scroll_diff_page_down()
            new_pos = sim.get_diff_scroll_position()
            assert new_pos > initial_pos, (
                f"Ctrl+D should scroll down: {initial_pos} -> {new_pos}"
            )
            # It should move more than a single line
            single_line_pos = initial_pos
            # A half-page scroll should move significantly more than j
            assert new_pos - initial_pos > 1, (
                "Ctrl+D should scroll more than a single line"
            )

    asyncio.run(run())


def test_ctrl_u_scrolls_half_page_up(scrollable_diff_data: DiffData) -> None:
    """Ctrl+U should scroll the diff up by approximately half a page."""

    async def run() -> None:
        async with UserSimulator.from_diff_data(scrollable_diff_data) as sim:
            # First scroll to the bottom so we have room
            await sim.scroll_diff_to_bottom()
            bottom_pos = sim.get_diff_scroll_position()
            assert bottom_pos > 0

            await sim.scroll_diff_page_up()
            new_pos = sim.get_diff_scroll_position()
            assert new_pos < bottom_pos, (
                f"Ctrl+U should scroll up: {bottom_pos} -> {new_pos}"
            )
            # Should move more than a single line
            assert bottom_pos - new_pos > 1, (
                "Ctrl+U should scroll more than a single line"
            )

    asyncio.run(run())


# ======================================================================
# Focus behavior
# ======================================================================


def test_diff_view_focused_on_start(scrollable_diff_data: DiffData) -> None:
    """DiffView should have focus automatically when the app starts.

    This ensures vim keys work immediately without the user pressing Tab.
    """

    async def run() -> None:
        async with UserSimulator.from_diff_data(scrollable_diff_data) as sim:
            assert sim.get_focused_widget_id() == "diff-view", (
                "DiffView should be auto-focused on mount"
            )

    asyncio.run(run())


def test_vim_keys_work_without_manual_focus(scrollable_diff_data: DiffData) -> None:
    """j/k should work immediately on startup without pressing Tab first.

    Since DiffView is auto-focused, vim keys should scroll the diff
    right away.
    """

    async def run() -> None:
        async with UserSimulator.from_diff_data(scrollable_diff_data) as sim:
            # Don't press Tab — just try scrolling immediately
            initial_pos = sim.get_diff_scroll_position()
            await sim.scroll_diff_down()
            assert sim.get_diff_scroll_position() > initial_pos, (
                "j should scroll the diff without needing to Tab-focus first"
            )

    asyncio.run(run())


# ======================================================================
# Integration
# ======================================================================


def test_navigate_file_then_scroll_diff(scrollable_diff_data: DiffData) -> None:
    """Arrow Down to change file, then j to scroll — both should work in sequence."""

    async def run() -> None:
        async with UserSimulator.from_diff_data(scrollable_diff_data) as sim:
            # Navigate to the second file
            await sim.navigate_file_down()
            assert sim.get_current_file() == "src/beta.py"

            # Now scroll the diff for that file
            initial_pos = sim.get_diff_scroll_position()
            await sim.scroll_diff_down()
            await sim.scroll_diff_down()
            new_pos = sim.get_diff_scroll_position()
            assert new_pos > initial_pos, (
                "j should scroll the diff after navigating to a new file with arrows"
            )

    asyncio.run(run())


def test_n_p_still_work(scrollable_diff_data: DiffData) -> None:
    """n/p file navigation should continue to work alongside arrow keys."""

    async def run() -> None:
        async with UserSimulator.from_diff_data(scrollable_diff_data) as sim:
            assert sim.get_current_file() == "src/alpha.py"

            await sim.next_file()
            assert sim.get_current_file() == "src/beta.py", "n should advance to next file"

            await sim.next_file()
            assert sim.get_current_file() == "src/gamma.py", "n should advance again"

            await sim.prev_file()
            assert sim.get_current_file() == "src/beta.py", "p should go back"

    asyncio.run(run())
