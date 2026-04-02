# Spike: Piped stdin + Textual keyboard input coexistence

## How Textual reads keyboard input internally

Textual's `LinuxDriver` (used on macOS/Linux) is the key class. Located at:
`textual/drivers/linux_driver.py`

In `__init__`, it captures:
```python
self._file = sys.__stderr__       # output goes to stderr
self.fileno = sys.__stdin__.fileno()  # input fd (typically 0)
```

In `run_input_thread`, it reads raw bytes from that fd using a selector loop:
```python
selector.register(self.fileno, selectors.EVENT_READ)
# ...
unicode_data = decode(read(fileno, 1024 * 4), ...)
```

Key detail: it uses `os.read(fileno, ...)` directly -- low-level POSIX reads on the
file descriptor number. It also uses `termios.tcsetattr` and `termios.tcgetattr` on
the same fd to configure raw terminal mode.

Output goes to `sys.__stderr__` (not stdout), which is how Textual avoids conflicts
with stdout piping.

## Does the `sys.stdin = open("/dev/tty")` swap work?

**No.** Textual uses `sys.__stdin__` (Python's backup reference to the original
stdin), not `sys.stdin`. The `__stdin__` attribute is set once at interpreter startup
and is never affected by reassigning `sys.stdin`. So:

```python
sys.stdin = open("/dev/tty", "r")  # This does NOT help Textual
```

Textual will still call `sys.__stdin__.fileno()` which returns 0, and fd 0 still
points to the pipe.

Furthermore, even if you could swap `sys.__stdin__`, the driver captures `self.fileno`
as an integer in `__init__`, so the fd number is baked in.

## The correct pattern: `os.dup2()`

The solution is to operate at the OS file descriptor level:

```python
import os, sys

def read_piped_input() -> str:
    if not sys.stdin.isatty():
        piped_data = sys.stdin.buffer.read().decode()
        tty_fd = os.open("/dev/tty", os.O_RDONLY)
        os.dup2(tty_fd, 0)   # Replace fd 0 with /dev/tty
        os.close(tty_fd)
        sys.stdin.close()
        sys.stdin = os.fdopen(0, "r")
        return piped_data
    return ""
```

This works because:
1. `os.dup2(tty_fd, 0)` replaces what fd 0 points to at the kernel level
2. `sys.__stdin__.fileno()` still returns 0, but now fd 0 is the real terminal
3. `termios` calls on fd 0 work correctly (they would fail on a pipe)
4. The selector + `os.read(0, ...)` loop in the input thread reads real keypresses

**Critical**: this must happen BEFORE Textual's driver is instantiated, because the
driver calls `termios.tcgetattr(self.fileno)` during `start_application_mode()`.

## Recommended pattern for cli.py

```python
#!/usr/bin/env python3
import os
import sys

def main():
    # Step 1: Read piped diff data before Textual touches stdin
    if not sys.stdin.isatty():
        diff_text = sys.stdin.buffer.read().decode()
        tty_fd = os.open("/dev/tty", os.O_RDONLY)
        os.dup2(tty_fd, 0)
        os.close(tty_fd)
        sys.stdin.close()
        sys.stdin = os.fdopen(0, "r")
    else:
        diff_text = None  # No piped input; could run git diff ourselves

    # Step 2: Now safe to import and run Textual
    from prview.app import DiffNavApp
    app = DiffNavApp(diff_text)
    app.run()
```

## Other observations

- Textual writes output to `sys.__stderr__`, so stdout is free. This means
  `git diff | prview` will not conflict with Textual's rendering.
- The `LinuxDriver.run_input_thread` has a comment on line 433: "This can occur if
  the stdin is piped" -- suggesting the Textual authors are aware of the pipe scenario
  but chose not to handle it automatically.
- Textual does NOT open `/dev/tty` anywhere in its source code. It relies entirely
  on fd 0 being a real terminal. The `os.dup2` approach is the only clean fix.
- On platforms without `/dev/tty` (Windows), a different approach would be needed,
  but Textual uses `WindowsDriver` there which has its own input mechanism.

## Risk assessment

**Low risk.** The `os.dup2` pattern is well-established (used by `less`, `fzf`, and
many other Unix tools that accept piped input while maintaining terminal interaction).
The spike confirms it works with Textual.
