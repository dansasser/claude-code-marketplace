Run the full Preflight pipeline (Gates 1-8).

## Process

Execute all 8 quality gates in sequence:

1. **lint-test** - Linting, type checking, unit tests
2. **coverage** - Test coverage threshold check
3. **cross-platform** - Windows + Ubuntu compatibility
4. **python-matrix** - Python 3.9-3.13 testing
5. **security** - Secrets, vulnerabilities, licenses
6. **api-compat** - Breaking change detection
7. **packaging** - Build, install, entry point verification
8. **github-pr** - Create PR with full report (only if 1-7 pass)

## Behavior

- Initialize pipeline state if not already running
- Run each gate in sequence via its dedicated agent
- Stop at first failure
- Report detailed failure context with file:line references
- On full success, create PR with Preflight Results table

## On Failure

```
PIPELINE STOPPED at Gate 3 (cross-platform)

Issues found: [details]

Fix issues and re-run: /preflight
Or run just this gate: /gate 3
```

## On Success

```
PIPELINE COMPLETE - All 8 gates passed!

PR #123 created: https://github.com/owner/repo/pull/123
```

Use the preflight-orchestrator agent to coordinate all gates.
