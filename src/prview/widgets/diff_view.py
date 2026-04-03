"""Diff view widget — renders a unified diff for a selected file."""

from __future__ import annotations

import time

from rich.text import Text
from textual.binding import Binding
from textual.containers import VerticalScroll
from textual.widgets import Static

from prview.models import DiffFile, DiffLine

# Timeout for the gg chord (seconds)
_GG_TIMEOUT = 0.5


class DiffView(VerticalScroll):
    """Scrollable widget that displays a unified diff for a single file."""

    can_focus = True

    BINDINGS = [
        Binding("j", "scroll_down_line", "Scroll Down", show=False),
        Binding("k", "scroll_up_line", "Scroll Up", show=False),
        Binding("G", "scroll_to_bottom", "Scroll to Bottom", show=False),
        Binding("g", "scroll_to_top_chord", "Scroll to Top", show=False),
        Binding("ctrl+d", "scroll_half_page_down", "Half Page Down", show=False),
        Binding("ctrl+u", "scroll_half_page_up", "Half Page Up", show=False),
        Binding("d", "scroll_page_down", "Page Down", show=False),
        Binding("u", "scroll_page_up", "Page Up", show=False),
    ]

    DEFAULT_CSS = """
    DiffView {
        height: 1fr;
        width: 1fr;
    }
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._current_file: DiffFile | None = None
        self._last_g_time: float = 0.0

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
    # Vim-style scroll actions
    # ------------------------------------------------------------------

    def action_scroll_down_line(self) -> None:
        """Scroll down one line."""
        self.scroll_relative(y=1)

    def action_scroll_up_line(self) -> None:
        """Scroll up one line."""
        self.scroll_relative(y=-1)

    def action_scroll_to_bottom(self) -> None:
        """Scroll to the bottom of the diff."""
        self.scroll_end()

    def action_scroll_to_top_chord(self) -> None:
        """Scroll to top on gg chord (two g presses within timeout)."""
        now = time.monotonic()
        if now - self._last_g_time < _GG_TIMEOUT:
            self.scroll_home()
            self._last_g_time = 0.0
        else:
            self._last_g_time = now

    def action_scroll_half_page_down(self) -> None:
        """Scroll down half a page."""
        self.scroll_relative(y=self.size.height // 2)

    def action_scroll_half_page_up(self) -> None:
        """Scroll up half a page."""
        self.scroll_relative(y=-(self.size.height // 2))

    def action_scroll_page_down(self) -> None:
        """Scroll down one full page."""
        self.scroll_page_down()

    def action_scroll_page_up(self) -> None:
        """Scroll up one full page."""
        self.scroll_page_up()

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
