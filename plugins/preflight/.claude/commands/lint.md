Quick lint check (Gate 1 only).

## Purpose

Run just the linting and testing checks without the full pipeline.

## Process

1. Run ruff check with auto-fix
2. Run ruff format check
3. Run mypy type checking
4. Run pytest

## Usage

```
/lint
```

## Output

```
QUICK LINT CHECK

Ruff: 0 errors, 2 warnings
Format: OK
Mypy: 0 type errors
Pytest: 142 passed, 0 failed

Status: PASS
```

Or on failure:

```
QUICK LINT CHECK

Ruff: 3 errors
  - src/utils.py:45 F401 unused import
  - src/api.py:23 E501 line too long
  - src/api.py:67 B006 mutable default argument

Mypy: 1 type error
  - src/config.py:12 error: Incompatible return type

Status: FAIL
```

## Note

This is a quick check - it does NOT update pipeline state.
For full pipeline with state tracking, use /preflight or /gate 1.

Use the lint-test agent for this check.
