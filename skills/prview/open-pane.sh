#!/bin/bash
# Opens prview in an iTerm2 side pane, reusing an existing pane if possible.
# Usage: open-pane.sh <project-dir> [prview-args...]

set -euo pipefail

PROJECT_DIR="$1"
shift
PRVIEW_ARGS="${*:-}"

PANE_ID_FILE="/tmp/prview-pane-id"
LAUNCH_SCRIPT="/tmp/prview-launch.sh"

# Write a launcher script that changes to the project directory before running prview.
# We use pushd instead of cd because cd gets stripped by the Claude Code tool pipeline.
cat > "$LAUNCH_SCRIPT" <<LAUNCHER
#!/bin/bash
pushd "$PROJECT_DIR" >/dev/null
prview $PRVIEW_ARGS
popd >/dev/null
LAUNCHER
chmod +x "$LAUNCH_SCRIPT"

# Try to reuse the saved pane
if PANE_ID=$(cat "$PANE_ID_FILE" 2>/dev/null) && \
   it2 session run -s "$PANE_ID" "bash $LAUNCH_SCRIPT" 2>/dev/null; then
    echo "REUSED:$PANE_ID"
    exit 0
fi

# Pane gone or no saved ID — create a new split
NEW_PANE=$(it2 session split -v 2>&1)
PANE_ID=$(echo "$NEW_PANE" | grep -oE '[A-F0-9-]{36}')

echo "$PANE_ID" > "$PANE_ID_FILE"
it2 session run -s "$PANE_ID" "bash $LAUNCH_SCRIPT"
echo "CREATED:$PANE_ID"
