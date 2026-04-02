"""Tests for the FileList widget."""

from __future__ import annotations

import asyncio

from textual.app import App, ComposeResult

from prview.models import DiffData
from prview.state import ReviewState
from prview.widgets.file_list import FileList, FileListItem


class FileListApp(App):
    """Minimal app for testing the FileList widget."""

    def __init__(self, diff_data: DiffData, review_state: ReviewState) -> None:
        super().__init__()
        self.diff_data = diff_data
        self.review_state = review_state
        self.selected_file = None

    def compose(self) -> ComposeResult:
        yield FileList()

    def on_mount(self) -> None:
        file_list = self.query_one(FileList)
        file_list.load(self.diff_data, self.review_state)

    def on_file_list_file_selected(self, message: FileList.FileSelected) -> None:
        self.selected_file = message.diff_file


def test_load_populates_list(sample_diff_data: DiffData, tmp_path) -> None:
    """FileList.load() should create one child per file in the diff."""
    state = ReviewState(state_dir=tmp_path / ".prview")

    async def run() -> None:
        app = FileListApp(sample_diff_data, state)
        async with app.run_test():
            file_list = app.query_one(FileList)
            items = file_list.query(FileListItem)
            assert len(items) == len(sample_diff_data.files)

    asyncio.run(run())


def test_file_status_display(sample_diff_data: DiffData, tmp_path) -> None:
    """Each file entry should show the correct status letter."""
    state = ReviewState(state_dir=tmp_path / ".prview")

    async def run() -> None:
        app = FileListApp(sample_diff_data, state)
        async with app.run_test():
            file_list = app.query_one(FileList)
            items = list(file_list.query(FileListItem))

            # The sample_diff_data has: added, modified, deleted, renamed
            expected = {
                "src/new_file.py": "[A]",
                "src/existing.py": "[M]",
                "old_module.py": "[D]",
                "src/renamed.py": "[R]",
            }
            for item in items:
                path = item.diff_file.path
                assert path in expected
                letter = expected[path]
                label_text = item._render_label()
                assert letter in label_text, f"Expected {letter} in label for {path}"

    asyncio.run(run())


def test_file_selected_message(sample_diff_data: DiffData, tmp_path) -> None:
    """Selecting a file should post a FileSelected message."""
    state = ReviewState(state_dir=tmp_path / ".prview")

    async def run() -> None:
        app = FileListApp(sample_diff_data, state)
        async with app.run_test() as pilot:
            file_list = app.query_one(FileList)
            file_list.focus()
            await pilot.pause()
            # Move to first item then select it
            await pilot.press("down")
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            assert app.selected_file is not None

    asyncio.run(run())


def test_mark_reviewed(sample_diff_data: DiffData, tmp_path) -> None:
    """mark_reviewed should toggle the checkmark indicator."""
    state = ReviewState(state_dir=tmp_path / ".prview")

    async def run() -> None:
        app = FileListApp(sample_diff_data, state)
        async with app.run_test():
            file_list = app.query_one(FileList)
            path = "src/new_file.py"

            # Initially not reviewed - no checkmark
            item = file_list._file_items[path]
            assert not item.reviewed
            label_before = item._render_label()
            assert "\u2713" not in label_before

            # Mark as reviewed
            file_list.mark_reviewed(path, True)
            assert item.reviewed
            label_after = item._render_label()
            assert "\u2713" in label_after

            # Mark as not reviewed again
            file_list.mark_reviewed(path, False)
            assert not item.reviewed
            label_reverted = item._render_label()
            assert "\u2713" not in label_reverted

    asyncio.run(run())
