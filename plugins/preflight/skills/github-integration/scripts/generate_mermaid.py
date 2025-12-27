#!/usr/bin/env python3
"""
Phase 8: Mermaid Generation

Generates Mermaid flowcharts from git diff showing file changes.
Creates visual representation of what changed in a PR.

Uses ONLY Python stdlib for cross-platform compatibility.
ALL file operations use pathlib/shutil, NEVER shell commands.
"""
import json
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class FileChange:
    """Represents a changed file."""
    path: str
    status: str  # A=added, M=modified, D=deleted, R=renamed
    insertions: int = 0
    deletions: int = 0
    old_path: Optional[str] = None  # For renames


def run_git(args: List[str], cwd: Optional[Path] = None) -> Tuple[int, str, str]:
    """Run a git command and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=cwd,
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except FileNotFoundError:
        return 1, "", "git not found"
    except Exception as e:
        return 1, "", str(e)


def get_default_branch(cwd: Optional[Path] = None) -> str:
    """Get the default branch (main or master)."""
    code, stdout, _ = run_git(
        ["symbolic-ref", "refs/remotes/origin/HEAD", "--short"],
        cwd
    )
    if code == 0 and stdout:
        return stdout.split("/")[-1]

    code, _, _ = run_git(["rev-parse", "--verify", "main"], cwd)
    if code == 0:
        return "main"

    return "master"


def get_changed_files(
    base_branch: Optional[str] = None,
    cwd: Optional[Path] = None
) -> List[FileChange]:
    """
    Get list of changed files compared to base branch.

    Args:
        base_branch: Branch to compare against (default: main/master)
        cwd: Working directory

    Returns:
        List of FileChange objects
    """
    if base_branch is None:
        base_branch = get_default_branch(cwd)

    # Get file status with stats
    code, stdout, _ = run_git(
        ["diff", "--name-status", f"{base_branch}...HEAD"],
        cwd
    )

    if code != 0 or not stdout:
        return []

    changes = []
    for line in stdout.split("\n"):
        if not line:
            continue

        parts = line.split("\t")
        if len(parts) < 2:
            continue

        status = parts[0][0]  # First character is status
        path = parts[-1]
        old_path = parts[1] if len(parts) > 2 else None

        changes.append(FileChange(
            path=path,
            status=status,
            old_path=old_path,
        ))

    # Get line counts
    code, stdout, _ = run_git(
        ["diff", "--numstat", f"{base_branch}...HEAD"],
        cwd
    )

    if code == 0 and stdout:
        for line in stdout.split("\n"):
            if not line:
                continue

            parts = line.split("\t")
            if len(parts) < 3:
                continue

            try:
                insertions = int(parts[0]) if parts[0] != "-" else 0
                deletions = int(parts[1]) if parts[1] != "-" else 0
            except ValueError:
                continue

            path = parts[-1]

            # Find matching change
            for change in changes:
                if change.path == path:
                    change.insertions = insertions
                    change.deletions = deletions
                    break

    return changes


def categorize_files(changes: List[FileChange]) -> Dict[str, List[FileChange]]:
    """
    Categorize files by directory/type.

    Returns dict with categories like 'src', 'tests', 'config', etc.
    """
    categories: Dict[str, List[FileChange]] = defaultdict(list)

    for change in changes:
        path = Path(change.path)
        parts = path.parts

        # Determine category
        if len(parts) == 1:
            # Root files
            if path.suffix in [".json", ".toml", ".yaml", ".yml", ".ini", ".cfg"]:
                categories["config"].append(change)
            elif path.suffix in [".md", ".rst", ".txt"]:
                categories["docs"].append(change)
            else:
                categories["root"].append(change)
        elif parts[0] in ["src", "lib", "app"]:
            categories["source"].append(change)
        elif parts[0] in ["tests", "test", "__tests__", "spec"]:
            categories["tests"].append(change)
        elif parts[0] in ["docs", "documentation"]:
            categories["docs"].append(change)
        elif parts[0] == ".github":
            categories["ci"].append(change)
        elif parts[0] in ["scripts", "bin"]:
            categories["scripts"].append(change)
        else:
            categories["other"].append(change)

    return dict(categories)


def escape_mermaid_text(text: str) -> str:
    """Escape special characters for Mermaid."""
    # Replace characters that break Mermaid syntax
    text = text.replace('"', "'")
    text = text.replace("<", "")
    text = text.replace(">", "")
    text = text.replace("{", "(")
    text = text.replace("}", ")")
    text = text.replace("[", "(")
    text = text.replace("]", ")")
    return text


def get_status_icon(status: str) -> str:
    """Get ASCII status indicator (no emojis for Windows compatibility)."""
    icons = {
        "A": "+",  # Added
        "M": "*",  # Modified
        "D": "-",  # Deleted
        "R": ">",  # Renamed
    }
    return icons.get(status, "?")


def generate_flowchart(
    changes: List[FileChange],
    title: str = "Changes",
    max_files: int = 20,
) -> str:
    """
    Generate a Mermaid flowchart showing file changes.

    Args:
        changes: List of file changes
        title: Chart title
        max_files: Maximum files to show (prevent huge diagrams)

    Returns:
        Mermaid flowchart string
    """
    if not changes:
        return "flowchart LR\n    A[No changes detected]"

    categories = categorize_files(changes)

    lines = [
        "flowchart LR",
        f"    subgraph {escape_mermaid_text(title)}",
    ]

    node_id = 0
    file_count = 0

    # Category display order
    category_order = ["source", "tests", "config", "docs", "ci", "scripts", "root", "other"]

    for category in category_order:
        if category not in categories:
            continue

        cat_changes = categories[category]
        if not cat_changes:
            continue

        # Category subgraph
        cat_label = category.capitalize()
        lines.append(f"        subgraph {cat_label}")

        for change in cat_changes:
            if file_count >= max_files:
                lines.append(f"            N{node_id}[...and more]")
                node_id += 1
                break

            # Create node
            icon = get_status_icon(change.status)
            filename = Path(change.path).name
            stats = ""
            if change.insertions or change.deletions:
                stats = f" +{change.insertions}/-{change.deletions}"

            label = f"{icon} {escape_mermaid_text(filename)}{stats}"
            lines.append(f"            N{node_id}[{label}]")

            node_id += 1
            file_count += 1

        lines.append("        end")

        if file_count >= max_files:
            break

    lines.append("    end")
    lines.append("")

    # Return raw Mermaid content without code fences
    # The PR template will wrap it in fences
    return "\n".join(lines)


def generate_summary_diagram(changes: List[FileChange]) -> str:
    """
    Generate a summary diagram showing change statistics.

    Returns:
        Mermaid pie chart string
    """
    if not changes:
        return ""

    categories = categorize_files(changes)

    # Count files per category
    counts = {cat: len(files) for cat, files in categories.items()}

    if not counts:
        return ""

    lines = [
        "pie showData",
        '    title "Files Changed by Category"',
    ]

    for cat, count in sorted(counts.items(), key=lambda x: -x[1]):
        lines.append(f'    "{cat.capitalize()}" : {count}')

    # Return raw Mermaid content without code fences
    return "\n".join(lines)


def generate_mermaid(
    project_dir: Optional[Path] = None,
    base_branch: Optional[str] = None,
    include_summary: bool = True,
    max_files: int = 20,
) -> Dict[str, Any]:
    """
    Generate Mermaid diagrams for git changes.

    Args:
        project_dir: Path to project root (default: cwd)
        base_branch: Branch to compare against
        include_summary: Include pie chart summary
        max_files: Maximum files to show in flowchart

    Returns:
        Dict with diagram strings and metadata
    """
    if project_dir is None:
        project_dir = Path.cwd()

    if base_branch is None:
        base_branch = get_default_branch(project_dir)

    changes = get_changed_files(base_branch, project_dir)

    if not changes:
        return {
            "success": False,
            "project_dir": str(project_dir),
            "base_branch": base_branch,
            "file_count": 0,
            "flowchart": "",
            "summary": "",
            "message": "[WARN] No changes detected",
        }

    flowchart = generate_flowchart(changes, "PR Changes", max_files)

    summary = ""
    if include_summary and len(changes) > 5:
        summary = generate_summary_diagram(changes)

    # Calculate stats
    total_insertions = sum(c.insertions for c in changes)
    total_deletions = sum(c.deletions for c in changes)

    added = len([c for c in changes if c.status == "A"])
    modified = len([c for c in changes if c.status == "M"])
    deleted = len([c for c in changes if c.status == "D"])

    return {
        "success": True,
        "project_dir": str(project_dir),
        "base_branch": base_branch,
        "file_count": len(changes),
        "stats": {
            "added": added,
            "modified": modified,
            "deleted": deleted,
            "insertions": total_insertions,
            "deletions": total_deletions,
        },
        "flowchart": flowchart,
        "summary": summary,
        "message": f"[OK] Generated diagram for {len(changes)} files",
    }


def main():
    """Generate Mermaid diagrams and output result."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate Mermaid diagrams from git diff")
    parser.add_argument("project_dir", nargs="?", help="Project directory")
    parser.add_argument("--base", "-b", help="Base branch to compare against")
    parser.add_argument("--max-files", "-m", type=int, default=20, help="Max files to show")
    parser.add_argument("--no-summary", action="store_true", help="Skip summary pie chart")
    parser.add_argument("--json", action="store_true", help="Output JSON only")

    args = parser.parse_args()

    project_dir = Path(args.project_dir) if args.project_dir else None

    result = generate_mermaid(
        project_dir=project_dir,
        base_branch=args.base,
        include_summary=not args.no_summary,
        max_files=args.max_files,
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(result["message"])
        if result["success"]:
            print()
            print("## Flowchart")
            print(result["flowchart"])
            if result["summary"]:
                print()
                print("## Summary")
                print(result["summary"])

    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
