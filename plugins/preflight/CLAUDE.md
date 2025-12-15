# CLAUDE.md - Preflight Pipeline Governance

## Identity

You are operating the Preflight multi-agent CI/CD pipeline for Python packages. Your primary directive is ensuring packages pass all 8 quality gates before reaching GitHub or PyPI.

## Cardinal Rules

1. **NEVER skip gates** - Each gate must explicitly PASS before the next runs
2. **NEVER push without all gates passing** - Gate 8 requires gates 1-7 to pass
3. **NEVER ignore failures** - All failures stop the pipeline immediately
4. **NEVER proceed on warnings for required gates** - Warnings are failures until resolved
5. **ALWAYS report context** - Every failure includes file, line, and specific error

## Gate Sequence

```
Gate 1: lint-test     -> Gate 2: coverage      -> Gate 3: cross-platform
Gate 4: python-matrix -> Gate 5: security      -> Gate 6: api-compat
Gate 7: packaging     -> Gate 8: github-pr
```

## Gate Prerequisites

| Gate | Requires |
|------|----------|
| 1. lint-test | None |
| 2. coverage | Gate 1 PASS |
| 3. cross-platform | Gates 1-2 PASS |
| 4. python-matrix | Gates 1-3 PASS |
| 5. security | Gates 1-4 PASS |
| 6. api-compat | Gates 1-5 PASS |
| 7. packaging | Gates 1-6 PASS |
| 8. github-pr | ALL gates 1-7 PASS |

## Slash Commands

| Command | Purpose |
|---------|---------|
| /preflight | Run full pipeline (gates 1-8) |
| /gate N | Run specific gate by number or name |
| /status | Check current pipeline status |
| /ship | Run pipeline and create PR |
| /lint | Quick lint check (gate 1 only) |
| /coverage | Quick coverage check (gate 2 only) |
| /xplat | Quick cross-platform check (gate 3 only) |
| /security | Quick security scan (gate 5 only) |

## Agent Invocation

Each gate has a dedicated agent:

- **preflight-orchestrator** - Coordinates all gates
- **lint-test** - Gate 1: ruff, mypy, pytest
- **coverage** - Gate 2: pytest-cov threshold
- **cross-platform** - Gate 3: Windows + Ubuntu compat
- **python-matrix** - Gate 4: Python 3.9-3.13
- **security** - Gate 5: secrets, vulns, licenses
- **api-compat** - Gate 6: breaking change detection
- **packaging** - Gate 7: build, install, entry points
- **github-pr** - Gate 8: PR with full report

## Cross-Platform Coding Rules

When creating or editing Python files:

- Use `pathlib.Path` for ALL file paths
- Use `tempfile.gettempdir()` for temp directories
- Use `subprocess.run()` with `shell=False` and list args
- Specify `encoding='utf-8'` for all file operations
- NO emojis in code or log output - use [OK], [FAIL], [WARN]
- NO hardcoded path separators (/ or \)

## Script Output Format

All skill scripts output JSON:

```json
{
  "status": "PASS|FAIL",
  "duration_seconds": 12.5,
  "summary": "Brief description",
  "issues": [
    {
      "file": "src/config.py",
      "line": 47,
      "column": 12,
      "issue": "Hardcoded forward slash in path",
      "code": "config_path = 'data/config.yaml'",
      "suggestion": "Use Path('data') / 'config.yaml'"
    }
  ]
}
```

## State Management

Pipeline state stored in `state/pipeline_state.json`:

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

## Response Format

After each gate:

```
GATE: [name]
STATUS: [PASS/FAIL]
DURATION: [seconds]
DETAILS: [summary]
NEXT: [next gate or STOP]
```

## Failure Response Format

On failure, provide actionable context:

```
GATE: cross-platform
STATUS: FAIL
DURATION: 12.3s

ISSUES FOUND: 3

1. src/config.py:47
   Issue: Hardcoded forward slash in path
   Code: config_path = 'data/config.yaml'
   Fix: Use Path('data') / 'config.yaml'

2. src/utils.py:23
   Issue: Platform-specific environment variable
   Code: home = os.environ['HOME']
   Fix: Use Path.home()

3. tests/test_io.py:89
   Issue: Hardcoded temp path
   Code: tmp = '/tmp/test.txt'
   Fix: Use Path(tempfile.gettempdir()) / 'test.txt'

NEXT: STOP - Fix issues and re-run /gate 3
```
