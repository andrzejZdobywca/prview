# prview — Improvement Notes

These are raw notes for future work. We develop from this list — elaborate items into plans, implement them, remove when done.

## Bugs
- CLI crashes when `/dev/tty` is unavailable (CI, IDE terminals) — fix started, needs real terminal testing

## Agent Roles
- Predefined reusable agents: Developer, QA, Reviewer, Architect
- QA agent should be able to call widget/app methods directly (every UI action needs a programmatic API, not just keybindings)
- Pre-commit or pre-merge reviewer agent that checks code quality, regressions, missing tests
- **Change narration agent** — reviews what changed, why, and how it connects to the plan. Summarizes for PR descriptions and commit messages. Links changes back to NOTES.md items. Could run at PR creation time rather than pre-commit. Goal: anyone reading the PR can understand the intent without digging through code

## Development Workflow
- Develop entirely from NOTES.md → plans → implementation → remove note when done
- Changes should be traceable: note → plan → PR → commits
- An agent (or hook) at PR/merge time that generates a summary linking changes to the original note/plan
- PRs and commits should reference which note they address

## UX
- j/k should immediately preview the file (no Enter required to see diff)
- Keybinding to open current file in default IDE ($EDITOR / code / cursor)
- Inline comments on specific lines, stored locally in .prview/comments.json
- GitHub PR comment sync — show existing GH comments inline, submit new ones as a review via gh CLI

## Distribution
- Make prview runnable globally without sourcing venv (pipx, shell alias, or standalone binary)

## Code Quality
- No tests for cli.py or app.py integration
