# Architecture

Interactive terminal diff browser. Source lives in `src/prview/` (~700 lines across 12 modules). For vision and roadmap, see [DESIGN.md](DESIGN.md).

## Data Flow

```
stdin / git diff / gh pr diff
        │
        ▼
   raw diff text        ← cli.py orchestrates input
        │
        ▼
   unidiff.PatchSet     ← diff_parser.py wraps unidiff
        │
        ▼
     DiffData           ← models.py (pure dataclasses)
        │
        ▼
   DiffnavApp           ← app.py (Textual App)
    ┌───┴───┐
FileList  DiffView      ← widgets/ (left and right panes)
```

### Startup sequence (cli.py)

1. **Read piped stdin** — if input is piped, read it before Textual loads, then restore `/dev/tty` via `os.dup2` so Textual can read keyboard input
2. **Get diff text** — if no pipe, call `git diff` or `gh pr diff` via `git.py`
3. **Parse** — `diff_parser.parse()` converts raw text to `DiffData`
4. **Launch** — construct `DiffnavApp` with `DiffData` + `ReviewState`, call `app.run()`

## Module Map

| Module | Responsibility | Key exports |
|--------|---------------|-------------|
| `cli.py` | CLI args, piped stdin handling, app launch | `main()` |
| `models.py` | Pure data layer — no I/O | `DiffData`, `DiffFile`, `DiffHunk`, `DiffLine` |
| `diff_parser.py` | unidiff → DiffData conversion | `parse(text) → DiffData` |
| `git.py` | All subprocess calls (git, gh) | `get_diff()`, `get_staged_diff()`, `get_pr_diff()` |
| `state.py` | Review progress persistence | `ReviewState` |
| `app.py` | Textual App, layout, keybindings, message routing | `DiffnavApp` |
| `widgets/file_list.py` | Left pane — file list with status badges | `FileList`, `FileListItem` |
| `widgets/diff_view.py` | Right pane — diff rendering | `DiffView` |
| `widgets/help.py` | Modal help overlay | `HelpScreen` |
| `styles/app.tcss` | Textual CSS — split-pane layout | — |

## Key Abstractions

### DiffData (models.py)

The central contract between parsing and display. Four nested dataclasses:

| Type | Contains | Purpose |
|------|----------|---------|
| `DiffData` | `list[DiffFile]`, `base_ref`, `head_ref` | Top-level container |
| `DiffFile` | `path`, `status`, `list[DiffHunk]`, line counts | One changed file |
| `DiffHunk` | `header`, `list[DiffLine]` | One `@@` block |
| `DiffLine` | `type`, `content`, `old_lineno`, `new_lineno` | One line of diff |

File status is one of: `added`, `modified`, `deleted`, `renamed`.

Designed to be diffable itself — this enables future diff-of-diffs without a rewrite.

### ReviewState (state.py)

Persists reviewed files to `.prview/reviews.json` in the working directory:

```json
{ "version": 1, "reviewed": ["src/app.py", "src/utils.py"] }
```

Writes immediately on toggle. Gracefully handles missing/corrupt files.

## UI Architecture

### Layout

```
Header
├── FileList (#file-list)    width: 1fr, 30-50 chars, right border
└── DiffView (#diff-view)    width: 3fr
Footer
```

Styled via `styles/app.tcss`. FileList is capped at 50 columns to keep the diff pane dominant.

### Message Flow

```
FileList cursor moves → posts FileList.FileSelected(diff_file)
       │
       ▼
DiffnavApp.on_file_list_file_selected() → calls DiffView.show_file()
```

Widgets don't know about each other. The App acts as message router. This is standard Textual message-passing — keeps widgets decoupled and testable.

### Rendering

- **FileList** renders each item as: `[✓] [A] path/to/file.py +42 -3`
- **DiffView** builds a single `Rich.Text` object per file (not per-line widgets), enabling efficient scrolling of large diffs
- `show_file()` is idempotent — skips re-render if the same file is already displayed

## I/O Boundary

All external I/O is isolated in two modules:

- **git.py** — subprocess wrappers for `git diff`, `git diff --cached`, `gh pr diff`, `git rev-parse`. Raises `GitError` on failure.
- **state.py** — file I/O for `.prview/reviews.json`. Creates directory if missing.
- **cli.py** — the `/dev/tty` restoration trick for piped stdin. Uses `select.select()` to detect pipe, `os.dup2()` to swap fd 0 back to the terminal.

## Extension Points

| To add... | Where |
|-----------|-------|
| New input source (API, etc.) | Add function in `git.py`, route in `cli.py` to `parse()` |
| New widget | Create in `widgets/`, compose in `app.py` |
| New keybinding | Add to `BINDINGS` in `app.py`, implement `action_*` method |
| New file status | Add to `DiffFile.status` type, `STATUS_MAP` in `file_list.py` |
| Diff-of-diffs | DiffData is already designed to be diffable — see DESIGN.md |
