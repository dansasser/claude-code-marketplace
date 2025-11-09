# Claude Code Marketplace - Daniel T Sasser II

Claude Code plugins for ollama integration and AI-assisted development.

## Available Plugins

### claude-ollama-agents

Intelligent multi-agent system for delegating analysis, code review, and complex reasoning tasks to local ollama models.

**Features:**
- Saves 70%+ of Claude's context budget
- Automatic model selection and capability matching
- Parallel multi-perspective analysis
- Cross-platform compatible (Windows/macOS/Linux)
- 5 slash commands: /analyze, /review, /architect, /models, /deep-analyze
- 3 specialized agents for ollama model orchestration

**Version:** 1.0.0
**Category:** Productivity
**License:** MIT

[Full Documentation](./plugins/claude-ollama-agents/README.md)

## Installation

### Add This Marketplace to Claude Code

```bash
# In Claude Code, run:
/plugin marketplace add dansasser/claude-code-marketplace
```

### Install Plugins

After adding the marketplace, you can browse and install plugins:

```bash
# Browse available plugins
/plugin

# Or install directly
/plugin install claude-ollama-agents
```

### Manual Installation

If you prefer manual installation:

```bash
# Clone this repository
git clone https://github.com/dansasser/claude-code-marketplace.git

# Navigate to the plugin you want
cd claude-code-marketplace/plugins/claude-ollama-agents

# Run the installer
./install.sh
```

## Prerequisites

Plugins in this marketplace may have specific requirements. Check each plugin's README for details.

**For claude-ollama-agents:**
1. Install ollama from [ollama.ai](https://ollama.ai)
2. Pull models: `ollama pull kimi-k2-thinking:cloud`
3. Install ollama-prompt: `pip install ollama-prompt`

## Plugin Structure

This marketplace follows the official Claude Code plugin structure:

```
claude-code-marketplace/
├── .claude-plugin/
│   └── marketplace.json      # Marketplace definition
└── plugins/
    └── claude-ollama-agents/  # Individual plugins
        ├── .claude-plugin/
        │   └── plugin.json
        ├── agents/            # Subagents
        ├── commands/          # Slash commands
        ├── scripts/           # Helper scripts
        └── README.md
```

## Contributing

Contributions are welcome! To add a plugin to this marketplace:

1. Fork this repository
2. Add your plugin to `plugins/`
3. Update `.claude-plugin/marketplace.json`
4. Submit a pull request

## Support

- **Issues:** [GitHub Issues](https://github.com/dansasser/claude-code-marketplace/issues)
- **Contact:** contact@dansasser.me
- **Website:** [dansasser.me](https://dansasser.me)

## License

This marketplace and its plugins are licensed under the MIT License. See individual plugin directories for specific license files.

## About

Created and maintained by Daniel T Sasser II

Part of the SIM-ONE Framework ecosystem for AI-assisted development.
