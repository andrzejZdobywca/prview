#!/bin/bash
# Opens prview in the "prview-viewer" iTerm2 pane (created by /dev-session).
# Falls back to creating a new vertical split if no named pane exists.
# Usage: open-pane.sh <project-dir> [prview-args...]

set -euo pipefail

PROJECT_DIR="$1"
shift
PRVIEW_ARGS="${*:-}"

PANE_NAME="prview-viewer"
LAUNCH_SCRIPT="/tmp/prview-launch.sh"

cat > "$LAUNCH_SCRIPT" <<LAUNCHER
#!/bin/bash
pushd "$PROJECT_DIR" >/dev/null
prview $PRVIEW_ARGS
popd >/dev/null
LAUNCHER
chmod +x "$LAUNCH_SCRIPT"

# Find the named prview-viewer pane
PANE_ID=$(it2 session list --json 2>/dev/null \
    | python3 -c "
import json, sys
for s in json.load(sys.stdin):
    if s.get('name','') == '$PANE_NAME':
        print(s['id'])
        break
" 2>/dev/null || true)

if [ -n "$PANE_ID" ]; then
    it2 session run -s "$PANE_ID" "bash $LAUNCH_SCRIPT"
    echo "REUSED:$PANE_ID"
    exit 0
fi

# No named pane — fall back to creating a new split
NEW_PANE=$(it2 session split -v 2>&1)
PANE_ID=$(echo "$NEW_PANE" | grep -oE '[A-F0-9-]{36}')
it2 session set-name -s "$PANE_ID" "$PANE_NAME"
it2 session run -s "$PANE_ID" "bash $LAUNCH_SCRIPT"
echo "CREATED:$PANE_ID"
