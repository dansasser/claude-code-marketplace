#!/usr/bin/env python3
"""
Phase 2: Workflow Generation

Generates CI workflow from templates based on detected project type.
Supports Python and Node.js projects.

Uses ONLY Python stdlib for cross-platform compatibility.
ALL file operations use pathlib/shutil, NEVER shell commands.
"""
import json
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, Optional


# Template directory relative to this script
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


def get_template_path(project_type: str) -> Optional[Path]:
    """
    Get the template path for a project type.

    Args:
        project_type: 'python', 'node', or 'node-typescript'

    Returns:
        Path to template file, or None if not found
    """
    if project_type == "python":
        template = TEMPLATES_DIR / "ci-python.yml"
    elif project_type in ["node", "node-typescript"]:
        template = TEMPLATES_DIR / "ci-node.yml"
    else:
        return None

    return template if template.exists() else None


def detect_project_type(project_dir: Path) -> str:
    """Detect project type from project files."""
    # Check for Python
    if any((project_dir / f).exists() for f in [
        "pyproject.toml", "setup.py", "setup.cfg", "requirements.txt"
    ]):
        return "python"

    # Check for Node.js
    if (project_dir / "package.json").exists():
        if (project_dir / "tsconfig.json").exists():
            return "node-typescript"
        return "node"

    return "unknown"


def customize_python_workflow(content: str, project_dir: Path) -> str:
    """
    Customize Python workflow template for specific project.

    Args:
        content: Template content
        project_dir: Project directory for detection

    Returns:
        Customized workflow content
    """
    # Detect source directory
    src_dirs = ["src", "lib", project_dir.name]
    for src in src_dirs:
        if (project_dir / src).is_dir():
            content = content.replace("mypy src", f"mypy {src}")
            break

    # Detect if poetry is used
    if (project_dir / "poetry.lock").exists():
        content = content.replace(
            "pip install -e",
            "pip install poetry && poetry install && pip install -e"
        )

    return content


def customize_node_workflow(content: str, project_dir: Path) -> str:
    """
    Customize Node.js workflow template for specific project.

    Args:
        content: Template content
        project_dir: Project directory for detection

    Returns:
        Customized workflow content
    """
    # Detect package manager
    if (project_dir / "yarn.lock").exists():
        content = content.replace('cache: "npm"', 'cache: "yarn"')
        content = content.replace("npm ci", "yarn install --frozen-lockfile")
        content = content.replace("npm run", "yarn")
        content = content.replace("npm test", "yarn test")
    elif (project_dir / "pnpm-lock.yaml").exists():
        content = content.replace('cache: "npm"', 'cache: "pnpm"')
        content = content.replace("npm ci", "pnpm install --frozen-lockfile")
        content = content.replace("npm run", "pnpm")
        content = content.replace("npm test", "pnpm test")
    elif (project_dir / "bun.lockb").exists():
        # Bun workflows need different setup
        content = content.replace(
            "uses: actions/setup-node@v4",
            "uses: oven-sh/setup-bun@v1"
        )
        content = content.replace('cache: "npm"', "")
        content = content.replace("npm ci", "bun install --frozen-lockfile")
        content = content.replace("npm run", "bun run")
        content = content.replace("npm test", "bun test")
        content = content.replace("npx tsc", "bunx tsc")

    return content


def generate_workflow(
    project_dir: Optional[Path] = None,
    project_type: Optional[str] = None,
    output_path: Optional[Path] = None,
    force: bool = False,
) -> Dict[str, Any]:
    """
    Generate CI workflow for a project.

    Args:
        project_dir: Path to project root (default: cwd)
        project_type: Override detected project type
        output_path: Custom output path (default: .github/workflows/ci.yml)
        force: Overwrite existing workflow file

    Returns:
        Dict with generation result
    """
    if project_dir is None:
        project_dir = Path.cwd()

    if project_type is None:
        project_type = detect_project_type(project_dir)

    if project_type == "unknown":
        return {
            "success": False,
            "project_dir": str(project_dir),
            "project_type": project_type,
            "error": "Could not detect project type",
            "message": "[FAIL] Unknown project type - cannot generate workflow",
        }

    # Get template
    template_path = get_template_path(project_type)
    if template_path is None:
        return {
            "success": False,
            "project_dir": str(project_dir),
            "project_type": project_type,
            "error": f"No template found for {project_type}",
            "message": f"[FAIL] No template for {project_type}",
        }

    # Determine output path
    if output_path is None:
        workflows_dir = project_dir / ".github" / "workflows"
        output_path = workflows_dir / "ci.yml"
    else:
        workflows_dir = output_path.parent

    # Check if file exists
    if output_path.exists() and not force:
        return {
            "success": False,
            "project_dir": str(project_dir),
            "project_type": project_type,
            "output_path": str(output_path),
            "error": "Workflow file already exists (use force=True to overwrite)",
            "message": f"[WARN] {output_path} already exists",
        }

    # Create workflows directory
    workflows_dir.mkdir(parents=True, exist_ok=True)

    # Read template
    try:
        content = template_path.read_text(encoding="utf-8")
    except IOError as e:
        return {
            "success": False,
            "project_dir": str(project_dir),
            "project_type": project_type,
            "error": f"Cannot read template: {e}",
            "message": "[FAIL] Cannot read template",
        }

    # Customize template
    if project_type == "python":
        content = customize_python_workflow(content, project_dir)
    elif project_type in ["node", "node-typescript"]:
        content = customize_node_workflow(content, project_dir)

    # Write workflow
    try:
        output_path.write_text(content, encoding="utf-8")
    except IOError as e:
        return {
            "success": False,
            "project_dir": str(project_dir),
            "project_type": project_type,
            "error": f"Cannot write workflow: {e}",
            "message": "[FAIL] Cannot write workflow",
        }

    return {
        "success": True,
        "project_dir": str(project_dir),
        "project_type": project_type,
        "template_path": str(template_path),
        "output_path": str(output_path),
        "message": f"[OK] Generated {output_path}",
    }


def main():
    """Generate workflow and output result."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate CI workflow")
    parser.add_argument("project_dir", nargs="?", help="Project directory")
    parser.add_argument("--type", "-t", help="Project type (python, node)")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--force", "-f", action="store_true", help="Overwrite existing")
    parser.add_argument("--json", action="store_true", help="Output JSON only")

    args = parser.parse_args()

    project_dir = Path(args.project_dir) if args.project_dir else None
    output_path = Path(args.output) if args.output else None

    result = generate_workflow(
        project_dir=project_dir,
        project_type=args.type,
        output_path=output_path,
        force=args.force,
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(result["message"])
        if result["success"]:
            print(f"  Template: {result.get('template_path', 'N/A')}")
            print(f"  Output: {result.get('output_path', 'N/A')}")

    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
