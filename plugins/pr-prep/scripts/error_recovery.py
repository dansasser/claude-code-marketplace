#!/usr/bin/env python3
"""
Phase 5b: Error Diagnosis and Recovery

Smart error diagnosis and recovery for CI failures.
Shared module used by run_ci_python.py and run_ci_node.py.

Uses ONLY Python stdlib for cross-platform compatibility.
ALL file operations use pathlib/shutil, NEVER shell commands.
"""
import re
import shutil
import subprocess
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ErrorType(Enum):
    """Classification of CI errors."""
    CODE_ERROR = "code_error"           # Actual bug in code - cannot auto-fix
    DEP_CORRUPTION = "dep_corruption"   # node_modules or .venv corrupted
    LOCK_DESYNC = "lock_desync"         # Lock file out of sync with config
    STALE_ARTIFACTS = "stale_artifacts" # Old build files causing issues
    CACHE_POISON = "cache_poison"       # npm/pip cache corrupted
    VERSION_MISMATCH = "version_mismatch"  # Wrong Node/Python version
    UNKNOWN = "unknown"                 # Cannot classify


# Error patterns for diagnosis
# Each pattern maps to an ErrorType
ERROR_PATTERNS: Dict[ErrorType, List[str]] = {
    ErrorType.DEP_CORRUPTION: [
        r"Cannot find module",
        r"Module not found",
        r"No module named",
        r"ENOENT.*node_modules",
        r"ModuleNotFoundError",
        r"ImportError.*No module",
        r"Cannot resolve",
        r"Could not find a version",
        r"Package .* is not installed",
    ],
    ErrorType.LOCK_DESYNC: [
        r"peer dep.*conflict",
        r"ERESOLVE",
        r"unable to resolve dependency tree",
        r"Your lockfile needs to be updated",
        r"poetry.lock.*out of sync",
        r"Run.*npm install",
        r"expected identifier.*package-lock",
        r"lockfile version",
    ],
    ErrorType.STALE_ARTIFACTS: [
        r"Cannot find.*dist/",
        r"ENOENT.*dist/",
        r"File.*dist.*does not exist",
        r"stale.*build",
        r"Output file.*not found",
        r"Build output.*missing",
        r"\.egg-info.*corrupt",
    ],
    ErrorType.CACHE_POISON: [
        r"EINTEGRITY",
        r"sha512.*integrity",
        r"sha1.*integrity",
        r"Cached.*corrupted",
        r"cache.*invalid",
        r"checksum mismatch",
        r"integrity check failed",
    ],
    ErrorType.VERSION_MISMATCH: [
        r"engine.*not compatible",
        r"requires.*node.*>=",
        r"python.*required",
        r"unsupported.*version",
        r"requires python",
        r"node version",
        r"engines.*node",
    ],
}


def diagnose_error(stderr: str, stdout: str) -> ErrorType:
    """
    Classify error based on output patterns.

    Args:
        stderr: Standard error output from failed command
        stdout: Standard output from failed command

    Returns:
        ErrorType classification
    """
    combined = f"{stderr}\n{stdout}".lower()

    for error_type, patterns in ERROR_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, combined, re.IGNORECASE):
                return error_type

    # If no pattern matched but there's an error, it's likely code
    return ErrorType.CODE_ERROR


def recover_node(
    error_type: ErrorType,
    project_dir: Path,
    package_manager: str = "npm"
) -> Tuple[bool, str]:
    """
    Attempt recovery for Node.js projects.

    Args:
        error_type: Classified error type
        project_dir: Path to project root
        package_manager: npm, yarn, pnpm, or bun

    Returns:
        Tuple of (recovery_attempted, message)

    ALL file operations use pathlib/shutil, NEVER shell commands.
    """
    node_modules = project_dir / "node_modules"
    dist_dir = project_dir / "dist"

    # Map package managers to their lock files
    lock_files = {
        "npm": "package-lock.json",
        "yarn": "yarn.lock",
        "pnpm": "pnpm-lock.yaml",
        "bun": "bun.lockb",
    }
    lock_file = project_dir / lock_files.get(package_manager, "package-lock.json")

    # Map package managers to install commands
    install_cmd = {
        "npm": ["npm", "install"],
        "yarn": ["yarn", "install"],
        "pnpm": ["pnpm", "install"],
        "bun": ["bun", "install"],
    }.get(package_manager, ["npm", "install"])

    try:
        if error_type == ErrorType.DEP_CORRUPTION:
            # Delete node_modules and reinstall
            msg = "[INFO] Detected dependency corruption. Cleaning node_modules..."
            if node_modules.exists():
                shutil.rmtree(node_modules)
            subprocess.run(install_cmd, cwd=project_dir, check=True)
            return True, f"{msg}\n[OK] Reinstalled dependencies"

        elif error_type == ErrorType.LOCK_DESYNC:
            # Delete lock file and node_modules, reinstall
            msg = "[INFO] Detected lock file desync. Regenerating..."
            if lock_file.exists():
                lock_file.unlink()
            if node_modules.exists():
                shutil.rmtree(node_modules)
            subprocess.run(install_cmd, cwd=project_dir, check=True)
            return True, f"{msg}\n[OK] Regenerated lock file"

        elif error_type == ErrorType.STALE_ARTIFACTS:
            # Delete dist and rebuild
            msg = "[INFO] Detected stale build artifacts. Cleaning..."
            if dist_dir.exists():
                shutil.rmtree(dist_dir)
            # Also clean .next, .nuxt, etc.
            for cache_dir in [".next", ".nuxt", ".cache", "build"]:
                cache_path = project_dir / cache_dir
                if cache_path.exists():
                    shutil.rmtree(cache_path)
            return True, f"{msg}\n[OK] Cleaned build artifacts"

        elif error_type == ErrorType.CACHE_POISON:
            # Clean npm/yarn/pnpm/bun cache
            msg = "[INFO] Detected cache corruption. Cleaning..."
            if package_manager == "npm":
                subprocess.run(["npm", "cache", "clean", "--force"], check=True)
            elif package_manager == "yarn":
                subprocess.run(["yarn", "cache", "clean"], check=True)
            elif package_manager == "pnpm":
                subprocess.run(["pnpm", "store", "prune"], check=True)
            elif package_manager == "bun":
                subprocess.run(["bun", "pm", "cache", "rm"], check=True)

            if node_modules.exists():
                shutil.rmtree(node_modules)
            subprocess.run(install_cmd, cwd=project_dir, check=True)
            return True, f"{msg}\n[OK] Cleaned cache and reinstalled"

        # CODE_ERROR, VERSION_MISMATCH, UNKNOWN - cannot auto-fix
        return False, "[WARN] Cannot auto-fix this error type"

    except subprocess.CalledProcessError as e:
        return False, f"[FAIL] Recovery failed: {e}"
    except Exception as e:
        return False, f"[FAIL] Recovery error: {e}"


def recover_python(
    error_type: ErrorType,
    project_dir: Path,
    package_manager: str = "pip"
) -> Tuple[bool, str]:
    """
    Attempt recovery for Python projects.

    Args:
        error_type: Classified error type
        project_dir: Path to project root
        package_manager: pip, poetry, pipenv, or uv

    Returns:
        Tuple of (recovery_attempted, message)

    ALL file operations use pathlib/shutil, NEVER shell commands.
    """
    venv_dir = project_dir / ".venv"
    dist_dir = project_dir / "dist"
    egg_info_dirs = list(project_dir.glob("*.egg-info"))
    pycache_dirs = list(project_dir.rglob("__pycache__"))

    # Determine install command
    if package_manager == "poetry":
        install_cmd = ["poetry", "install"]
    elif package_manager == "pipenv":
        install_cmd = ["pipenv", "install", "--dev"]
    elif package_manager == "uv":
        install_cmd = ["uv", "pip", "install", "-e", ".[dev]"]
    else:
        install_cmd = ["pip", "install", "-e", ".[dev]"]

    try:
        if error_type == ErrorType.DEP_CORRUPTION:
            msg = "[INFO] Detected dependency corruption. Cleaning environment..."

            # Clean pycache first (safe, won't break anything)
            for cache in pycache_dirs:
                if cache.exists():
                    shutil.rmtree(cache)

            # Try reinstall without nuking venv first
            try:
                subprocess.run(install_cmd, cwd=project_dir, check=True)
                return True, f"{msg}\n[OK] Reinstalled dependencies"
            except subprocess.CalledProcessError:
                # If that fails, nuke venv
                if venv_dir.exists():
                    shutil.rmtree(venv_dir)
                subprocess.run(install_cmd, cwd=project_dir, check=True)
                return True, f"{msg}\n[OK] Recreated venv and reinstalled"

        elif error_type == ErrorType.STALE_ARTIFACTS:
            msg = "[INFO] Detected stale build artifacts. Cleaning..."

            # Delete dist and egg-info
            if dist_dir.exists():
                shutil.rmtree(dist_dir)
            for egg in egg_info_dirs:
                if egg.exists():
                    shutil.rmtree(egg)

            # Clean pycache
            for cache in pycache_dirs:
                if cache.exists():
                    shutil.rmtree(cache)

            return True, f"{msg}\n[OK] Cleaned build artifacts"

        elif error_type == ErrorType.CACHE_POISON:
            msg = "[INFO] Detected cache corruption. Cleaning..."

            # Purge pip cache
            if package_manager in ["pip", "uv"]:
                subprocess.run(["pip", "cache", "purge"], check=False)

            # Clean pycache
            for cache in pycache_dirs:
                if cache.exists():
                    shutil.rmtree(cache)

            # Reinstall
            if venv_dir.exists():
                shutil.rmtree(venv_dir)
            subprocess.run(install_cmd, cwd=project_dir, check=True)
            return True, f"{msg}\n[OK] Cleaned cache and reinstalled"

        # CODE_ERROR, VERSION_MISMATCH, LOCK_DESYNC (Python rarely has this),
        # UNKNOWN - cannot auto-fix
        return False, "[WARN] Cannot auto-fix this error type"

    except subprocess.CalledProcessError as e:
        return False, f"[FAIL] Recovery failed: {e}"
    except Exception as e:
        return False, f"[FAIL] Recovery error: {e}"


def can_recover(error_type: ErrorType) -> bool:
    """
    Check if this error type is potentially recoverable.

    Note: LOCK_DESYNC is included here for Node.js projects (recover_node handles it).
    Python projects rarely have lock desync issues, so recover_python doesn't handle it,
    but we still report it as potentially recoverable for completeness.
    """
    return error_type in [
        ErrorType.DEP_CORRUPTION,
        ErrorType.LOCK_DESYNC,  # Handled by recover_node, not recover_python
        ErrorType.STALE_ARTIFACTS,
        ErrorType.CACHE_POISON,
    ]


def format_error_report(
    error_type: ErrorType,
    stderr: str,
    stdout: str,
    command: str
) -> str:
    """Format a human-readable error report."""
    report = [
        f"[FAIL] Command failed: {command}",
        f"Error type: {error_type.value}",
        "",
    ]

    if error_type == ErrorType.CODE_ERROR:
        report.append("This appears to be a code error that requires manual fixing.")
    elif error_type == ErrorType.VERSION_MISMATCH:
        report.append("Version mismatch detected. Check your Node/Python version.")
    elif can_recover(error_type):
        report.append("This error may be recoverable. Attempting auto-fix...")

    if stderr:
        report.append("")
        report.append("--- stderr ---")
        # Truncate if too long
        if len(stderr) > 2000:
            report.append(stderr[:2000] + "\n... (truncated)")
        else:
            report.append(stderr)

    return "\n".join(report)
