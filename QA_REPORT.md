# prview QA Report

**Date:** 2026-04-02
**Method:** Static code review of all source, test, fixture, and configuration files.
Runtime verification (pip install, pytest, integration test) was not possible due to
shell access restrictions. Items that require runtime confirmation are marked accordingly.

---

## 1. Installation and Imports

### pyproject.toml structure: PASS
- `[project.scripts]` correctly maps `prview` to `prview.cli:main`.
- `[tool.hatch.build.targets.wheel]` correctly points at `src/prview`.
- Dependencies (`textual>=0.40.0`, `unidiff>=0.7.0`) and dev deps (`pytest>=7.0`) are declared.
- `requires-python = ">=3.11"` matches the use of `X | Y` union type syntax throughout.

### Module structure: PASS
All expected modules exist and import from the correct locations:
- `src/prview/__init__.py` -- exports `__version__`
- `src/prview/models.py` -- `DiffData`, `DiffFile`, `DiffHunk`, `DiffLine`
- `src/prview/diff_parser.py` -- `parse`
- `src/prview/state.py` -- `ReviewState`
- `src/prview/git.py` -- `get_diff`, `get_staged_diff`, `get_repo_root`, `GitError`
- `src/prview/widgets/file_list.py` -- `FileList`
- `src/prview/widgets/diff_view.py` -- `DiffView`
- `src/prview/widgets/help.py` -- `HelpScreen`
- `src/prview/app.py` -- `DiffnavApp`
- `src/prview/cli.py` -- `main`
- `src/prview/__main__.py` -- correctly calls `main()` for `python -m prview`

### Import chain correctness: PASS
All cross-module imports are valid. No circular imports detected.

**NEEDS RUNTIME:** Actual `pip install -e ".[dev]"` and `from prview.X import Y` verification.

---

## 2. Test Suite

### Test file existence and structure: PASS
Test files exist for all major modules:
- `tests/test_diff_parser.py` -- 9 tests (file count, each status type, edge cases)
- `tests/test_state.py` -- 8 tests (toggle, persistence, clear, corrupt JSON, etc.)
- `tests/test_git.py` -- 7 tests (all git functions, error handling)
- `tests/test_file_list.py` -- 4 tests (load, status display, selection, mark reviewed)
- `tests/test_diff_view.py` -- 5 tests (render, hunk headers, line numbers, clear, colors)
- `tests/conftest.py` -- fixtures including `sample_diff_data` and `fixtures_dir`

### Test quality assessment: PASS
- Tests cover happy paths AND edge cases (empty diff, whitespace-only, corrupt JSON).
- Widget tests use Textual's `run_test()` pilot correctly.
- Git tests properly mock `subprocess.run`.
- State tests use `tmp_path` for isolation.

### Potential test issue: NOTE
In `test_file_list.py::test_file_selected_message`, the test presses `down` then `enter`.
If the ListView already highlights the first item on mount, pressing `down` moves to
the second item. The assertion only checks `selected_file is not None`, so this is not
a failure, but the test is not precise about *which* file is selected.

**NEEDS RUNTIME:** `python -m pytest tests/ -v` to confirm all pass.

---

## 3. Diff Parser

### Parser logic: PASS
- Empty/whitespace input returns `DiffData()` with no files -- correct.
- Uses `unidiff.PatchSet` for parsing -- well-tested library.
- Strips `a/` and `b/` prefixes correctly.
- Maps file statuses (`added`, `modified`, `deleted`, `renamed`) correctly.
- Line type mapping handles `add`, `remove`, `context`; skips unknown types.
- Line numbers use `or None` to convert 0 to None -- correct for unidiff behavior.

### Fixture alignment: PASS
The `sample.diff` fixture contains 4 files (added, modified, deleted, renamed) and the
test expectations match the fixture content exactly.

**NEEDS RUNTIME:** Parsing a real `git log -1 -p` diff to verify end-to-end.

---

## 4. Integration Test (Textual Pilot)

### Code review of app.py: PASS
The app correctly:
- Composes Header, Horizontal(FileList, DiffView), Footer.
- Auto-selects the first file on mount (line 53).
- Handles file selection messages from FileList.
- Implements toggle focus, mark reviewed, next/prev file, show help.
- The `_navigate_file` method bounds-checks correctly.

### Potential issue in action_toggle_focus: MINOR CONCERN
`file_list.has_focus` checks if the FileList widget itself has focus. However, in a
ListView, focus might be on a child ListItem. Textual's `has_focus` checks the widget
itself, while `has_focus_within` checks any descendant. If a ListItem has focus rather
than the FileList container, `has_focus` would be False and the toggle would always
focus the file list. This depends on Textual's ListView focus behavior -- ListView
typically manages focus on itself, so this is likely fine, but worth runtime testing.

**NEEDS RUNTIME:** Full integration test with Textual pilot.

---

## 5. Edge Cases

### Empty diff: PASS
`parse("")` returns `DiffData()` with empty files list. Test exists in
`test_diff_parser.py::TestEdgeCases::test_empty_string`.

### CLI with empty diff: PASS
`cli.py` line 70-71 checks `if not diff_data.files` and prints "No changes to display."
then returns. This correctly avoids launching the TUI with no data.

### App with 0 files: PASS
`app.py::on_mount` guards with `if self._diff_data.files:` before accessing the first
file. If there are no files, no file is auto-selected and no diff is shown. The
`_navigate_file` method also checks `if not self._diff_data.files or self._current_file is None`.

### Large diff: NOT TESTED
No test exists for a diff with 100+ files. The parser delegates to `unidiff.PatchSet`
which handles large inputs. No obvious memory or performance issues in the code, but
this should be verified at runtime.

---

## 6. Code Quality - Detailed Review

### cli.py -- os.dup2 usage: PASS
The `_read_piped_stdin()` function (lines 14-25) correctly implements the pattern from
the spike findings:
1. Checks `sys.stdin.isatty()` -- returns None if already a tty.
2. Reads all piped data with `sys.stdin.buffer.read().decode()`.
3. Opens `/dev/tty` and uses `os.dup2(tty_fd, 0)` to replace fd 0.
4. Closes the temporary fd.
5. Closes old stdin and reopens fd 0.
6. This happens BEFORE Textual is imported (Textual imports are deferred to lines 66-68).

This matches the spike's recommended pattern exactly.

### help.py -- dismiss behavior: PASS
`HelpScreen` extends `ModalScreen` and binds Escape, `?`, and `q` all to
`action_dismiss_help` which calls `self.dismiss()`. This is the correct Textual API
for dismissing modal screens.

One subtlety: the app-level binding for `q` is `action_quit`. Since `HelpScreen` is
pushed as a screen and has its own `q` binding mapped to `dismiss_help`, the screen-level
binding takes priority. This is correct -- pressing `q` on the help screen dismisses
help instead of quitting the app.

### app.py -- 0 files handling: PASS
As noted above, the `on_mount` method guards file access. The CLI also prevents the app
from launching with 0 files.

### models.py: PASS
Clean dataclass design. All fields have sensible types and defaults.

### state.py: PASS
- Handles missing directory, missing file, and corrupt JSON gracefully.
- Uses `sorted()` for deterministic JSON output.
- Thread-safety is not addressed (single-threaded app, so this is fine).

### git.py: PASS
- `get_diff` returns `.strip()` which could strip meaningful trailing content from a
  diff, but in practice `git diff` output ends with a newline, so stripping is fine.
- Error handling raises `GitError` with the stderr message.
- `get_pr_diff` correctly delegates to `gh pr diff`.

### widgets/file_list.py: PASS
- Status map covers all 4 statuses with fallback `("?", "white")`.
- Uses Rich markup for colored labels.
- The `[` character in the label is escaped as `\\[` (line 43) to prevent Rich from
  interpreting it as a markup tag. Correct.

### widgets/diff_view.py: PASS
- Uses `markup=False` on the Static widget (line 37) since it passes a Rich Text object.
  This prevents double-interpretation of markup.
- Line number formatting with configurable width is clean.
- Both `_build_content` and `_render_line` exist -- the latter for testing convenience.

### CSS (app.tcss): MINOR CONCERN
The top-level `Screen { layout: horizontal; }` sets horizontal layout on ALL screens,
including the `HelpScreen` modal. However, `HelpScreen` has its own `DEFAULT_CSS` with
`align: center middle` and only contains a single Static widget, so the horizontal
layout doesn't cause visible issues. Still, it would be cleaner to scope this to the
main screen only (e.g., using a container class).

---

## 7. Missing Items / Recommendations

### No `pytest-textual-snapshot` or similar
Widget tests use `run_test()` which is good, but there are no snapshot tests to catch
visual regressions.

### No test for cli.py
The CLI module (`_read_piped_stdin`, `_parse_args`, `main`) has no dedicated test file.
Testing `_parse_args` is straightforward; testing `_read_piped_stdin` would require fd
manipulation in tests but is doable.

### No test for app.py integration
There is no test that creates `DiffnavApp` with real diff data and exercises the full
flow (the QA spec includes one, but it is not in the test suite).

### `get_diff` strips output
`get_diff()` calls `.strip()` on stdout. If a diff's last line has no trailing newline
(e.g., "No newline at end of file" marker), the strip could remove a meaningful trailing
space. Low risk but worth noting.

---

## Summary

| Check                                    | Status           |
|------------------------------------------|------------------|
| 1. pyproject.toml / package structure    | PASS             |
| 2. Module imports (static)               | PASS             |
| 3. Test suite structure and quality      | PASS             |
| 4. Diff parser correctness              | PASS             |
| 5. Empty diff edge case                 | PASS             |
| 6. Large diff edge case                 | NOT TESTED (runtime needed) |
| 7. App handles 0 files                  | PASS             |
| 8. cli.py os.dup2 pattern               | PASS             |
| 9. help.py dismiss behavior             | PASS             |
| 10. Code quality (all modules)          | PASS             |
| 11. CSS scoping                         | MINOR CONCERN    |
| 12. CLI test coverage                   | MISSING (no test_cli.py) |
| 13. App integration test coverage       | MISSING (no test_app.py) |
| 14. Runtime: pip install                | NEEDS RUNTIME    |
| 15. Runtime: pytest                     | NEEDS RUNTIME    |
| 16. Runtime: real diff parsing          | NEEDS RUNTIME    |
| 17. Runtime: Textual pilot integration  | NEEDS RUNTIME    |

**Overall assessment:** The codebase is well-structured, follows good practices, and has
no blocking bugs found in static review. The code aligns with the spike findings and
implements all expected features. Two gaps in test coverage (cli.py and app.py integration)
are noted. Runtime verification of installation, test execution, and the Textual pilot
integration test is still needed.
