Quick cross-platform compatibility check.

## Purpose

Run just the cross-platform checks without the full pipeline.

## Process

Check for common cross-platform issues:
- Hardcoded path separators (/ or \)
- Platform-specific environment variables
- Hardcoded temp paths
- Shell command compatibility
- Line ending issues
- Case sensitivity problems

## Usage

```
/xplat
```

## Output

```
CROSS-PLATFORM CHECK

Paths:           OK
Line endings:    OK
Env vars:        OK
Case sensitivity: OK
Shell commands:  OK
Temp paths:      OK

Status: PASS - No cross-platform issues found
```

Or on failure:

```
CROSS-PLATFORM CHECK

Issues found: 3

1. src/config.py:47 [env_vars]
   Code: home = os.environ['HOME']
   Fix: Use Path.home()

2. src/utils.py:23 [paths]
   Code: path = 'data/config.yaml'
   Fix: Use Path('data') / 'config.yaml'

3. tests/test_io.py:89 [temp_paths]
   Code: tmp = '/tmp/test.txt'
   Fix: Use Path(tempfile.gettempdir()) / 'test.txt'

Status: FAIL - 3 issues need fixing
```

## Note

This is a quick check - it does NOT update pipeline state.
For full pipeline with state tracking, use /preflight or /gate 3.

Use the cross-platform agent for this check.
