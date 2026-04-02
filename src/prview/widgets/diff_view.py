"""Diff view widget — renders a unified diff for a selected file."""

from __future__ import annotations

from rich.text import Text
from textual.containers import VerticalScroll
from textual.widgets import Static

from prview.models import DiffFile, DiffLine


class DiffView(VerticalScroll):
    """Scrollable widget that displays a unified diff for a single file."""

    can_focus = True

    DEFAULT_CSS = """
    DiffView {
        height: 1fr;
        width: 1fr;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._current_file: DiffFile | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def show_file(self, diff_file: DiffFile) -> None:
        """Render the given file's diff."""
        if self._current_file is not None and self._current_file.path == diff_file.path:
            return
        self._current_file = diff_file
        self.remove_children()
        content = self._build_content(diff_file)
        self.mount(Static(content, markup=False))

    def clear(self) -> None:
        """Clear the diff view."""
        self._current_file = None
        self.remove_children()

    # ------------------------------------------------------------------
    # Rendering
    # ------------------------------------------------------------------

    @staticmethod
    def _build_content(diff_file: DiffFile) -> Text:
        """Build a single Rich Text object for the entire file diff."""
        result = Text()
        for i, hunk in enumerate(diff_file.hunks):
            result.append(hunk.header, style="cyan dim")
            result.append("\n")
            for line in hunk.lines:
                old = DiffView._format_lineno(line.old_lineno)
                new = DiffView._format_lineno(line.new_lineno)

                if line.type == "add":
                    indicator = "+"
                    style = "green"
                elif line.type == "remove":
                    indicator = "-"
                    style = "red"
                else:
                    indicator = " "
                    style = ""

                text = f"{old} | {new} | {indicator} | {line.content}\n"
                result.append(text, style=style)

            if i < len(diff_file.hunks) - 1:
                result.append("\n")
        return result

    @staticmethod
    def _format_lineno(n: int | None, width: int = 5) -> str:
        if n is None:
            return " " * width
        return str(n).rjust(width)

    @staticmethod
    def _render_line(line: DiffLine) -> Text:
        """Render a single diff line (used for testing/external access)."""
        old = DiffView._format_lineno(line.old_lineno)
        new = DiffView._format_lineno(line.new_lineno)

        if line.type == "add":
            indicator = "+"
            style = "green"
        elif line.type == "remove":
            indicator = "-"
            style = "red"
        else:
            indicator = " "
            style = ""

        return Text(f"{old} | {new} | {indicator} | {line.content}", style=style)
