#!/usr/bin/env python3
"""Detect case sensitivity issues that break on Linux."""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


def find_duplicate_case_files(directory: Path) -> list[dict]:
    """Find files that differ only by case."""
    issues = []

    # Group files by lowercase path
    path_groups: dict[str, list[Path]] = defaultdict(list)

    for file_path in directory.rglob("*"):
        if file_path.is_file():
            if any(
                part in file_path.parts
                for part in [".venv", "venv", "__pycache__", ".git", "node_modules"]
            ):
                continue

            # Get relative path and lowercase it
            rel_path = file_path.relative_to(directory)
            lower_path = str(rel_path).lower()
            path_groups[lower_path].append(file_path)

    # Find groups with multiple files (case conflicts)
    for lower_path, files in path_groups.items():
        if len(files) > 1:
            issues.append(
                {
                    "issue": "Files differ only by case",
                    "files": [str(f.relative_to(directory)) for f in files],
                    "suggestion": "Rename files to have unique names (Linux is case-sensitive)",
                }
            )

    return issues


def check_import_case_mismatches(directory: Path) -> list[dict]:
    """Check for import statements with wrong case."""
    issues = []

    # Build map of actual module names
    module_names: dict[str, str] = {}  # lowercase -> actual

    for py_file in directory.rglob("*.py"):
        if any(
            part in py_file.parts
            for part in [".venv", "venv", "__pycache__", ".git", "node_modules"]
        ):
            continue

        # Get module name from file
        rel_path = py_file.relative_to(directory)
        module_parts = list(rel_path.parts)

        # Remove .py extension
        if module_parts[-1].endswith(".py"):
            module_parts[-1] = module_parts[-1][:-3]

        # Skip __init__ for package imports
        if module_parts[-1] == "__init__":
            module_parts = module_parts[:-1]

        if module_parts:
            module_name = ".".join(module_parts)
            module_names[module_name.lower()] = module_name

    # Now check imports in all files
    import_pattern = re.compile(
        r"^(?:from|import)\s+([\w.]+)", re.MULTILINE
    )

    for py_file in directory.rglob("*.py"):
        if any(
            part in py_file.parts
            for part in [".venv", "venv", "__pycache__", ".git", "node_modules"]
        ):
            continue

        try:
            content = py_file.read_text(encoding="utf-8")
        except (UnicodeDecodeError, PermissionError):
            continue

        for match in import_pattern.finditer(content):
            imported = match.group(1)
            imported_lower = imported.lower()

            # Check if it's a local module with wrong case
            if imported_lower in module_names:
                actual = module_names[imported_lower]
                if imported != actual:
                    # Find line number
                    line_num = content[: match.start()].count("\n") + 1

                    issues.append(
                        {
                            "file": str(py_file.relative_to(directory)),
                            "line": line_num,
                            "issue": f"Import case mismatch",
                            "code": f"import {imported}",
                            "actual_module": actual,
                            "suggestion": f"Use: import {actual}",
                        }
                    )

    return issues


def scan_directory(directory: Path) -> dict:
    """Scan directory for case sensitivity issues."""
    all_issues = []

    # Check for duplicate case files
    duplicate_issues = find_duplicate_case_files(directory)
    all_issues.extend(duplicate_issues)

    # Check for import case mismatches
    import_issues = check_import_case_mismatches(directory)
    all_issues.extend(import_issues)

    return {
        "status": "FAIL" if all_issues else "PASS",
        "issues_found": len(all_issues),
        "issues": all_issues,
    }


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Check for case sensitivity issues")
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
