"""High-level user interaction simulator for prview testing.

Wraps Textual's Pilot to provide semantic methods like
navigate_file_down() instead of raw key presses.  This separates
"what the user does" from "how the framework works."
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from textual.pilot import Pilot

from prview.app import DiffnavApp
from prview.models import DiffData
from prview.state import ReviewState
from prview.widgets.diff_view import DiffView
from prview.widgets.file_list import FileList, FileListItem


class UserSimulator:
    """High-level user interaction simulator for prview testing.

    Wraps Textual's Pilot to provide semantic methods like
    navigate_file_down() instead of raw key presses.
    """

    def __init__(self, pilot: Pilot, app: DiffnavApp) -> None:
        self._pilot = pilot
        self._app = app

    # ------------------------------------------------------------------
    # Factory
    # ------------------------------------------------------------------

    @classmethod
    @asynccontextmanager
    async def from_diff_data(
        cls,
        diff_data: DiffData,
        *,
        state_dir=None,
    ) -> AsyncGenerator["UserSimulator", None]:
        """Create a simulator with a running app loaded with the given diff data.

        Parameters
        ----------
        diff_data:
            The diff to load into the app.
        state_dir:
            Temporary directory for ReviewState persistence.
            If *None* a no-op in-memory path is used.
        """
        import tempfile
        from pathlib import Path

        if state_dir is None:
            _tmpdir = tempfile.mkdtemp()
            state_dir = Path(_tmpdir) / ".prview"

        review_state = ReviewState(state_dir=state_dir)
        app = DiffnavApp(diff_data=diff_data, review_state=review_state)

        async with app.run_test(size=(120, 40)) as pilot:
            # Let the app fully mount and settle
            await pilot.pause()
            yield cls(pilot, app)

    # ------------------------------------------------------------------
    # Navigation – file list (arrow keys, global)
    # ------------------------------------------------------------------

    async def navigate_file_down(self) -> None:
        """Press Arrow Down to move to the next file in the list."""
        await self._pilot.press("down")
        await self._pilot.pause()

    async def navigate_file_up(self) -> None:
        """Press Arrow Up to move to the previous file in the list."""
        await self._pilot.press("up")
        await self._pilot.pause()

    async def next_file(self) -> None:
        """Press ``n`` to advance to the next file."""
        await self._pilot.press("n")
        await self._pilot.pause()

    async def prev_file(self) -> None:
        """Press ``p`` to go back to the previous file."""
        await self._pilot.press("p")
        await self._pilot.pause()

    # ------------------------------------------------------------------
    # Diff scrolling – vim keys
    # ------------------------------------------------------------------

    async def scroll_diff_down(self) -> None:
        """Press ``j`` to scroll the diff view down by one line."""
        await self._pilot.press("j")
        await self._pilot.pause()

    async def scroll_diff_up(self) -> None:
        """Press ``k`` to scroll the diff view up by one line."""
        await self._pilot.press("k")
        await self._pilot.pause()

    async def scroll_diff_to_top(self) -> None:
        """Press ``gg`` (two g presses) to scroll the diff view to the top."""
        await self._pilot.press("g")
        await self._pilot.press("g")
        await self._pilot.pause()

    async def scroll_diff_to_bottom(self) -> None:
        """Press ``G`` (Shift+G) to scroll the diff view to the bottom."""
        await self._pilot.press("G")
        await self._pilot.pause()

    async def scroll_diff_page_down(self) -> None:
        """Press ``Ctrl+D`` to scroll the diff view down by half a page."""
        await self._pilot.press("ctrl+d")
        await self._pilot.pause()

    async def scroll_diff_page_up(self) -> None:
        """Press ``Ctrl+U`` to scroll the diff view up by half a page."""
        await self._pilot.press("ctrl+u")
        await self._pilot.pause()

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    async def mark_reviewed(self) -> None:
        """Press ``m`` to toggle the reviewed state of the current file."""
        await self._pilot.press("m")
        await self._pilot.pause()

    async def toggle_focus(self) -> None:
        """Press ``Tab`` to toggle focus between file list and diff view."""
        await self._pilot.press("tab")
        await self._pilot.pause()

    async def press_key(self, key: str) -> None:
        """Press an arbitrary key."""
        await self._pilot.press(key)
        await self._pilot.pause()

    async def press_keys(self, *keys: str) -> None:
        """Press a sequence of keys."""
        for key in keys:
            await self._pilot.press(key)
        await self._pilot.pause()

    # ------------------------------------------------------------------
    # Queries
    # ------------------------------------------------------------------

    def get_current_file(self) -> str | None:
        """Return the path of the currently highlighted/selected file, or None.

        Checks the file list highlight index first; falls back to the app's
        internal ``_current_file`` which is set on mount even before the
        user interacts with the list.
        """
        file_list = self._app.query_one("#file-list", FileList)
        idx = file_list.index
        if idx is not None:
            items = list(file_list.query(FileListItem))
            if 0 <= idx < len(items):
                return items[idx].diff_file.path
        # Fallback: the app tracks the current file independently
        if self._app._current_file is not None:
            return self._app._current_file.path
        return None

    def get_diff_scroll_position(self) -> float:
        """Return the diff view's current vertical scroll offset (pixels)."""
        diff_view = self._app.query_one("#diff-view", DiffView)
        return diff_view.scroll_y

    def get_focused_widget_id(self) -> str | None:
        """Return the DOM id of the currently focused widget, or None."""
        focused = self._app.focused
        if focused is None:
            return None
        return focused.id

    def is_file_reviewed(self, path: str) -> bool:
        """Check whether a file is marked as reviewed in the review state."""
        return self._app._review_state.is_reviewed(path)

    def get_file_count(self) -> int:
        """Return the total number of files in the diff."""
        return len(self._app._diff_data.files)

    def get_file_list_index(self) -> int | None:
        """Return the current index of the file list cursor."""
        file_list = self._app.query_one("#file-list", FileList)
        return file_list.index
