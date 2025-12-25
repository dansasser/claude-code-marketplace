#!/usr/bin/env python3
"""
Phase 0: Environment Detection

Detects OS, shell, available tools, and paths.
Runs ONCE at startup, results stored in state.

Uses ONLY Python stdlib for cross-platform compatibility.
"""
import json
import os
import platform
import shutil
import sys
from pathlib import Path
from typing import Dict, Any, Optional


def get_shell() -> str:
    """Detect current shell."""
    if platform.system() == "Windows":
        # Check if running in Git Bash, PowerShell, or cmd
        shell = os.environ.get("SHELL", "")
        if "bash" in shell.lower():
            return "bash"
        comspec = os.environ.get("COMSPEC", "")
        if "powershell" in comspec.lower():
            return "powershell"
        return "cmd"
    else:
        shell = os.environ.get("SHELL", "/bin/sh")
        return Path(shell).name


def find_tool(name: str) -> Optional[str]:
    """Find tool path using shutil.which (cross-platform)."""
    return shutil.which(name)


def detect_python() -> Dict[str, Any]:
    """Detect Python environment."""
    return {
        "executable": sys.executable,
        "version": platform.python_version(),
        "version_info": list(sys.version_info[:3]),
    }


def detect_node() -> Dict[str, Any]:
    """Detect Node.js environment."""
    node_path = find_tool("node")
    npm_path = find_tool("npm")
    npx_path = find_tool("npx")

    node_version = None
    if node_path:
        import subprocess
        try:
            result = subprocess.run(
                [node_path, "--version"],
                capture_output=True,
                text=True,
                encoding="utf-8"
            )
            if result.returncode == 0:
                node_version = result.stdout.strip().lstrip("v")
        except Exception:
            pass

    return {
        "node": node_path,
        "npm": npm_path,
        "npx": npx_path,
        "version": node_version,
    }


def detect_git() -> Dict[str, Any]:
    """Detect git installation."""
    git_path = find_tool("git")
    gh_path = find_tool("gh")

    git_version = None
    if git_path:
        import subprocess
        try:
            result = subprocess.run(
                [git_path, "--version"],
                capture_output=True,
                text=True,
                encoding="utf-8"
            )
            if result.returncode == 0:
                # "git version 2.43.0" -> "2.43.0"
                git_version = result.stdout.strip().split()[-1]
        except Exception:
            pass

    return {
        "git": git_path,
        "gh": gh_path,
        "version": git_version,
    }


def detect_ci_tools() -> Dict[str, Optional[str]]:
    """Detect CI-related tools."""
    return {
        "ruff": find_tool("ruff"),
        "mypy": find_tool("mypy"),
        "pytest": find_tool("pytest"),
        "eslint": find_tool("eslint"),
        "tsc": find_tool("tsc"),
    }


def detect_environment() -> Dict[str, Any]:
    """
    Detect complete runtime environment.

    Returns JSON-serializable dict with:
    - os: Operating system info
    - shell: Current shell
    - python: Python environment
    - node: Node.js environment
    - git: Git and gh CLI
    - tools: CI-related tools
    - is_ci: Whether running in CI environment
    - cwd: Current working directory
    """
    env = {
        "os": {
            "system": platform.system().lower(),  # windows, linux, darwin
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
        },
        "shell": get_shell(),
        "python": detect_python(),
        "node": detect_node(),
        "git": detect_git(),
        "tools": detect_ci_tools(),
        "is_ci": any(
            os.environ.get(v)
            for v in ["CI", "GITHUB_ACTIONS", "JENKINS_URL", "TRAVIS", "CIRCLECI"]
        ),
        "cwd": str(Path.cwd()),
        "home": str(Path.home()),
    }

    return env


def main():
    """Run environment detection and output JSON."""
    env = detect_environment()
    print(json.dumps(env, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
