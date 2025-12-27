Show current Preflight pipeline status.

## Process

Read state/pipeline_state.json and display the current pipeline status.

```bash
python .claude/skills/state-management/scripts/read_state.py --format summary
```

## Output Format

```
Pipeline: abc123
Started: 2024-01-15 10:30:00
Package: mypackage 1.0.0

Gates:
  1. lint-test:      [PASS] (45s)
  2. coverage:       [PASS] (32s)
  3. cross-platform: [....] (running)
  4. python-matrix:  [    ] (pending)
  5. security:       [    ] (pending)
  6. api-compat:     [    ] (pending)
  7. packaging:      [    ] (pending)
  8. github-pr:      [    ] (pending)

Current: Gate 3 (cross-platform) running
```

## Status Indicators

- `[PASS]` - Gate passed
- `[FAIL]` - Gate failed
- `[....]` - Gate running
- `[    ]` - Gate pending

## If No Pipeline

```
No pipeline initialized.

Start a new pipeline with: /preflight
Or run a specific gate with: /gate 1
```

## Additional Info

If a gate failed, show failure summary:
```
Gate 3 FAILED:
  - 3 cross-platform issues found
  - Run /gate 3 for details
```
