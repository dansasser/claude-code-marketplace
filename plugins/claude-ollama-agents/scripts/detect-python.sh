#!/bin/bash
# Python path detection and configuration for claude-ollama-agents
#
# This script automatically detects the Python installation and saves
# the configuration to ~/.claude/agents/config.json
#
# Detection priority:
# 1. Existing configuration
# 2. Environment variable: $CLAUDE_PYTHON_PATH
# 3. System python3 (via `which python3`)
# 4. Common conda locations

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/config.sh"

detect_python() {
    local python_path=""

    # 1. Check config file
    if config_exists; then
        python_path=$(get_config_value "python.executable")

        if [[ -n "$python_path" ]] && command -v "$python_path" &> /dev/null; then
            echo "$python_path"
            return 0
        fi
    fi

    # 2. Check environment variable
    if [[ -n "$CLAUDE_PYTHON_PATH" ]] && command -v "$CLAUDE_PYTHON_PATH" &> /dev/null; then
        echo "$CLAUDE_PYTHON_PATH"
        return 0
    fi

    # 3. Try which python3
    if command -v python3 &> /dev/null; then
        python_path=$(which python3)
        echo "$python_path"
        return 0
    fi

    # 4. Search common conda locations (Windows/Linux/Mac)
    local search_paths=(
        "$USERPROFILE/miniconda3/envs/ai/python3"
        "$USERPROFILE/miniconda3/envs/ai/python3.exe"
        "$USERPROFILE/miniconda3/envs/ai/Scripts/python.exe"
        "$USERPROFILE/anaconda3/envs/ai/python3"
        "$USERPROFILE/anaconda3/envs/ai/python3.exe"
        "$HOME/miniconda3/envs/ai/bin/python3"
        "$HOME/anaconda3/envs/ai/bin/python3"
        "$HOME/.pyenv/shims/python3"
    )

    for path in "${search_paths[@]}"; do
        # Expand path
        eval "expanded_path=$path"
        if [[ -f "$expanded_path" ]]; then
            echo "$expanded_path"
            return 0
        fi
    done

    # Not found
    return 1
}

save_config() {
    local python_path="$1"
    local python_version="$2"

    # Use detected python if available, fallback to python3
    local py_cmd="${python_path:-python3}"

    "$py_cmd" - "$python_path" "$python_version" <<'PYTHON'
import json
import sys
from pathlib import Path
from datetime import datetime

# Get arguments passed safely via sys.argv
python_path = sys.argv[1]
python_version = sys.argv[2]

config_file = Path.home() / '.claude' / 'agents' / 'config.json'
config_file.parent.mkdir(parents=True, exist_ok=True)

# Load existing config or create new
try:
    with open(config_file, 'r', encoding='utf-8') as f:
        config = json.load(f)
except FileNotFoundError:
    config = {"version": "1.0"}
except json.JSONDecodeError:
    config = {"version": "1.0"}

# Update python config
config['python'] = {
    'executable': python_path,
    'version': python_version,
    'auto_detected': True,
    'verified_at': datetime.now().isoformat()
}

# Save
with open(config_file, 'w', encoding='utf-8') as f:
    json.dump(config, f, indent=2)

print(f"[OK] Python configuration saved: {config_file}")
PYTHON
}

prompt_user() {
    echo ""
    echo "[WARN] Python executable not found automatically"
    echo ""
    echo "Please provide the full path to your python3 executable:"
    echo "Examples:"
    echo "  - Windows: C:\\Users\\YourName\\miniconda3\\envs\\ai\\python3.exe"
    echo "  - Linux/Mac: /home/username/miniconda3/envs/ai/bin/python3"
    echo ""
    read -r -p "Python path: " user_path

    # Validate
    if [[ -f "$user_path" ]]; then
        echo "$user_path"
        return 0
    else
        echo "[FAIL] File not found: $user_path"
        return 1
    fi
}

validate_python() {
    local python_path="$1"

    # Test if python works
    if ! "$python_path" --version &> /dev/null; then
        echo "[FAIL] Python executable is not valid: $python_path"
        return 1
    fi

    # Get version
    local version
    version=$("$python_path" --version 2>&1 | awk '{print $2}')

    # Check minimum version (3.8+)
    local major
    major=$(echo "$version" | cut -d. -f1)
    local minor
    minor=$(echo "$version" | cut -d. -f2)

    if [[ "$major" -lt 3 ]] || { [[ "$major" -eq 3 ]] && [[ "$minor" -lt 8 ]]; }; then
        echo "[WARN] Python version $version detected. Recommended: 3.8+"
    fi

    echo "$version"
    return 0
}

# Main execution
main() {
    local python_path
    local python_version

    echo "[INFO] Detecting Python installation..."

    # Try auto-detection
    python_path=$(detect_python)

    # If failed, prompt user
    if [[ $? -ne 0 ]]; then
        echo "[INFO] Auto-detection failed"
        python_path=$(prompt_user)
        if [[ $? -ne 0 ]]; then
            echo "[FAIL] Could not configure Python"
            exit 1
        fi
    else
        echo "[OK] Found Python: $python_path"
    fi

    # Validate and get version
    python_version=$(validate_python "$python_path")
    if [[ $? -ne 0 ]]; then
        echo "[FAIL] Python validation failed"
        exit 1
    fi

    echo "[OK] Python version: $python_version"

    # Save configuration
    save_config "$python_path" "$python_version"

    echo "[OK] Python configured successfully"
    echo ""
    echo "Configuration saved to: ~/.claude/agents/config.json"
    echo "Python path: $python_path"
    echo "Python version: $python_version"
}

# Run main if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
