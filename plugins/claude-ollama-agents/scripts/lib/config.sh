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

    # Use python to parse JSON
    python3 <<PYTHON
import json
from pathlib import Path

try:
    config_file = Path.home() / '.claude' / 'agents' / 'config.json'
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # Navigate nested keys (e.g., "python.executable")
    value = config
    for key_part in "$key".split('.'):
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

    python3 <<PYTHON
import json
from pathlib import Path

config_file = Path.home() / '.claude' / 'agents' / 'config.json'
config_file.parent.mkdir(parents=True, exist_ok=True)

# Load existing config or create new
try:
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
except:
    config = {"version": "1.0"}

# Navigate to parent and set value
keys = "$key".split('.')
current = config

for key_part in keys[:-1]:
    if key_part not in current:
        current[key_part] = {}
    current = current[key_part]

# Set the final value
current[keys[-1]] = "$value"

# Save
with open(config_file, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2)
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
    python3 <<PYTHON
import json
from pathlib import Path

try:
    config_file = Path.home() / '.claude' / 'agents' / 'config.json'
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)

    # Check required fields
    if 'version' not in config:
        exit(1)

    if 'python' in config:
        python_config = config['python']
        if 'executable' not in python_config or 'version' not in python_config:
            exit(1)

    exit(0)
except:
    exit(1)
PYTHON
}

# Export functions for sourcing
export -f get_config_value
export -f set_config_value
export -f config_exists
export -f validate_config
