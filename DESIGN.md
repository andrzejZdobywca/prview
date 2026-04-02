# prview — Interactive Terminal Diff Browser

## Vision

A keyboard-driven TUI for reviewing git diffs and PRs from the terminal. Built for developers who live in tmux and want GitHub-quality review UX without leaving the terminal.

**Core insight:** PR review is a stateful workflow — triage files, examine changes in context, track progress, leave feedback, submit. Every terminal tool today only handles "look at a diff." prview builds the workflow.

## Tech Stack

- **Python 3.11+** with **Textual** framework (split-pane layouts, Tree widget, syntax highlighting, CSS styling)
- **unidiff** library for diff parsing (battle-tested, no need to write a parser)
- **Rich** (Textual dependency) for syntax highlighting via Pygments
- Distribution: `pip install prview` / `pipx install prview`

## Design Principles

### From Jane Street's Iron code review system

1. **Diff-centric review** — Show the diff between two points in history, not individual commits. Filters out noise from rebases, intermediate refactors, backed-out changes.
2. **Diff-of-diffs** — When an author updates their PR after feedback, show what changed *between review rounds*. The killer feature no other terminal tool has.
3. **Review as a workflow** — Track state: which files are reviewed, where you left off, what changed since last time.

### From terminal-first PR review pain points

1. **File-level navigation** — No more scrolling through a linear stream. File tree on the left, diff on the right.
2. **Mark-as-reviewed** — Track progress across files in large PRs. Know where you left off.
3. **Collapse irrelevant files** — Hide lockfiles, generated code, migrations. Focus on what matters.
4. **Local annotations** — Leave notes on lines without needing GitHub integration. Export later.
5. **Full-file context** — See the whole file at any point, not just 3 lines of context around hunks.

### From pragmatic engineering

1. **Ship fast, iterate** — MVP is the smallest thing that's useful. Don't over-engineer.
2. **Don't build what exists** — Use `unidiff` for parsing, Textual for UI, `gh` CLI for GitHub.
3. **Design for the future, build for today** — The `DiffData` abstraction must support diff-of-diffs later, but don't implement it yet.

## Input Modes

```
prview                          # unstaged changes (git diff)
prview --staged                 # staged changes (git diff --cached)
prview main..feature            # branch comparison
prview --pr 123                 # GitHub PR diff (via gh pr diff)
git diff | prview               # piped input
```

## Keyboard Bindings

```
j/k  or ↓/↑     Navigate file list
Enter            Select file, jump to diff view
n/p              Next/previous hunk within a file
]/[              Next/previous file (from diff view)
Tab              Toggle focus between panels
m                Mark/unmark file as reviewed
o                Open full file at PR's HEAD revision
h                Toggle hidden/ignored files
c                Add local comment/annotation on current line
/                Search within current diff
S                Save review checkpoint (for diff-of-diffs)
?                Show help overlay
q                Quit
```

## Architecture

```
tools/prview/
├── pyproject.toml              # Package config, entry point, dependencies
├── src/
│   └── prview/
│       ├── __init__.py
│       ├── app.py              # Textual App subclass, layout, keybindings
│       ├── cli.py              # CLI argument parsing
│       ├── models.py           # DiffData dataclasses (designed to be diffable)
│       ├── diff_parser.py      # Thin wrapper around unidiff → DiffData
│       ├── git.py              # Git/gh command wrappers
│       ├── state.py            # Review state persistence (.prview/)
│       ├── widgets/
│       │   ├── file_list.py    # Left panel — file list with status/stats
│       │   ├── diff_view.py    # Right panel — syntax-highlighted diff
│       │   └── help.py         # Help overlay
│       └── styles/
│           └── app.tcss        # Textual CSS
└── tests/
    ├── test_diff_parser.py
    ├── test_models.py
    └── fixtures/
        └── sample.diff
```

### Key abstraction: DiffData

A dataclass layer between `unidiff` and the widgets. This serves two purposes:
1. Decouples parsing from display (can later accept GitHub API diffs, not just unified diffs)
2. Must be **diffable itself** — this is what enables diff-of-diffs without a rewrite

```python
@dataclass
class DiffLine:
    type: Literal["add", "remove", "context"]
    content: str
    old_lineno: int | None
    new_lineno: int | None

@dataclass
class DiffHunk:
    header: str
    lines: list[DiffLine]

@dataclass
class DiffFile:
    path: str
    old_path: str | None        # for renames
    status: Literal["added", "modified", "deleted", "renamed"]
    hunks: list[DiffHunk]
    added_lines: int
    removed_lines: int

@dataclass
class DiffData:
    files: list[DiffFile]
    base_ref: str | None
    head_ref: str | None
```

## Roadmap

### Week 1-2: MVP (v0.1) — "Review workflow, not just a viewer"

- [ ] Spike: piped stdin + Textual keyboard coexistence (technical risk #1)
- [ ] Diff parser: `unidiff` → `DiffData` models
- [ ] CLI: accept piped input or run `git diff` internally
- [ ] File list widget: changed files with `+/-` counts, `A/M/D/R` status
- [ ] Diff view widget: unified diff with color coding and line numbers
- [ ] App shell: split-pane layout, keyboard navigation (`j/k`, `Tab`, `q`)
- [ ] Mark-as-reviewed: `m` key toggles, state saved to `.prview/reviews.json`
- [ ] Ship to PyPI

### Week 3-4: Attention Management (v0.2)

- [ ] File filtering: `.prview-ignore` glob patterns, `h` to toggle visibility
- [ ] Expanded context: configurable lines around hunks, `o` for full file view
- [ ] Hunk navigation: `n/p` to jump between hunks
- [ ] CLI args: `--staged`, `branch1..branch2`
- [ ] Search within diff: `/` key

### Week 5-6: Diff-of-Diffs (v0.3) — "The killer feature"

- [ ] Snapshot diffs to `.prview/snapshots/` on explicit checkpoint (`S` key)
- [ ] On re-open, detect changes since last checkpoint
- [ ] Render diff-of-diff: highlight what's new/changed since last review
- [ ] `prview review <branch>` workflow: auto-snapshot on first view, show delta on subsequent views

### Week 7-8: GitHub Integration (v0.4)

- [ ] `prview pr 123` — fetch PR diff via `gh` CLI
- [ ] PR metadata header: title, description, CI status, reviewers, labels
- [ ] Read inline review comments from GitHub
- [ ] Write inline comments, submit as GitHub review
- [ ] Sync mark-as-reviewed with GitHub's "viewed" checkboxes

### Beyond

- Side-by-side diff mode toggle
- Local comment annotations with GitHub export
- Fuzzy file finder (`Ctrl+P`)
- Merge conflict resolver
- Custom color themes
- Standalone binary via PyInstaller/nuitka

## Technical Risks

| Risk | Severity | Mitigation |
|---|---|---|
| Piped stdin + Textual keyboard conflict | High | Textual reads from `/dev/tty`; spike this day one |
| Textual performance with huge diffs (10k+ lines) | High | Lazy-render only visible viewport |
| Textual rendering in tmux | Medium | Test in tmux from day one |
| Color scheme clashes across terminals | Low | Ship one dark theme, test on common terminals |

## Dogfooding

From day one, use prview to review prview's own changes:
- After every change: `git diff | python -m prview`
- Before every commit: `git diff --cached | python -m prview`
- Test against large real-world diffs (e.g., CPython merge commits with 500+ files)

## References

- [Jane Street: Designing a code review tool, Part 1](https://blog.janestreet.com/designing-a-code-review-tool-part-1/)
- [Jane Street: Patches or Diffs](https://blog.janestreet.com/designing-a-code-review-tool-part-2-patches-or-diffs/)
- [Jane Street: Code review that isn't boring](https://blog.janestreet.com/code-review-that-isnt-boring/)
- [Jane Street: patdiff](https://github.com/janestreet/patdiff)
- [Textual framework](https://textual.textualize.io/)
- [unidiff library](https://pypi.org/project/unidiff/)
