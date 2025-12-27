#!/usr/bin/env python3
"""
Phase 5: Node.js CI Execution

Runs local CI checks for Node.js/TypeScript projects:
- npm/yarn/pnpm/bun ci (install)
- lint (eslint or configured script)
- typecheck (tsc)
- build
- test

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
    recover_node,
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
    package_manager: str = "npm"
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
            shell=False,
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
    """Detect Node package manager from lock files."""
    if (project_dir / "bun.lockb").exists():
        return "bun"
    if (project_dir / "pnpm-lock.yaml").exists():
        return "pnpm"
    if (project_dir / "yarn.lock").exists():
        return "yarn"
    return "npm"


def get_package_json(project_dir: Path) -> Dict[str, Any]:
    """Read package.json if it exists."""
    pkg_path = project_dir / "package.json"
    if pkg_path.exists():
        try:
            with open(pkg_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            pass
    return {}


def has_script(project_dir: Path, script_name: str) -> bool:
    """Check if package.json has a specific script."""
    pkg = get_package_json(project_dir)
    return script_name in pkg.get("scripts", {})


def get_run_cmd(package_manager: str) -> List[str]:
    """Get the run command prefix for a package manager."""
    if package_manager == "npm":
        return ["npm", "run"]
    elif package_manager == "yarn":
        return ["yarn"]
    elif package_manager == "pnpm":
        return ["pnpm"]
    elif package_manager == "bun":
        return ["bun", "run"]
    return ["npm", "run"]


def run_install(project_dir: Path, package_manager: str) -> CheckResult:
    """Run package installation (ci for npm, install --frozen-lockfile for others)."""
    name = "install"

    if package_manager == "npm":
        cmd = ["npm", "ci"]
    elif package_manager == "yarn":
        cmd = ["yarn", "install", "--frozen-lockfile"]
    elif package_manager == "pnpm":
        cmd = ["pnpm", "install", "--frozen-lockfile"]
    elif package_manager == "bun":
        cmd = ["bun", "install", "--frozen-lockfile"]
    else:
        cmd = ["npm", "ci"]

    code, stdout, stderr, duration = run_command(cmd, cwd=project_dir, timeout=600)

    return CheckResult(
        name=name,
        passed=code == 0,
        exit_code=code,
        stdout=stdout,
        stderr=stderr,
        duration=duration,
    )


def run_lint(project_dir: Path, package_manager: str) -> CheckResult:
    """Run linting via package.json script or eslint directly."""
    name = "lint"

    # Check for lint script in package.json
    if has_script(project_dir, "lint"):
        cmd = get_run_cmd(package_manager) + ["lint"]
    elif has_script(project_dir, "lint:check"):
        cmd = get_run_cmd(package_manager) + ["lint:check"]
    else:
        # Fall back to eslint directly
        cmd = ["npx", "eslint", "."]

    code, stdout, stderr, duration = run_command(cmd, cwd=project_dir)

    return CheckResult(
        name=name,
        passed=code == 0,
        exit_code=code,
        stdout=stdout,
        stderr=stderr,
        duration=duration,
    )


def run_typecheck(project_dir: Path, package_manager: str) -> CheckResult:
    """Run TypeScript type checking."""
    name = "type (tsc)"

    # Check for typecheck script in package.json
    if has_script(project_dir, "typecheck"):
        cmd = get_run_cmd(package_manager) + ["typecheck"]
    elif has_script(project_dir, "type-check"):
        cmd = get_run_cmd(package_manager) + ["type-check"]
    elif has_script(project_dir, "tsc"):
        cmd = get_run_cmd(package_manager) + ["tsc"]
    else:
        # Fall back to tsc directly (no emit)
        cmd = ["npx", "tsc", "--noEmit"]

    code, stdout, stderr, duration = run_command(cmd, cwd=project_dir)

    return CheckResult(
        name=name,
        passed=code == 0,
        exit_code=code,
        stdout=stdout,
        stderr=stderr,
        duration=duration,
    )


def run_build(project_dir: Path, package_manager: str) -> CheckResult:
    """Run build via package.json script."""
    name = "build"

    if not has_script(project_dir, "build"):
        # No build script, skip gracefully
        return CheckResult(
            name=name,
            passed=True,
            exit_code=0,
            stdout="[SKIP] No build script found",
            stderr="",
            duration=0.0,
        )

    cmd = get_run_cmd(package_manager) + ["build"]
    code, stdout, stderr, duration = run_command(cmd, cwd=project_dir, timeout=600)

    return CheckResult(
        name=name,
        passed=code == 0,
        exit_code=code,
        stdout=stdout,
        stderr=stderr,
        duration=duration,
    )


def run_test(project_dir: Path, package_manager: str) -> CheckResult:
    """Run tests via package.json script."""
    name = "test"

    if not has_script(project_dir, "test"):
        # No test script, skip gracefully
        return CheckResult(
            name=name,
            passed=True,
            exit_code=0,
            stdout="[SKIP] No test script found",
            stderr="",
            duration=0.0,
        )

    cmd = get_run_cmd(package_manager) + ["test"]
    code, stdout, stderr, duration = run_command(cmd, cwd=project_dir, timeout=600)

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
        package_manager: npm, yarn, pnpm, or bun
        max_retries: Maximum recovery attempts
        **kwargs: Additional args for check_fn

    Returns:
        CheckResult with recovery info if attempted
    """
    result = check_fn(project_dir, package_manager, **kwargs)

    if result.passed:
        return result

    # Diagnose error
    error_type = diagnose_error(result.stderr, result.stdout)
    result.error_type = error_type

    if not can_recover(error_type):
        return result

    # Attempt recovery
    for attempt in range(max_retries):
        recovered, msg = recover_node(error_type, project_dir, package_manager)
        result.recovery_attempted = True
        result.recovery_message = msg

        if not recovered:
            break

        # Retry the check
        retry_result = check_fn(project_dir, package_manager, **kwargs)
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
    skip_install: bool = False,
    skip_lint: bool = False,
    skip_type: bool = False,
    skip_build: bool = False,
    skip_test: bool = False,
) -> CIResult:
    """
    Run complete CI pipeline for Node.js project.

    Args:
        project_dir: Path to project root (default: cwd)
        package_manager: npm, yarn, pnpm, or bun (auto-detected if None)
        skip_install: Skip dependency installation
        skip_lint: Skip linting
        skip_type: Skip TypeScript check
        skip_build: Skip build
        skip_test: Skip tests

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

    print(f"[INFO] Running Node.js CI in {project_dir}")
    print(f"[INFO] Package manager: {package_manager}")
    print()

    # Install dependencies
    if not skip_install:
        print("[INFO] Installing dependencies...")
        result = run_check_with_recovery(
            run_install, project_dir, package_manager
        )
        checks.append(result)
        status = "[OK]" if result.passed else "[FAIL]"
        print(f"  {status} install ({result.duration:.1f}s)")
        if not result.passed:
            all_passed = False
            # If install fails, skip remaining steps
            print("[WARN] Install failed, skipping remaining checks")
            return CIResult(
                passed=False,
                checks=checks,
                project_dir=str(project_dir),
                package_manager=package_manager,
                total_duration=time.time() - start_time,
            )

    # Lint check
    if not skip_lint:
        print("[INFO] Running lint...")
        result = run_check_with_recovery(
            run_lint, project_dir, package_manager
        )
        checks.append(result)
        status = "[OK]" if result.passed else "[FAIL]"
        print(f"  {status} lint ({result.duration:.1f}s)")
        if not result.passed:
            all_passed = False

    # Type check (only if TypeScript project)
    tsconfig = project_dir / "tsconfig.json"
    if not skip_type and tsconfig.exists():
        print("[INFO] Running type check (tsc)...")
        result = run_check_with_recovery(
            run_typecheck, project_dir, package_manager
        )
        checks.append(result)
        status = "[OK]" if result.passed else "[FAIL]"
        print(f"  {status} type ({result.duration:.1f}s)")
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
        if "[SKIP]" in result.stdout:
            print(f"  [SKIP] build (no script)")
        else:
            print(f"  {status} build ({result.duration:.1f}s)")
        if not result.passed:
            all_passed = False

    # Tests
    if not skip_test:
        print("[INFO] Running tests...")
        result = run_check_with_recovery(
            run_test, project_dir, package_manager
        )
        checks.append(result)
        status = "[OK]" if result.passed else "[FAIL]"
        if "[SKIP]" in result.stdout:
            print(f"  [SKIP] test (no script)")
        else:
            print(f"  {status} test ({result.duration:.1f}s)")
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

    parser = argparse.ArgumentParser(description="Run Node.js CI checks")
    parser.add_argument("project_dir", nargs="?", help="Project directory")
    parser.add_argument("--package-manager", "-p", help="Package manager")
    parser.add_argument("--skip-install", action="store_true", help="Skip install")
    parser.add_argument("--skip-lint", action="store_true", help="Skip lint")
    parser.add_argument("--skip-type", action="store_true", help="Skip type check")
    parser.add_argument("--skip-build", action="store_true", help="Skip build")
    parser.add_argument("--skip-test", action="store_true", help="Skip tests")
    parser.add_argument("--json", action="store_true", help="Output JSON only")

    args = parser.parse_args()

    project_dir = Path(args.project_dir) if args.project_dir else None

    result = run_ci(
        project_dir=project_dir,
        package_manager=args.package_manager,
        skip_install=args.skip_install,
        skip_lint=args.skip_lint,
        skip_type=args.skip_type,
        skip_build=args.skip_build,
        skip_test=args.skip_test,
    )

    if args.json:
        print(json.dumps(result.to_dict(), indent=2))

    return 0 if result.passed else 1


if __name__ == "__main__":
    sys.exit(main())
