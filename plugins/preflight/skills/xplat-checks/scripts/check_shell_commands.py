#!/usr/bin/env python3
"""Detect shell command compatibility issues."""

import argparse
import json
import re
import sys
from pathlib import Path


# Patterns to detect
SHELL_PATTERNS = [
    # os.system calls
    (
        r"os\.system\s*\(",
        "os.system() call",
        "Use subprocess.run() with shell=False and list arguments",
    ),
    # subprocess with shell=True
    (
        r"subprocess\.\w+\s*\([^)]*shell\s*=\s*True",
        "subprocess with shell=True",
        "Use shell=False with list arguments for cross-platform compatibility",
    ),
    # Direct bash/sh references
    (
        r'["\']/bin/bash["\']',
        "Hardcoded /bin/bash path",
        "Use sys.executable or platform-independent approach",
    ),
    (
        r'["\']/bin/sh["\']',
        "Hardcoded /bin/sh path",
        "Use sys.executable or platform-independent approach",
    ),
    # Bash-specific syntax in subprocess
    (
        r'subprocess\.\w+\s*\([^)]*["\'].*\|.*["\']',
        "Pipe operator in subprocess string",
        "Use subprocess.PIPE and multiple subprocess calls",
    ),
    # Unix commands that may not exist on Windows
    (
        r'subprocess\.\w+\s*\([^)]*["\']rm\s+-',
        "Unix rm command",
        "Use shutil.rmtree() or os.remove() for cross-platform",
    ),
    (
        r'subprocess\.\w+\s*\([^)]*["\']chmod\s+',
        "Unix chmod command",
        "Use os.chmod() for cross-platform permission changes",
    ),
    (
        r'subprocess\.\w+\s*\([^)]*["\']ln\s+-',
        "Unix ln command",
        "Use os.symlink() for cross-platform symbolic links",
    ),
]


def scan_file(file_path: Path) -> list[dict]:
    """Scan a single file for shell command issues."""
    issues = []

    try:
        content = file_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError):
        return issues

    lines = content.split("\n")

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        for pattern, issue_desc, suggestion in SHELL_PATTERNS:
            matches = re.finditer(pattern, line)
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
    parser = argparse.ArgumentParser(description="Check for shell command issues")
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
