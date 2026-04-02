# prview

Interactive terminal diff browser built with Python 3.11+, Textual, and unidiff.

## Development

- Package manager: uv
- Run: `uv run prview` or `uv run python -m prview`
- Tests: `uv run pytest`

## Git workflow

- Never commit directly to `main`. Always create a feature branch and open a PR.

## Agent workflow

- When delegating tasks, spawn a **team teammate** so the lead (main session) can continue working in parallel.
- Teammates should use `isolation: "worktree"` so they work on their own branch in a separate worktree.
- Permission requests from teammates will bubble up to the lead for approval.
