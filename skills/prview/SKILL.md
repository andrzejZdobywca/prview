---
name: prview
description: Open the prview TUI diff browser in an iTerm2 side pane. Use when the user wants to view PR diffs, open prview, or browse diffs interactively.
user-invocable: true
argument-hint: "[args like HEAD~3, --staged, main..feature]"
allowed-tools: [Bash]
---

# Open prview in a side pane

First, check that `prview` is installed:

```bash
command -v prview >/dev/null 2>&1 && echo "OK" || echo "MISSING"
```

If `MISSING`, tell the user to install it with `uv tool install prview` and stop.

Next, check if there's already a prview pane open:

```bash
PANE_ID=$(cat /tmp/prview-pane-id 2>/dev/null) && it2 session list --json | python3 -c "import json,sys; ids=[s['id'] for s in json.load(sys.stdin)]; exit(0 if '$PANE_ID' in ids else 1)" && echo "EXISTING:$PANE_ID" || echo "NONE"
```

- If the output is `EXISTING:<ID>`, the pane is still alive. Run prview in it:
```bash
it2 session run -s "<PANE_ID>" "cd $(pwd) && prview $ARGUMENTS"
```

- If the output is `NONE`, create a new split pane:
```bash
it2 session split -v 2>&1
```
Save the new pane ID and run prview:
```bash
echo "<PANE_ID>" > /tmp/prview-pane-id && it2 session run -s "<PANE_ID>" "cd $(pwd) && prview $ARGUMENTS"
```

Report the result to the user. If any command fails, relay the error.
