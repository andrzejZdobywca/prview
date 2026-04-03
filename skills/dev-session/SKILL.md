---
name: dev-session
description: Create the prview dev session layout in iTerm2 with named panes (claude-code, prview-viewer, agent, shell). Use when starting a dev session or setting up the workspace.
user-invocable: true
allowed-tools: [Bash]
---

# Set up dev session layout

Run the setup script to create the iTerm2 pane layout:

```bash
bash <SKILL_BASE_DIR>/setup.sh "$(pwd)"
```

The script outputs `EXISTING:...` if panes already exist, or `CREATED` with pane IDs. Report the result to the user.
