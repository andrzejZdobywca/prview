#!/bin/bash
# Creates the prview dev session layout in iTerm2.
#
# Layout (claude-code = the pane where this script runs):
# ┌─────────────────────┬──────────┐
# │                     │  agent   │
# │    claude-code      ├──────────┤
# │                     │  shell   │
# ├─────────────────────┴──────────┤
# │        prview-viewer           │
# └────────────────────────────────┘
#
# Panes are tagged via session variables (user.pane_role) since
# iTerm2 overwrites display names with the running process.
#
# Usage: setup.sh [project-dir]

set -euo pipefail

PROJECT_DIR="${1:-$(pwd)}"

# Get current session's tab_id to scope checks to this tab only
# (window_id is shared across all tabs in a window; tab_id is unique per tab)
MY_ID=$(it2 session get-var id)
MY_TAB=$(it2 session list --json 2>/dev/null | python3 -c "
import json, sys
for s in json.load(sys.stdin):
    if s['id'] == '$MY_ID':
        print(s['tab_id'])
        break
")

# Check if the layout already exists in THIS tab
find_pane_in_tab() {
    local role="$1"
    it2 session list --json 2>/dev/null | python3 -c "
import json, sys, subprocess
for s in json.load(sys.stdin):
    if s['tab_id'] != '$MY_TAB':
        continue
    try:
        out = subprocess.check_output(
            ['it2', 'session', 'get-var', '-s', s['id'], 'user.pane_role'],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        if out == '$role':
            print(s['id'])
            break
    except Exception:
        pass
" 2>/dev/null
}

existing=$(find_pane_in_tab "claude-code")
if [ -n "$existing" ]; then
    echo "EXISTING"
    echo "Dev session panes already exist in this window. Skipping creation."
    exit 0
fi

# Helper: extract session ID from it2 split output
extract_id() {
    grep -oE '[A-F0-9-]{36}' | head -1
}

# Tag a pane with its role
tag_pane() {
    local id="$1" role="$2"
    it2 session set-var -s "$id" user.pane_role "$role"
}

# Current pane = claude-code (stays top-left — it2 split keeps original pane left/top)
CLAUDE_ID=$(it2 session get-var id)
tag_pane "$CLAUDE_ID" "claude-code"

# Split horizontally → bottom half = prview-viewer
PRVIEW_ID=$(it2 session split -s "$CLAUDE_ID" 2>&1 | extract_id)
tag_pane "$PRVIEW_ID" "prview-viewer"
it2 session run -s "$PRVIEW_ID" "cd '$PROJECT_DIR'"

# Focus back to top, split vertically → right half = will become agent+shell
it2 session focus "$CLAUDE_ID"
RIGHT_ID=$(it2 session split -v -s "$CLAUDE_ID" 2>&1 | extract_id)

# Split right column horizontally → top-right=agent, bottom-right=shell
SHELL_ID=$(it2 session split -s "$RIGHT_ID" 2>&1 | extract_id)
tag_pane "$RIGHT_ID" "agent"
tag_pane "$SHELL_ID" "shell"
it2 session run -s "$RIGHT_ID" "cd '$PROJECT_DIR'"
it2 session run -s "$SHELL_ID" "cd '$PROJECT_DIR'"

# Focus back to claude-code
it2 session focus "$CLAUDE_ID"

echo "CREATED"
echo "  claude-code:   $CLAUDE_ID"
echo "  prview-viewer: $PRVIEW_ID"
echo "  agent:         $RIGHT_ID"
echo "  shell:         $SHELL_ID"
