#!/bin/bash
# Check if a model is available and show context window
# Usage: check-model.sh <model-name>

# Model context windows (tokens)
declare -A CONTEXT_WINDOWS=(
    ["kimi-k2-thinking:cloud"]=128000
    ["kimi-k2:1t-cloud"]=1000000
    ["deepseek-v3.1:671b-cloud"]=64000
    ["qwen3-vl:235b-instruct-cloud"]=32768
    ["qwen2.5-coder"]=32768
    ["codellama"]=16384
    ["llama3.1"]=128000
)

# Model use cases
declare -A USE_CASES=(
    ["kimi-k2-thinking:cloud"]="Code review, security analysis, complex reasoning with deep thinking"
    ["kimi-k2:1t-cloud"]="Massive context tasks (1M tokens), entire codebases"
    ["deepseek-v3.1:671b-cloud"]="Alternative code analysis, comparisons"
    ["qwen3-vl:235b-instruct-cloud"]="Vision + language, screenshots, diagrams, OCR with reasoning"
    ["qwen2.5-coder"]="Fast code completion, simple analysis"
    ["codellama"]="Legacy code tasks"
    ["llama3.1"]="General purpose, good context window"
)

if [[ $# -eq 0 ]]; then
    echo "Usage: $0 <model-name>"
    echo ""
    echo "Available models:"
    for model in "${!CONTEXT_WINDOWS[@]}"; do
        printf "  %-35s %10s tokens - %s\n" \
            "$model" \
            "${CONTEXT_WINDOWS[$model]}" \
            "${USE_CASES[$model]}"
    done
    exit 0
fi

MODEL="$1"

# Check if model is in ollama
if ollama list | grep -q "$MODEL"; then
    echo "[OK] Model available: $MODEL"

    # Show context window if known
    if [[ -n "${CONTEXT_WINDOWS[$MODEL]}" ]]; then
        echo "  Context window: ${CONTEXT_WINDOWS[$MODEL]} tokens"
        echo "  Use case: ${USE_CASES[$MODEL]}"
    else
        echo "  Context window: Unknown (not in lookup table)"
    fi

    exit 0
else
    echo "[FAIL] Model not available: $MODEL"
    echo ""
    echo "Pull with: ollama pull $MODEL"
    exit 1
fi
