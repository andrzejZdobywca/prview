# prview

Interactive terminal diff browser for developers who live in the terminal. Built with [Textual](https://textual.textualize.io/) for a keyboard-driven review experience — file navigation, mark-as-reviewed tracking, and split-pane layout without leaving your shell.

## Installation

```bash
pip install prview
# or
pipx install prview
```

## Usage

```bash
prview                        # unstaged changes (git diff)
prview --staged               # staged changes (git diff --cached)
prview main..feature          # branch comparison
git diff | prview             # piped input
```

## Claude Code Plugin

prview is available as a [Claude Code](https://claude.ai/claude-code) plugin that opens the diff browser in an iTerm2 side pane.

**Install:**

```
/plugin marketplace add andrzejZdobywca/prview
/plugin install prview@prview
```

**Use:**

```
/prview
/prview --staged
/prview main..feature
```

## Key Bindings

| Key | Action |
|-----|--------|
| `j/k` or `↓/↑` | Navigate file list |
| `Enter` | Select file |
| `n/p` | Next/previous file |
| `Tab` | Toggle focus between panels |
| `m` | Mark/unmark file as reviewed |
| `?` | Show help overlay |
| `q` | Quit |

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for how the code is structured.

## Development

Requires Python 3.11+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run prview
uv run pytest
```
