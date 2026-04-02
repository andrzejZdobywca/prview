# Decision Log

Lightweight record of what was planned, implemented, and why.

## Convention

Each entry is a single Markdown file named `YYYY-MM-DD-<slug>.md` (e.g. `2026-04-02-initial-setup.md`).

### Entry template

```markdown
# <Title>

**Date**: YYYY-MM-DD
**Status**: planned | in-progress | done | dropped

## Context
Why this work was needed.

## Decision
What was decided / implemented.

## Commits
- `<short-sha>` <message>

## Notes
Anything else worth recording (trade-offs, follow-ups, open questions).
```

### Guidelines

- One entry per logical change or decision (not per commit).
- Keep entries short -- a few sentences per section is fine.
- Update status as work progresses rather than creating duplicate entries.
- Link to PRs or issues when relevant.
- When a PR is merged, add a one-line entry to `CHANGELOG.md` in this folder.
