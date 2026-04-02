# prview

Interactive terminal diff browser built with Python 3.11+, Textual, and unidiff.

## Development

- Package manager: uv
- Run: `uv run prview` or `uv run python -m prview`
- Tests: `uv run pytest`

## Git workflow

- Never commit directly to `main`. Always create a feature branch and open a PR.
- When spawning subagents for tasks, always use `isolation: "worktree"` so the agent works on its own branch in a separate worktree. This keeps the main working tree free for parallel work.
