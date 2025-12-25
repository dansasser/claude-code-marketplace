# PR Prep Plugin - Implementation Plan

## Overview

A Claude Code plugin that automates the complete PR preparation and publishing workflow. Takes any branch state (committed, uncommitted, unknown) and delivers a published package through GitHub.

**Key Principle:** Run CI locally BEFORE pushing to prevent GitHub CI failures.

---

## Full Workflow Diagram

```
START: Unknown branch state
    |
    v
+---------------------------+
| Phase 0: Environment      |
| Detection (ONCE)          |
|  - OS (Windows/Linux/Mac) |
|  - Python/Node paths      |
|  - MCP tools available    |
|  - gh CLI available       |
+------------+--------------+
             |
             v
+---------------------------+
| Phase 1: Project          |
| Detection                 |
|  - Python (pyproject.toml)|
|  - Node-TS (package.json  |
|    + tsconfig.json)       |
|  - Node-JS (package.json) |
+------------+--------------+
             |
             +-- Unknown --> STOP, ask user
             |
             v
+---------------------------+
| Phase 2: Workflow         |
| Validation                |
|  - Check .github/workflows|
|  - ci.yml exists?         |
+------------+--------------+
             |
             +-- Missing --> Generate from template
             |
             +-- Invalid --> Regenerate
             |
             v
+---------------------------+
| Phase 3: Branch Analysis  |
|  - git status             |
|  - Uncommitted changes?   |
|  - Unpushed commits?      |
|  - Diff since main/master |
+------------+--------------+
             |
             v
+---------------------------+
| Phase 4: Lock File Check  |
|  - package-lock.json sync |
|  - poetry.lock sync       |
|  - requirements.txt sync  |
+------------+--------------+
             |
             +-- Mismatch --> WARN, suggest fix
             |
             v
+----------------------------------------------+
| Phase 5: Local CI Execution                  |
| (with Smart Error Recovery)                  |
+----------------------------------------------+
             |
    +--------+--------+
    |                 |
    v                 v
+----------+    +----------+
| Python   |    | Node.js  |
| CI       |    | CI       |
|----------|    |----------|
| 1. ruff  |    | 1. npm ci|
| 2. mypy  |    | 2. lint  |
| 3. pytest|    | 3. tsc   |
| 4. build |    | 4. build |
+----+-----+    | 5. test  |
     |          +----+-----+
     |               |
     +-------+-------+
             |
             +-- FAIL?
             |
             v
+----------------------------------------------+
| Phase 5b: Error Diagnosis & Recovery         |
|                                              |
|  1. Parse error output                       |
|  2. Classify error type:                     |
|     - CODE_ERROR: Actual bug in code         |
|     - DEP_CORRUPTION: node_modules/.venv bad |
|     - LOCK_DESYNC: Lock file out of sync     |
|     - STALE_ARTIFACTS: Old build files       |
|     - CACHE_POISON: npm/pip cache issues     |
|     - VERSION_MISMATCH: Wrong Node/Python    |
|                                              |
|  3. If recoverable, auto-fix:                |
|     - DEP_CORRUPTION:                        |
|         shutil.rmtree("node_modules")        |
|         subprocess.run(["npm", "install"])   |
|     - LOCK_DESYNC:                           |
|         Path("package-lock.json").unlink()   |
|         subprocess.run(["npm", "install"])   |
|     - STALE_ARTIFACTS:                       |
|         shutil.rmtree("dist")                |
|         subprocess.run(["npm","run","build"])|
|     - CACHE_POISON:                          |
|         subprocess.run(["npm","cache",       |
|                         "clean","--force"])  |
|                                              |
|  4. Retry failed check (max 1 retry)         |
|                                              |
|  5. If still fails OR CODE_ERROR:            |
|     --> STOP, show errors, suggest fix       |
+----------------------------------------------+
             |
             +-- STILL FAIL --> STOP, show errors
             |
             +-- PASS (after recovery or first try)
             |
             v
+---------------------------+
| Phase 6: Git Operations   |
|  - git add . (all changes)|
|  - git commit -m "msg"    |
|    (conventional format)  |
+------------+--------------+
             |
             v
+---------------------------+
| Phase 7: Push             |
|  - git push -u origin HEAD|
+------------+--------------+
             |
             v
+---------------------------+
| Phase 8: PR Creation      |
|  (MCP default, gh backup) |
|  - Generate Mermaid       |
|  - Generate PR body       |
|  - mcp__github__          |
|    create_pull_request    |
+------------+--------------+
             |
             v
+---------------------------+
| Phase 9: GitHub CI        |
| Monitoring                |
|  - Poll PR status         |
|  - mcp__github__          |
|    pull_request_read      |
|  - Wait for checks        |
+------------+--------------+
             |
             +-- CI FAIL --> Report, suggest fixes
             |
             +-- CI PASS
             |
             v
+---------------------------+
| Phase 10: Merge & Release |
| (Optional, with approval) |
|  - mcp__github__          |
|    merge_pull_request     |
|  - Create version tag     |
|  - Triggers publish.yml   |
+------------+--------------+
             |
             v
END: Package published to PyPI/npm
```

---

## Plugin Structure

```
pr-prep/
├── .claude-plugin/
│   └── plugin.json              # Plugin manifest
├── agents/
│   ├── pr-prep-orchestrator.md  # Main workflow (phases 0-10)
│   └── pr-composer.md           # Mermaid + PR body generation
├── commands/
│   └── prep-pr.md               # Entry point: /prep-pr
├── scripts/
│   ├── detect_env.py            # Phase 0: OS, tools, paths
│   ├── detect_project.py        # Phase 1: Python vs Node
│   ├── validate_workflow.py     # Phase 2: Check CI workflow
│   ├── generate_workflow.py     # Phase 2: Generate CI workflow
│   ├── analyze_branch.py        # Phase 3: Git state analysis
│   ├── check_lockfiles.py       # Phase 4: Lock file consistency
│   ├── run_ci_python.py         # Phase 5: Python CI execution
│   ├── run_ci_node.py           # Phase 5: Node CI execution
│   ├── error_recovery.py        # Phase 5b: Smart error diagnosis & recovery
│   └── generate_mermaid.py      # Phase 8: Mermaid from git diff
├── templates/
│   ├── ci-python.yml            # Python CI workflow template
│   ├── ci-node.yml              # Node.js CI workflow template
│   └── pr-body.md               # PR description template
└── README.md
```

---

## Agents

### 1. pr-prep-orchestrator

**Purpose:** Coordinates all 10 phases from unknown branch state to published package.

**Tools:** Read, Write, Bash, Glob, Grep, Task (for pr-composer)

**Model:** sonnet

**Key Responsibilities:**
- Run environment detection ONCE at start, store in state
- Route to correct CI based on project type
- Enforce "no push without passing local CI"
- Use MCP GitHub tools by default, gh CLI as fallback
- Track state for resume capability

**GitHub Operations (MCP-first):**

| Operation | MCP Tool | gh Fallback |
|-----------|----------|-------------|
| Create PR | `mcp__github__create_pull_request` | `gh pr create` |
| Get PR status | `mcp__github__pull_request_read` | `gh pr view` |
| List PRs | `mcp__github__list_pull_requests` | `gh pr list` |
| Merge PR | `mcp__github__merge_pull_request` | `gh pr merge` |
| Get commits | `mcp__github__list_commits` | `gh api` |

### 2. pr-composer

**Purpose:** Generates detailed PR content with Mermaid diagrams.

**Tools:** Read, Glob, Grep

**Model:** haiku (lightweight, focused task)

**Key Responsibilities:**
- Analyze git diff to identify changed files
- Generate Mermaid flowchart showing changes
- Create structured PR body with:
  - Summary (from commit messages)
  - Changes visualization (Mermaid)
  - Local CI results table
  - Test plan checklist
- Generate changelog entries if needed

---

## Slash Command

### /prep-pr

**Usage:**
```
/prep-pr [options]
```

**Options:**
- `--no-push` - Run CI only, don't push or create PR
- `--no-commit` - Run CI only, don't stage/commit
- `--resume` - Resume from last failed phase
- `--merge` - Auto-merge after CI passes (requires approval)
- `--release` - Create version tag after merge (triggers publish)

**Default behavior:** Full pipeline through PR creation, stops before merge.

---

## Scripts (Python stdlib only)

All scripts use Python standard library for cross-platform compatibility.
**CRITICAL: All file operations use pathlib/shutil, NEVER shell commands like rm/del.**

### detect_env.py
```python
# Detects: OS, shell, python path, node path, npm path
# Checks: MCP tools available, gh CLI available
# Output: JSON with environment state
```

### detect_project.py
```python
# Checks for: pyproject.toml, setup.py, package.json, tsconfig.json
# Detects: source dirs, test dirs, package manager
# Output: JSON with project type and config
```

### validate_workflow.py
```python
# Checks: .github/workflows/ci.yml exists
# Validates: Required jobs present (lint, test, build)
# Output: JSON with validation status
```

### generate_workflow.py
```python
# Templates: ci-python.yml, ci-node.yml
# Generates: .github/workflows/ci.yml
# Customizes: Based on detected project config
```

### analyze_branch.py
```python
# Runs: git status, git diff, git log
# Detects: Uncommitted, unstaged, unpushed changes
# Output: JSON with complete branch state
```

### check_lockfiles.py
```python
# Compares: package.json vs package-lock.json timestamps
# Compares: pyproject.toml vs poetry.lock
# Output: JSON with sync status and warnings
```

### run_ci_python.py
```python
# Executes: ruff check, mypy, pytest, python -m build
# Captures: Exit codes, stdout, stderr, duration
# Includes: Error diagnosis and recovery (see below)
# Output: JSON with results per check
```

### run_ci_node.py
```python
# Executes: npm ci, npm run lint, tsc --noEmit, npm run build, npm test
# Captures: Exit codes, stdout, stderr, duration
# Includes: Error diagnosis and recovery (see below)
# Output: JSON with results per check
```

### generate_mermaid.py
```python
# Parses: git diff output
# Generates: Mermaid flowchart showing file changes
# Categories: Added, Modified, Deleted files
# Output: Mermaid markdown string
```

### error_recovery.py (NEW - shared module)
```python
"""
Smart error diagnosis and recovery for CI failures.
Uses ONLY Python stdlib for cross-platform compatibility.
"""
from pathlib import Path
import shutil
import subprocess
import re
from enum import Enum
from typing import Optional, Dict, Any

class ErrorType(Enum):
    CODE_ERROR = "code_error"           # Actual bug - cannot auto-fix
    DEP_CORRUPTION = "dep_corruption"   # node_modules or .venv corrupted
    LOCK_DESYNC = "lock_desync"         # Lock file out of sync
    STALE_ARTIFACTS = "stale_artifacts" # Old build files causing issues
    CACHE_POISON = "cache_poison"       # npm/pip cache corrupted
    VERSION_MISMATCH = "version_mismatch"  # Wrong Node/Python version
    UNKNOWN = "unknown"                 # Cannot classify

# Error patterns for diagnosis
ERROR_PATTERNS = {
    ErrorType.DEP_CORRUPTION: [
        r"Cannot find module",
        r"Module not found",
        r"No module named",
        r"ENOENT.*node_modules",
        r"ModuleNotFoundError",
        r"ImportError.*No module",
    ],
    ErrorType.LOCK_DESYNC: [
        r"peer dep.*conflict",
        r"ERESOLVE",
        r"unable to resolve dependency tree",
        r"Your lockfile needs to be updated",
        r"poetry.lock.*out of sync",
    ],
    ErrorType.STALE_ARTIFACTS: [
        r"Cannot find.*dist/",
        r"ENOENT.*dist/",
        r"File.*dist.*does not exist",
        r"stale.*build",
    ],
    ErrorType.CACHE_POISON: [
        r"EINTEGRITY",
        r"sha512.*integrity",
        r"Cached.*corrupted",
        r"cache.*invalid",
    ],
    ErrorType.VERSION_MISMATCH: [
        r"engine.*not compatible",
        r"requires.*node",
        r"python.*required",
        r"unsupported.*version",
    ],
}

def diagnose_error(stderr: str, stdout: str) -> ErrorType:
    """Classify error based on output patterns."""
    combined = stderr + stdout

    for error_type, patterns in ERROR_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, combined, re.IGNORECASE):
                return error_type

    # If no pattern matched but there's an error, it's likely code
    return ErrorType.CODE_ERROR

def recover_node(error_type: ErrorType, project_dir: Path) -> bool:
    """
    Attempt recovery for Node.js projects.
    Returns True if recovery was attempted.
    ALL file operations use pathlib/shutil.
    """
    node_modules = project_dir / "node_modules"
    lock_file = project_dir / "package-lock.json"
    dist_dir = project_dir / "dist"

    if error_type == ErrorType.DEP_CORRUPTION:
        # Delete node_modules and reinstall
        if node_modules.exists():
            shutil.rmtree(node_modules)
        subprocess.run(["npm", "install"], cwd=project_dir, check=True)
        return True

    elif error_type == ErrorType.LOCK_DESYNC:
        # Delete lock file and reinstall
        if lock_file.exists():
            lock_file.unlink()
        if node_modules.exists():
            shutil.rmtree(node_modules)
        subprocess.run(["npm", "install"], cwd=project_dir, check=True)
        return True

    elif error_type == ErrorType.STALE_ARTIFACTS:
        # Delete dist and rebuild
        if dist_dir.exists():
            shutil.rmtree(dist_dir)
        subprocess.run(["npm", "run", "build"], cwd=project_dir, check=True)
        return True

    elif error_type == ErrorType.CACHE_POISON:
        # Clean npm cache
        subprocess.run(["npm", "cache", "clean", "--force"], check=True)
        if node_modules.exists():
            shutil.rmtree(node_modules)
        subprocess.run(["npm", "install"], cwd=project_dir, check=True)
        return True

    return False  # CODE_ERROR or UNKNOWN - cannot auto-fix

def recover_python(error_type: ErrorType, project_dir: Path) -> bool:
    """
    Attempt recovery for Python projects.
    Returns True if recovery was attempted.
    ALL file operations use pathlib/shutil.
    """
    venv_dir = project_dir / ".venv"
    dist_dir = project_dir / "dist"
    egg_info = list(project_dir.glob("*.egg-info"))
    pycache = list(project_dir.rglob("__pycache__"))

    if error_type == ErrorType.DEP_CORRUPTION:
        # Delete .venv and reinstall
        if venv_dir.exists():
            shutil.rmtree(venv_dir)
        # Clean pycache
        for cache in pycache:
            shutil.rmtree(cache)
        subprocess.run(["pip", "install", "-e", ".[dev]"],
                      cwd=project_dir, check=True)
        return True

    elif error_type == ErrorType.STALE_ARTIFACTS:
        # Delete dist and egg-info
        if dist_dir.exists():
            shutil.rmtree(dist_dir)
        for egg in egg_info:
            shutil.rmtree(egg)
        subprocess.run(["python", "-m", "build"],
                      cwd=project_dir, check=True)
        return True

    elif error_type == ErrorType.CACHE_POISON:
        # Purge pip cache
        subprocess.run(["pip", "cache", "purge"], check=True)
        if venv_dir.exists():
            shutil.rmtree(venv_dir)
        subprocess.run(["pip", "install", "-e", ".[dev]"],
                      cwd=project_dir, check=True)
        return True

    return False  # CODE_ERROR or UNKNOWN - cannot auto-fix
```

---

## CI Workflow Templates

### ci-python.yml
```yaml
name: CI

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install ruff
      - run: ruff check .

  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install mypy
      - run: mypy . --ignore-missing-imports

  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
        python-version: ["3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -e ".[dev]"
      - run: pytest tests/ -v

  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install build
      - run: python -m build
```

### ci-node.yml
```yaml
name: CI

on:
  push:
    branches: [main, master]
  pull_request:
    branches: [main, master]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - run: npm ci
      - run: npm run lint

  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - run: npm ci
      - run: npm run typecheck

  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "20"
      - run: npm ci
      - run: npm run build

  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [18, 20, 22]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      - run: npm ci
      - run: npm test
```

---

## PR Body Template

```markdown
## Summary

{{ summary_from_commits }}

## Changes

```mermaid
{{ mermaid_diagram }}
```

## Local CI Results

All checks passed locally before push:

| Check | Status | Duration | Details |
|-------|--------|----------|---------|
{{ ci_results_table }}

## Test Plan

- [x] Lint passes locally
- [x] Type check passes locally
- [x] All tests pass locally
- [x] Build succeeds locally
- [ ] GitHub CI passes
- [ ] Manual testing (if applicable)

---
Generated by [PR Prep](https://github.com/dansasser/claude-code-marketplace/tree/main/plugins/pr-prep)
```

---

## Command Count Analysis

| Phase | Commands | Type | Platform Safe |
|-------|----------|------|---------------|
| 0 | 1 | Python script | Yes (stdlib) |
| 1 | 1 | Python script | Yes (stdlib) |
| 2 | 1-2 | Python script | Yes (stdlib) |
| 3 | 3 | git status/diff/log | Yes (git cross-platform) |
| 4 | 1 | Python script | Yes (stdlib) |
| 5 | 4-5 | python -m / npm | Yes (cross-platform) |
| 6 | 2 | git add/commit | Yes (git cross-platform) |
| 7 | 1 | git push | Yes (git cross-platform) |
| 8 | 1 | MCP tool | Yes (no shell) |
| 9 | 1-3 | MCP tool (polling) | Yes (no shell) |
| 10 | 2 | MCP tool + git tag | Yes |

**Total: ~18-22 commands**
**Environment checks: 1 (Phase 0 only)**
**All commands cross-platform safe**

---

## Error Handling

On ANY phase failure:

1. Capture error context (phase, command, exit code, stderr)
2. Save state to `~/.claude/pr-prep-state.json`
3. Display error with file:line if applicable
4. Suggest fix command
5. STOP pipeline
6. User can resume with `/prep-pr --resume`

**State file structure:**
```json
{
  "started_at": "ISO8601",
  "project_dir": "/path/to/project",
  "environment": { ... },
  "project": { ... },
  "phases": {
    "env_detect": "PASS",
    "project_detect": "PASS",
    "workflow_valid": "PASS",
    "branch_analysis": "PASS",
    "lockfile_check": "PASS",
    "local_ci": "FAIL",
    "git_commit": "PENDING",
    "git_push": "PENDING",
    "pr_create": "PENDING",
    "ci_monitor": "PENDING",
    "merge_release": "PENDING"
  },
  "last_error": {
    "phase": "local_ci",
    "check": "pytest",
    "message": "2 tests failed",
    "details": "..."
  }
}
```

---

## Implementation Order

1. **Scripts first** (foundation)
   - detect_env.py
   - detect_project.py
   - analyze_branch.py

2. **Error recovery** (critical for robustness)
   - error_recovery.py (shared module with ErrorType enum, patterns, recovery functions)

3. **CI execution scripts** (uses error_recovery)
   - run_ci_python.py
   - run_ci_node.py
   - check_lockfiles.py

4. **Workflow generation**
   - validate_workflow.py
   - generate_workflow.py
   - templates/ci-python.yml
   - templates/ci-node.yml

5. **PR composition**
   - generate_mermaid.py
   - templates/pr-body.md
   - agents/pr-composer.md

6. **Main orchestrator**
   - agents/pr-prep-orchestrator.md

7. **Entry point**
   - commands/prep-pr.md

8. **Plugin packaging**
   - .claude-plugin/plugin.json
   - README.md

---

## Key Design Decisions

1. **MCP GitHub tools are default** - gh CLI is fallback only
2. **One environment check at startup** - stored in state, not per-command
3. **All file operations use Python stdlib** - pathlib, shutil, never shell commands
4. **Smart error recovery with retry** - diagnose, fix, retry once, then fail
5. **Cross-platform by design** - no emojis, no Unix assumptions
6. **State persistence for resume** - can continue after failures

---

## Output Location

`C:\Claude\repos\claude-code-marketplace\plugins\pr-prep\`
