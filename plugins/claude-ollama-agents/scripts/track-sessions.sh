#!/bin/bash
# Manage parallel orchestration session registry

REGISTRY_DIR=$(python3 -c "from pathlib import Path; print(Path.home() / '.claude' / 'orchestrations')")
mkdir -p "$REGISTRY_DIR"

command="$1"

case "$command" in
    create)
        # Create new orchestration
        # Usage: track-sessions.sh create <target> <strategy> [model]
        if [[ $# -lt 3 ]]; then
            echo "Usage: $0 create <target> <strategy> [model]"
            exit 1
        fi

        TARGET="$2"
        STRATEGY="$3"
        MODEL="${4:-kimi-k2-thinking:cloud}"

        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
        ORCH_ID="orch_${TIMESTAMP}_$$"
        REGISTRY_FILE="$REGISTRY_DIR/${ORCH_ID}.json"

        cat > "$REGISTRY_FILE" <<EOF
{
  "orchestration_id": "$ORCH_ID",
  "target": "$TARGET",
  "strategy": "$STRATEGY",
  "model": "$MODEL",
  "angles": [],
  "created_at": "$(date -Iseconds)",
  "registry_file": "$REGISTRY_FILE"
}
EOF
        echo "$ORCH_ID"
        ;;

    add)
        # Add angle session to orchestration
        # Usage: track-sessions.sh add <orch_id> <angle_number> <angle_name> <session_id> [was_chunked] [result_file]
        if [[ $# -lt 5 ]]; then
            echo "Usage: $0 add <orch_id> <angle_number> <angle_name> <session_id> [was_chunked] [result_file]"
            exit 1
        fi

        ORCH_ID="$2"
        ANGLE_NUM="$3"
        ANGLE_NAME="$4"
        SESSION_ID="$5"
        WAS_CHUNKED="${6:-false}"
        RESULT_FILE="${7:-}"

        REGISTRY_FILE="$REGISTRY_DIR/${ORCH_ID}.json"

        if [[ ! -f "$REGISTRY_FILE" ]]; then
            echo "Error: Orchestration $ORCH_ID not found"
            exit 1
        fi

        # Create angle entry
        ANGLE_ENTRY=$(cat <<EOF
{
  "angle_number": $ANGLE_NUM,
  "angle_name": "$ANGLE_NAME",
  "session_id": "$SESSION_ID",
  "was_chunked": $WAS_CHUNKED,
  "result_file": "$RESULT_FILE",
  "completed_at": "$(date -Iseconds)"
}
EOF
)

        # Add to registry using Python (more reliable than jq for complex JSON editing)
        python3 <<PYTHON
import json
import sys
from pathlib import Path

registry_file = Path.home() / '.claude' / 'orchestrations' / '${ORCH_ID}.json'
angle_entry = $ANGLE_ENTRY

with open(registry_file, 'r') as f:
    data = json.load(f)

data['angles'].append(angle_entry)

with open(registry_file, 'w') as f:
    json.dump(data, f, indent=2)

print(f"Added angle $ANGLE_NUM to {str(registry_file)}")
PYTHON
        ;;

    list)
        # List all angles in orchestration
        # Usage: track-sessions.sh list <orch_id>
        if [[ $# -lt 2 ]]; then
            echo "Usage: $0 list <orch_id>"
            exit 1
        fi

        ORCH_ID="$2"
        REGISTRY_FILE="$REGISTRY_DIR/${ORCH_ID}.json"

        if [[ ! -f "$REGISTRY_FILE" ]]; then
            echo "Error: Orchestration $ORCH_ID not found"
            exit 1
        fi

        cat "$REGISTRY_FILE"
        ;;

    get)
        # Get specific session ID by angle number
        # Usage: track-sessions.sh get <orch_id> <angle_number>
        if [[ $# -lt 3 ]]; then
            echo "Usage: $0 get <orch_id> <angle_number>"
            exit 1
        fi

        ORCH_ID="$2"
        ANGLE_NUM="$3"
        REGISTRY_FILE="$REGISTRY_DIR/${ORCH_ID}.json"

        if [[ ! -f "$REGISTRY_FILE" ]]; then
            echo "Error: Orchestration $ORCH_ID not found"
            exit 1
        fi

        python3 <<PYTHON
import json
import sys
from pathlib import Path

registry_file = Path.home() / '.claude' / 'orchestrations' / '${ORCH_ID}.json'

with open(registry_file, 'r') as f:
    data = json.load(f)

for angle in data['angles']:
    if angle['angle_number'] == $ANGLE_NUM:
        print(angle['session_id'])
        exit(0)

print("Angle $ANGLE_NUM not found", file=sys.stderr)
exit(1)
PYTHON
        ;;

    get-all-sessions)
        # Get all session IDs as array
        # Usage: track-sessions.sh get-all-sessions <orch_id>
        if [[ $# -lt 2 ]]; then
            echo "Usage: $0 get-all-sessions <orch_id>"
            exit 1
        fi

        ORCH_ID="$2"
        REGISTRY_FILE="$REGISTRY_DIR/${ORCH_ID}.json"

        if [[ ! -f "$REGISTRY_FILE" ]]; then
            echo "Error: Orchestration $ORCH_ID not found"
            exit 1
        fi

        python3 <<PYTHON
import json
from pathlib import Path

registry_file = Path.home() / '.claude' / 'orchestrations' / '${ORCH_ID}.json'

with open(registry_file, 'r') as f:
    data = json.load(f)

session_ids = [angle['session_id'] for angle in data['angles']]
print(' '.join(session_ids))
PYTHON
        ;;

    list-all)
        # List all orchestrations
        # Usage: track-sessions.sh list-all
        ls -1 "$REGISTRY_DIR"/*.json 2>/dev/null | while read -r file; do
            python3 <<PYTHON
import json
with open("$file", 'r') as f:
    data = json.load(f)
print(f"{data['orchestration_id']}: {data['strategy']} on {data['target']} ({len(data['angles'])} angles)")
PYTHON
        done
        ;;

    *)
        echo "Usage: $0 <command> [args...]"
        echo ""
        echo "Commands:"
        echo "  create <target> <strategy> [model]           Create new orchestration"
        echo "  add <orch_id> <angle_num> <name> <session>   Add angle to orchestration"
        echo "  list <orch_id>                               Show full orchestration details"
        echo "  get <orch_id> <angle_num>                    Get session ID for angle"
        echo "  get-all-sessions <orch_id>                   Get all session IDs"
        echo "  list-all                                     List all orchestrations"
        exit 1
        ;;
esac
