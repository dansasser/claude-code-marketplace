#!/bin/bash
# Generate prompts for combining session results

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <combination_type> <orch_id> [angle_numbers...]"
    echo ""
    echo "Combination types:"
    echo "  two-way <orch_id> <angle1> <angle2>           Combine two perspectives"
    echo "  three-way <orch_id> <angle1> <angle2> <angle3> Combine three perspectives"
    echo "  full-synthesis <orch_id>                      Combine all angles"
    echo "  custom <orch_id> <angle1,angle2,...>          Custom angle combination"
    exit 1
fi

COMBINATION_TYPE="$1"
ORCH_ID="$2"
REGISTRY_DIR=$(python3 -c "from pathlib import Path; print(Path.home() / '.claude' / 'orchestrations')")
REGISTRY_FILE="$REGISTRY_DIR/${ORCH_ID}.json"

if [[ ! -f "$REGISTRY_FILE" ]]; then
    echo "Error: Orchestration $ORCH_ID not found"
    exit 1
fi

# Load orchestration data
ORCH_DATA=$(cat "$REGISTRY_FILE")
TARGET=$(echo "$ORCH_DATA" | python3 -c "import json,sys; print(json.load(sys.stdin)['target'])")
STRATEGY=$(echo "$ORCH_DATA" | python3 -c "import json,sys; print(json.load(sys.stdin)['strategy'])")

# Function to get angle summary
get_angle_summary() {
    local angle_num=$1
    local session_id=$2
    local angle_name=$3
    local result_file=$4

    if [[ -n "$result_file" ]] && [[ -f "$result_file" ]]; then
        # Extract response/thinking from result file
        RESPONSE=$(python3 <<PYTHON
import json
import sys

try:
    with open("$result_file", 'r') as f:
        data = json.load(f)

    # Try 'thinking' field first (for kimi-k2-thinking), then 'response'
    content = data.get('thinking') or data.get('response') or ''

    # Truncate to first 2000 chars for summary
    if len(content) > 2000:
        content = content[:2000] + "...[truncated]"

    print(content)
except Exception as e:
    print(f"[Error reading result: {e}]", file=sys.stderr)
PYTHON
)
    else
        RESPONSE="[Result file not available - session ID: $session_id]"
    fi

    echo "$RESPONSE"
}

case "$COMBINATION_TYPE" in
    two-way)
        if [[ $# -lt 4 ]]; then
            echo "Usage: $0 two-way <orch_id> <angle1> <angle2>"
            exit 1
        fi

        ANGLE1="$3"
        ANGLE2="$4"

        # Get angle details
        ANGLE1_DATA=$(python3 <<PYTHON
import json
from pathlib import Path

registry_file = Path.home() / '.claude' / 'orchestrations' / '${ORCH_ID}.json'
with open(registry_file, 'r') as f:
    data = json.load(f)
for angle in data['angles']:
    if angle['angle_number'] == $ANGLE1:
        print(f"{angle['angle_name']}|{angle['session_id']}|{angle.get('result_file', '')}")
        break
PYTHON
)

        ANGLE2_DATA=$(python3 <<PYTHON
import json
from pathlib import Path

registry_file = Path.home() / '.claude' / 'orchestrations' / '${ORCH_ID}.json'
with open(registry_file, 'r') as f:
    data = json.load(f)
for angle in data['angles']:
    if angle['angle_number'] == $ANGLE2:
        print(f"{angle['angle_name']}|{angle['session_id']}|{angle.get('result_file', '')}")
        break
PYTHON
)

        IFS='|' read -r ANGLE1_NAME ANGLE1_SESSION ANGLE1_FILE <<< "$ANGLE1_DATA"
        IFS='|' read -r ANGLE2_NAME ANGLE2_SESSION ANGLE2_FILE <<< "$ANGLE2_DATA"

        SUMMARY1=$(get_angle_summary $ANGLE1 "$ANGLE1_SESSION" "$ANGLE1_NAME" "$ANGLE1_FILE")
        SUMMARY2=$(get_angle_summary $ANGLE2 "$ANGLE2_SESSION" "$ANGLE2_NAME" "$ANGLE2_FILE")

        # Generate two-way combination prompt
        cat <<EOF
CONTEXT: You previously analyzed "$TARGET" from two different perspectives:

=== PERSPECTIVE 1: $ANGLE1_NAME (Session: $ANGLE1_SESSION) ===
$SUMMARY1

=== PERSPECTIVE 2: $ANGLE2_NAME (Session: $ANGLE2_SESSION) ===
$SUMMARY2

TASK: Cross-reference these two perspectives and identify:
1. How do findings from $ANGLE1_NAME relate to $ANGLE2_NAME?
2. Where do these perspectives conflict or reinforce each other?
3. What insights emerge from combining both viewpoints?
4. What actionable recommendations span both perspectives?

Provide a synthesis that integrates both analyses.
EOF
        ;;

    three-way)
        if [[ $# -lt 5 ]]; then
            echo "Usage: $0 three-way <orch_id> <angle1> <angle2> <angle3>"
            exit 1
        fi

        ANGLE1="$3"
        ANGLE2="$4"
        ANGLE3="$5"

        # Get all three angles (similar to two-way but with 3)
        ANGLES=($ANGLE1 $ANGLE2 $ANGLE3)
        SUMMARIES=()
        NAMES=()
        SESSIONS=()

        for angle_num in "${ANGLES[@]}"; do
            ANGLE_DATA=$(python3 <<PYTHON
import json
from pathlib import Path

registry_file = Path.home() / '.claude' / 'orchestrations' / '${ORCH_ID}.json'
with open(registry_file, 'r') as f:
    data = json.load(f)
for angle in data['angles']:
    if angle['angle_number'] == $angle_num:
        print(f"{angle['angle_name']}|{angle['session_id']}|{angle.get('result_file', '')}")
        break
PYTHON
)
            IFS='|' read -r NAME SESSION FILE <<< "$ANGLE_DATA"
            NAMES+=("$NAME")
            SESSIONS+=("$SESSION")
            SUMMARIES+=("$(get_angle_summary $angle_num "$SESSION" "$NAME" "$FILE")")
        done

        cat <<EOF
CONTEXT: You previously analyzed "$TARGET" from three different perspectives:

=== PERSPECTIVE 1: ${NAMES[0]} (Session: ${SESSIONS[0]}) ===
${SUMMARIES[0]}

=== PERSPECTIVE 2: ${NAMES[1]} (Session: ${SESSIONS[1]}) ===
${SUMMARIES[1]}

=== PERSPECTIVE 3: ${NAMES[2]} (Session: ${SESSIONS[2]}) ===
${SUMMARIES[2]}

TASK: Perform a three-way cross-analysis:
1. What common themes emerge across all three perspectives?
2. Where do perspectives conflict, and how can conflicts be resolved?
3. What unique insights does each perspective contribute?
4. What high-priority actions are supported by multiple perspectives?

Provide a comprehensive synthesis integrating all three analyses.
EOF
        ;;

    full-synthesis)
        # Combine all angles
        ALL_ANGLES=$(python3 <<PYTHON
import json
from pathlib import Path

registry_file = Path.home() / '.claude' / 'orchestrations' / '${ORCH_ID}.json'
with open(registry_file, 'r') as f:
    data = json.load(f)
for angle in data['angles']:
    print(f"{angle['angle_number']}|{angle['angle_name']}|{angle['session_id']}|{angle.get('result_file', '')}")
PYTHON
)

        PROMPT="CONTEXT: You previously performed a comprehensive $STRATEGY analysis of \"$TARGET\" from multiple perspectives:\n\n"

        while IFS='|' read -r num name session file; do
            SUMMARY=$(get_angle_summary "$num" "$session" "$name" "$file")
            PROMPT+="=== PERSPECTIVE $num: $name (Session: $session) ===\n"
            PROMPT+="$SUMMARY\n\n"
        done <<< "$ALL_ANGLES"

        PROMPT+="TASK: Create an executive summary with:\n"
        PROMPT+="1. Top 5 critical issues (across all perspectives)\n"
        PROMPT+="2. Quick wins (easy high-impact fixes)\n"
        PROMPT+="3. Major refactoring needs\n"
        PROMPT+="4. Priority recommendations\n"
        PROMPT+="5. Overall health assessment\n\n"
        PROMPT+="Provide a comprehensive final report synthesizing all perspectives."

        echo -e "$PROMPT"
        ;;

    custom)
        if [[ $# -lt 3 ]]; then
            echo "Usage: $0 custom <orch_id> <angle1,angle2,...>"
            exit 1
        fi

        CUSTOM_ANGLES="$3"
        IFS=',' read -ra ANGLE_ARRAY <<< "$CUSTOM_ANGLES"

        PROMPT="CONTEXT: You previously analyzed \"$TARGET\" from selected perspectives:\n\n"

        for angle_num in "${ANGLE_ARRAY[@]}"; do
            ANGLE_DATA=$(python3 <<PYTHON
import json
from pathlib import Path

registry_file = Path.home() / '.claude' / 'orchestrations' / '${ORCH_ID}.json'
with open(registry_file, 'r') as f:
    data = json.load(f)
for angle in data['angles']:
    if angle['angle_number'] == $angle_num:
        print(f"{angle['angle_name']}|{angle['session_id']}|{angle.get('result_file', '')}")
        break
PYTHON
)
            IFS='|' read -r NAME SESSION FILE <<< "$ANGLE_DATA"
            SUMMARY=$(get_angle_summary "$angle_num" "$SESSION" "$NAME" "$FILE")

            PROMPT+="=== PERSPECTIVE $angle_num: $NAME (Session: $SESSION) ===\n"
            PROMPT+="$SUMMARY\n\n"
        done

        PROMPT+="TASK: Synthesize insights from these selected perspectives and identify:\n"
        PROMPT+="1. Common themes and patterns\n"
        PROMPT+="2. Conflicts or contradictions\n"
        PROMPT+="3. Combined recommendations\n"
        PROMPT+="4. Next steps\n"

        echo -e "$PROMPT"
        ;;

    *)
        echo "Unknown combination type: $COMBINATION_TYPE"
        echo "Valid types: two-way, three-way, full-synthesis, custom"
        exit 1
        ;;
esac
