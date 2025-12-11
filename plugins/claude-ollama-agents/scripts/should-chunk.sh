#!/bin/bash
# Determine if chunking is needed for a task
# Usage: should-chunk.sh <file|directory> <model>

if [[ $# -lt 2 ]]; then
    echo "Usage: $0 <file|directory> <model>"
    echo ""
    echo "Determines if chunking is needed based on:"
    echo "  - File/directory size"
    echo "  - Model context window"
    echo "  - 80% threshold for safety"
    exit 1
fi

PATH_ARG="$1"
MODEL="$2"

# Model context windows
declare -A CONTEXT_WINDOWS=(
    ["kimi-k2-thinking:cloud"]=128000
    ["kimi-k2:1t-cloud"]=1000000
    ["deepseek-v3.1:671b-cloud"]=64000
    ["qwen3-vl:235b-instruct-cloud"]=32768
    ["qwen2.5-coder"]=32768
    ["codellama"]=16384
    ["llama3.1"]=128000
)

# Get context window for model
CONTEXT_WINDOW="${CONTEXT_WINDOWS[$MODEL]}"
if [[ -z "$CONTEXT_WINDOW" ]]; then
    CONTEXT_WINDOW=32768  # Conservative default
    echo "Warning: Unknown model, using default context window: $CONTEXT_WINDOW" >&2
fi

# Calculate 80% threshold
THRESHOLD=$((CONTEXT_WINDOW * 80 / 100))

# Estimate tokens
if [[ -f "$PATH_ARG" ]]; then
    BYTES=$(wc -c < "$PATH_ARG")
elif [[ -d "$PATH_ARG" ]]; then
    BYTES=$(find "$PATH_ARG" -type f -exec wc -c {} + | awk '{s+=$1} END {print s}')
else
    echo "Error: Path not found: $PATH_ARG" >&2
    exit 1
fi

# Add prompt overhead (~1000 tokens)
ESTIMATED_TOKENS=$((BYTES / 4 + 1000))

# Decision
echo "Path: $PATH_ARG"
echo "Type: $(if [[ -d "$PATH_ARG" ]]; then echo "directory"; else echo "file"; fi)"
echo "Model: $MODEL"
echo "Context window: $CONTEXT_WINDOW tokens"
echo "Threshold (80%): $THRESHOLD tokens"
echo "Estimated tokens: $ESTIMATED_TOKENS"
echo ""

# For directories, also suggest directory operations
if [[ -d "$PATH_ARG" ]]; then
    echo "--- Directory Operation Recommendations ---"
    echo ""
    echo "For efficient directory analysis, consider using:"
    echo ""
    echo "  Structure overview (~500 tokens):"
    echo "    @./${PATH_ARG%/}/:tree"
    echo ""
    echo "  Security patterns (~1000 tokens each):"
    echo "    @./${PATH_ARG%/}/:search:eval"
    echo "    @./${PATH_ARG%/}/:search:password"
    echo ""
    echo "  Code quality (~1000 tokens each):"
    echo "    @./${PATH_ARG%/}/:search:TODO"
    echo "    @./${PATH_ARG%/}/:search:FIXME"
    echo ""
    echo "  Import analysis (~1000 tokens):"
    echo "    @./${PATH_ARG%/}/:search:import"
    echo ""
    echo "Directory operations are much more token-efficient than"
    echo "reading all files individually."
    echo ""
    echo "-------------------------------------------"
    echo ""
fi

if [[ $ESTIMATED_TOKENS -gt $THRESHOLD ]]; then
    echo "[WARN] CHUNKING REQUIRED"
    echo "  Estimated tokens ($ESTIMATED_TOKENS) exceed 80% threshold ($THRESHOLD)"
    echo "  Recommend using ollama-chunked-analyzer agent"

    # Suggest chunk count
    SUGGESTED_CHUNKS=$(( (ESTIMATED_TOKENS + THRESHOLD - 1) / THRESHOLD ))
    echo "  Suggested chunks: $SUGGESTED_CHUNKS"

    # For directories, suggest structure-first approach
    if [[ -d "$PATH_ARG" ]]; then
        echo ""
        echo "  For directories, consider structure-first approach:"
        echo "    1. @./${PATH_ARG%/}/:tree for overview"
        echo "    2. @./${PATH_ARG%/}/:search:PATTERN for targeted analysis"
        echo "    3. Individual file reads only for deep dives"
    fi

    exit 0
else
    echo "[OK] NO CHUNKING NEEDED"
    echo "  Estimated tokens ($ESTIMATED_TOKENS) within safe limit"
    echo "  Can use direct ollama-prompt call"

    # Show headroom
    HEADROOM=$((THRESHOLD - ESTIMATED_TOKENS))
    HEADROOM_PCT=$((HEADROOM * 100 / THRESHOLD))
    echo "  Headroom: $HEADROOM tokens ($HEADROOM_PCT%)"

    # For directories, still recommend directory ops for efficiency
    if [[ -d "$PATH_ARG" ]]; then
        echo ""
        echo "  Tip: Even though chunking isn't required, using"
        echo "  directory operations (@./dir/:tree, @./dir/:search:)"
        echo "  will be more token-efficient than reading all files."
    fi

    exit 1
fi
