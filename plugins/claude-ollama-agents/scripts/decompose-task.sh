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

# Determine scope for each angle based on target type
if [[ "$TARGET_TYPE" == "directory" ]]; then
    # For directories, suggest focused scopes per angle
    case "$STRATEGY" in
        "Software Quality")
            ANGLES[0]='{"number": 1, "name": "Security", "description": "Vulnerabilities, attack vectors, security patterns", "scope": "Focus on auth, validation, input handling files"}'
            ANGLES[1]='{"number": 2, "name": "Architecture", "description": "Design patterns, modularity, coupling, scalability", "scope": "Full directory structure"}'
            ANGLES[2]='{"number": 3, "name": "Performance", "description": "Bottlenecks, efficiency, resource usage", "scope": "Focus on loops, queries, I/O operations"}'
            ANGLES[3]='{"number": 4, "name": "Code Quality", "description": "Maintainability, readability, best practices", "scope": "Full directory review"}'
            ;;
    esac
else
    # For files, all angles analyze the same file
    for i in "${!ANGLES[@]}"; do
        ANGLES[$i]=$(echo "${ANGLES[$i]}" | sed "s/}/,\"scope\":\"$TARGET\"}/")
    done
fi

# Select best model for each angle
ENRICHED_ANGLES=()
for i in "${!ANGLES[@]}"; do
    ANGLE_JSON="${ANGLES[$i]}"

    # Extract task_type from angle
    TASK_TYPE=$(echo "$ANGLE_JSON" | python3 -c "import json,sys; print(json.load(sys.stdin).get('task_type', 'general'))")

    # Extract scope (if exists)
    ANGLE_SCOPE=$(echo "$ANGLE_JSON" | python3 -c "import json,sys; print(json.load(sys.stdin).get('scope', '$TARGET'))")

    # Select model for this angle
    SELECTED_MODEL=$(~/.claude/scripts/select-model.sh "$TASK_TYPE" "$ANGLE_SCOPE" 2>/dev/null)

    if [[ -z "$SELECTED_MODEL" ]]; then
        # Fallback if model selection fails
        SELECTED_MODEL="kimi-k2-thinking:cloud"
    fi

    # Add model to angle JSON
    ENRICHED_ANGLE=$(echo "$ANGLE_JSON" | python3 -c "import json,sys; data=json.load(sys.stdin); data['model']='$SELECTED_MODEL'; print(json.dumps(data))")
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
