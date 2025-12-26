#!/usr/bin/env python3
"""
Phase 1: Project Detection

Detects project type (Python, Node-TS, Node-JS) based on config files.

Uses ONLY Python stdlib for cross-platform compatibility.
"""
import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional


class ProjectType:
    """Project type constants."""
    PYTHON = "python"
    NODE_TS = "node-ts"
    NODE_JS = "node-js"
    UNKNOWN = "unknown"


def detect_python_project(project_dir: Path) -> Optional[Dict[str, Any]]:
    """Detect Python project configuration."""
    pyproject = project_dir / "pyproject.toml"
    setup_py = project_dir / "setup.py"
    setup_cfg = project_dir / "setup.cfg"
    requirements = project_dir / "requirements.txt"

    config_file = None
    if pyproject.exists():
        config_file = "pyproject.toml"
    elif setup_py.exists():
        config_file = "setup.py"
    elif setup_cfg.exists():
        config_file = "setup.cfg"
    elif requirements.exists():
        config_file = "requirements.txt"
    else:
        return None

    # Detect package manager
    package_manager = "pip"
    if (project_dir / "poetry.lock").exists():
        package_manager = "poetry"
    elif (project_dir / "Pipfile").exists():
        package_manager = "pipenv"
    elif (project_dir / "uv.lock").exists():
        package_manager = "uv"

    # Detect lock file
    lock_file = None
    for lf in ["poetry.lock", "Pipfile.lock", "uv.lock", "requirements.lock"]:
        if (project_dir / lf).exists():
            lock_file = lf
            break

    return {
        "type": ProjectType.PYTHON,
        "config_file": config_file,
        "package_manager": package_manager,
        "lock_file": lock_file,
    }


def detect_node_project(project_dir: Path) -> Optional[Dict[str, Any]]:
    """Detect Node.js/TypeScript project configuration."""
    package_json = project_dir / "package.json"

    if not package_json.exists():
        return None

    # Check for TypeScript
    tsconfig = project_dir / "tsconfig.json"
    is_typescript = tsconfig.exists()

    # Detect package manager
    package_manager = "npm"
    lock_file = None

    if (project_dir / "pnpm-lock.yaml").exists():
        package_manager = "pnpm"
        lock_file = "pnpm-lock.yaml"
    elif (project_dir / "yarn.lock").exists():
        package_manager = "yarn"
        lock_file = "yarn.lock"
    elif (project_dir / "bun.lockb").exists():
        package_manager = "bun"
        lock_file = "bun.lockb"
    elif (project_dir / "package-lock.json").exists():
        package_manager = "npm"
        lock_file = "package-lock.json"

    # Read package.json to get scripts
    scripts = []
    try:
        with open(package_json, "r", encoding="utf-8") as f:
            pkg = json.load(f)
            scripts = list(pkg.get("scripts", {}).keys())
    except Exception:
        pass

    return {
        "type": ProjectType.NODE_TS if is_typescript else ProjectType.NODE_JS,
        "config_file": "package.json",
        "package_manager": package_manager,
        "lock_file": lock_file,
        "has_typescript": is_typescript,
        "scripts": scripts,
    }


def detect_source_dirs(project_dir: Path) -> List[str]:
    """Detect common source directories."""
    source_dirs = []
    for src_dir in ["src", "lib", "app", "source", "pkg"]:
        if (project_dir / src_dir).is_dir():
            source_dirs.append(src_dir)
    return source_dirs


def detect_test_dirs(project_dir: Path) -> List[str]:
    """Detect common test directories."""
    test_dirs = []
    for test_dir in ["tests", "test", "__tests__", "spec", "specs"]:
        if (project_dir / test_dir).is_dir():
            test_dirs.append(test_dir)
    return test_dirs


def detect_ci_workflow(project_dir: Path) -> Optional[str]:
    """Check if CI workflow exists."""
    workflows_dir = project_dir / ".github" / "workflows"
    if not workflows_dir.exists():
        return None

    # Look for common CI workflow names
    for name in ["ci.yml", "ci.yaml", "test.yml", "test.yaml", "main.yml", "main.yaml"]:
        if (workflows_dir / name).exists():
            return f".github/workflows/{name}"

    # Check for any workflow file
    workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
    if workflow_files:
        return str(workflow_files[0].relative_to(project_dir))

    return None


def detect_project(project_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Detect project type and configuration.

    Returns JSON-serializable dict with:
    - type: python, node-ts, node-js, or unknown
    - config_file: Main config file (pyproject.toml, package.json, etc.)
    - package_manager: pip, poetry, npm, yarn, pnpm, etc.
    - lock_file: Lock file if present
    - source_dirs: Detected source directories
    - test_dirs: Detected test directories
    - ci_workflow: CI workflow file if exists
    """
    if project_dir is None:
        project_dir = Path.cwd()
    else:
        project_dir = Path(project_dir)

    # Try to detect project type
    python_info = detect_python_project(project_dir)
    node_info = detect_node_project(project_dir)

    # Prefer explicit project type
    # If both exist, prefer Node.js (more likely to be the main project)
    if node_info:
        project_info = node_info
    elif python_info:
        project_info = python_info
    else:
        project_info = {
            "type": ProjectType.UNKNOWN,
            "config_file": None,
            "package_manager": None,
            "lock_file": None,
        }

    # Add common info
    project_info["source_dirs"] = detect_source_dirs(project_dir)
    project_info["test_dirs"] = detect_test_dirs(project_dir)
    project_info["ci_workflow"] = detect_ci_workflow(project_dir)
    project_info["project_dir"] = str(project_dir)

    return project_info


def main():
    """Run project detection and output JSON."""
    # Accept optional project directory as argument
    project_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    project = detect_project(project_dir)
    print(json.dumps(project, indent=2))
    return 0 if project["type"] != ProjectType.UNKNOWN else 1


if __name__ == "__main__":
    sys.exit(main())
