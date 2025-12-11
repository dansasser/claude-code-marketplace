#!/bin/bash
# Configuration helper library for claude-ollama-agents
#
# Provides functions to read/write configuration stored in:
# ~/.claude/agents/config.json

CONFIG_FILE="$HOME/.claude/agents/config.json"

get_config_value() {
    local key="$1"

    if [[ ! -f "$CONFIG_FILE" ]]; then
        return 1
    fi

    # Use python to parse JSON - pass key via sys.argv for safety
    "${PYTHON_PATH:-python3}" - "$key" <<'PYTHON'
import json
import sys
from pathlib import Path

try:
    key = sys.argv[1]
    config_file = Path.home() / '.claude' / 'agents' / 'config.json'
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # Navigate nested keys (e.g., "python.executable")
    value = config
    for key_part in key.split('.'):
        if isinstance(value, dict):
            value = value.get(key_part, {})
        else:
            value = {}
            break

    if value and not isinstance(value, dict):
        print(value)
except Exception:
    pass
PYTHON
}

set_config_value() {
    local key="$1"
    local value="$2"

    # Ensure config directory exists
    mkdir -p "$(dirname "$CONFIG_FILE")"

    # Use python to update JSON - pass key/value via sys.argv for safety
    "${PYTHON_PATH:-python3}" - "$key" "$value" <<'PYTHON'
import json
import sys
from pathlib import Path

key = sys.argv[1]
value = sys.argv[2]

config_file = Path.home() / '.claude' / 'agents' / 'config.json'
config_file.parent.mkdir(parents=True, exist_ok=True)

# Load existing config or create new
try:
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
except FileNotFoundError:
    config = {"version": "1.0"}
except json.JSONDecodeError as e:
    print(f"[WARN] Invalid JSON in config, creating new: {e}", file=sys.stderr)
    config = {"version": "1.0"}

# Navigate to parent and set value
keys = key.split('.')
current = config

for key_part in keys[:-1]:
    if key_part not in current:
        current[key_part] = {}
    current = current[key_part]

# Set the final value
current[keys[-1]] = value

# Save
try:
    with open(config_file, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2)
except (IOError, OSError) as e:
    print(f"[FAIL] Could not write config: {e}", file=sys.stderr)
    sys.exit(1)
PYTHON
}

config_exists() {
    [[ -f "$CONFIG_FILE" ]]
}

validate_config() {
    if [[ ! -f "$CONFIG_FILE" ]]; then
        return 1
    fi

    # Check if config has required structure
    "${PYTHON_PATH:-python3}" <<'PYTHON'
import json
import sys
from pathlib import Path

try:
    config_file = Path.home() / '.claude' / 'agents' / 'config.json'
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # Check required fields
    if 'version' not in config:
        sys.exit(1)

    if 'python' in config:
        python_config = config['python']
        if 'executable' not in python_config or 'version' not in python_config:
            sys.exit(1)

    sys.exit(0)
except Exception:
    sys.exit(1)
PYTHON
    # Return the exit status from Python
    return $?
}

# Export functions for sourcing
export -f get_config_value
export -f set_config_value
export -f config_exists
export -f validate_config
