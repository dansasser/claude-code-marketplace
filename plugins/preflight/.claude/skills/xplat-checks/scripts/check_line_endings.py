#!/usr/bin/env python3
"""Detect line ending issues."""

import argparse
import json
import sys
from pathlib import Path


def check_file_line_endings(file_path: Path) -> dict | None:
    """Check line endings in a single file."""
    try:
        content = file_path.read_bytes()
    except (PermissionError, OSError):
        return None

    # Count different line endings
    crlf_count = content.count(b"\r\n")
    lf_count = content.count(b"\n") - crlf_count  # Subtract CRLF from LF count
    cr_count = content.count(b"\r") - crlf_count  # Standalone CR

    # Determine dominant and issues
    if crlf_count > 0 and lf_count > 0:
        return {
            "file": str(file_path),
            "issue": "Mixed line endings (CRLF and LF)",
            "crlf_count": crlf_count,
            "lf_count": lf_count,
            "suggestion": "Normalize to LF and add .gitattributes",
        }
    elif crlf_count > 0:
        return {
            "file": str(file_path),
            "issue": "CRLF line endings",
            "crlf_count": crlf_count,
            "suggestion": "Convert to LF and add .gitattributes",
        }
    elif cr_count > 0:
        return {
            "file": str(file_path),
            "issue": "Old-style CR line endings",
            "cr_count": cr_count,
            "suggestion": "Convert to LF",
        }

    return None


def check_gitattributes(directory: Path) -> dict | None:
    """Check if .gitattributes exists with proper config."""
    gitattributes = directory / ".gitattributes"

    if not gitattributes.exists():
        return {
            "file": ".gitattributes",
            "issue": "Missing .gitattributes file",
            "suggestion": "Create .gitattributes with: * text=auto eol=lf",
        }

    content = gitattributes.read_text(encoding="utf-8")

    # Check for eol normalization
    if "text=auto" not in content and "eol=" not in content:
        return {
            "file": ".gitattributes",
            "issue": ".gitattributes missing line ending normalization",
            "suggestion": "Add: * text=auto eol=lf",
        }

    return None


def scan_directory(directory: Path) -> dict:
    """Scan all text files in directory for line ending issues."""
    all_issues = []
    files_scanned = 0

    # Check .gitattributes first
    gitattr_issue = check_gitattributes(directory)
    if gitattr_issue:
        all_issues.append(gitattr_issue)

    # Check Python files
    extensions = [".py", ".md", ".txt", ".yaml", ".yml", ".json", ".toml"]

    for ext in extensions:
        for file_path in directory.rglob(f"*{ext}"):
            if any(
                part in file_path.parts
                for part in [".venv", "venv", "__pycache__", ".git", "node_modules"]
            ):
                continue

            files_scanned += 1
            issue = check_file_line_endings(file_path)
            if issue:
                all_issues.append(issue)

    return {
        "status": "FAIL" if all_issues else "PASS",
        "files_scanned": files_scanned,
        "issues_found": len(all_issues),
        "issues": all_issues,
    }


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Check for line ending issues")
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
