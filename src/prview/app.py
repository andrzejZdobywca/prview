"""Main Textual application for prview."""

from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal
from textual.widgets import Header, Footer

from prview.models import DiffData, DiffFile
from prview.state import ReviewState
from prview.widgets.file_list import FileList
from prview.widgets.diff_view import DiffView
from prview.widgets.help import HelpScreen


class DiffnavApp(App):
    """Interactive terminal diff browser."""

    CSS_PATH = "styles/app.tcss"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("tab", "toggle_focus", "Toggle Focus"),
        Binding("m", "mark_reviewed", "Mark Reviewed"),
        Binding("question_mark", "show_help", "Help"),
        Binding("n", "next_file", "Next File"),
        Binding("p", "prev_file", "Prev File"),
    ]

    def __init__(
        self,
        diff_data: DiffData,
        review_state: ReviewState,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self._diff_data = diff_data
        self._review_state = review_state
        self._current_file: DiffFile | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield FileList(id="file-list")
            yield DiffView(id="diff-view")
        yield Footer()

    def on_mount(self) -> None:
        file_list = self.query_one("#file-list", FileList)
        file_list.load(self._diff_data, self._review_state)
        # Auto-select first file
        if self._diff_data.files:
            first = self._diff_data.files[0]
            self._current_file = first
            diff_view = self.query_one("#diff-view", DiffView)
            diff_view.show_file(first)
        file_list.focus()

    def on_file_list_file_selected(self, message: FileList.FileSelected) -> None:
        self._current_file = message.diff_file
        diff_view = self.query_one("#diff-view", DiffView)
        diff_view.show_file(message.diff_file)

    def action_toggle_focus(self) -> None:
        file_list = self.query_one("#file-list", FileList)
        diff_view = self.query_one("#diff-view", DiffView)
        if file_list.has_focus:
            diff_view.focus()
        else:
            file_list.focus()

    def action_mark_reviewed(self) -> None:
        if self._current_file is None:
            return
        path = self._current_file.path
        self._review_state.toggle_reviewed(path)
        reviewed = self._review_state.is_reviewed(path)
        file_list = self.query_one("#file-list", FileList)
        file_list.mark_reviewed(path, reviewed)

    def action_show_help(self) -> None:
        self.push_screen(HelpScreen())

    def action_next_file(self) -> None:
        self._navigate_file(1)

    def action_prev_file(self) -> None:
        self._navigate_file(-1)

    def _navigate_file(self, direction: int) -> None:
        if not self._diff_data.files or self._current_file is None:
            return
        files = self._diff_data.files
        try:
            idx = next(
                i for i, f in enumerate(files) if f.path == self._current_file.path
            )
        except StopIteration:
            return
        new_idx = idx + direction
        if 0 <= new_idx < len(files):
            new_file = files[new_idx]
            self._current_file = new_file
            diff_view = self.query_one("#diff-view", DiffView)
            diff_view.show_file(new_file)
            # Also update file list selection
            file_list = self.query_one("#file-list", FileList)
            file_list.index = new_idx
