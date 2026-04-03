#!/bin/bash
# Opens prview in the "prview-viewer" iTerm2 pane (created by /dev-session).
# Falls back to creating a new vertical split if no tagged pane exists.
# Usage: open-pane.sh <project-dir> [prview-args...]

set -euo pipefail

PROJECT_DIR="$1"
shift
PRVIEW_ARGS="${*:-}"

LAUNCH_SCRIPT="/tmp/prview-launch.sh"

cat > "$LAUNCH_SCRIPT" <<LAUNCHER
#!/bin/bash
pushd "$PROJECT_DIR" >/dev/null
prview $PRVIEW_ARGS
popd >/dev/null
LAUNCHER
chmod +x "$LAUNCH_SCRIPT"

# Find the prview-viewer pane in the same window as the current session
PANE_ID=$(it2 session list --json 2>/dev/null | python3 -c "
import json, sys, subprocess
my_id = subprocess.check_output(['it2', 'session', 'get-var', 'id'],
                                 stderr=subprocess.DEVNULL).decode().strip()
sessions = json.load(sys.stdin)
my_tab = next(s['tab_id'] for s in sessions if s['id'] == my_id)
for s in sessions:
    if s['tab_id'] != my_tab:
        continue
    try:
        out = subprocess.check_output(
            ['it2', 'session', 'get-var', '-s', s['id'], 'user.pane_role'],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        if out == 'prview-viewer':
            print(s['id'])
            break
    except Exception:
        pass
" 2>/dev/null || true)

if [ -n "$PANE_ID" ]; then
    it2 session run -s "$PANE_ID" "bash $LAUNCH_SCRIPT"
    echo "REUSED:$PANE_ID"
    exit 0
fi

# No tagged pane — fall back to creating a new split
NEW_PANE=$(it2 session split -v 2>&1)
PANE_ID=$(echo "$NEW_PANE" | grep -oE '[A-F0-9-]{36}')
it2 session set-var -s "$PANE_ID" user.pane_role "prview-viewer"
it2 session run -s "$PANE_ID" "bash $LAUNCH_SCRIPT"
echo "CREATED:$PANE_ID"
