"""File list widget for prview.

Displays changed files with status indicators, line counts, and review state.
"""

from __future__ import annotations

from textual.binding import Binding
from textual.message import Message
from textual.widgets import ListView, ListItem, Label
from textual.app import ComposeResult

from prview.models import DiffData, DiffFile
from prview.state import ReviewState
from prview.widgets.diff_view import DiffView


STATUS_MAP: dict[str, tuple[str, str]] = {
    "added": ("A", "green"),
    "modified": ("M", "yellow"),
    "deleted": ("D", "red"),
    "renamed": ("R", "blue"),
}


class FileListItem(ListItem):
    """A single file entry in the file list."""

    def __init__(self, diff_file: DiffFile, reviewed: bool = False) -> None:
        super().__init__()
        self.diff_file = diff_file
        self.reviewed = reviewed

    def compose(self) -> ComposeResult:
        yield Label(self._render_label())

    def _render_label(self) -> str:
        letter, color = STATUS_MAP.get(self.diff_file.status, ("?", "white"))
        check = "\u2713 " if self.reviewed else "  "
        added = self.diff_file.added_lines
        removed = self.diff_file.removed_lines
        return (
            f"{check}"
            f"[{color}]\\[{letter}][/{color}] "
            f"{self.diff_file.path}  "
            f"[green]+{added}[/green] [red]-{removed}[/red]"
        )

    def set_reviewed(self, reviewed: bool) -> None:
        self.reviewed = reviewed
        label = self.query_one(Label)
        label.update(self._render_label())


class FileList(ListView):
    """Widget that shows a list of changed files in the diff."""

    can_focus = True

    BINDINGS = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
    ]

    class FileSelected(Message):
        """Posted when a file is selected."""

        def __init__(self, diff_file: DiffFile) -> None:
            super().__init__()
            self.diff_file = diff_file

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._file_items: dict[str, FileListItem] = {}

    def load(self, diff_data: DiffData, review_state: ReviewState) -> None:
        """Populate the list from diff data and review state."""
        self.clear()
        self._file_items.clear()
        for diff_file in diff_data.files:
            reviewed = review_state.is_reviewed(diff_file.path)
            item = FileListItem(diff_file, reviewed=reviewed)
            self._file_items[diff_file.path] = item
            self.append(item)

    def mark_reviewed(self, path: str, reviewed: bool) -> None:
        """Update the visual indicator for a file's review state."""
        if path in self._file_items:
            self._file_items[path].set_reviewed(reviewed)

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        """Post FileSelected on cursor movement so the diff updates immediately."""
        item = event.item
        if isinstance(item, FileListItem):
            self.post_message(self.FileSelected(item.diff_file))

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Move focus to the diff pane on Enter."""
        try:
            self.app.query_one("#diff-view", DiffView).focus()
        except Exception:
            pass
