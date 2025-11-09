# Claude Ollama Agents Plugin

Intelligent multi-agent system for delegating analysis, code review, and complex reasoning tasks to local ollama models. Preserves Claude's context budget while leveraging specialized models for deep analysis.

## Features

- **Slash Commands**: Easy-to-use commands for common analysis tasks
- **Multi-Model Support**: Automatic model discovery and intelligent selection
- **Context Efficiency**: Save 70%+ of Claude's context budget
- **Parallel Analysis**: Multi-perspective deep analysis with orchestration
- **Chunked Processing**: Automatic handling of large files
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Installation

### Prerequisites

1. **ollama** - Install the ollama application from [ollama.ai](https://ollama.ai)

2. **Pull Models** - Download the models you want to use
   ```bash
   # Recommended models for this plugin
   ollama pull kimi-k2-thinking:cloud
   ollama pull qwen3-vl:235b-instruct-cloud
   ollama pull deepseek-v3.1:671b-cloud
   ```

3. **ollama-prompt** - Python interface to ollama models
   ```bash
   pip install ollama-prompt
   ```

### Install Plugin

**Option 1: Direct Installation (Recommended)**

```bash
# Clone or download this repository
git clone https://github.com/dansasser/claude-ollama-agents.git
cd claude-ollama-agents

# Run installer
./install.sh
```

**Option 2: Via Claude Code Plugin System**

```bash
# In Claude Code, add to your plugin marketplace or install directly
# Create ~/.claude/marketplaces/local.json:
{
  "name": "local-plugins",
  "owner": {
    "name": "Local User"
  },
  "plugins": [
    {
      "name": "claude-ollama-agents",
      "source": "/path/to/claude-ollama-agents"
    }
  ]
}

# Or install from GitHub:
{
  "name": "claude-ollama-agents",
  "source": {
    "source": "github",
    "repo": "dansasser/claude-ollama-agents"
  }
}
```

The installer will:
- Install agents to `~/.claude/agents/`
- Install slash commands to `~/.claude/commands/`
- Install helper scripts to `~/.claude/scripts/`
- Create model registry at `~/.claude/model-capabilities.json`
- Create orchestration directory at `~/.claude/orchestrations/`
- Discover installed ollama models

## Slash Commands

### /claude-ollama-agents:analyze

Analyze files with automatic model and strategy selection.

```bash
# General analysis
/claude-ollama-agents:analyze src/auth.py

# Focused analysis
/claude-ollama-agents:analyze implementation-plan.md security
/claude-ollama-agents:analyze README.md architecture
/claude-ollama-agents:analyze api.py performance
```

**Focus Areas:**
- `security`: Vulnerabilities, attack vectors
- `architecture`: Design patterns, structure
- `performance`: Bottlenecks, optimizations
- `quality`: Code quality, best practices
- `general`: Comprehensive overview

### /claude-ollama-agents:review

Comprehensive code review with multiple strictness levels.

```bash
# Standard review
/claude-ollama-agents:review src/auth.py

# Quick review (major issues only)
/claude-ollama-agents:review main.py quick

# Thorough review (multi-perspective)
/claude-ollama-agents:review src/api/ thorough
```

**Strictness Levels:**
- `quick`: Fast review, critical issues only
- `standard`: Balanced review (default)
- `thorough`: Deep multi-perspective analysis

**Review Checklist:**
- Security vulnerabilities
- Code quality issues
- Bug detection
- Performance concerns
- Best practice violations
- Test coverage

### /claude-ollama-agents:architect

Architecture analysis and design pattern evaluation.

```bash
# Full architecture analysis
/claude-ollama-agents:architect src/

# Specific aspects
/claude-ollama-agents:architect docs/architecture.md patterns
/claude-ollama-agents:architect src/api/ scalability
/claude-ollama-agents:architect system/ security
/claude-ollama-agents:architect src/ dependencies
```

**Aspects:**
- `patterns`: Design and architectural patterns
- `scalability`: Horizontal/vertical scaling analysis
- `security`: Security architecture review
- `dependencies`: Dependency graph and coupling
- `all`: Comprehensive architecture review (default)

### /claude-ollama-agents:models

Manage ollama model registry.

```bash
# Discover new models
/claude-ollama-agents:models discover

# List all models
/claude-ollama-agents:models list

# Check specific model
/claude-ollama-agents:models check kimi-k2-thinking:cloud

# Show defaults
/claude-ollama-agents:models defaults
```

**Actions:**
- `discover`: Scan and register ollama models
- `list`: Show all registered models
- `check <model>`: Verify model availability
- `defaults`: Show default model selections

### /claude-ollama-agents:deep-analyze

Multi-perspective deep analysis using parallel orchestrator.

```bash
# Auto-select perspectives
/claude-ollama-agents:deep-analyze implementation-plan.md

# Specific perspectives
/claude-ollama-agents:deep-analyze src/auth.py security,testing
/claude-ollama-agents:deep-analyze architecture.md architecture,scalability
```

**Perspectives:**
- `security`: Vulnerabilities and threat modeling
- `architecture`: Design patterns and structure
- `implementation`: Code quality and best practices
- `testing`: Test coverage and validation
- `performance`: Bottlenecks and optimization

**Use When:**
- Comprehensive code reviews needed
- Making architectural decisions
- Security audits
- Pre-production validation
- Complex refactoring planning

## Model Selection Guide

### Code Analysis
- **Best**: `kimi-k2-thinking:cloud` (reasoning + code)
- **Alternative**: `deepseek-v3.1:671b-cloud`
- **Lightweight**: `qwen2.5-coder:3b`

### Vision Tasks
- **Best**: `qwen3-vl:235b-instruct-cloud`
- **Lightweight**: `qwen3:1.7b`

### Reasoning Tasks
- **Best**: `kimi-k2-thinking:cloud`
- **Alternative**: `deepseek-v3.1:671b-cloud`

### Architecture Analysis
- **Best**: `deepseek-v3.1:671b-cloud`
- **Alternative**: `kimi-k2-thinking:cloud`

## How It Works

### Architecture

```
User Request (via Slash Command)
    |
    v
Claude (Task Router)
    |
    +-- Small tasks --> ollama-prompt (Direct)
    |
    +-- Large files --> Chunked Analyzer
    |
    +-- Deep analysis --> Parallel Orchestrator
                              |
                              +-- Security perspective
                              +-- Architecture perspective
                              +-- Implementation perspective
                              +-- Testing perspective
                              |
                              v
                         Synthesis & Report
```

### Context Efficiency

**Problem:** Claude has 200K token budget. Large file analysis can consume 50-100K tokens.

**Solution:** Delegate to ollama agents.

**Example Savings:**
```
Direct Reading:
- 5 documentation files: 40,000 tokens
- 5 code files: 25,000 tokens
- Total: 65,000 tokens (32.5% of budget)

Via Agents:
- Analysis report: 5,000 tokens
- Savings: 60,000 tokens (30% of budget)
- Efficiency: 13x more efficient
```

### Automatic Features

1. **Model Discovery**: Scans ollama and registers capabilities
2. **Chunking Detection**: Automatically chunks large files
3. **Capability Matching**: Selects best model for task
4. **Fallback Chains**: Uses alternative models if preferred unavailable
5. **Parallel Execution**: Runs multiple perspectives concurrently

## Configuration

### Model Registry

Location: `~/.claude/model-capabilities.json`

**Structure:**
```json
{
  "models": {
    "kimi-k2-thinking:cloud": {
      "capabilities": ["code", "reasoning"],
      "context_window": 262144,
      "family": "deepseek",
      "cost": "cloud"
    }
  },
  "user_defaults": {
    "code": "kimi-k2-thinking:cloud",
    "vision": "qwen3-vl:235b-instruct-cloud"
  },
  "task_preferences": {
    "code": {
      "preferred": ["kimi-k2-thinking:cloud"],
      "fallback": ["deepseek-v3.1:671b-cloud", "qwen2.5-coder:3b"]
    }
  }
}
```

### Customization

**Change Default Models:**
Edit `user_defaults` section in registry:
```json
"user_defaults": {
  "code": "your-preferred-code-model",
  "vision": "your-preferred-vision-model"
}
```

**Add Custom Model:**
```bash
# Pull model
ollama pull your-model

# Discover it
/models discover
```

## Examples

### Example 1: Security Review

```bash
# Review authentication module for security issues
/claude-ollama-agents:review src/auth/login.py standard

# Deep security analysis
/claude-ollama-agents:deep-analyze src/auth/ security,testing
```

### Example 2: Architecture Analysis

```bash
# Analyze overall architecture
/claude-ollama-agents:architect src/ all

# Focus on scalability
/claude-ollama-agents:architect src/api/ scalability

# Check design patterns
/claude-ollama-agents:architect docs/architecture.md patterns
```

### Example 3: Implementation Review

```bash
# Quick check before commit
/claude-ollama-agents:review src/feature.py quick

# Thorough review before PR
/claude-ollama-agents:review src/feature.py thorough

# Analyze specific concern
/claude-ollama-agents:analyze src/feature.py performance
```

### Example 4: Large File Analysis

```bash
# Automatically chunks if needed
/claude-ollama-agents:analyze docs/implementation-plan.md

# Deep analysis with multiple perspectives
/claude-ollama-agents:deep-analyze docs/design.md architecture,security,implementation
```

## Troubleshooting

### Model Not Found

```bash
# Check if model is available
/claude-ollama-agents:models check kimi-k2-thinking:cloud

# If not, pull it
ollama pull kimi-k2-thinking:cloud

# Rediscover models
/claude-ollama-agents:models discover
```

### Path Errors (Windows)

The plugin automatically handles Windows path issues. All scripts use `Path.home()` internally for cross-platform compatibility.

### Unicode Errors (Windows)

All output uses ASCII characters (`[OK]`, `[FAIL]`, `[WARN]`) instead of emojis for Windows compatibility.

## Performance Tips

1. **Use /analyze for quick checks**: Faster than deep analysis
2. **Use /deep-analyze sparingly**: Powerful but thorough
3. **Leverage chunking**: Large files handled automatically
4. **Keep models updated**: Newer models often perform better
5. **Use specific focus areas**: Faster than general analysis

## File Structure

```
claude-ollama-agents/
├── .claude-plugin/               # Plugin manifest
│   └── plugin.json              # Plugin metadata and configuration
├── README.md                     # This file
├── LICENSE                       # MIT License
├── PACKAGE-CONTENTS.md          # Detailed package inventory
├── install.sh                    # Installation script
├── agents/                       # Agent definitions
│   ├── ollama-task-router.md    # Meta-orchestrator agent
│   ├── ollama-chunked-analyzer.md   # Large file handler
│   └── ollama-parallel-orchestrator.md  # Multi-perspective analysis
├── commands/                     # Slash commands
│   ├── analyze.md               # /analyze command
│   ├── review.md                # /review command
│   ├── architect.md             # /architect command
│   ├── models.md                # /models command
│   └── deep-analyze.md          # /deep-analyze command
└── scripts/                      # Helper scripts
    ├── discover-models.sh       # Model discovery
    ├── query-model-capabilities.sh  # Query model capabilities
    ├── check-model.sh           # Check model availability
    ├── should-chunk.sh          # Chunking decision logic
    ├── decompose-task.sh        # Task decomposition
    ├── track-sessions.sh        # Session tracking
    └── combine-sessions.sh      # Result synthesis
```

## Advanced Usage

### Custom Perspectives

Edit `/deep-analyze` command to add custom perspectives:

```bash
ollama-code -p "Custom perspective analysis of {{arg1}}:
- Your specific concerns
- Your analysis criteria
- Your validation rules
"
```

### Integration with CI/CD

```bash
# In your CI pipeline
~/.claude/scripts/check-model.sh kimi-k2-thinking:cloud
if [[ $? -eq 0 ]]; then
    # Run automated review
    ollama-code -p "Review changes in PR for security and quality"
fi
```

### Batch Analysis

```bash
# Analyze multiple files
for file in src/*.py; do
    /analyze "$file" security
done
```

## Contributing

Contributions welcome! Please:
1. Follow existing code style
2. Test on Windows, macOS, and Linux
3. Use ASCII-only output (no emojis)
4. Use `Path.home()` in Python heredocs
5. Specify `encoding='utf-8'` for file operations

## License

MIT License - See LICENSE file

## Credits

Created for Claude Code by Daniel T Sasser II
Part of the SIM-ONE Framework ecosystem

## Support

Issues and questions:
- Open an issue on GitHub
- Check CLAUDE.md for workflow guidelines
- Review helper scripts in ~/.claude/scripts/

## Changelog

### v1.0.0 (2025-01-09)
- Initial release
- Slash commands: analyze, review, architect, models, deep-analyze
- Multi-model support with auto-discovery
- Parallel orchestrator for deep analysis
- Cross-platform compatibility (Windows/macOS/Linux)
- Automatic chunking for large files
- Context-efficient delegation system
