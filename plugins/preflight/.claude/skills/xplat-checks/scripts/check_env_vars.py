#!/usr/bin/env python3
"""Detect platform-specific environment variable usage."""

import argparse
import json
import re
import sys
from pathlib import Path


# Patterns to detect with their fixes
ENV_VAR_PATTERNS = [
    # Unix-specific
    (
        r'\$HOME(?![A-Z_])',
        "$HOME environment variable",
        "Use Path.home() instead",
    ),
    (
        r'\$USER(?![A-Z_])',
        "$USER environment variable",
        "Use getpass.getuser() instead",
    ),
    (
        r'os\.environ\s*\[\s*["\']HOME["\']\s*\]',
        "os.environ['HOME']",
        "Use Path.home() instead",
    ),
    (
        r'os\.environ\s*\[\s*["\']USER["\']\s*\]',
        "os.environ['USER']",
        "Use getpass.getuser() instead",
    ),
    (
        r'os\.environ\.get\s*\(\s*["\']HOME["\']',
        "os.environ.get('HOME')",
        "Use Path.home() instead",
    ),
    (
        r'os\.environ\.get\s*\(\s*["\']USER["\']',
        "os.environ.get('USER')",
        "Use getpass.getuser() instead",
    ),
    # Windows-specific
    (
        r'%USERPROFILE%',
        "%USERPROFILE% environment variable",
        "Use Path.home() instead",
    ),
    (
        r'%USERNAME%',
        "%USERNAME% environment variable",
        "Use getpass.getuser() instead",
    ),
    (
        r'%TEMP%',
        "%TEMP% environment variable",
        "Use tempfile.gettempdir() instead",
    ),
    (
        r'%TMP%',
        "%TMP% environment variable",
        "Use tempfile.gettempdir() instead",
    ),
    (
        r'os\.environ\s*\[\s*["\']USERPROFILE["\']\s*\]',
        "os.environ['USERPROFILE']",
        "Use Path.home() instead",
    ),
    (
        r'os\.environ\s*\[\s*["\']TEMP["\']\s*\]',
        "os.environ['TEMP']",
        "Use tempfile.gettempdir() instead",
    ),
]


def scan_file(file_path: Path) -> list[dict]:
    """Scan a single file for environment variable issues."""
    issues = []

    try:
        content = file_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError):
        return issues

    lines = content.split("\n")

    for line_num, line in enumerate(lines, 1):
        # Skip comments
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        for pattern, issue_desc, suggestion in ENV_VAR_PATTERNS:
            matches = re.finditer(pattern, line, re.IGNORECASE)
            for match in matches:
                issues.append(
                    {
                        "file": str(file_path),
                        "line": line_num,
                        "column": match.start() + 1,
                        "issue": issue_desc,
                        "code": line.strip()[:100],
                        "suggestion": suggestion,
                    }
                )

    return issues


def scan_directory(directory: Path) -> dict:
    """Scan all Python files in directory."""
    all_issues = []
    files_scanned = 0

    for py_file in directory.rglob("*.py"):
        if any(
            part in py_file.parts
            for part in [".venv", "venv", "__pycache__", ".git", "node_modules"]
        ):
            continue

        files_scanned += 1
        issues = scan_file(py_file)
        all_issues.extend(issues)

    return {
        "status": "FAIL" if all_issues else "PASS",
        "files_scanned": files_scanned,
        "issues_found": len(all_issues),
        "issues": all_issues,
    }


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Check for platform-specific environment variables"
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to scan (default: current)",
    )
    args = parser.parse_args()

    directory = Path(args.directory).resolve()

    if not directory.exists():
        result = {"status": "ERROR", "message": f"Directory not found: {directory}"}
        print(json.dumps(result, indent=2))
        return 1

    result = scan_directory(directory)
    print(json.dumps(result, indent=2))

    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
