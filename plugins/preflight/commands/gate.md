Run a specific Preflight gate by number or name.

## Usage

```
/gate <number|name>
```

## Examples

```
/gate 1
/gate lint-test
/gate 3
/gate cross-platform
/gate security
```

## Gate Reference

| Number | Name | Purpose |
|--------|------|---------|
| 1 | lint-test | Linting, types, tests |
| 2 | coverage | Coverage threshold |
| 3 | cross-platform | Windows + Ubuntu |
| 4 | python-matrix | Python 3.9-3.13 |
| 5 | security | Secrets, vulns |
| 6 | api-compat | Breaking changes |
| 7 | packaging | Build verification |
| 8 | github-pr | Create PR |

## Prerequisite Checking

Each gate checks its prerequisites before running:
- Gate 1: No prerequisites
- Gate 2: Gate 1 must pass
- Gate 3: Gates 1-2 must pass
- Gate 4: Gates 1-3 must pass
- Gate 5: Gates 1-4 must pass
- Gate 6: Gates 1-5 must pass
- Gate 7: Gates 1-6 must pass
- Gate 8: ALL gates 1-7 must pass

If prerequisites not met, the gate will REFUSE to run and report which gates are blocking.

## Output

```
GATE: cross-platform
STATUS: PASS
DURATION: 12.3s
DETAILS: [summary]
NEXT: python-matrix
```

Invoke the appropriate gate agent based on the argument.
