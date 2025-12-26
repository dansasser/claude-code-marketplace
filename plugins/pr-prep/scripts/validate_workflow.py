#!/usr/bin/env python3
"""
Phase 2: Workflow Validation

Checks if .github/workflows CI files exist and are valid.
Detects Python vs Node.js workflows based on project type.

Uses ONLY Python stdlib for cross-platform compatibility.
ALL file operations use pathlib/shutil, NEVER shell commands.
"""
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class WorkflowInfo:
    """Information about a GitHub Actions workflow file."""
    name: str
    path: str
    exists: bool
    is_valid: bool
    has_lint: bool
    has_type_check: bool
    has_test: bool
    has_build: bool
    triggers: List[str]
    errors: List[str]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "name": self.name,
            "path": self.path,
            "exists": self.exists,
            "is_valid": self.is_valid,
            "has_lint": self.has_lint,
            "has_type_check": self.has_type_check,
            "has_test": self.has_test,
            "has_build": self.has_build,
            "triggers": self.triggers,
            "errors": self.errors,
        }


def parse_yaml_basic(content: str) -> Dict[str, Any]:
    """
    Basic YAML parsing without external dependencies.

    This is a simplified parser that handles common workflow patterns.
    For complex YAML, consider using PyYAML if available.
    """
    result: Dict[str, Any] = {}

    # Extract 'on' triggers
    on_match = re.search(r'^on:\s*\n((?:[ ]+.+\n)*)', content, re.MULTILINE)
    if on_match:
        triggers_block = on_match.group(1)
        triggers = re.findall(r'^\s+(\w+):', triggers_block, re.MULTILINE)
        result["on"] = triggers
    else:
        # Check for simple on: [push, pull_request] format
        on_simple = re.search(r'^on:\s*\[([^\]]+)\]', content, re.MULTILINE)
        if on_simple:
            result["on"] = [t.strip() for t in on_simple.group(1).split(",")]

    # Extract job names
    jobs_match = re.search(r'^jobs:\s*\n((?:[ ]+.+\n)*)', content, re.MULTILINE)
    if jobs_match:
        jobs_block = jobs_match.group(1)
        job_names = re.findall(r'^  (\w+):', jobs_block, re.MULTILINE)
        result["jobs"] = job_names

    return result


def check_workflow_steps(content: str) -> Dict[str, bool]:
    """
    Check what CI steps are present in a workflow.

    Returns dict with has_lint, has_type_check, has_test, has_build.
    """
    content_lower = content.lower()

    # Check for common patterns
    has_lint = any(pattern in content_lower for pattern in [
        "ruff", "eslint", "lint", "flake8", "pylint", "biome"
    ])

    has_type_check = any(pattern in content_lower for pattern in [
        "mypy", "pyright", "tsc", "typescript", "type-check", "typecheck"
    ])

    has_test = any(pattern in content_lower for pattern in [
        "pytest", "jest", "vitest", "mocha", "test", "npm test", "yarn test"
    ])

    has_build = any(pattern in content_lower for pattern in [
        "python -m build", "npm run build", "yarn build", "pnpm build",
        "bun run build", "setup.py", "wheel"
    ])

    return {
        "has_lint": has_lint,
        "has_type_check": has_type_check,
        "has_test": has_test,
        "has_build": has_build,
    }


def validate_workflow_file(workflow_path: Path) -> WorkflowInfo:
    """
    Validate a single workflow file.

    Args:
        workflow_path: Path to the workflow YAML file

    Returns:
        WorkflowInfo with validation results
    """
    name = workflow_path.stem
    path = str(workflow_path)
    errors: List[str] = []

    if not workflow_path.exists():
        return WorkflowInfo(
            name=name,
            path=path,
            exists=False,
            is_valid=False,
            has_lint=False,
            has_type_check=False,
            has_test=False,
            has_build=False,
            triggers=[],
            errors=["File does not exist"],
        )

    try:
        content = workflow_path.read_text(encoding="utf-8")
    except IOError as e:
        return WorkflowInfo(
            name=name,
            path=path,
            exists=True,
            is_valid=False,
            has_lint=False,
            has_type_check=False,
            has_test=False,
            has_build=False,
            triggers=[],
            errors=[f"Cannot read file: {e}"],
        )

    # Basic YAML validation
    if not content.strip():
        errors.append("File is empty")
        return WorkflowInfo(
            name=name,
            path=path,
            exists=True,
            is_valid=False,
            has_lint=False,
            has_type_check=False,
            has_test=False,
            has_build=False,
            triggers=[],
            errors=errors,
        )

    # Check for required sections
    if "on:" not in content:
        errors.append("Missing 'on:' trigger section")

    if "jobs:" not in content:
        errors.append("Missing 'jobs:' section")

    # Parse basic structure
    parsed = parse_yaml_basic(content)
    triggers = parsed.get("on", [])

    # Check for common trigger issues
    if not triggers:
        errors.append("No triggers defined")
    elif "push" not in triggers and "pull_request" not in triggers:
        errors.append("Missing push or pull_request trigger")

    # Check steps
    steps = check_workflow_steps(content)

    is_valid = len(errors) == 0

    return WorkflowInfo(
        name=name,
        path=path,
        exists=True,
        is_valid=is_valid,
        has_lint=steps["has_lint"],
        has_type_check=steps["has_type_check"],
        has_test=steps["has_test"],
        has_build=steps["has_build"],
        triggers=triggers,
        errors=errors,
    )


def find_workflows(project_dir: Path) -> List[Path]:
    """Find all workflow files in a project."""
    workflows_dir = project_dir / ".github" / "workflows"

    if not workflows_dir.exists():
        return []

    workflows = []
    for ext in ["*.yml", "*.yaml"]:
        workflows.extend(workflows_dir.glob(ext))

    return sorted(workflows)


def detect_expected_workflow_type(project_dir: Path) -> str:
    """Detect expected workflow type based on project files."""
    # Check for Python
    if any((project_dir / f).exists() for f in [
        "pyproject.toml", "setup.py", "setup.cfg", "requirements.txt"
    ]):
        return "python"

    # Check for Node.js
    if (project_dir / "package.json").exists():
        # Check for TypeScript
        if (project_dir / "tsconfig.json").exists():
            return "node-typescript"
        return "node"

    return "unknown"


def validate_workflows(project_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Validate all CI workflows in a project.

    Args:
        project_dir: Path to project root (default: cwd)

    Returns:
        Dict with validation results and recommendations
    """
    if project_dir is None:
        project_dir = Path.cwd()

    workflows_dir = project_dir / ".github" / "workflows"
    workflows = find_workflows(project_dir)
    project_type = detect_expected_workflow_type(project_dir)

    # Validate each workflow
    workflow_results = [validate_workflow_file(wf) for wf in workflows]

    # Check if any workflow covers CI
    has_ci_workflow = any(
        wf.has_lint or wf.has_test or wf.has_build
        for wf in workflow_results
        if wf.is_valid
    )

    # Generate recommendations
    recommendations: List[str] = []

    if not workflows_dir.exists():
        recommendations.append("Create .github/workflows directory")

    if not workflows:
        recommendations.append(f"Add CI workflow for {project_type} project")

    if workflows and not has_ci_workflow:
        recommendations.append("Existing workflows don't include CI checks")

    # Check for missing steps
    if workflow_results:
        all_has_lint = any(wf.has_lint for wf in workflow_results)
        all_has_test = any(wf.has_test for wf in workflow_results)
        all_has_build = any(wf.has_build for wf in workflow_results)

        if not all_has_lint:
            recommendations.append("Add linting step to workflow")
        if not all_has_test:
            recommendations.append("Add test step to workflow")
        if not all_has_build:
            recommendations.append("Add build step to workflow")

    # Determine overall status
    all_valid = all(wf.is_valid for wf in workflow_results) if workflow_results else False
    needs_workflow = not workflows or not has_ci_workflow

    return {
        "project_dir": str(project_dir),
        "project_type": project_type,
        "workflows_dir": str(workflows_dir),
        "workflows_dir_exists": workflows_dir.exists(),
        "workflow_count": len(workflows),
        "workflows": [wf.to_dict() for wf in workflow_results],
        "has_ci_workflow": has_ci_workflow,
        "all_valid": all_valid,
        "needs_workflow": needs_workflow,
        "recommendations": recommendations,
        "summary": (
            "[OK] CI workflows configured"
            if has_ci_workflow and all_valid
            else "[WARN] CI workflow needs attention"
        ),
    }


def main():
    """Validate workflows and output JSON result."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate GitHub Actions workflows")
    parser.add_argument("project_dir", nargs="?", help="Project directory")
    parser.add_argument("--json", action="store_true", help="Output JSON only")

    args = parser.parse_args()

    project_dir = Path(args.project_dir) if args.project_dir else None
    result = validate_workflows(project_dir)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"[INFO] Validating workflows in {result['project_dir']}")
        print(f"[INFO] Project type: {result['project_type']}")
        print()

        if result["workflows"]:
            for wf in result["workflows"]:
                status = "[OK]" if wf["is_valid"] else "[FAIL]"
                print(f"  {status} {wf['name']}")
                if wf["errors"]:
                    for err in wf["errors"]:
                        print(f"      - {err}")
                else:
                    features = []
                    if wf["has_lint"]:
                        features.append("lint")
                    if wf["has_type_check"]:
                        features.append("type")
                    if wf["has_test"]:
                        features.append("test")
                    if wf["has_build"]:
                        features.append("build")
                    if features:
                        print(f"      Features: {', '.join(features)}")
        else:
            print("  No workflows found")

        if result["recommendations"]:
            print()
            print("[INFO] Recommendations:")
            for rec in result["recommendations"]:
                print(f"  - {rec}")

        print()
        print(result["summary"])

    return 0 if result["has_ci_workflow"] and result["all_valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
