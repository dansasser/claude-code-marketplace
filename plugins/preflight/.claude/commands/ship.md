Run the full pipeline and create a PR.

## Purpose

This is equivalent to /preflight but with explicit intent to ship the code.

## Process

1. Run all 8 gates in sequence
2. Stop at any failure
3. If ALL gates pass, create PR via github-pr agent

## Behavior

Same as /preflight, but makes the shipping intent clear.

```
SHIPPING PIPELINE

Running Gate 1 (lint-test)...
  PASS (45s)

Running Gate 2 (coverage)...
  PASS (32s)

Running Gate 3 (cross-platform)...
  PASS (89s)

...

Running Gate 8 (github-pr)...
  PASS (12s)

SHIPPED!

PR #123 created: https://github.com/owner/repo/pull/123

Labels: enhancement, tested
All 8 quality gates passed.
```

## On Failure

```
SHIP BLOCKED at Gate 5 (security)

Critical issue found:
  - API key exposed in src/config.py:23

Cannot ship until all gates pass.
Fix issues and run /ship again.
```

## IMPORTANT

Will NOT create PR if ANY gate fails. This is the final quality check before code reaches GitHub.

Use the preflight-orchestrator agent to coordinate.
