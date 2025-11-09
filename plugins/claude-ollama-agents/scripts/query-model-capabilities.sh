#!/bin/bash
# Query model capabilities using ollama show and infer from name/family

if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <model_name>"
    exit 1
fi

MODEL="$1"
REGISTRY_FILE=$(python3 -c "from pathlib import Path; print(Path.home() / '.claude' / 'model-capabilities.json')")

# Get model details from ollama
MODEL_INFO=$(ollama show "$MODEL" 2>/dev/null)

if [[ $? -ne 0 ]]; then
    echo "Error: Could not query model $MODEL"
    exit 1
fi

# Parse model details
ARCHITECTURE=$(echo "$MODEL_INFO" | grep -i "architecture" | awk '{print $2}' | tr '[:upper:]' '[:lower:]')
PARAM_SIZE=$(echo "$MODEL_INFO" | grep -i "parameters" | awk '{print $2}' | tr '[:upper:]' '[:lower:]')
CONTEXT_WINDOW=$(echo "$MODEL_INFO" | grep -i "context length" | awk '{print $3}')

# Extract family from architecture or model name
if [[ -n "$ARCHITECTURE" ]]; then
    # Map architectures to families
    if [[ "$ARCHITECTURE" == *"qwen"* ]]; then
        FAMILY="qwen"
    elif [[ "$ARCHITECTURE" == *"deepseek"* ]]; then
        FAMILY="deepseek"
    elif [[ "$ARCHITECTURE" == *"llama"* ]]; then
        FAMILY="llama"
    elif [[ "$ARCHITECTURE" == *"mistral"* ]]; then
        FAMILY="mistral"
    elif [[ "$ARCHITECTURE" == *"gemma"* ]]; then
        FAMILY="gemma"
    else
        FAMILY="$ARCHITECTURE"
    fi
else
    # Infer from model name
    MODEL_LOWER=$(echo "$MODEL" | tr '[:upper:]' '[:lower:]')
    if [[ "$MODEL_LOWER" == *"qwen"* ]]; then
        FAMILY="qwen"
    elif [[ "$MODEL_LOWER" == *"kimi"* ]]; then
        FAMILY="kimi"
    elif [[ "$MODEL_LOWER" == *"deepseek"* ]]; then
        FAMILY="deepseek"
    elif [[ "$MODEL_LOWER" == *"llama"* ]]; then
        FAMILY="llama"
    elif [[ "$MODEL_LOWER" == *"mistral"* ]]; then
        FAMILY="mistral"
    elif [[ "$MODEL_LOWER" == *"gemma"* ]]; then
        FAMILY="gemma"
    else
        FAMILY="unknown"
    fi
fi

# Default context window if not found
if [[ -z "$CONTEXT_WINDOW" ]]; then
    CONTEXT_WINDOW=8192
fi

# Infer capabilities from model name and family
CAPABILITIES=()

# First, parse explicit capabilities from ollama show output
OLLAMA_CAPS=$(echo "$MODEL_INFO" | sed -n '/Capabilities/,/^$/p' | tail -n +2 | awk '{print $1}' | grep -v "^$" | tr -d '\r')

# Map ollama capabilities to our taxonomy
while IFS= read -r cap; do
    [[ -z "$cap" ]] && continue
    cap_lower=$(echo "$cap" | tr '[:upper:]' '[:lower:]' | tr -d '\r\n')
    case "$cap_lower" in
        vision)
            [[ ! " ${CAPABILITIES[@]} " =~ " vision " ]] && CAPABILITIES+=("vision")
            ;;
        tools)
            [[ ! " ${CAPABILITIES[@]} " =~ " code " ]] && CAPABILITIES+=("code")
            ;;
        thinking)
            [[ ! " ${CAPABILITIES[@]} " =~ " reasoning " ]] && CAPABILITIES+=("reasoning")
            ;;
        completion)
            [[ ! " ${CAPABILITIES[@]} " =~ " general " ]] && CAPABILITIES+=("general")
            ;;
    esac
done <<< "$OLLAMA_CAPS"

# Load inference rules from registry
NAME_PATTERNS=$(python3 <<PYTHON
import json
from pathlib import Path

registry_file = Path.home() / '.claude' / 'model-capabilities.json'
with open(registry_file, 'r') as f:
    data = json.load(f)
patterns = data.get('capability_inference', {}).get('name_patterns', {})
for cap, patterns_list in patterns.items():
    for pattern in patterns_list:
        print(f"{cap}:{pattern}")
PYTHON
)

# Check name patterns
MODEL_LOWER=$(echo "$MODEL" | tr '[:upper:]' '[:lower:]')
while IFS=':' read -r capability pattern; do
    if echo "$MODEL_LOWER" | grep -q "$pattern"; then
        if [[ ! " ${CAPABILITIES[@]} " =~ " ${capability} " ]]; then
            CAPABILITIES+=("$capability")
        fi
    fi
done <<< "$NAME_PATTERNS"

# Check family capabilities
if [[ -n "$FAMILY" ]]; then
    FAMILY_CAPS=$(python3 <<PYTHON
import json
from pathlib import Path

registry_file = Path.home() / '.claude' / 'model-capabilities.json'
with open(registry_file, 'r') as f:
    data = json.load(f)
family_caps = data.get('capability_inference', {}).get('family_capabilities', {})
caps = family_caps.get("$FAMILY", [])
for cap in caps:
    print(cap)
PYTHON
)
    while IFS= read -r cap; do
        if [[ -n "$cap" ]] && [[ ! " ${CAPABILITIES[@]} " =~ " ${cap} " ]]; then
            CAPABILITIES+=("$cap")
        fi
    done <<< "$FAMILY_CAPS"
fi

# Default to general if no capabilities inferred
if [[ ${#CAPABILITIES[@]} -eq 0 ]]; then
    CAPABILITIES=("general")
fi

# Determine cost (cloud vs local)
COST="local"
if [[ "$MODEL" == *":cloud"* ]]; then
    COST="cloud"
fi

# Build capabilities JSON array (ensure no newlines)
CAPS_JSON=$(printf '"%s",' "${CAPABILITIES[@]}" | tr -d '\r\n' | sed 's/,$//')

# Add model to registry
python3 <<PYTHON
import json
from datetime import datetime
from pathlib import Path

model_name = "$MODEL"
registry_file = Path.home() / '.claude' / 'model-capabilities.json'

with open(registry_file, 'r') as f:
    data = json.load(f)

# Create model entry
model_entry = {
    "capabilities": [$CAPS_JSON],
    "context_window": $CONTEXT_WINDOW,
    "family": "$FAMILY" if "$FAMILY" else "unknown",
    "parameter_size": "$PARAM_SIZE" if "$PARAM_SIZE" else "unknown",
    "cost": "$COST",
    "verified": False,
    "auto_discovered": True,
    "discovered_at": datetime.now().isoformat(),
    "strengths": "Auto-discovered model",
    "weaknesses": "Capabilities inferred, not verified",
    "notes": "Automatically added by discover-models.sh"
}

# Add to registry
if 'models' not in data:
    data['models'] = {}

data['models'][model_name] = model_entry
data['last_updated'] = datetime.now().isoformat()

# Save
with open(registry_file, 'w') as f:
    json.dump(data, f, indent=2)

print(f"Added {model_name} to registry:")
print(f"  Capabilities: {model_entry['capabilities']}")
print(f"  Family: {model_entry['family']}")
print(f"  Context: {model_entry['context_window']}")
print(f"  Cost: {model_entry['cost']}")
PYTHON
