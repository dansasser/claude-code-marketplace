#!/usr/bin/env python3
"""Detect hardcoded path separators in Python code."""

import argparse
import json
import re
import sys
from pathlib import Path


# Patterns to detect
PATTERNS = [
    # Forward slash in string that looks like a path
    (
        r'["\'][\w./]+/[\w./]+["\']',
        "Potential hardcoded forward slash in path",
        "Use Path() / 'subpath' or os.path.join()",
    ),
    # Backslash in string (escaped)
    (
        r'["\'].*\\\\.*["\']',
        "Hardcoded backslash in path",
        "Use Path() / 'subpath' or os.path.join()",
    ),
    # Forward slash inside os.path.join
    (
        r"os\.path\.join\([^)]*[\"'][^\"']*/[^\"']*[\"']",
        "Forward slash inside os.path.join()",
        "Remove slashes from os.path.join() arguments",
    ),
]

# Patterns to ignore (false positives)
IGNORE_PATTERNS = [
    r'https?://',  # URLs
    r'["\']/',  # Root path (might be intentional)
    r'//',  # Comments or protocol
    r'\\\n',  # Line continuation
    r'\\n',  # Newline escape
    r'\\t',  # Tab escape
    r'\\r',  # Carriage return escape
    r're\.',  # Regex patterns
    r'pattern\s*=',  # Regex pattern assignment
]


def should_ignore(line: str) -> bool:
    """Check if line should be ignored."""
    for pattern in IGNORE_PATTERNS:
        if re.search(pattern, line):
            return True
    return False


def scan_file(file_path: Path) -> list[dict]:
    """Scan a single file for path issues."""
    issues = []

    try:
        content = file_path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError):
        return issues

    lines = content.split("\n")

    for line_num, line in enumerate(lines, 1):
        # Skip comments and empty lines
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Skip if line should be ignored
        if should_ignore(line):
            continue

        for pattern, issue_desc, suggestion in PATTERNS:
            matches = re.finditer(pattern, line)
            for match in matches:
                # Double-check it's not a false positive
                matched_text = match.group()
                if should_ignore(matched_text):
                    continue

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

    # Find all Python files
    for py_file in directory.rglob("*.py"):
        # Skip virtual environments and cache
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
    parser = argparse.ArgumentParser(description="Check for hardcoded path separators")
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
