#!/bin/bash
# Suggest decomposition strategy and angles for parallel analysis

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <target> <user_prompt>"
    exit 1
fi

TARGET="$1"
USER_PROMPT="$2"

# Determine if target is file or directory
if [[ -f "$TARGET" ]]; then
    TARGET_TYPE="file"
elif [[ -d "$TARGET" ]]; then
    TARGET_TYPE="directory"
else
    echo "{\"error\": \"Target not found: $TARGET\"}"
    exit 1
fi

# Analyze prompt for strategy hints
PROMPT_LOWER=$(echo "$USER_PROMPT" | tr '[:upper:]' '[:lower:]')

# Default strategy
STRATEGY="Software Quality"
ANGLES=()

# Strategy selection logic
if [[ "$PROMPT_LOWER" =~ (feature|pr|pull request|implementation) ]]; then
    STRATEGY="Feature Analysis"
    ANGLES=(
        '{"number": 1, "name": "Requirements", "description": "Does it meet specs and requirements?", "task_type": "code"}'
        '{"number": 2, "name": "User Experience", "description": "UX/UI concerns, accessibility, usability", "task_type": "general"}'
        '{"number": 3, "name": "Integration", "description": "How does it fit with existing system?", "task_type": "architecture"}'
        '{"number": 4, "name": "Edge Cases", "description": "What breaks? What is missing?", "task_type": "code"}'
    )
elif [[ "$PROMPT_LOWER" =~ (test|testing|coverage|documentation|docs) ]]; then
    STRATEGY="Implementation Review"
    ANGLES=(
        '{"number": 1, "name": "Correctness", "description": "Logic bugs, edge cases, error handling", "task_type": "code"}'
        '{"number": 2, "name": "Testing", "description": "Coverage, test quality, missing tests", "task_type": "code"}'
        '{"number": 3, "name": "Documentation", "description": "Clarity, completeness, accuracy", "task_type": "general"}'
        '{"number": 4, "name": "Dependencies", "description": "External deps, version conflicts, licensing", "task_type": "code"}'
    )
else
    # Default: Software Quality
    STRATEGY="Software Quality"
    ANGLES=(
        '{"number": 1, "name": "Security", "description": "Vulnerabilities, attack vectors, security patterns", "task_type": "security"}'
        '{"number": 2, "name": "Architecture", "description": "Design patterns, modularity, coupling, scalability", "task_type": "architecture"}'
        '{"number": 3, "name": "Performance", "description": "Bottlenecks, efficiency, resource usage", "task_type": "performance"}'
        '{"number": 4, "name": "Code Quality", "description": "Maintainability, readability, best practices", "task_type": "code"}'
    )
fi

# Determine scope and directory operations for each angle based on target type
if [[ "$TARGET_TYPE" == "directory" ]]; then
    # For directories, use directory operations for efficiency
    # Format: @./dir/:operation
    DIR_REF="@./${TARGET%/}/"  # Normalize path for @./ syntax

    case "$STRATEGY" in
        "Software Quality")
            # Security: Use search operations for vulnerability patterns
            ANGLES[0]="{\"number\": 1, \"name\": \"Security\", \"description\": \"Vulnerabilities, attack vectors, security patterns\", \"scope\": \"${DIR_REF}\", \"directory_ops\": [\"${DIR_REF}:search:eval\", \"${DIR_REF}:search:exec\", \"${DIR_REF}:search:password\", \"${DIR_REF}:search:secret\"]}"

            # Architecture: Use tree for structure overview
            ANGLES[1]="{\"number\": 2, \"name\": \"Architecture\", \"description\": \"Design patterns, modularity, coupling, scalability\", \"scope\": \"${DIR_REF}\", \"directory_ops\": [\"${DIR_REF}:tree\", \"${DIR_REF}:search:import\"]}"

            # Performance: Use search for performance patterns
            ANGLES[2]="{\"number\": 3, \"name\": \"Performance\", \"description\": \"Bottlenecks, efficiency, resource usage\", \"scope\": \"${DIR_REF}\", \"directory_ops\": [\"${DIR_REF}:search:for.*range\", \"${DIR_REF}:search:while\", \"${DIR_REF}:search:query\"]}"

            # Code Quality: Use tree + search for TODOs
            ANGLES[3]="{\"number\": 4, \"name\": \"Code Quality\", \"description\": \"Maintainability, readability, best practices\", \"scope\": \"${DIR_REF}\", \"directory_ops\": [\"${DIR_REF}:tree\", \"${DIR_REF}:search:TODO\", \"${DIR_REF}:search:FIXME\"]}"
            ;;
        "Feature Analysis")
            ANGLES[0]="{\"number\": 1, \"name\": \"Requirements\", \"description\": \"Does it meet specs and requirements?\", \"scope\": \"${DIR_REF}\", \"directory_ops\": [\"${DIR_REF}:tree\"]}"
            ANGLES[1]="{\"number\": 2, \"name\": \"User Experience\", \"description\": \"UX/UI concerns, accessibility, usability\", \"scope\": \"${DIR_REF}\", \"directory_ops\": [\"${DIR_REF}:tree\"]}"
            ANGLES[2]="{\"number\": 3, \"name\": \"Integration\", \"description\": \"How does it fit with existing system?\", \"scope\": \"${DIR_REF}\", \"directory_ops\": [\"${DIR_REF}:tree\", \"${DIR_REF}:search:import\"]}"
            ANGLES[3]="{\"number\": 4, \"name\": \"Edge Cases\", \"description\": \"What breaks? What is missing?\", \"scope\": \"${DIR_REF}\", \"directory_ops\": [\"${DIR_REF}:search:TODO\", \"${DIR_REF}:search:FIXME\"]}"
            ;;
        "Implementation Review")
            ANGLES[0]="{\"number\": 1, \"name\": \"Correctness\", \"description\": \"Logic bugs, edge cases, error handling\", \"scope\": \"${DIR_REF}\", \"directory_ops\": [\"${DIR_REF}:tree\"]}"
            ANGLES[1]="{\"number\": 2, \"name\": \"Testing\", \"description\": \"Coverage, test quality, missing tests\", \"scope\": \"${DIR_REF}\", \"directory_ops\": [\"${DIR_REF}:search:test\", \"${DIR_REF}:search:pytest\"]}"
            ANGLES[2]="{\"number\": 3, \"name\": \"Documentation\", \"description\": \"Clarity, completeness, accuracy\", \"scope\": \"${DIR_REF}\", \"directory_ops\": [\"${DIR_REF}:search:docstring\", \"${DIR_REF}:tree\"]}"
            ANGLES[3]="{\"number\": 4, \"name\": \"Dependencies\", \"description\": \"External deps, version conflicts, licensing\", \"scope\": \"${DIR_REF}\", \"directory_ops\": [\"${DIR_REF}:search:import\", \"${DIR_REF}:search:require\"]}"
            ;;
    esac
else
    # For files, all angles analyze the same file (no directory ops)
    # Use Python for safe JSON manipulation instead of fragile sed
    for i in "${!ANGLES[@]}"; do
        ANGLES[$i]=$(echo "${ANGLES[$i]}" | "${PYTHON_PATH:-python3}" -c "
import json
import sys
data = json.load(sys.stdin)
data['scope'] = '@./' + sys.argv[1]
data['directory_ops'] = []
print(json.dumps(data))
" "$TARGET" 2>/dev/null || echo "${ANGLES[$i]}")
    done
fi

# Select best model for each angle
ENRICHED_ANGLES=()
for i in "${!ANGLES[@]}"; do
    ANGLE_JSON="${ANGLES[$i]}"

    # Extract task_type from angle
    TASK_TYPE=$(echo "$ANGLE_JSON" | "${PYTHON_PATH:-python3}" -c "import json,sys; print(json.load(sys.stdin).get('task_type', 'general'))")

    # Extract scope (if exists)
    ANGLE_SCOPE=$(echo "$ANGLE_JSON" | "${PYTHON_PATH:-python3}" -c "import json,sys; print(json.load(sys.stdin).get('scope', '$TARGET'))")

    # Select model for this angle
    SELECTED_MODEL=$(~/.claude/scripts/select-model.sh "$TASK_TYPE" "$ANGLE_SCOPE" 2>/dev/null)

    if [[ -z "$SELECTED_MODEL" ]]; then
        # Fallback if model selection fails
        SELECTED_MODEL="kimi-k2-thinking:cloud"
    fi

    # Add model to angle JSON - pass model via sys.argv for safety
    ENRICHED_ANGLE=$(echo "$ANGLE_JSON" | "${PYTHON_PATH:-python3}" -c "
import json
import sys
data = json.load(sys.stdin)
data['model'] = sys.argv[1]
print(json.dumps(data))
" "$SELECTED_MODEL")
    ENRICHED_ANGLES+=("$ENRICHED_ANGLE")
done

# Build JSON output with enriched angles
ANGLES_JSON=$(printf '%s\n' "${ENRICHED_ANGLES[@]}" | paste -sd,)

# Determine rationale
RATIONALE="Target is a $TARGET_TYPE"
if [[ "$PROMPT_LOWER" =~ (comprehensive|thorough|deep|complete|all aspects) ]]; then
    RATIONALE="$RATIONALE, prompt contains deep analysis keywords"
fi
if [[ "$TARGET_TYPE" == "directory" ]]; then
    RATIONALE="$RATIONALE, multi-file analysis benefits from parallel perspectives"
fi

# Output JSON
cat <<EOF
{
  "strategy": "$STRATEGY",
  "target": "$TARGET",
  "target_type": "$TARGET_TYPE",
  "angles": [$ANGLES_JSON],
  "rationale": "$RATIONALE"
}
EOF
