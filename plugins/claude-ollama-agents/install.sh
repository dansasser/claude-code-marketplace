#!/bin/bash
# Claude Ollama Agents Plugin Installer
# Installs slash commands, scripts, and initializes model registry

set -e

echo "Claude Ollama Agents Plugin Installer"
echo "======================================"
echo ""

# Determine home directory cross-platform
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    CLAUDE_HOME="$HOME/.claude"
else
    CLAUDE_HOME="${HOME}/.claude"
fi

# Create directories if they don't exist
echo "[1/8] Creating directories..."
mkdir -p "${CLAUDE_HOME}/commands"
mkdir -p "${CLAUDE_HOME}/agents"
mkdir -p "${CLAUDE_HOME}/scripts"
mkdir -p "${CLAUDE_HOME}/orchestrations"

# Install agents
echo "[2/8] Installing agents..."
cp agents/*.md "${CLAUDE_HOME}/agents/"
echo "  - Installed: ollama-task-router.md"
echo "  - Installed: ollama-chunked-analyzer.md"
echo "  - Installed: ollama-parallel-orchestrator.md"

# Install slash commands
echo "[3/8] Installing slash commands..."
cp commands/*.md "${CLAUDE_HOME}/commands/"
echo "  - Installed: /analyze"
echo "  - Installed: /review"
echo "  - Installed: /architect"
echo "  - Installed: /models"
echo "  - Installed: /deep-analyze"

# Install helper scripts
echo "[4/8] Installing helper scripts..."
cp scripts/*.sh "${CLAUDE_HOME}/scripts/"
chmod +x "${CLAUDE_HOME}/scripts/"*.sh
echo "  - Installed discover-models.sh"
echo "  - Installed query-model-capabilities.sh"
echo "  - Installed check-model.sh"
echo "  - Installed should-chunk.sh"
echo "  - Installed decompose-task.sh"
echo "  - Installed track-sessions.sh"
echo "  - Installed combine-sessions.sh"

# Initialize model registry if doesn't exist
echo "[5/8] Initializing model registry..."
REGISTRY_FILE="${CLAUDE_HOME}/model-capabilities.json"

if [[ ! -f "$REGISTRY_FILE" ]]; then
    cat > "$REGISTRY_FILE" <<'EOF'
{
  "version": "1.0",
  "last_updated": "",
  "last_scan": "",
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
EOF
    echo "  - Created model registry"
else
    echo "  - Model registry already exists"
fi

# Check for ollama-prompt dependency
echo "[6/7] Checking dependencies..."
if ! python3 -c "import ollama_prompt" 2>/dev/null; then
    echo "  - Warning: ollama-prompt not found"
    echo ""
    read -p "Install ollama-prompt now? [y/N] " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "  - Installing ollama-prompt..."
        pip install ollama-prompt
        if [[ $? -eq 0 ]]; then
            echo "  - ollama-prompt installed successfully"
        else
            echo "  - Error: Failed to install ollama-prompt"
            echo "  - Please run: pip install ollama-prompt"
        fi
    else
        echo "  - Skipped ollama-prompt installation"
        echo "  - You'll need to run: pip install ollama-prompt"
    fi
else
    echo "  - ollama-prompt is installed"
fi

# Discover installed models
echo "[7/7] Discovering ollama models..."
if command -v ollama &> /dev/null; then
    "${CLAUDE_HOME}/scripts/discover-models.sh" || echo "  - Warning: Model discovery failed (ollama may not be running)"
else
    echo "  - Warning: ollama not found in PATH"
    echo "  - Install ollama from: https://ollama.ai"
fi

# Installation summary
echo ""
echo "[8/8] Installation complete!"
echo ""
echo "======================================"
echo "Available Slash Commands:"
echo "======================================"
echo "/analyze <file> [focus]       - Analyze file with ollama"
echo "/review <file> [strictness]   - Code review (quick/standard/thorough)"
echo "/architect <file> [aspect]    - Architecture analysis"
echo "/models [action]              - Manage ollama models"
echo "/deep-analyze <file> [persp]  - Multi-perspective deep analysis"
echo ""
echo "======================================"
echo "Quick Start:"
echo "======================================"
echo "1. Pull recommended models:"
echo "   ollama pull kimi-k2-thinking:cloud"
echo "   ollama pull qwen3-vl:235b-instruct-cloud"
echo "   ollama pull deepseek-v3.1:671b-cloud"
echo "2. Install ollama-prompt: pip install ollama-prompt"
echo "3. Discover models: /models discover"
echo "4. Try it: /analyze README.md"
echo ""
echo "For detailed documentation, see README.md"
echo ""
