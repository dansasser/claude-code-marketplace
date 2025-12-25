---
description: Full PR preparation pipeline with local CI validation
argument-hint: [--no-push] [--resume] [--merge] [--release]
---

# Prepare PR

Automate the complete PR preparation workflow from any branch state to published package.

## What This Command Does

1. **Detects** your environment and project type (Python or Node.js)
2. **Validates** CI workflow exists (creates one if missing)
3. **Analyzes** git state (uncommitted, unstaged, unpushed changes)
4. **Checks** lock file consistency
5. **Runs** local CI (lint, type, test, build) with smart error recovery
6. **Commits** changes if needed
7. **Pushes** to remote
8. **Creates** detailed PR with Mermaid diagrams

## Usage

```
/prep-pr              # Full pipeline
/prep-pr --no-push    # Run CI only, don't push
/prep-pr --resume     # Resume from last failure
/prep-pr --merge      # Auto-merge after CI passes
/prep-pr --release    # Create version tag after merge
```

## Options

- `--no-push` - Run local CI validation only, don't push or create PR
- `--resume` - Resume from last saved state (useful after fixing errors)
- `--merge` - Wait for GitHub CI, then auto-merge the PR
- `--release` - After merge, create a version tag for release

## Requirements

- Git repository with a remote configured
- Python 3.10+ (for running helper scripts)
- For Python projects: ruff, mypy, pytest, build
- For Node projects: npm/yarn/pnpm/bun, eslint, tsc

## Example Workflow

```
$ /prep-pr

[INFO] Starting PR preparation...
[OK] Environment: Windows 11, PowerShell
[OK] Project: Python (pip), pyproject.toml detected
[OK] Workflow: .github/workflows/ci.yml exists
[INFO] Analyzing git state...
[OK] Branch: feature/auth (3 commits ahead of main)
[INFO] Running local CI...
[OK] lint (ruff) - 1.2s
[OK] type (mypy) - 3.4s
[OK] test (pytest) - 8.7s
[OK] build - 2.1s
[INFO] Pushing to origin/feature/auth...
[OK] Pushed successfully
[INFO] Creating pull request...
[OK] PR #42 created: https://github.com/user/repo/pull/42
```

## Error Recovery

If CI fails, the system will:

1. **Diagnose** the error type (dependency, lock file, stale artifacts, cache)
2. **Attempt** automatic recovery for recoverable errors
3. **Report** clearly if manual intervention is needed

For code errors, you'll need to fix the issue and run `/prep-pr --resume`.

## Generated PR Format

The PR will include:

- **Summary** - Synthesized from commit messages
- **Changes** - Mermaid diagram showing modified files
- **CI Results** - Table of local check results
- **Test Plan** - Checklist for review

---

Execute the pr-prep-orchestrator agent to begin the pipeline.

Pass the following context to the orchestrator:
- Current working directory: $CWD
- Command arguments: $ARGUMENTS
- Available tools: scripts in ./scripts/, MCP GitHub tools, gh CLI fallback

The orchestrator will handle all phases and report progress.
