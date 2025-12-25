# PR Prep

Automated PR preparation with local CI validation, smart error recovery, and Mermaid diagram generation.

## Overview

Takes any branch state (committed, uncommitted, unknown) and delivers a published package through GitHub.

**Key Principle:** Run CI locally BEFORE pushing to prevent GitHub CI failures.

## Features

- Detects Python and Node.js/TypeScript projects automatically
- Generates CI workflows if missing
- Runs local CI checks (lint, type, test, build)
- Smart error recovery (fixes corrupted deps, stale artifacts, lock file issues)
- Creates detailed PRs with Mermaid diagrams
- Uses MCP GitHub tools by default, gh CLI as fallback
- Cross-platform (Windows, Linux, macOS)

## Installation

```bash
claude plugins install pr-prep
```

## Usage

```bash
/prep-pr              # Full pipeline
/prep-pr --no-push    # Run CI only, don't push
/prep-pr --resume     # Resume from last failure
/prep-pr --merge      # Auto-merge after CI passes
/prep-pr --release    # Create version tag after merge
```

## Documentation

See [PLAN.md](./PLAN.md) for full implementation details.

## License

MIT
