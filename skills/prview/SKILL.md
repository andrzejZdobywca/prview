---
name: prview
description: Open the prview TUI diff browser in an iTerm2 side pane. Use when the user wants to view PR diffs, open prview, or browse diffs interactively.
user-invocable: true
argument-hint: "[args like HEAD~3, --staged, main..feature]"
allowed-tools: [Bash]
---

# Open prview in a side pane

Run the open-pane script. It checks that `prview` is installed, reuses an existing pane if possible, or creates a new one. The base directory for this skill is provided above — use it to locate `open-pane.sh`:

```bash
command -v prview >/dev/null 2>&1 && bash <SKILL_BASE_DIR>/open-pane.sh "$(pwd)" $ARGUMENTS || echo "MISSING: install with 'uv tool install prview'"
```

The script outputs `REUSED:<pane-id>` or `CREATED:<pane-id>`. If the output is `MISSING`, tell the user to install prview and stop. Otherwise report the result. If the command fails, relay the error.
