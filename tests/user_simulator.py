"""UserSimulator — high-level test helper that wraps Textual's Pilot.

Provides ergonomic methods for simulating user interactions in prview tests.
"""

from __future__ import annotations

import contextlib
from typing import AsyncIterator

from textual.pilot import Pilot

from prview.app import DiffnavApp
from prview.models import DiffData
from prview.state import ReviewState
from prview.widgets.diff_view import DiffView
from prview.widgets.file_list import FileList, FileListItem


class UserSimulator:
    """High-level wrapper around a Textual Pilot for prview integration tests."""

    def __init__(self, app: DiffnavApp, pilot: Pilot) -> None:
        self.app = app
        self.pilot = pilot

    @classmethod
    @contextlib.asynccontextmanager
    async def from_diff_data(
        cls,
        diff_data: DiffData,
        *,
        state_dir: str | None = None,
    ) -> AsyncIterator[UserSimulator]:
        """Create a UserSimulator from DiffData.

        Usage::

            async with UserSimulator.from_diff_data(diff_data) as sim:
                await sim.navigate_file_down()
                assert sim.get_current_file() == "path/to/file.py"
        """
        import tempfile
        from pathlib import Path

        if state_dir is None:
            tmp = tempfile.mkdtemp()
            review_state = ReviewState(state_dir=Path(tmp) / ".prview")
        else:
            review_state = ReviewState(state_dir=state_dir)

        app = DiffnavApp(diff_data=diff_data, review_state=review_state)
        async with app.run_test() as pilot:
            await pilot.pause()
            yield cls(app, pilot)

    # ------------------------------------------------------------------
    # Key press helpers
    # ------------------------------------------------------------------

    async def press_key(self, key: str) -> None:
        """Press a single key."""
        await self.pilot.press(key)
        await self.pilot.pause()

    async def press_keys(self, *keys: str) -> None:
        """Press multiple keys in sequence."""
        for key in keys:
            await self.pilot.press(key)
            await self.pilot.pause()

    # ------------------------------------------------------------------
    # File navigation (arrow keys — handled globally by the app)
    # ------------------------------------------------------------------

    async def navigate_file_down(self) -> None:
        """Navigate to the next file in the file list (arrow down)."""
        await self.press_key("down")

    async def navigate_file_up(self) -> None:
        """Navigate to the previous file in the file list (arrow up)."""
        await self.press_key("up")

    # ------------------------------------------------------------------
    # Diff scrolling (vim keys — handled by DiffView)
    # ------------------------------------------------------------------

    async def scroll_diff_down(self) -> None:
        """Scroll the diff view down one line (j)."""
        await self.press_key("j")

    async def scroll_diff_up(self) -> None:
        """Scroll the diff view up one line (k)."""
        await self.press_key("k")

    async def scroll_diff_to_top(self) -> None:
        """Scroll to the top of the diff (gg)."""
        await self.press_keys("g", "g")

    async def scroll_diff_to_bottom(self) -> None:
        """Scroll to the bottom of the diff (G)."""
        await self.press_key("G")

    async def scroll_diff_page_down(self) -> None:
        """Scroll the diff down half a page (ctrl+d)."""
        await self.press_key("ctrl+d")

    async def scroll_diff_page_up(self) -> None:
        """Scroll the diff up half a page (ctrl+u)."""
        await self.press_key("ctrl+u")

    # ------------------------------------------------------------------
    # Other actions
    # ------------------------------------------------------------------

    async def mark_reviewed(self) -> None:
        """Mark the current file as reviewed (m)."""
        await self.press_key("m")

    async def next_file(self) -> None:
        """Go to the next file (n)."""
        await self.press_key("n")

    async def prev_file(self) -> None:
        """Go to the previous file (p)."""
        await self.press_key("p")

    async def toggle_focus(self) -> None:
        """Toggle focus between panes (Tab)."""
        await self.press_key("tab")

    # ------------------------------------------------------------------
    # State queries
    # ------------------------------------------------------------------

    def get_current_file(self) -> str | None:
        """Return the path of the currently highlighted file."""
        file_list = self.app.query_one("#file-list", FileList)
        highlighted = file_list.highlighted_child
        if isinstance(highlighted, FileListItem):
            return highlighted.diff_file.path
        return None

    def get_diff_scroll_position(self) -> float:
        """Return the diff view's vertical scroll offset."""
        diff_view = self.app.query_one("#diff-view", DiffView)
        return diff_view.scroll_offset.y

    def get_focused_widget_id(self) -> str | None:
        """Return the ID of the currently focused widget."""
        focused = self.app.focused
        if focused is not None:
            return focused.id
        return None
