---
name: state-management
description: Pipeline state management for tracking gate progress, prerequisites, and results. Used by all gate agents to coordinate pipeline execution.
---

# State Management Skill

Scripts for reading and writing pipeline state, checking prerequisites, and initializing pipelines.

## Scripts

### init_pipeline.py

Initialize a new pipeline run.

```bash
python .claude/skills/state-management/scripts/init_pipeline.py [--target-package NAME] [--target-version VERSION]
```

Creates a new pipeline_state.json with fresh UUID and timestamps.

### read_state.py

Get current pipeline state.

```bash
python .claude/skills/state-management/scripts/read_state.py [--gate GATE_NAME] [--format json|summary]
```

Options:
- `--gate`: Get status of specific gate only
- `--format`: Output format (default: json)

### write_state.py

Update gate status after execution.

```bash
python .claude/skills/state-management/scripts/write_state.py <gate> <PASS|FAIL> [--details JSON]
```

Arguments:
- `gate`: Gate name (e.g., lint-test, coverage)
- `status`: PASS or FAIL
- `--details`: JSON string with gate-specific details

### check_prerequisites.py

Verify prerequisites for a gate.

```bash
python .claude/skills/state-management/scripts/check_prerequisites.py <gate>
```

Returns:
- Exit code 0: Prerequisites met, gate can run
- Exit code 1: Prerequisites NOT met, lists blocking gates

## State File Location

`state/pipeline_state.json`

## State Schema

```json
{
  "pipeline_id": "uuid-string",
  "started_at": "2024-01-15T10:30:00Z",
  "current_gate": "coverage",
  "target_package": "my-package",
  "target_version": "1.2.0",
  "gates": {
    "lint-test": {
      "status": "PASS|FAIL|PENDING|RUNNING",
      "started_at": "ISO8601",
      "completed_at": "ISO8601",
      "duration_seconds": 45.2,
      "details": {
        "lint_errors": 0,
        "type_errors": 0,
        "tests_passed": 142,
        "tests_failed": 0
      }
    }
  }
}
```

## Gate Prerequisites

| Gate | Required Prerequisites |
|------|----------------------|
| lint-test | None |
| coverage | lint-test PASS |
| cross-platform | lint-test, coverage PASS |
| python-matrix | lint-test, coverage, cross-platform PASS |
| security | lint-test, coverage, cross-platform, python-matrix PASS |
| api-compat | lint-test, coverage, cross-platform, python-matrix, security PASS |
| packaging | lint-test, coverage, cross-platform, python-matrix, security, api-compat PASS |
| github-pr | ALL gates (1-7) PASS |

## Usage Examples

### Starting a new pipeline

```bash
# Initialize
python .claude/skills/state-management/scripts/init_pipeline.py --target-package mylib --target-version 1.0.0

# Check status
python .claude/skills/state-management/scripts/read_state.py
```

### Running a gate

```bash
# Check if gate can run
python .claude/skills/state-management/scripts/check_prerequisites.py coverage
if [ $? -eq 0 ]; then
    # Run the gate...
    python .claude/skills/state-management/scripts/write_state.py coverage PASS --details '{"total_coverage": 87.3}'
fi
```

### Getting summary

```bash
python .claude/skills/state-management/scripts/read_state.py --format summary
```

Output:
```
Pipeline: abc123
Started: 2024-01-15 10:30:00

Gates:
  1. lint-test:      PASS (45s)
  2. coverage:       PASS (32s)
  3. cross-platform: RUNNING
  4. python-matrix:  PENDING
  5. security:       PENDING
  6. api-compat:     PENDING
  7. packaging:      PENDING
  8. github-pr:      PENDING
```
