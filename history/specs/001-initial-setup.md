# Initial project setup and foundations

**Date**: 2026-04-02
**Status**: done

## Context
prview needed to go from zero to a working interactive TUI diff browser, with a clean development workflow and agent-based collaboration model.

## Decision
The project was bootstrapped as a Python 3.11+ package using Textual for the TUI and unidiff for diff parsing, managed with uv. The following foundational pieces were put in place:

1. **CodeRabbit disabled** -- automated reviews turned off in favor of the agent-based workflow.
2. **README added** -- documents usage, key bindings, and dev setup.
3. **Parallel agent workflow** -- CLAUDE.md updated to use team teammates with worktree isolation.
4. **Instant file preview** -- cursor navigation triggers immediate file preview in the TUI.
5. **Agent roles defined** -- Developer, Reviewer, QA, and Chronicler roles with clear responsibilities.

## Commits
- `c5f418e` Initial commit: prview project
- `16215b3` Clean up leftover files from diffnav and rename SPEC.md to DESIGN.md
- `7ad536b` Add CLAUDE.md with dev setup and workflow guidelines (#1)
- `82c10a1` Disable CodeRabbit reviews (#2)
- `ab8aa60` Add README with usage, key bindings, and dev setup (#3)
- `523a388` Update CLAUDE.md: use team teammates for parallel work (#4)
- `d999344` Instant file preview on cursor navigation (#5)
- `cdf3759` Define agent roles: developer, reviewer, qa, chronicler (#6)

## Notes
- The Chronicler role (this log) was introduced as part of the agent roles definition.
- NOTES.md serves as a scratchpad for quick thoughts; history/CHANGELOG.md is the one-line-per-change log updated on PR merges.
