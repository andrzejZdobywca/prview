#!/bin/bash
# Creates the prview dev session layout in iTerm2.
#
# Layout:
# ┌──────────┬─────────────────────┐
# │  agent   │                     │
# ├──────────┤    claude-code      │
# │  shell   │                     │
# ├──────────┴─────────────────────┤
# │                                │
# │        prview-viewer           │
# │                                │
# └────────────────────────────────┘
#
# Usage: setup.sh [project-dir]

set -euo pipefail

PROJECT_DIR="${1:-$(pwd)}"

# Check if the layout already exists by looking for named panes
existing=$(it2 session list --json 2>/dev/null \
    | python3 -c "
import json, sys
names = {s.get('name','') for s in json.load(sys.stdin)}
needed = {'claude-code', 'prview-viewer', 'agent', 'shell'}
found = names & needed
if found:
    print(','.join(sorted(found)))
" 2>/dev/null || true)

if [ -n "$existing" ]; then
    echo "EXISTING:$existing"
    echo "Dev session panes already exist. Skipping creation."
    exit 0
fi

# Helper: extract session ID from it2 split output
extract_id() {
    grep -oE '[A-F0-9-]{36}' | head -1
}

# Current pane becomes claude-code
CLAUDE_ID=$(it2 session get-var id)
it2 session set-name -s "$CLAUDE_ID" "claude-code"

# Split horizontally → bottom half becomes prview-viewer
PRVIEW_ID=$(it2 session split -s "$CLAUDE_ID" 2>&1 | extract_id)
it2 session set-name -s "$PRVIEW_ID" "prview-viewer"
it2 session run -s "$PRVIEW_ID" "cd '$PROJECT_DIR'"

# Focus back to claude-code (top), split vertically → left half
it2 session focus "$CLAUDE_ID"
LEFT_ID=$(it2 session split -v -s "$CLAUDE_ID" 2>&1 | extract_id)

# The new pane from -v split goes to the right, so LEFT_ID is actually
# the new right pane. But we want claude-code on the right.
# Let's check: in iTerm2, -v split creates a pane to the right of current.
# So LEFT_ID is the right pane. We need to swap names.
# Actually: the current pane stays on the left, new pane goes right.
# So CLAUDE_ID is now left, LEFT_ID is right.
# We want claude-code on the RIGHT, agent+shell on the LEFT.
# So swap: LEFT_ID becomes claude-code, CLAUDE_ID becomes the left column.
it2 session set-name -s "$LEFT_ID" "claude-code"
LEFT_COL_ID="$CLAUDE_ID"

# Split the left column horizontally → top=agent, bottom=shell
it2 session focus "$LEFT_COL_ID"
SHELL_ID=$(it2 session split -s "$LEFT_COL_ID" 2>&1 | extract_id)
it2 session set-name -s "$LEFT_COL_ID" "agent"
it2 session set-name -s "$SHELL_ID" "shell"
it2 session run -s "$SHELL_ID" "cd '$PROJECT_DIR'"

# Focus back to claude-code
it2 session focus "$LEFT_ID"

echo "CREATED"
echo "  claude-code:   $LEFT_ID"
echo "  prview-viewer: $PRVIEW_ID"
echo "  agent:         $LEFT_COL_ID"
echo "  shell:         $SHELL_ID"
