"""
Spike: Can piped stdin and Textual keyboard input coexist?

Usage:
    echo "hello from pipe" | python spike/stdin_tty_spike.py
    python spike/stdin_tty_spike.py   # no pipe, uses default text

Critical finding: Textual's LinuxDriver reads input via sys.__stdin__.fileno(),
which returns file descriptor 0. Simply doing `sys.stdin = open("/dev/tty")` does
NOT work because Textual ignores sys.stdin entirely.

Solution: use os.dup2() to replace fd 0 at the OS level with /dev/tty after
reading all piped data. This way sys.__stdin__.fileno() still returns 0, but
fd 0 now points to the real terminal.
"""

import os
import sys


def read_piped_input() -> str:
    """Read piped input (if any) and restore stdin to /dev/tty.

    If stdin is a pipe, reads all data from it, then replaces file descriptor 0
    with /dev/tty so that Textual's LinuxDriver can read keyboard input.

    Returns:
        The piped input text, or a default message if running interactively.
    """
    if not sys.stdin.isatty():
        # stdin is a pipe -- read all data from it
        piped_data = sys.stdin.buffer.read().decode()

        # Now replace fd 0 with /dev/tty at the OS level.
        # This is necessary because Textual uses sys.__stdin__.fileno() (which is 0)
        # to read keyboard input -- it does NOT use sys.stdin.
        tty_fd = os.open("/dev/tty", os.O_RDONLY)
        os.dup2(tty_fd, 0)  # Replace fd 0 with the tty
        os.close(tty_fd)    # Close the extra fd

        # Also fix sys.stdin so Python-level reads work too
        sys.stdin.close()
        sys.stdin = os.fdopen(0, "r")

        return piped_data
    else:
        return "No piped input -- running interactively.\nTry: echo 'hello world' | python spike/stdin_tty_spike.py"


# Read piped data BEFORE importing/starting Textual
input_text = read_piped_input()


from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.binding import Binding


class CounterDisplay(Static):
    """A simple counter widget."""

    def __init__(self, initial_text: str) -> None:
        super().__init__()
        self.display_text = initial_text
        self.counter = 0

    def on_mount(self) -> None:
        self._refresh_display()

    def increment(self) -> None:
        self.counter += 1
        self._refresh_display()

    def decrement(self) -> None:
        self.counter -= 1
        self._refresh_display()

    def _refresh_display(self) -> None:
        self.update(
            f"Counter: {self.counter}\n"
            f"---\n"
            f"Input text:\n{self.display_text}\n"
            f"---\n"
            f"Press j/k to increment/decrement counter, q to quit"
        )


class StdinSpikeApp(App):
    """Minimal Textual app to test piped stdin + keyboard coexistence."""

    TITLE = "stdin + tty spike"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("j", "increment", "Increment (j)"),
        Binding("k", "decrement", "Decrement (k)"),
    ]

    def __init__(self, text: str) -> None:
        super().__init__()
        self.text = text

    def compose(self) -> ComposeResult:
        yield Header()
        yield CounterDisplay(self.text)
        yield Footer()

    def action_increment(self) -> None:
        self.query_one(CounterDisplay).increment()

    def action_decrement(self) -> None:
        self.query_one(CounterDisplay).decrement()


if __name__ == "__main__":
    app = StdinSpikeApp(input_text)
    app.run()
