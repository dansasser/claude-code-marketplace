#!/bin/bash
# Discover available ollama models and update capabilities registry

# Use Python to get proper home directory path (cross-platform)
REGISTRY_FILE=$(python3 -c "from pathlib import Path; print(Path.home() / '.claude' / 'model-capabilities.json')")
CACHE_DIR=$(python3 -c "from pathlib import Path; print(Path.home() / '.claude' / 'cache')")
mkdir -p "$CACHE_DIR"

# Initialize registry if it doesn't exist
if [[ ! -f "$REGISTRY_FILE" ]]; then
    echo "Creating new model capabilities registry..."
    cat > "$REGISTRY_FILE" <<'REGISTRY_TEMPLATE'
{
  "version": "1.0",
  "last_updated": "TIMESTAMP",
  "last_scan": "TIMESTAMP",
  "models": {},
  "user_defaults": {
    "vision": "qwen3-vl:235b-instruct-cloud",
    "code": "kimi-k2-thinking:cloud",
    "reasoning": "kimi-k2-thinking:cloud",
    "tool_use": "kimi-k2-thinking:cloud"
  },
  "task_preferences": {
    "vision": {
      "description": "Image analysis, OCR, screenshots, diagrams",
      "preferred": ["qwen3-vl:235b-instruct-cloud"],
      "fallback": [],
      "required_capabilities": ["vision"]
    },
    "code": {
      "description": "Code review, security analysis, refactoring",
      "preferred": ["kimi-k2-thinking:cloud"],
      "fallback": [],
      "required_capabilities": ["code"]
    },
    "reasoning": {
      "description": "Multi-step reasoning, complex analysis",
      "preferred": ["kimi-k2-thinking:cloud"],
      "fallback": [],
      "required_capabilities": ["reasoning"]
    },
    "architecture": {
      "description": "System design, architectural analysis",
      "preferred": ["kimi-k2-thinking:cloud"],
      "fallback": [],
      "required_capabilities": ["code", "reasoning"]
    },
    "security": {
      "description": "Security analysis, vulnerability detection",
      "preferred": ["kimi-k2-thinking:cloud"],
      "fallback": [],
      "required_capabilities": ["code", "security"]
    },
    "performance": {
      "description": "Performance analysis, bottleneck detection",
      "preferred": ["kimi-k2-thinking:cloud"],
      "fallback": [],
      "required_capabilities": ["code"]
    },
    "general": {
      "description": "General purpose tasks",
      "preferred": ["kimi-k2-thinking:cloud"],
      "fallback": [],
      "required_capabilities": []
    }
  },
  "capability_inference": {
    "name_patterns": {
      "vision": ["vision", "vl", "vlm", "visual", "multimodal"],
      "code": ["code", "coder", "coding", "deepseek", "kimi"],
      "reasoning": ["thinking", "reason", "kimi", "deepseek"],
      "chat": ["chat", "instruct"],
      "general": ["llama", "mistral", "qwen", "gemma"]
    },
    "family_capabilities": {
      "kimi": ["code", "reasoning", "architecture", "security"],
      "qwen": ["vision", "code", "general"],
      "deepseek": ["code", "reasoning"],
      "llama": ["general"],
      "mistral": ["general", "code"],
      "gemma": ["general"]
    }
  }
}
REGISTRY_TEMPLATE
    # Set timestamp
    TIMESTAMP=$(date -Iseconds)
    python3 <<PYTHON
import json
from pathlib import Path

registry_file = Path.home() / '.claude' / 'model-capabilities.json'
with open(registry_file, 'r') as f:
    data = json.load(f)
data['last_updated'] = "$TIMESTAMP"
data['last_scan'] = "$TIMESTAMP"
with open(registry_file, 'w') as f:
    json.dump(data, f, indent=2)
PYTHON
fi

# Get currently available models
echo "Scanning available ollama models..."
AVAILABLE_MODELS=$(ollama list | tail -n +2 | awk '{print $1}')

if [[ -z "$AVAILABLE_MODELS" ]]; then
    echo "No ollama models found. Is ollama running?"
    exit 1
fi

# Save available models list to cache
echo "$AVAILABLE_MODELS" > "$CACHE_DIR/available_models.txt"

# Check for new models
NEW_MODELS=()
KNOWN_MODELS=$(python3 <<PYTHON
import json
from pathlib import Path

registry_file = Path.home() / '.claude' / 'model-capabilities.json'
with open(registry_file, 'r') as f:
    data = json.load(f)
for model in data.get('models', {}).keys():
    print(model)
PYTHON
)

while IFS= read -r model; do
    if ! echo "$KNOWN_MODELS" | grep -q "^${model}$"; then
        NEW_MODELS+=("$model")
    fi
done <<< "$AVAILABLE_MODELS"

# Report findings
TOTAL_AVAILABLE=$(echo "$AVAILABLE_MODELS" | wc -l)
TOTAL_NEW=${#NEW_MODELS[@]}

echo "Found $TOTAL_AVAILABLE available model(s)"
echo "Discovered $TOTAL_NEW new model(s)"

# Query capabilities for new models
if [[ $TOTAL_NEW -gt 0 ]]; then
    echo ""
    echo "Querying capabilities for new models..."

    for model in "${NEW_MODELS[@]}"; do
        echo "  - $model"
        ~/.claude/scripts/query-model-capabilities.sh "$model"
    done

    echo ""
    echo "Updated registry with new models (marked as auto-discovered)"
fi

# Auto-generate fallback lists from installed models
echo ""
echo "Building fallback lists from installed models..."

python3 <<PYTHON
import json
from datetime import datetime
from pathlib import Path

registry_file = Path.home() / '.claude' / 'model-capabilities.json'
with open(registry_file, 'r') as f:
    data = json.load(f)

# Get all available models
available_models = """$AVAILABLE_MODELS""".strip().split('\n')
models_db = data.get('models', {})
user_defaults = data.get('user_defaults', {})

# Categorize installed models by capability
categorized = {
    'vision': [],
    'code': [],
    'reasoning': [],
    'general': []
}

for model in available_models:
    if model in models_db:
        caps = models_db[model].get('capabilities', [])

        # Categorize based on capabilities
        if 'vision' in caps:
            categorized['vision'].append(model)
        if 'code' in caps:
            categorized['code'].append(model)
        if 'reasoning' in caps:
            categorized['reasoning'].append(model)
        # Everything goes in general
        categorized['general'].append(model)

# Build fallback lists (exclude preferred models)
task_prefs = data.get('task_preferences', {})

for task_type, prefs in task_prefs.items():
    preferred = prefs.get('preferred', [])

    # Determine which capability category to use
    capability_type = task_type
    if task_type in ['architecture', 'security', 'performance']:
        capability_type = 'code'

    # Get models with this capability
    candidates = categorized.get(capability_type, [])

    # Remove preferred models from fallback list
    fallback = [m for m in candidates if m not in preferred]

    # Sort fallback by preference (cloud models first, then by size)
    def sort_key(model_name):
        priority = 0
        # Cloud models higher priority
        if ':cloud' in model_name:
            priority += 100
        # Known good models
        if 'deepseek' in model_name.lower():
            priority += 50
        if 'kimi' in model_name.lower():
            priority += 40
        # Larger models higher priority (rough heuristic)
        if '671b' in model_name.lower():
            priority += 30
        if '235b' in model_name.lower():
            priority += 25
        if '90b' in model_name.lower():
            priority += 20
        if '7b' in model_name.lower():
            priority += 10
        if '3b' in model_name.lower():
            priority += 5
        return -priority  # Negative for descending sort

    fallback.sort(key=sort_key)

    # Update registry
    prefs['fallback'] = fallback

# Update last_scan timestamp
data['last_scan'] = datetime.now().isoformat()

# Save
with open(registry_file, 'w') as f:
    json.dump(data, f, indent=2)

# Print summary
print("Fallback lists generated:")
for task_type, prefs in task_prefs.items():
    preferred = prefs.get('preferred', [])
    fallback = prefs.get('fallback', [])
    print(f"  {task_type}:")
    print(f"    Preferred: {', '.join(preferred) if preferred else 'none'}")
    print(f"    Fallback: {', '.join(fallback[:3]) if fallback else 'none'}")
PYTHON


# Output summary in JSON format
cat <<EOF
{
  "total_available": $TOTAL_AVAILABLE,
  "total_new": $TOTAL_NEW,
  "new_models": [$(printf '"%s",' "${NEW_MODELS[@]}" | sed 's/,$//')],
  "registry_updated": $(if [[ $TOTAL_NEW -gt 0 ]]; then echo "true"; else echo "false"; fi),
  "cache_file": "$CACHE_DIR/available_models.txt"
}
EOF
