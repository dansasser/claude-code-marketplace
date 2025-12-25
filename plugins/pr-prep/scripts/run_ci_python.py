#!/usr/bin/env python3
"""
Phase 5: Python CI Execution

Runs local CI checks for Python projects:
- ruff check (lint)
- mypy (type check)
- pytest (tests)
- python -m build (package build)

Integrates with error_recovery for smart failure handling.

Uses ONLY Python stdlib for cross-platform compatibility.
ALL file operations use pathlib/shutil, NEVER shell commands.
"""
import json
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from error_recovery import (
    ErrorType,
    can_recover,
    diagnose_error,
    recover_python,
)


@dataclass
class CheckResult:
    """Result of a single CI check."""
    name: str
    passed: bool
    exit_code: int
    stdout: str
    stderr: str
    duration: float
    error_type: Optional[ErrorType] = None
    recovery_attempted: bool = False
    recovery_message: str = ""


@dataclass
class CIResult:
    """Complete CI run result."""
    passed: bool
    checks: List[CheckResult] = field(default_factory=list)
    project_dir: str = ""
    package_manager: str = "pip"
    total_duration: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "passed": self.passed,
            "checks": [
                {
                    "name": c.name,
                    "passed": c.passed,
                    "exit_code": c.exit_code,
                    "stdout": c.stdout[:2000] if len(c.stdout) > 2000 else c.stdout,
                    "stderr": c.stderr[:2000] if len(c.stderr) > 2000 else c.stderr,
                    "duration": round(c.duration, 2),
                    "error_type": c.error_type.value if c.error_type else None,
                    "recovery_attempted": c.recovery_attempted,
                    "recovery_message": c.recovery_message,
                }
                for c in self.checks
            ],
            "project_dir": self.project_dir,
            "package_manager": self.package_manager,
            "total_duration": round(self.total_duration, 2),
        }


def run_command(
    cmd: List[str],
    cwd: Optional[Path] = None,
    timeout: int = 300
) -> Tuple[int, str, str, float]:
    """
    Run a command and return (exit_code, stdout, stderr, duration).

    Args:
        cmd: Command and arguments
        cwd: Working directory
        timeout: Timeout in seconds (default 5 minutes)

    Returns:
        Tuple of (exit_code, stdout, stderr, duration_seconds)
    """
    start = time.time()
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=cwd,
            timeout=timeout,
        )
        duration = time.time() - start
        return result.returncode, result.stdout, result.stderr, duration
    except subprocess.TimeoutExpired:
        duration = time.time() - start
        return 124, "", f"Command timed out after {timeout}s", duration
    except FileNotFoundError:
        duration = time.time() - start
        return 127, "", f"Command not found: {cmd[0]}", duration
    except Exception as e:
        duration = time.time() - start
        return 1, "", str(e), duration


def detect_package_manager(project_dir: Path) -> str:
    """Detect Python package manager from project files."""
    if (project_dir / "poetry.lock").exists():
        return "poetry"
    if (project_dir / "Pipfile.lock").exists():
        return "pipenv"
    if (project_dir / "uv.lock").exists():
        return "uv"
    return "pip"


def run_ruff(project_dir: Path) -> CheckResult:
    """Run ruff linter."""
    name = "lint (ruff)"

    # Try ruff directly, then via python -m
    cmd = ["ruff", "check", "."]
    code, stdout, stderr, duration = run_command(cmd, cwd=project_dir)

    if code == 127:  # Command not found
        cmd = [sys.executable, "-m", "ruff", "check", "."]
        code, stdout, stderr, duration = run_command(cmd, cwd=project_dir)

    return CheckResult(
        name=name,
        passed=code == 0,
        exit_code=code,
        stdout=stdout,
        stderr=stderr,
        duration=duration,
    )


def run_mypy(project_dir: Path, src_dir: str = "src") -> CheckResult:
    """Run mypy type checker."""
    name = "type (mypy)"

    # Determine target directory
    target = project_dir / src_dir
    if not target.exists():
        # Try common alternatives
        for alt in [".", "lib", project_dir.name]:
            target = project_dir / alt
            if target.exists() and target.is_dir():
                break
        else:
            target = project_dir

    cmd = ["mypy", str(target)]
    code, stdout, stderr, duration = run_command(cmd, cwd=project_dir)

    if code == 127:
        cmd = [sys.executable, "-m", "mypy", str(target)]
        code, stdout, stderr, duration = run_command(cmd, cwd=project_dir)

    return CheckResult(
        name=name,
        passed=code == 0,
        exit_code=code,
        stdout=stdout,
        stderr=stderr,
        duration=duration,
    )


def run_pytest(project_dir: Path, test_dir: str = "tests") -> CheckResult:
    """Run pytest test suite."""
    name = "test (pytest)"

    # Check if tests directory exists
    tests_path = project_dir / test_dir
    if not tests_path.exists():
        # Try alternatives
        for alt in ["test", "."]:
            tests_path = project_dir / alt
            if (tests_path / "test_*.py").parent.exists():
                break

    cmd = ["pytest", "-v", "--tb=short"]
    code, stdout, stderr, duration = run_command(cmd, cwd=project_dir, timeout=600)

    if code == 127:
        cmd = [sys.executable, "-m", "pytest", "-v", "--tb=short"]
        code, stdout, stderr, duration = run_command(cmd, cwd=project_dir, timeout=600)

    return CheckResult(
        name=name,
        passed=code == 0,
        exit_code=code,
        stdout=stdout,
        stderr=stderr,
        duration=duration,
    )


def run_build(project_dir: Path) -> CheckResult:
    """Run Python package build."""
    name = "build"

    cmd = [sys.executable, "-m", "build"]
    code, stdout, stderr, duration = run_command(cmd, cwd=project_dir, timeout=300)

    return CheckResult(
        name=name,
        passed=code == 0,
        exit_code=code,
        stdout=stdout,
        stderr=stderr,
        duration=duration,
    )


def run_check_with_recovery(
    check_fn,
    project_dir: Path,
    package_manager: str,
    max_retries: int = 1,
    **kwargs
) -> CheckResult:
    """
    Run a check with error recovery.

    Args:
        check_fn: Function that returns CheckResult
        project_dir: Path to project root
        package_manager: pip, poetry, pipenv, or uv
        max_retries: Maximum recovery attempts
        **kwargs: Additional args for check_fn

    Returns:
        CheckResult with recovery info if attempted
    """
    result = check_fn(project_dir, **kwargs)

    if result.passed:
        return result

    # Diagnose error
    error_type = diagnose_error(result.stderr, result.stdout)
    result.error_type = error_type

    if not can_recover(error_type):
        return result

    # Attempt recovery
    for attempt in range(max_retries):
        recovered, msg = recover_python(error_type, project_dir, package_manager)
        result.recovery_attempted = True
        result.recovery_message = msg

        if not recovered:
            break

        # Retry the check
        retry_result = check_fn(project_dir, **kwargs)
        if retry_result.passed:
            # Keep recovery info but use retry result
            retry_result.error_type = error_type
            retry_result.recovery_attempted = True
            retry_result.recovery_message = f"{msg}\n[OK] Retry succeeded"
            return retry_result

    return result


def run_ci(
    project_dir: Optional[Path] = None,
    package_manager: Optional[str] = None,
    src_dir: str = "src",
    test_dir: str = "tests",
    skip_lint: bool = False,
    skip_type: bool = False,
    skip_test: bool = False,
    skip_build: bool = False,
) -> CIResult:
    """
    Run complete CI pipeline for Python project.

    Args:
        project_dir: Path to project root (default: cwd)
        package_manager: pip, poetry, pipenv, or uv (auto-detected if None)
        src_dir: Source directory name
        test_dir: Test directory name
        skip_lint: Skip ruff check
        skip_type: Skip mypy check
        skip_test: Skip pytest
        skip_build: Skip build

    Returns:
        CIResult with all check results
    """
    if project_dir is None:
        project_dir = Path.cwd()

    if package_manager is None:
        package_manager = detect_package_manager(project_dir)

    start_time = time.time()
    checks: List[CheckResult] = []
    all_passed = True

    print(f"[INFO] Running Python CI in {project_dir}")
    print(f"[INFO] Package manager: {package_manager}")
    print()

    # Lint check
    if not skip_lint:
        print("[INFO] Running lint (ruff)...")
        result = run_check_with_recovery(
            run_ruff, project_dir, package_manager
        )
        checks.append(result)
        status = "[OK]" if result.passed else "[FAIL]"
        print(f"  {status} lint ({result.duration:.1f}s)")
        if not result.passed:
            all_passed = False

    # Type check
    if not skip_type:
        print("[INFO] Running type check (mypy)...")
        result = run_check_with_recovery(
            run_mypy, project_dir, package_manager, src_dir=src_dir
        )
        checks.append(result)
        status = "[OK]" if result.passed else "[FAIL]"
        print(f"  {status} type ({result.duration:.1f}s)")
        if not result.passed:
            all_passed = False

    # Tests
    if not skip_test:
        print("[INFO] Running tests (pytest)...")
        result = run_check_with_recovery(
            run_pytest, project_dir, package_manager, test_dir=test_dir
        )
        checks.append(result)
        status = "[OK]" if result.passed else "[FAIL]"
        print(f"  {status} test ({result.duration:.1f}s)")
        if not result.passed:
            all_passed = False

    # Build
    if not skip_build:
        print("[INFO] Running build...")
        result = run_check_with_recovery(
            run_build, project_dir, package_manager
        )
        checks.append(result)
        status = "[OK]" if result.passed else "[FAIL]"
        print(f"  {status} build ({result.duration:.1f}s)")
        if not result.passed:
            all_passed = False

    total_duration = time.time() - start_time

    print()
    if all_passed:
        print(f"[OK] All CI checks passed ({total_duration:.1f}s)")
    else:
        failed = [c.name for c in checks if not c.passed]
        print(f"[FAIL] CI failed: {', '.join(failed)} ({total_duration:.1f}s)")

    return CIResult(
        passed=all_passed,
        checks=checks,
        project_dir=str(project_dir),
        package_manager=package_manager,
        total_duration=total_duration,
    )


def main():
    """Run CI and output JSON result."""
    import argparse

    parser = argparse.ArgumentParser(description="Run Python CI checks")
    parser.add_argument("project_dir", nargs="?", help="Project directory")
    parser.add_argument("--package-manager", "-p", help="Package manager")
    parser.add_argument("--src-dir", "-s", default="src", help="Source directory")
    parser.add_argument("--test-dir", "-t", default="tests", help="Test directory")
    parser.add_argument("--skip-lint", action="store_true", help="Skip lint")
    parser.add_argument("--skip-type", action="store_true", help="Skip type check")
    parser.add_argument("--skip-test", action="store_true", help="Skip tests")
    parser.add_argument("--skip-build", action="store_true", help="Skip build")
    parser.add_argument("--json", action="store_true", help="Output JSON only")

    args = parser.parse_args()

    project_dir = Path(args.project_dir) if args.project_dir else None

    result = run_ci(
        project_dir=project_dir,
        package_manager=args.package_manager,
        src_dir=args.src_dir,
        test_dir=args.test_dir,
        skip_lint=args.skip_lint,
        skip_type=args.skip_type,
        skip_test=args.skip_test,
        skip_build=args.skip_build,
    )

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))

    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
