"""Help screen widget for prview — shows keybindings in a modal overlay."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.widgets import Static


HELP_TEXT = """\
[bold underline]prview — Keybindings[/bold underline]

 [bold cyan]File Navigation[/bold cyan]
   ↑ / ↓           Move up / down in file list (global)
   n               Next file
   p               Previous file
   Tab             Toggle focus between file list and diff view

 [bold cyan]Diff Scrolling[/bold cyan]
   j / k           Scroll diff down / up one line
   d / u           Scroll diff down / up one page
   Ctrl+D / Ctrl+U Scroll diff down / up half page
   g g             Scroll to top of diff
   G               Scroll to bottom of diff

 [bold cyan]Review[/bold cyan]
   m               Mark / unmark current file as reviewed

 [bold cyan]General[/bold cyan]
   ?               Show / dismiss this help screen
   q               Quit (or dismiss help)
   Escape          Dismiss help

Press [bold]?[/bold], [bold]Escape[/bold], or [bold]q[/bold] to close.
"""


class HelpScreen(ModalScreen):
    """Modal screen that displays keybinding help."""

    DEFAULT_CSS = """
    HelpScreen {
        align: center middle;
    }

    HelpScreen > Static {
        width: 60;
        height: auto;
        max-height: 80%;
        padding: 2 4;
        border: thick $accent;
        background: $surface;
    }
    """

    BINDINGS = [
        Binding("escape", "dismiss_help", "Close", show=False),
        Binding("question_mark", "dismiss_help", "Close", show=False),
        Binding("q", "dismiss_help", "Close", show=False),
    ]

    def compose(self) -> ComposeResult:
        yield Static(HELP_TEXT)

    def action_dismiss_help(self) -> None:
        self.dismiss()
