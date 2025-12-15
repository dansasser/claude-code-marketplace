Quick coverage check.

## Purpose

Run just the test coverage analysis without the full pipeline.

## Process

1. Run pytest with coverage
2. Check against threshold (default 80%)
3. Report files below minimum

## Usage

```
/coverage
```

## Output

```
COVERAGE CHECK

Overall:  87.3%
Branch:   82.1%
Threshold: 80%

All files above minimum (60%)

Status: PASS
```

Or on failure:

```
COVERAGE CHECK

Overall:  72.5% (need 80%)
Shortfall: 7.5%

Files below 60% minimum:
  - src/auth.py: 45.2%
    Uncovered: lines 23-24, 45, 67, 89-91
  - src/api.py: 58.1%
    Uncovered: lines 12, 34, 56

Status: FAIL - Coverage below threshold
```

## Note

This is a quick check - it does NOT update pipeline state.
For full pipeline with state tracking, use /preflight or /gate 2.

Use the coverage agent for this check.
