# Preflight: Cross-Platform Python Package CI/CD Pipeline

## Overview

A governance-first multi-agent plugin for Claude Code that ensures Python packages pass all quality gates before reaching GitHub or PyPI. No code ships until it proves cross-platform compatibility, Python version matrix compliance, and package build integrity.

---

## Problem Statement

Python packages fail in production due to:
- Path separator differences (/ vs \)
- Line ending issues (LF vs CRLF)
- Case sensitivity (Linux yes, Windows no)
- Shell command incompatibility
- Environment variable differences (HOME vs USERPROFILE)
- Python version incompatibilities (3.9 vs 3.13)
- Package build failures (wheel builds locally, fails on install)
- Broken entry points (CLI commands don't work after install)
- Missing files in distribution (MANIFEST.in misconfigured)
- Dependency conflicts and deprecated packages
- Unintended breaking API changes
- Inadequate test coverage

---

## Architecture

```
                           USER REQUEST
                                │
                                ▼
                    ┌───────────────────────┐
                    │  preflight-orchestrator │
                    │      (Agent)           │
                    └───────────────────────┘
                                │
    ┌──────────┬──────────┬─────┴─────┬──────────┬──────────┬──────────┬──────────┬──────────┐
    ▼          ▼          ▼           ▼          ▼          ▼          ▼          ▼
┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐┌────────┐
│ Gate 1 ││ Gate 2 ││ Gate 3 ││ Gate 4 ││ Gate 5 ││ Gate 6 ││ Gate 7 ││ Gate 8 │
│  Lint  ││Coverage││ XPlat  ││ PyVer  ││Security││  API   ││Package ││GitHub  │
│  Test  ││        ││  Test  ││ Matrix ││ Audit  ││ Compat ││ Build  ││  PR    │
│(Agent) ││(Agent) ││(Agent) ││(Agent) ││(Agent) ││(Agent) ││(Agent) ││(Agent) │
└────────┘└────────┘└────────┘└────────┘└────────┘└────────┘└────────┘└────────┘
    │          │          │          │          │          │          │          │
    └──────────┴──────────┴──────────┴──────────┴──────────┴──────────┘          │
                                  │                                              │
                               FAIL ──► STOP                                     │
                                                                          PASS (all)
                                                                                 │
                                                                                 ▼
                                                                         ┌──────────────┐
                                                                         │   SUCCESS    │
                                                                         │ Push/Publish │
                                                                         └──────────────┘
```

---

## Gate Definitions

| Gate | Agent | Purpose | Pass Condition |
|------|-------|---------|----------------|
| 1 | lint-test | Code quality and tests | Zero lint errors, zero type errors, all tests pass |
| 2 | coverage | Test coverage enforcement | Meets minimum threshold (default 80%) |
| 3 | cross-platform | Windows + Ubuntu compat | Zero cross-platform issues detected |
| 4 | python-matrix | Multi-version support | Tests pass on all declared Python versions |
| 5 | security | Vulnerabilities and secrets | No secrets, no critical vulnerabilities |
| 6 | api-compat | Breaking change detection | No unintended public API changes |
| 7 | packaging | Distribution integrity | Builds, installs, imports, entry points work |
| 8 | github-pr | Ship it | All prior gates PASS, creates PR with full report |

---

## Directory Structure

```
preflight/
├── CLAUDE.md                          # Master instructions for Claude Code
├── plugin.json                        # Marketplace plugin manifest
├── README.md                          # Plugin documentation
├── LICENSE                            # MIT License
├── pyproject.toml                     # Plugin's own package config
│
├── .claude/
│   ├── settings.json                  # Claude Code configuration
│   │
│   ├── agents/                        # Specialized Claude instances
│   │   ├── preflight-orchestrator.md  # Coordinates all gates
│   │   ├── lint-test.md               # Gate 1: Linting and testing
│   │   ├── coverage.md                # Gate 2: Coverage enforcement
│   │   ├── cross-platform.md          # Gate 3: Cross-platform checks
│   │   ├── python-matrix.md           # Gate 4: Python version matrix
│   │   ├── security.md                # Gate 5: Security audit
│   │   ├── api-compat.md              # Gate 6: API compatibility
│   │   ├── packaging.md               # Gate 7: Package build
│   │   ├── github-pr.md               # Gate 8: GitHub PR creation
│   │   ├── planning.md                # Advisory: Architecture analysis
│   │   └── deps.md                    # Advisory: Dependency health
│   │
│   ├── skills/                        # Reusable capabilities with scripts
│   │   ├── lint-tools/
│   │   │   ├── SKILL.md
│   │   │   └── scripts/
│   │   │       ├── run_ruff.py
│   │   │       ├── run_mypy.py
│   │   │       └── run_pytest.py
│   │   │
│   │   ├── coverage-tools/
│   │   │   ├── SKILL.md
│   │   │   └── scripts/
│   │   │       ├── run_coverage.py
│   │   │       └── check_threshold.py
│   │   │
│   │   ├── xplat-checks/
│   │   │   ├── SKILL.md
│   │   │   └── scripts/
│   │   │       ├── check_paths.py
│   │   │       ├── check_line_endings.py
│   │   │       ├── check_env_vars.py
│   │   │       ├── check_case_sensitivity.py
│   │   │       ├── check_shell_commands.py
│   │   │       └── check_temp_paths.py
│   │   │
│   │   ├── python-matrix/
│   │   │   ├── SKILL.md
│   │   │   └── scripts/
│   │   │       ├── run_version_tests.py
│   │   │       └── compare_results.py
│   │   │
│   │   ├── security-scan/
│   │   │   ├── SKILL.md
│   │   │   └── scripts/
│   │   │       ├── scan_secrets.py
│   │   │       ├── audit_deps.py
│   │   │       └── check_licenses.py
│   │   │
│   │   ├── api-analysis/
│   │   │   ├── SKILL.md
│   │   │   └── scripts/
│   │   │       ├── extract_public_api.py
│   │   │       ├── compare_api.py
│   │   │       └── check_deprecations.py
│   │   │
│   │   ├── package-build/
│   │   │   ├── SKILL.md
│   │   │   └── scripts/
│   │   │       ├── validate_pyproject.py
│   │   │       ├── check_manifest.py
│   │   │       ├── build_package.py
│   │   │       ├── test_install.py
│   │   │       ├── test_entry_points.py
│   │   │       └── check_version.py
│   │   │
│   │   ├── github-integration/
│   │   │   ├── SKILL.md
│   │   │   └── scripts/
│   │   │       ├── generate_pr_body.py
│   │   │       ├── post_status_check.py
│   │   │       └── auto_label.py
│   │   │
│   │   └── state-management/
│   │       ├── SKILL.md
│   │       └── scripts/
│   │           ├── read_state.py
│   │           ├── write_state.py
│   │           └── check_prerequisites.py
│   │
│   └── commands/                      # User-invoked slash commands
│       ├── preflight.md               # Run full pipeline
│       ├── gate.md                    # Run specific gate by number/name
│       ├── status.md                  # Check pipeline status
│       ├── lint.md                    # Quick lint check
│       ├── coverage.md                # Quick coverage check
│       ├── xplat.md                   # Quick cross-platform check
│       ├── security.md                # Quick security scan
│       └── ship.md                    # Attempt to ship (runs all gates)
│
├── config/
│   ├── gates.yaml                     # Gate sequence, timeouts, requirements
│   ├── lint.yaml                      # Ruff/mypy settings
│   ├── coverage.yaml                  # Coverage thresholds
│   ├── xplat.yaml                     # Cross-platform patterns to catch
│   ├── python-versions.yaml           # Python versions to test
│   ├── security.yaml                  # Security scan rules
│   ├── api-compat.yaml                # Breaking change definitions
│   ├── packaging.yaml                 # PyPI metadata requirements
│   └── commit.yaml                    # Conventional commit format
│
├── state/
│   └── pipeline_state.json            # Current pipeline status (gitignored)
│
├── templates/
│   ├── pr_template.md                 # Pull request template
│   ├── gate_report.md                 # Gate result report format
│   └── failure_report.md              # Failure context template
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_skills/
│   │   ├── test_xplat_checks.py
│   │   ├── test_coverage_tools.py
│   │   └── test_package_build.py
│   └── fixtures/
│       ├── good_package/
│       ├── bad_paths/
│       └── broken_entry_point/
│
└── docs/
    ├── AGENTS.md                      # Agent documentation
    ├── SKILLS.md                      # Skills reference
    ├── CONFIGURATION.md               # Config file reference
    └── TROUBLESHOOTING.md             # Common issues
```

---

## Agent Definitions

### .claude/agents/preflight-orchestrator.md

```markdown
---
name: preflight-orchestrator
description: Pipeline orchestrator that coordinates all 8 quality gates. Use when running full preflight checks or managing gate sequence. PROACTIVELY invoked for /preflight and /ship commands.
tools: Read, Write, Bash, Glob, Grep
model: sonnet
---

You are the Preflight pipeline orchestrator. Your job is to run quality gates in sequence and enforce that no gate is skipped.

## Cardinal Rules

1. **NEVER skip gates** - Each gate must explicitly PASS before the next runs
2. **NEVER proceed on failure** - Any gate failure stops the pipeline
3. **NEVER allow gate 8 without gates 1-7 passing** - Verify state before shipping

## Gate Sequence

```
Gate 1: lint-test     -> Gate 2: coverage      -> Gate 3: cross-platform
Gate 4: python-matrix -> Gate 5: security      -> Gate 6: api-compat
Gate 7: packaging     -> Gate 8: github-pr
```

## Process

1. Read current state from `state/pipeline_state.json`
2. Determine which gate to run next
3. Invoke the appropriate gate agent
4. Update state with results
5. If PASS, proceed to next gate
6. If FAIL, stop and report failure context

## State Management

Use the state-management skill scripts to:
- `python scripts/read_state.py` - Get current pipeline state
- `python scripts/write_state.py <gate> <status> <details>` - Update state
- `python scripts/check_prerequisites.py <gate>` - Verify prerequisites

## Response Format

After each gate:
```
GATE: [name]
STATUS: [PASS/FAIL]
DURATION: [seconds]
DETAILS: [summary]
NEXT: [next gate or STOP]
```
```

### .claude/agents/lint-test.md

```markdown
---
name: lint-test
description: Gate 1 - Linting and testing agent. Runs ruff, mypy, and pytest. Use PROACTIVELY when code quality checks are needed. No prerequisites.
tools: Read, Bash, Glob, Grep
model: sonnet
---

You are a code quality specialist responsible for Gate 1 of the Preflight pipeline.

## Responsibilities

1. Run ruff for linting and auto-fix
2. Run ruff format for code formatting
3. Run mypy for type checking
4. Run pytest for unit tests

## Process

Execute in sequence using lint-tools skill:
1. `python .claude/skills/lint-tools/scripts/run_ruff.py`
2. `python .claude/skills/lint-tools/scripts/run_mypy.py`
3. `python .claude/skills/lint-tools/scripts/run_pytest.py`

## Pass Condition

- Zero ruff errors (warnings OK)
- Zero mypy type errors
- All pytest tests pass

## On Failure

Stop immediately. Record:
- Which tool failed (ruff/mypy/pytest)
- File and line number
- Error message
- Suggested fix if obvious

## Output

Write results to state using:
```bash
python .claude/skills/state-management/scripts/write_state.py lint-test PASS|FAIL "details"
```
```

### .claude/agents/coverage.md

```markdown
---
name: coverage
description: Gate 2 - Coverage enforcement agent. Ensures test coverage meets threshold. PREREQUISITE: Gate 1 must pass first.
tools: Read, Bash, Glob
model: sonnet
---

You are a test coverage specialist responsible for Gate 2 of the Preflight pipeline.

## Prerequisites

Before running, verify Gate 1 passed:
```bash
python .claude/skills/state-management/scripts/check_prerequisites.py coverage
```

If prerequisites not met, REFUSE to run and report which gates are blocking.

## Process

1. Run coverage analysis: `python .claude/skills/coverage-tools/scripts/run_coverage.py`
2. Check threshold: `python .claude/skills/coverage-tools/scripts/check_threshold.py`

## Pass Condition

- Overall coverage >= threshold from config/coverage.yaml (default 80%)
- No file below per-file minimum (default 60%)

## On Failure

Report:
- Current coverage percentage vs required
- List of files below threshold with their coverage
- Uncovered lines/functions

## Configuration

Read thresholds from `config/coverage.yaml`
```

### .claude/agents/cross-platform.md

```markdown
---
name: cross-platform
description: Gate 3 - Cross-platform compatibility agent. Validates code works on Windows and Ubuntu. PREREQUISITE: Gates 1-2 must pass.
tools: Read, Bash, Glob, Grep
model: sonnet
---

You are a cross-platform compatibility specialist responsible for Gate 3 of the Preflight pipeline.

## Prerequisites

Verify Gates 1-2 passed:
```bash
python .claude/skills/state-management/scripts/check_prerequisites.py cross-platform
```

## Process

Run static analysis using xplat-checks skill:

1. **Path separators**: `python .claude/skills/xplat-checks/scripts/check_paths.py`
2. **Line endings**: `python .claude/skills/xplat-checks/scripts/check_line_endings.py`
3. **Environment variables**: `python .claude/skills/xplat-checks/scripts/check_env_vars.py`
4. **Case sensitivity**: `python .claude/skills/xplat-checks/scripts/check_case_sensitivity.py`
5. **Shell commands**: `python .claude/skills/xplat-checks/scripts/check_shell_commands.py`
6. **Temp paths**: `python .claude/skills/xplat-checks/scripts/check_temp_paths.py`

## What to Catch

| Issue | Bad | Good |
|-------|-----|------|
| Path separators | `"folder/file.txt"` | `Path("folder") / "file.txt"` |
| Home directory | `$HOME`, `%USERPROFILE%` | `Path.home()` |
| Temp directory | `/tmp`, `C:\Temp` | `tempfile.gettempdir()` |
| Shell commands | `os.system("rm -rf")` | `shutil.rmtree()` |
| Line endings | Mixed CRLF/LF | Consistent LF with .gitattributes |

## Pass Condition

Zero cross-platform issues detected.

## On Failure

Report each issue with:
- File path
- Line number
- Issue type
- Current code
- Suggested fix
```

### .claude/agents/python-matrix.md

```markdown
---
name: python-matrix
description: Gate 4 - Python version matrix agent. Tests against Python 3.9-3.13. PREREQUISITE: Gates 1-3 must pass.
tools: Read, Bash, Glob
model: sonnet
---

You are a Python compatibility specialist responsible for Gate 4 of the Preflight pipeline.

## Prerequisites

Verify Gates 1-3 passed:
```bash
python .claude/skills/state-management/scripts/check_prerequisites.py python-matrix
```

## Process

1. Read target versions from `config/python-versions.yaml`
2. For each version, run: `python .claude/skills/python-matrix/scripts/run_version_tests.py <version>`
3. Compare results: `python .claude/skills/python-matrix/scripts/compare_results.py`

## Default Versions

- Python 3.9
- Python 3.10
- Python 3.11
- Python 3.12
- Python 3.13

## Pass Condition

All Python versions pass with identical test results.

## On Failure

Report:
- Which Python version(s) failed
- Specific test failures per version
- Syntax/feature incompatibilities detected
```

### .claude/agents/security.md

```markdown
---
name: security
description: Gate 5 - Security audit agent. Scans for secrets, vulnerabilities, and license issues. PREREQUISITE: Gates 1-4 must pass.
tools: Read, Bash, Glob, Grep
model: sonnet
---

You are a security specialist responsible for Gate 5 of the Preflight pipeline.

## Prerequisites

Verify Gates 1-4 passed:
```bash
python .claude/skills/state-management/scripts/check_prerequisites.py security
```

## Process

1. **Secrets scan**: `python .claude/skills/security-scan/scripts/scan_secrets.py`
2. **Dependency audit**: `python .claude/skills/security-scan/scripts/audit_deps.py`
3. **License check**: `python .claude/skills/security-scan/scripts/check_licenses.py`

## What to Catch

### Secrets
- API keys, tokens, passwords
- Private keys
- AWS credentials
- Database connection strings

### Vulnerabilities
- Known CVEs in dependencies
- Outdated packages with security fixes

### Licenses
- GPL in MIT-licensed projects
- License conflicts

## Pass Condition

- No secrets detected
- No critical/high vulnerabilities
- All licenses compatible

## Severity Levels

- **CRITICAL**: Exposed secrets, critical CVEs -> FAIL immediately
- **HIGH**: High-severity CVEs -> FAIL
- **MODERATE**: Moderate CVEs -> WARN, can pass
- **LOW**: Minor issues -> INFO only
```

### .claude/agents/api-compat.md

```markdown
---
name: api-compat
description: Gate 6 - API compatibility agent. Detects breaking changes in public API. PREREQUISITE: Gates 1-5 must pass.
tools: Read, Bash, Glob, Grep
model: sonnet
---

You are an API compatibility specialist responsible for Gate 6 of the Preflight pipeline.

## Prerequisites

Verify Gates 1-5 passed:
```bash
python .claude/skills/state-management/scripts/check_prerequisites.py api-compat
```

## Process

1. Extract current API: `python .claude/skills/api-analysis/scripts/extract_public_api.py`
2. Get baseline from last release tag
3. Compare: `python .claude/skills/api-analysis/scripts/compare_api.py`
4. Check deprecations: `python .claude/skills/api-analysis/scripts/check_deprecations.py`

## Breaking Changes

These are BREAKING and require major version bump:
- Removed public function/class/method
- Changed function signature (removed param, changed type)
- Changed return type
- Made optional parameter required

These are NON-BREAKING:
- Added new function/class/method
- Added optional parameter with default
- Added new module

## Pass Condition

- No unintended breaking changes
- OR breaking changes explicitly acknowledged in commit message with `BREAKING CHANGE:`

## On Failure

Report:
- Each breaking change with before/after
- File and line number
- Suggested resolution (major bump, revert, or acknowledge)
```

### .claude/agents/packaging.md

```markdown
---
name: packaging
description: Gate 7 - Package build agent. Validates package builds, installs, and entry points work. PREREQUISITE: Gates 1-6 must pass.
tools: Read, Write, Bash, Glob
model: sonnet
---

You are a Python packaging specialist responsible for Gate 7 of the Preflight pipeline.

## Prerequisites

Verify Gates 1-6 passed:
```bash
python .claude/skills/state-management/scripts/check_prerequisites.py packaging
```

## Process

Execute in sequence:

1. **Validate pyproject.toml**: `python .claude/skills/package-build/scripts/validate_pyproject.py`
2. **Check manifest**: `python .claude/skills/package-build/scripts/check_manifest.py`
3. **Build package**: `python .claude/skills/package-build/scripts/build_package.py`
4. **Test install**: `python .claude/skills/package-build/scripts/test_install.py`
5. **Test entry points**: `python .claude/skills/package-build/scripts/test_entry_points.py`
6. **Check version**: `python .claude/skills/package-build/scripts/check_version.py`

## Validation Checklist

- [ ] pyproject.toml has all required fields
- [ ] All files listed in package are present
- [ ] Wheel builds without errors
- [ ] Sdist builds without errors
- [ ] Package installs in clean venv
- [ ] All imports work after install
- [ ] All entry points respond to --help
- [ ] README renders correctly (twine check)
- [ ] Version is consistent across all locations

## Pass Condition

All checks pass. Package is ready for distribution.

## On Failure

Report specific failure:
- Which step failed
- Exact error message
- File/config causing issue
```

### .claude/agents/github-pr.md

```markdown
---
name: github-pr
description: Gate 8 - GitHub PR agent. Creates PR with full gate report. PREREQUISITE: ALL gates 1-7 must pass. REFUSES to run otherwise.
tools: Read, Write, Bash, Glob
model: sonnet
---

You are a GitHub integration specialist responsible for Gate 8 of the Preflight pipeline.

## Prerequisites

**ALL gates 1-7 must show PASS.** This is non-negotiable.

```bash
python .claude/skills/state-management/scripts/check_prerequisites.py github-pr
```

If ANY gate is not PASS, REFUSE to proceed. List all blocking gates.

## Process

1. Read full pipeline state
2. Generate PR body: `python .claude/skills/github-integration/scripts/generate_pr_body.py`
3. Determine labels: `python .claude/skills/github-integration/scripts/auto_label.py`
4. Create PR using GitHub MCP tools
5. Post status checks: `python .claude/skills/github-integration/scripts/post_status_check.py`

## PR Body Template

```markdown
## Summary
[Auto-generated from commits]

## Preflight Results

| Gate | Status | Details |
|------|--------|---------|
| 1. Lint/Test | PASS | 0 errors, 142 tests passed |
| 2. Coverage | PASS | 87.3% (threshold: 80%) |
| 3. Cross-Platform | PASS | Windows + Ubuntu identical |
| 4. Python Matrix | PASS | 3.9, 3.10, 3.11, 3.12, 3.13 |
| 5. Security | PASS | No secrets, no vulnerabilities |
| 6. API Compat | PASS | No breaking changes |
| 7. Package Build | PASS | Wheel + sdist verified |

## Test Plan
- [ ] Review code changes
- [ ] Verify CI passes
- [ ] Manual testing if needed
```

## Labels to Apply

Based on conventional commits:
- `feat:` -> `enhancement`
- `fix:` -> `bug`
- `docs:` -> `documentation`
- `BREAKING CHANGE:` -> `breaking-change`

## NEVER

- Create PR if any gate failed
- Skip the gate verification step
- Omit the Preflight Results section
```

### .claude/agents/planning.md

```markdown
---
name: planning
description: Advisory agent for architecture analysis and tech debt identification. No gate prerequisites - can run anytime.
tools: Read, Glob, Grep, Bash
model: sonnet
---

You are an architecture analyst. You help developers understand their codebase structure and identify areas for improvement.

## Capabilities

1. **Architecture Analysis**: Map codebase structure, identify patterns
2. **Dependency Mapping**: Internal module dependencies
3. **Complexity Scoring**: Identify high-complexity hotspots
4. **Tech Debt Detection**: Find TODOs, FIXMEs, complex functions

## Process

1. Scan codebase structure
2. Analyze import patterns
3. Calculate complexity metrics
4. Identify improvement opportunities

## Output

Provide actionable report with:
- Architecture diagram (ASCII)
- Dependency graph
- Complexity hotspots (file:line)
- Tech debt inventory
- Prioritized recommendations
```

### .claude/agents/deps.md

```markdown
---
name: deps
description: Advisory agent for dependency health checks. No prerequisites - can run anytime.
tools: Read, Bash, Glob
model: sonnet
---

You are a dependency management specialist. You help maintain healthy, secure, up-to-date dependencies.

## Capabilities

1. **Lock file sync**: Verify requirements.txt matches pyproject.toml
2. **Version bounds**: Check for too-loose or too-tight bounds
3. **Deprecated packages**: Flag unmaintained dependencies
4. **Conflict detection**: Find dependency conflicts
5. **Update recommendations**: Suggest safe updates

## Output

Provide report with:
- Sync status
- Version bound warnings
- Deprecated package list
- Conflict warnings
- Recommended updates with risk assessment
```

---

## Skill Definitions

### .claude/skills/xplat-checks/SKILL.md

```markdown
---
name: xplat-checks
description: Cross-platform compatibility checking tools. Detects path issues, line endings, environment variables, and shell commands that break on Windows or Linux.
---

# Cross-Platform Checks

Scripts for detecting cross-platform compatibility issues in Python code.

## Scripts

### check_paths.py
Detects hardcoded path separators.
```bash
python .claude/skills/xplat-checks/scripts/check_paths.py [directory]
```

### check_line_endings.py
Detects mixed or wrong line endings.
```bash
python .claude/skills/xplat-checks/scripts/check_line_endings.py [directory]
```

### check_env_vars.py
Finds platform-specific environment variable usage.
```bash
python .claude/skills/xplat-checks/scripts/check_env_vars.py [directory]
```

### check_case_sensitivity.py
Finds files that differ only by case.
```bash
python .claude/skills/xplat-checks/scripts/check_case_sensitivity.py [directory]
```

### check_shell_commands.py
Detects bash-specific shell commands.
```bash
python .claude/skills/xplat-checks/scripts/check_shell_commands.py [directory]
```

### check_temp_paths.py
Finds hardcoded temp directory paths.
```bash
python .claude/skills/xplat-checks/scripts/check_temp_paths.py [directory]
```

## Output Format

All scripts output JSON:
```json
{
  "status": "PASS|FAIL",
  "issues": [
    {
      "file": "src/config.py",
      "line": 47,
      "issue": "Hardcoded forward slash in path",
      "code": "config_path = 'data/config.yaml'",
      "suggestion": "Use Path('data') / 'config.yaml'"
    }
  ]
}
```
```

### .claude/skills/state-management/SKILL.md

```markdown
---
name: state-management
description: Pipeline state management for tracking gate progress and prerequisites.
---

# State Management

Scripts for reading and writing pipeline state.

## Scripts

### read_state.py
Get current pipeline state.
```bash
python .claude/skills/state-management/scripts/read_state.py
```

### write_state.py
Update gate status.
```bash
python .claude/skills/state-management/scripts/write_state.py <gate> <PASS|FAIL> "<details_json>"
```

### check_prerequisites.py
Verify prerequisites for a gate.
```bash
python .claude/skills/state-management/scripts/check_prerequisites.py <gate>
```
Returns exit code 0 if prerequisites met, 1 if not.

## State File Location

`state/pipeline_state.json`

## State Schema

```json
{
  "pipeline_id": "uuid",
  "started_at": "ISO8601",
  "current_gate": "coverage",
  "gates": {
    "lint-test": {
      "status": "PASS",
      "started_at": "ISO8601",
      "completed_at": "ISO8601",
      "duration_seconds": 45,
      "details": {}
    }
  }
}
```
```

---

## Slash Commands

### .claude/commands/preflight.md

```markdown
Run the full Preflight pipeline (Gates 1-8).

Execute all gates in sequence:
1. lint-test
2. coverage
3. cross-platform
4. python-matrix
5. security
6. api-compat
7. packaging
8. github-pr (only if 1-7 pass)

Stop at first failure. Report which gate failed and why.

Use the preflight-orchestrator agent to coordinate.
```

### .claude/commands/gate.md

```markdown
Run a specific Preflight gate.

Usage: /gate <number|name>

Examples:
- /gate 1
- /gate lint-test
- /gate cross-platform

The gate will check its prerequisites before running.
If prerequisites not met, it will report which gates must pass first.
```

### .claude/commands/status.md

```markdown
Show current Preflight pipeline status.

Read state/pipeline_state.json and display:
- Current pipeline ID
- Each gate's status (PASS/FAIL/PENDING/RUNNING)
- Duration for completed gates
- Failure details if any
- Next gate to run
```

### .claude/commands/ship.md

```markdown
Attempt to ship the code.

This is equivalent to /preflight but with intent to create a PR at the end.

Process:
1. Run all 8 gates in sequence
2. Stop at any failure
3. If all pass, create PR via github-pr agent

WILL NOT create PR if any gate fails.
```

---

## Configuration Files

### config/gates.yaml

```yaml
pipeline:
  name: preflight
  version: 1.0.0

gates:
  - name: lint-test
    agent: lint-test
    required: true
    timeout_seconds: 300

  - name: coverage
    agent: coverage
    required: true
    timeout_seconds: 120
    depends_on: [lint-test]

  - name: cross-platform
    agent: cross-platform
    required: true
    timeout_seconds: 300
    depends_on: [lint-test, coverage]

  - name: python-matrix
    agent: python-matrix
    required: true
    timeout_seconds: 600
    depends_on: [lint-test, coverage, cross-platform]

  - name: security
    agent: security
    required: true
    timeout_seconds: 180
    depends_on: [lint-test, coverage, cross-platform, python-matrix]

  - name: api-compat
    agent: api-compat
    required: true
    timeout_seconds: 120
    depends_on: [lint-test, coverage, cross-platform, python-matrix, security]

  - name: packaging
    agent: packaging
    required: true
    timeout_seconds: 300
    depends_on: [lint-test, coverage, cross-platform, python-matrix, security, api-compat]

  - name: github-pr
    agent: github-pr
    required: true
    requires_all_gates: true

settings:
  fail_fast: true
  state_file: state/pipeline_state.json
```

### config/coverage.yaml

```yaml
coverage:
  minimum_threshold: 80
  per_file_minimum: 60
  branch_coverage: true

  exclude_patterns:
    - "*/tests/*"
    - "*/__pycache__/*"
    - "*/.venv/*"
```

### config/xplat.yaml

```yaml
cross_platform:
  path_patterns:
    forbidden:
      - pattern: '(?<!["\'])\/(?!\/|\*)'
        description: "Unquoted forward slash"
      - pattern: '\\\\\\\\'
        description: "Hardcoded backslash"

    recommended:
      - "Path(__file__).parent"
      - "Path.home()"
      - "os.path.join()"

  env_vars:
    forbidden:
      - pattern: '\$HOME(?![A-Z_])'
        use_instead: "Path.home()"
      - pattern: '%USERPROFILE%'
        use_instead: "Path.home()"
      - pattern: '%TEMP%'
        use_instead: "tempfile.gettempdir()"

  temp_paths:
    forbidden:
      - "/tmp"
      - "/var/tmp"
      - "C:\\Temp"
      - "C:\\Windows\\Temp"
```

### config/python-versions.yaml

```yaml
python_matrix:
  minimum: "3.9"
  maximum: "3.13"

  versions:
    - "3.9"
    - "3.10"
    - "3.11"
    - "3.12"
    - "3.13"

  test_command: "pytest -v"
```

### config/security.yaml

```yaml
security:
  secrets:
    patterns:
      - "api_key"
      - "api_secret"
      - "password"
      - "secret"
      - "token"
      - "private_key"
      - "aws_access_key"

  vulnerabilities:
    fail_on: [critical, high]
    warn_on: [moderate]

  licenses:
    allowed:
      - "MIT"
      - "Apache-2.0"
      - "BSD-2-Clause"
      - "BSD-3-Clause"
    forbidden:
      - "GPL-2.0"
      - "GPL-3.0"
      - "AGPL-3.0"
```

---

## CLAUDE.md

```markdown
# CLAUDE.md - Preflight Pipeline Governance

## Identity

You are operating the Preflight multi-agent CI/CD pipeline for Python packages. Your primary directive is ensuring packages pass all 8 quality gates before reaching GitHub or PyPI.

## Cardinal Rules

1. **NEVER skip gates** - Each gate must explicitly PASS before the next runs
2. **NEVER push without all gates passing** - Gate 8 requires gates 1-7 to pass
3. **NEVER ignore failures** - All failures stop the pipeline
4. **NEVER proceed on warnings for required gates** - Warnings in required gates are failures

## Gate Sequence

```
Gate 1: lint-test     -> Gate 2: coverage      -> Gate 3: cross-platform
Gate 4: python-matrix -> Gate 5: security      -> Gate 6: api-compat
Gate 7: packaging     -> Gate 8: github-pr
```

## Agent Commands

| Command | Agent | Gate |
|---------|-------|------|
| /preflight | preflight-orchestrator | All |
| /gate 1 | lint-test | 1 |
| /gate 2 | coverage | 2 |
| /gate 3 | cross-platform | 3 |
| /gate 4 | python-matrix | 4 |
| /gate 5 | security | 5 |
| /gate 6 | api-compat | 6 |
| /gate 7 | packaging | 7 |
| /gate 8 | github-pr | 8 |
| /ship | preflight-orchestrator | All + PR |
| /status | (direct) | N/A |

## Cross-Platform Rules

When creating or editing Python files:
- Use `pathlib.Path` for ALL file paths
- Use `tempfile` for temporary files
- Use `subprocess.run()` with `shell=False`
- NO emojis in code or logs
- Specify `encoding='utf-8'` for all file operations

## Response Format

After each gate:
```
GATE: [name]
STATUS: [PASS/FAIL]
DURATION: [seconds]
DETAILS: [summary]
NEXT: [next gate or STOP]
```
```

---

## Plugin Manifest

### plugin.json

```json
{
  "name": "preflight",
  "display_name": "Preflight - Python Package CI/CD Pipeline",
  "version": "1.0.0",
  "description": "Multi-agent CI/CD pipeline ensuring Python packages pass cross-platform, multi-version, and quality gates before shipping.",
  "author": "Gorombo",
  "license": "MIT",
  "repository": "https://github.com/gorombo/preflight",

  "claude_code_version": ">=1.0.0",

  "agents": [
    {"name": "preflight-orchestrator", "description": "Coordinates all gates"},
    {"name": "lint-test", "gate": 1},
    {"name": "coverage", "gate": 2},
    {"name": "cross-platform", "gate": 3},
    {"name": "python-matrix", "gate": 4},
    {"name": "security", "gate": 5},
    {"name": "api-compat", "gate": 6},
    {"name": "packaging", "gate": 7},
    {"name": "github-pr", "gate": 8},
    {"name": "planning", "advisory": true},
    {"name": "deps", "advisory": true}
  ],

  "skills": [
    "lint-tools",
    "coverage-tools",
    "xplat-checks",
    "python-matrix",
    "security-scan",
    "api-analysis",
    "package-build",
    "github-integration",
    "state-management"
  ],

  "commands": [
    {"name": "preflight", "description": "Run full pipeline"},
    {"name": "gate", "description": "Run specific gate"},
    {"name": "status", "description": "Check pipeline status"},
    {"name": "ship", "description": "Run pipeline and create PR"}
  ],

  "dependencies": {
    "python": ">=3.9",
    "packages": [
      "ruff>=0.1.0",
      "mypy>=1.0.0",
      "pytest>=7.0.0",
      "pytest-cov>=4.0.0",
      "build>=1.0.0",
      "twine>=4.0.0",
      "pip-audit>=2.0.0"
    ]
  },

  "tags": [
    "ci-cd",
    "python",
    "cross-platform",
    "testing",
    "quality"
  ]
}
```

---

## Implementation Phases

### Phase 1: Foundation
- [ ] Initialize repo with directory structure
- [ ] Create CLAUDE.md
- [ ] Create plugin.json
- [ ] Create config/*.yaml files
- [ ] Create state management skill + scripts
- [ ] Create slash commands

### Phase 2: Gate 1 - Lint/Test
- [ ] Create lint-test agent
- [ ] Create lint-tools skill
- [ ] Implement run_ruff.py
- [ ] Implement run_mypy.py
- [ ] Implement run_pytest.py
- [ ] Test end-to-end

### Phase 3: Gate 2 - Coverage
- [ ] Create coverage agent
- [ ] Create coverage-tools skill
- [ ] Implement run_coverage.py
- [ ] Implement check_threshold.py
- [ ] Test with prerequisites

### Phase 4: Gate 3 - Cross-Platform
- [ ] Create cross-platform agent
- [ ] Create xplat-checks skill
- [ ] Implement all check_*.py scripts
- [ ] Test end-to-end

### Phase 5: Gate 4 - Python Matrix
- [ ] Create python-matrix agent
- [ ] Create python-matrix skill
- [ ] Implement run_version_tests.py
- [ ] Implement compare_results.py
- [ ] Test across versions

### Phase 6: Gate 5 - Security
- [ ] Create security agent
- [ ] Create security-scan skill
- [ ] Implement scan_secrets.py
- [ ] Implement audit_deps.py
- [ ] Implement check_licenses.py

### Phase 7: Gate 6 - API Compat
- [ ] Create api-compat agent
- [ ] Create api-analysis skill
- [ ] Implement extract_public_api.py
- [ ] Implement compare_api.py
- [ ] Implement check_deprecations.py

### Phase 8: Gate 7 - Packaging
- [ ] Create packaging agent
- [ ] Create package-build skill
- [ ] Implement all build/test scripts
- [ ] Test full build cycle

### Phase 9: Gate 8 - GitHub PR
- [ ] Create github-pr agent
- [ ] Create github-integration skill
- [ ] Implement PR generation scripts
- [ ] Test with GitHub MCP

### Phase 10: Integration
- [ ] Create preflight-orchestrator agent
- [ ] Full pipeline integration testing
- [ ] Documentation
- [ ] Marketplace preparation

---

## Success Criteria

- [ ] No code reaches GitHub without passing all 8 gates
- [ ] Cross-platform issues caught before push
- [ ] Python version compatibility verified
- [ ] Package builds verified before publish
- [ ] Security issues blocked
- [ ] Breaking API changes detected
- [ ] PRs include full gate report
- [ ] Pipeline runs in < 10 minutes
- [ ] Plugin installable from Claude Code
```
