#!/bin/bash
# Agent Bootstrap - Common initialization for all claude-ollama-agents
#
# Source this at the start of every agent to ensure Python is configured.
#
# Usage:
#   source "$HOME/.claude/plugins/.../scripts/lib/agent-bootstrap.sh"
#   # Now use $PYTHON_PATH instead of python3

# Get the directory of this script
BOOTSTRAP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$(dirname "$BOOTSTRAP_DIR")"

# Source config library
source "$BOOTSTRAP_DIR/config.sh"

# Check if python is configured
if ! config_exists; then
    echo "[WARN] First-time setup required - detecting Python installation..."
    "$SCRIPTS_DIR/detect-python.sh"

    # Check if detection succeeded
    if [[ $? -ne 0 ]]; then
        echo "[FAIL] Python configuration failed"
        echo "Please run: $SCRIPTS_DIR/detect-python.sh"
        exit 2
    fi
fi

# Get python path from config
PYTHON_PATH=$(get_config_value "python.executable")

# Validate python path
if [[ -z "$PYTHON_PATH" ]]; then
    echo "[FAIL] Python not configured in ~/.claude/agents/config.json"
    echo "Run: $SCRIPTS_DIR/detect-python.sh"
    exit 2
fi

if ! command -v "$PYTHON_PATH" &> /dev/null; then
    echo "[FAIL] Python executable not found: $PYTHON_PATH"
    echo "Configuration may be invalid. Re-run: $SCRIPTS_DIR/detect-python.sh"
    exit 2
fi

# Export PYTHON_PATH for use in scripts
export PYTHON_PATH

# Optional: Verbose mode (set AGENT_VERBOSE=1 to enable)
if [[ "$AGENT_VERBOSE" == "1" ]]; then
    echo "[DEBUG] Python configured: $PYTHON_PATH"
fi
