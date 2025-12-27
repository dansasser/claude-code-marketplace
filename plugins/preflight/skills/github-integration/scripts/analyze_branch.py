#!/usr/bin/env python3
"""
Phase 3: Branch Analysis

Analyzes git state: uncommitted, unstaged, unpushed changes.

Uses ONLY Python stdlib for cross-platform compatibility.
"""
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional


def run_git(args: List[str], cwd: Optional[Path] = None) -> tuple[int, str, str]:
    """
    Run a git command and return (returncode, stdout, stderr).

    All git commands are cross-platform safe.
    """
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=cwd
        )
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except FileNotFoundError:
        return 1, "", "git not found"
    except Exception as e:
        return 1, "", str(e)


def get_current_branch(cwd: Optional[Path] = None) -> Optional[str]:
    """Get the current branch name."""
    code, stdout, _ = run_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd)
    return stdout if code == 0 else None


def get_default_branch(cwd: Optional[Path] = None) -> str:
    """Get the default branch (main or master)."""
    # Try to get from remote
    code, stdout, _ = run_git(
        ["symbolic-ref", "refs/remotes/origin/HEAD", "--short"],
        cwd
    )
    if code == 0 and stdout:
        # "origin/main" -> "main"
        return stdout.split("/")[-1]

    # Check if main exists
    code, _, _ = run_git(["rev-parse", "--verify", "main"], cwd)
    if code == 0:
        return "main"

    # Check if master exists
    code, _, _ = run_git(["rev-parse", "--verify", "master"], cwd)
    if code == 0:
        return "master"

    return "main"  # Default fallback


def get_uncommitted_changes(cwd: Optional[Path] = None) -> Dict[str, List[str]]:
    """Get uncommitted changes (staged and unstaged)."""
    changes = {
        "staged": [],
        "unstaged": [],
        "untracked": [],
    }

    # Get status in porcelain format
    code, stdout, _ = run_git(["status", "--porcelain"], cwd)
    if code != 0:
        return changes

    for line in stdout.split("\n"):
        if not line:
            continue

        # Porcelain format: XY filename
        # X = staged status, Y = unstaged status
        index_status = line[0]
        worktree_status = line[1]
        filename = line[3:]

        if index_status == "?":
            changes["untracked"].append(filename)
        else:
            if index_status not in [" ", "?"]:
                changes["staged"].append(filename)
            if worktree_status not in [" ", "?"]:
                changes["unstaged"].append(filename)

    return changes


def get_unpushed_commits(cwd: Optional[Path] = None) -> List[Dict[str, str]]:
    """Get commits that haven't been pushed to remote."""
    commits = []

    # Get unpushed commits
    code, stdout, _ = run_git(
        ["log", "@{u}..", "--format=%H|%s|%an|%ai"],
        cwd
    )

    if code != 0 or not stdout:
        # Maybe no upstream set, try origin/current-branch
        branch = get_current_branch(cwd)
        if branch:
            code, stdout, _ = run_git(
                ["log", f"origin/{branch}..", "--format=%H|%s|%an|%ai"],
                cwd
            )

    if code == 0 and stdout:
        for line in stdout.split("\n"):
            if not line:
                continue
            parts = line.split("|", 3)
            if len(parts) == 4:
                commits.append({
                    "sha": parts[0][:7],
                    "message": parts[1],
                    "author": parts[2],
                    "date": parts[3],
                })

    return commits


def get_diff_since_base(
    base_branch: Optional[str] = None,
    cwd: Optional[Path] = None
) -> Dict[str, Any]:
    """Get diff statistics since branching from base."""
    if base_branch is None:
        base_branch = get_default_branch(cwd)

    diff_info = {
        "base_branch": base_branch,
        "files_changed": 0,
        "insertions": 0,
        "deletions": 0,
        "changed_files": [],
    }

    # Get diff stats
    code, stdout, _ = run_git(
        ["diff", "--stat", f"{base_branch}...HEAD"],
        cwd
    )

    if code == 0 and stdout:
        lines = stdout.split("\n")
        for line in lines[:-1]:  # Skip summary line
            if " | " in line:
                filename = line.split(" | ")[0].strip()
                diff_info["changed_files"].append(filename)

        # Parse summary line
        if lines:
            summary = lines[-1]
            # "3 files changed, 45 insertions(+), 12 deletions(-)"
            import re
            files_match = re.search(r"(\d+) files? changed", summary)
            ins_match = re.search(r"(\d+) insertions?", summary)
            del_match = re.search(r"(\d+) deletions?", summary)

            if files_match:
                diff_info["files_changed"] = int(files_match.group(1))
            if ins_match:
                diff_info["insertions"] = int(ins_match.group(1))
            if del_match:
                diff_info["deletions"] = int(del_match.group(1))

    return diff_info


def get_remote_status(cwd: Optional[Path] = None) -> Dict[str, Any]:
    """Check remote tracking status."""
    status = {
        "has_remote": False,
        "remote_name": None,
        "remote_url": None,
        "tracking_branch": None,
        "ahead": 0,
        "behind": 0,
    }

    # Get remote
    code, stdout, _ = run_git(["remote"], cwd)
    if code == 0 and stdout:
        remote = stdout.split("\n")[0]
        status["has_remote"] = True
        status["remote_name"] = remote

        # Get remote URL
        code, url, _ = run_git(["remote", "get-url", remote], cwd)
        if code == 0:
            status["remote_url"] = url

    # Get tracking branch
    code, stdout, _ = run_git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], cwd)
    if code == 0 and stdout:
        status["tracking_branch"] = stdout

    # Get ahead/behind count
    code, stdout, _ = run_git(["rev-list", "--left-right", "--count", "@{u}...HEAD"], cwd)
    if code == 0 and stdout:
        parts = stdout.split()
        if len(parts) == 2:
            status["behind"] = int(parts[0])
            status["ahead"] = int(parts[1])

    return status


def analyze_branch(project_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Analyze complete git branch state.

    Returns JSON-serializable dict with:
    - current_branch: Current branch name
    - default_branch: Default branch (main/master)
    - uncommitted: Staged, unstaged, untracked files
    - unpushed_commits: Commits not yet pushed
    - diff_since_base: Changes since branching from default
    - remote: Remote tracking status
    - is_clean: True if no uncommitted changes
    - is_pushed: True if all commits pushed
    """
    if project_dir is None:
        project_dir = Path.cwd()

    current = get_current_branch(project_dir)
    default = get_default_branch(project_dir)
    uncommitted = get_uncommitted_changes(project_dir)
    unpushed = get_unpushed_commits(project_dir)
    diff = get_diff_since_base(default, project_dir)
    remote = get_remote_status(project_dir)

    # Calculate summary flags
    has_uncommitted = bool(
        uncommitted["staged"] or
        uncommitted["unstaged"] or
        uncommitted["untracked"]
    )

    return {
        "current_branch": current,
        "default_branch": default,
        "uncommitted": uncommitted,
        "unpushed_commits": unpushed,
        "diff_since_base": diff,
        "remote": remote,
        "is_clean": not has_uncommitted,
        "is_pushed": len(unpushed) == 0,
        "project_dir": str(project_dir),
    }


def main():
    """Run branch analysis and output JSON."""
    project_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    analysis = analyze_branch(project_dir)
    print(json.dumps(analysis, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
