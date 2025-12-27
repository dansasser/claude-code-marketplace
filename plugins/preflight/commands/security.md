Quick security scan.

## Purpose

Run just the security checks without the full pipeline.

## Process

1. Scan for exposed secrets (API keys, passwords, tokens)
2. Audit dependencies for known vulnerabilities
3. Check license compatibility

## Usage

```
/security
```

## Output

```
SECURITY SCAN

Secrets:         OK (156 files scanned)
Vulnerabilities: OK (45 packages, 0 critical, 0 high)
Licenses:        OK (all compatible)

Status: PASS - No security issues found
```

Or on failure:

```
SECURITY SCAN

CRITICAL ISSUES:

1. [SECRET] src/config.py:23
   Type: API Key
   Match: api_key = 'sk-...'
   Fix: Use environment variable

2. [VULNERABILITY] requests 2.25.0
   CVE-2023-32681 (HIGH)
   Fix: Upgrade to >=2.31.0

3. [LICENSE] gpl-package
   License: GPL-3.0 (incompatible with MIT)
   Fix: Find MIT-licensed alternative

Status: FAIL - 3 security issues need attention
```

## Note

This is a quick check - it does NOT update pipeline state.
For full pipeline with state tracking, use /preflight or /gate 5.

Use the security agent for this check.
