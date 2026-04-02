"""Help screen widget for prview — shows keybindings in a modal overlay."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.binding import Binding
from textual.screen import ModalScreen
from textual.widgets import Static


HELP_TEXT = """\
[bold underline]prview — Keybindings[/bold underline]

 [bold cyan]Navigation[/bold cyan]
   j / ↓          Move down in file list
   k / ↑          Move up in file list
   Enter           Select file / expand
   n               Next file (from diff view)
   p               Previous file (from diff view)
   Tab             Toggle focus between file list and diff view

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
