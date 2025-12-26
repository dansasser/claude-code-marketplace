#!/usr/bin/env python3
"""
Phase 4: Lock File Check

Validates lock file consistency with config files:
- package-lock.json vs package.json for npm
- yarn.lock vs package.json for yarn
- pnpm-lock.yaml vs package.json for pnpm
- poetry.lock vs pyproject.toml for poetry
- Pipfile.lock vs Pipfile for pipenv

Uses ONLY Python stdlib for cross-platform compatibility.
ALL file operations use pathlib/shutil, NEVER shell commands.
"""
import hashlib
import json
import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class LockfileStatus:
    """Status of a lockfile check."""
    config_file: str
    lock_file: str
    config_exists: bool
    lock_exists: bool
    is_synced: bool
    message: str
    needs_update: bool = False
    last_modified_config: Optional[float] = None
    last_modified_lock: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "config_file": self.config_file,
            "lock_file": self.lock_file,
            "config_exists": self.config_exists,
            "lock_exists": self.lock_exists,
            "is_synced": self.is_synced,
            "message": self.message,
            "needs_update": self.needs_update,
            "last_modified_config": self.last_modified_config,
            "last_modified_lock": self.last_modified_lock,
        }


def get_file_mtime(path: Path) -> Optional[float]:
    """Get file modification time, or None if doesn't exist."""
    try:
        return path.stat().st_mtime
    except (OSError, FileNotFoundError):
        return None


def get_file_hash(path: Path) -> Optional[str]:
    """Get MD5 hash of file contents."""
    try:
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except (OSError, FileNotFoundError):
        return None


def parse_package_json(project_dir: Path) -> Dict[str, Any]:
    """Parse package.json and extract dependencies."""
    pkg_path = project_dir / "package.json"
    if not pkg_path.exists():
        return {}

    try:
        with open(pkg_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return {
            "dependencies": data.get("dependencies", {}),
            "devDependencies": data.get("devDependencies", {}),
            "peerDependencies": data.get("peerDependencies", {}),
            "optionalDependencies": data.get("optionalDependencies", {}),
        }
    except (json.JSONDecodeError, IOError):
        return {}


def parse_package_lock(project_dir: Path) -> Dict[str, Any]:
    """Parse package-lock.json and extract locked versions."""
    lock_path = project_dir / "package-lock.json"
    if not lock_path.exists():
        return {}

    try:
        with open(lock_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # v2/v3 lockfile has packages at root level
        packages = data.get("packages", {})
        if packages:
            return {"packages": packages, "version": data.get("lockfileVersion", 1)}

        # v1 lockfile has dependencies at root level
        return {"dependencies": data.get("dependencies", {}), "version": 1}
    except (json.JSONDecodeError, IOError):
        return {}


def check_npm_sync(project_dir: Path) -> LockfileStatus:
    """Check if package-lock.json is in sync with package.json."""
    config_file = "package.json"
    lock_file = "package-lock.json"

    config_path = project_dir / config_file
    lock_path = project_dir / lock_file

    config_exists = config_path.exists()
    lock_exists = lock_path.exists()

    if not config_exists:
        return LockfileStatus(
            config_file=config_file,
            lock_file=lock_file,
            config_exists=False,
            lock_exists=lock_exists,
            is_synced=True,
            message="No package.json found",
        )

    if not lock_exists:
        return LockfileStatus(
            config_file=config_file,
            lock_file=lock_file,
            config_exists=True,
            lock_exists=False,
            is_synced=False,
            message="Lock file missing - run npm install",
            needs_update=True,
        )

    # Get modification times
    config_mtime = get_file_mtime(config_path)
    lock_mtime = get_file_mtime(lock_path)

    # If package.json is newer than lock file, likely out of sync
    if config_mtime and lock_mtime and config_mtime > lock_mtime:
        return LockfileStatus(
            config_file=config_file,
            lock_file=lock_file,
            config_exists=True,
            lock_exists=True,
            is_synced=False,
            message="package.json modified after lock file - run npm install",
            needs_update=True,
            last_modified_config=config_mtime,
            last_modified_lock=lock_mtime,
        )

    # Try running npm ci --dry-run to verify sync (if npm available)
    try:
        result = subprocess.run(
            ["npm", "ci", "--dry-run"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=project_dir,
            timeout=30,
        )
        if result.returncode != 0:
            # Check for specific sync issues
            stderr = result.stderr.lower()
            if "peer dep" in stderr or "eresolve" in stderr:
                return LockfileStatus(
                    config_file=config_file,
                    lock_file=lock_file,
                    config_exists=True,
                    lock_exists=True,
                    is_synced=False,
                    message="Lock file has dependency conflicts",
                    needs_update=True,
                    last_modified_config=config_mtime,
                    last_modified_lock=lock_mtime,
                )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass  # npm not available, skip dry-run check

    return LockfileStatus(
        config_file=config_file,
        lock_file=lock_file,
        config_exists=True,
        lock_exists=True,
        is_synced=True,
        message="Lock file appears in sync",
        last_modified_config=config_mtime,
        last_modified_lock=lock_mtime,
    )


def check_yarn_sync(project_dir: Path) -> LockfileStatus:
    """Check if yarn.lock is in sync with package.json."""
    config_file = "package.json"
    lock_file = "yarn.lock"

    config_path = project_dir / config_file
    lock_path = project_dir / lock_file

    config_exists = config_path.exists()
    lock_exists = lock_path.exists()

    if not config_exists:
        return LockfileStatus(
            config_file=config_file,
            lock_file=lock_file,
            config_exists=False,
            lock_exists=lock_exists,
            is_synced=True,
            message="No package.json found",
        )

    if not lock_exists:
        return LockfileStatus(
            config_file=config_file,
            lock_file=lock_file,
            config_exists=True,
            lock_exists=False,
            is_synced=False,
            message="Lock file missing - run yarn install",
            needs_update=True,
        )

    config_mtime = get_file_mtime(config_path)
    lock_mtime = get_file_mtime(lock_path)

    if config_mtime and lock_mtime and config_mtime > lock_mtime:
        return LockfileStatus(
            config_file=config_file,
            lock_file=lock_file,
            config_exists=True,
            lock_exists=True,
            is_synced=False,
            message="package.json modified after lock file - run yarn install",
            needs_update=True,
            last_modified_config=config_mtime,
            last_modified_lock=lock_mtime,
        )

    return LockfileStatus(
        config_file=config_file,
        lock_file=lock_file,
        config_exists=True,
        lock_exists=True,
        is_synced=True,
        message="Lock file appears in sync",
        last_modified_config=config_mtime,
        last_modified_lock=lock_mtime,
    )


def check_pnpm_sync(project_dir: Path) -> LockfileStatus:
    """Check if pnpm-lock.yaml is in sync with package.json."""
    config_file = "package.json"
    lock_file = "pnpm-lock.yaml"

    config_path = project_dir / config_file
    lock_path = project_dir / lock_file

    config_exists = config_path.exists()
    lock_exists = lock_path.exists()

    if not config_exists:
        return LockfileStatus(
            config_file=config_file,
            lock_file=lock_file,
            config_exists=False,
            lock_exists=lock_exists,
            is_synced=True,
            message="No package.json found",
        )

    if not lock_exists:
        return LockfileStatus(
            config_file=config_file,
            lock_file=lock_file,
            config_exists=True,
            lock_exists=False,
            is_synced=False,
            message="Lock file missing - run pnpm install",
            needs_update=True,
        )

    config_mtime = get_file_mtime(config_path)
    lock_mtime = get_file_mtime(lock_path)

    if config_mtime and lock_mtime and config_mtime > lock_mtime:
        return LockfileStatus(
            config_file=config_file,
            lock_file=lock_file,
            config_exists=True,
            lock_exists=True,
            is_synced=False,
            message="package.json modified after lock file - run pnpm install",
            needs_update=True,
            last_modified_config=config_mtime,
            last_modified_lock=lock_mtime,
        )

    return LockfileStatus(
        config_file=config_file,
        lock_file=lock_file,
        config_exists=True,
        lock_exists=True,
        is_synced=True,
        message="Lock file appears in sync",
        last_modified_config=config_mtime,
        last_modified_lock=lock_mtime,
    )


def check_bun_sync(project_dir: Path) -> LockfileStatus:
    """Check if bun.lockb is in sync with package.json."""
    config_file = "package.json"
    lock_file = "bun.lockb"

    config_path = project_dir / config_file
    lock_path = project_dir / lock_file

    config_exists = config_path.exists()
    lock_exists = lock_path.exists()

    if not config_exists:
        return LockfileStatus(
            config_file=config_file,
            lock_file=lock_file,
            config_exists=False,
            lock_exists=lock_exists,
            is_synced=True,
            message="No package.json found",
        )

    if not lock_exists:
        return LockfileStatus(
            config_file=config_file,
            lock_file=lock_file,
            config_exists=True,
            lock_exists=False,
            is_synced=False,
            message="Lock file missing - run bun install",
            needs_update=True,
        )

    config_mtime = get_file_mtime(config_path)
    lock_mtime = get_file_mtime(lock_path)

    if config_mtime and lock_mtime and config_mtime > lock_mtime:
        return LockfileStatus(
            config_file=config_file,
            lock_file=lock_file,
            config_exists=True,
            lock_exists=True,
            is_synced=False,
            message="package.json modified after lock file - run bun install",
            needs_update=True,
            last_modified_config=config_mtime,
            last_modified_lock=lock_mtime,
        )

    return LockfileStatus(
        config_file=config_file,
        lock_file=lock_file,
        config_exists=True,
        lock_exists=True,
        is_synced=True,
        message="Lock file appears in sync",
        last_modified_config=config_mtime,
        last_modified_lock=lock_mtime,
    )


def check_poetry_sync(project_dir: Path) -> LockfileStatus:
    """Check if poetry.lock is in sync with pyproject.toml."""
    config_file = "pyproject.toml"
    lock_file = "poetry.lock"

    config_path = project_dir / config_file
    lock_path = project_dir / lock_file

    config_exists = config_path.exists()
    lock_exists = lock_path.exists()

    if not config_exists:
        return LockfileStatus(
            config_file=config_file,
            lock_file=lock_file,
            config_exists=False,
            lock_exists=lock_exists,
            is_synced=True,
            message="No pyproject.toml found",
        )

    if not lock_exists:
        return LockfileStatus(
            config_file=config_file,
            lock_file=lock_file,
            config_exists=True,
            lock_exists=False,
            is_synced=False,
            message="Lock file missing - run poetry lock",
            needs_update=True,
        )

    config_mtime = get_file_mtime(config_path)
    lock_mtime = get_file_mtime(lock_path)

    if config_mtime and lock_mtime and config_mtime > lock_mtime:
        return LockfileStatus(
            config_file=config_file,
            lock_file=lock_file,
            config_exists=True,
            lock_exists=True,
            is_synced=False,
            message="pyproject.toml modified after lock file - run poetry lock",
            needs_update=True,
            last_modified_config=config_mtime,
            last_modified_lock=lock_mtime,
        )

    # Try poetry check to verify sync
    try:
        result = subprocess.run(
            ["poetry", "check", "--lock"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=project_dir,
            timeout=30,
        )
        if result.returncode != 0:
            return LockfileStatus(
                config_file=config_file,
                lock_file=lock_file,
                config_exists=True,
                lock_exists=True,
                is_synced=False,
                message="poetry check --lock failed - run poetry lock",
                needs_update=True,
                last_modified_config=config_mtime,
                last_modified_lock=lock_mtime,
            )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass  # poetry not available

    return LockfileStatus(
        config_file=config_file,
        lock_file=lock_file,
        config_exists=True,
        lock_exists=True,
        is_synced=True,
        message="Lock file appears in sync",
        last_modified_config=config_mtime,
        last_modified_lock=lock_mtime,
    )


def check_pipenv_sync(project_dir: Path) -> LockfileStatus:
    """Check if Pipfile.lock is in sync with Pipfile."""
    config_file = "Pipfile"
    lock_file = "Pipfile.lock"

    config_path = project_dir / config_file
    lock_path = project_dir / lock_file

    config_exists = config_path.exists()
    lock_exists = lock_path.exists()

    if not config_exists:
        return LockfileStatus(
            config_file=config_file,
            lock_file=lock_file,
            config_exists=False,
            lock_exists=lock_exists,
            is_synced=True,
            message="No Pipfile found",
        )

    if not lock_exists:
        return LockfileStatus(
            config_file=config_file,
            lock_file=lock_file,
            config_exists=True,
            lock_exists=False,
            is_synced=False,
            message="Lock file missing - run pipenv lock",
            needs_update=True,
        )

    config_mtime = get_file_mtime(config_path)
    lock_mtime = get_file_mtime(lock_path)

    if config_mtime and lock_mtime and config_mtime > lock_mtime:
        return LockfileStatus(
            config_file=config_file,
            lock_file=lock_file,
            config_exists=True,
            lock_exists=True,
            is_synced=False,
            message="Pipfile modified after lock file - run pipenv lock",
            needs_update=True,
            last_modified_config=config_mtime,
            last_modified_lock=lock_mtime,
        )

    return LockfileStatus(
        config_file=config_file,
        lock_file=lock_file,
        config_exists=True,
        lock_exists=True,
        is_synced=True,
        message="Lock file appears in sync",
        last_modified_config=config_mtime,
        last_modified_lock=lock_mtime,
    )


def detect_and_check_lockfiles(project_dir: Path) -> List[LockfileStatus]:
    """
    Detect project type and check all relevant lock files.

    Returns list of LockfileStatus for all detected lock file types.
    """
    results = []

    # Node.js projects
    if (project_dir / "package.json").exists():
        # Check which lock file exists
        if (project_dir / "bun.lockb").exists():
            results.append(check_bun_sync(project_dir))
        elif (project_dir / "pnpm-lock.yaml").exists():
            results.append(check_pnpm_sync(project_dir))
        elif (project_dir / "yarn.lock").exists():
            results.append(check_yarn_sync(project_dir))
        else:
            # Default to npm
            results.append(check_npm_sync(project_dir))

    # Python projects
    if (project_dir / "poetry.lock").exists() or (
        (project_dir / "pyproject.toml").exists()
        and "poetry" in (project_dir / "pyproject.toml").read_text(encoding="utf-8").lower()
    ):
        results.append(check_poetry_sync(project_dir))

    if (project_dir / "Pipfile").exists():
        results.append(check_pipenv_sync(project_dir))

    return results


def check_lockfiles(project_dir: Optional[Path] = None) -> Dict[str, Any]:
    """
    Check all lock files in a project.

    Args:
        project_dir: Path to project root (default: cwd)

    Returns:
        Dict with overall status and individual lock file results
    """
    if project_dir is None:
        project_dir = Path.cwd()

    results = detect_and_check_lockfiles(project_dir)

    all_synced = all(r.is_synced for r in results) if results else True
    needs_update = any(r.needs_update for r in results)

    return {
        "project_dir": str(project_dir),
        "all_synced": all_synced,
        "needs_update": needs_update,
        "lockfiles": [r.to_dict() for r in results],
        "summary": (
            "[OK] All lock files in sync"
            if all_synced
            else "[WARN] Lock files need updating"
        ),
    }


def main():
    """Check lock files and output JSON result."""
    import argparse

    parser = argparse.ArgumentParser(description="Check lock file consistency")
    parser.add_argument("project_dir", nargs="?", help="Project directory")
    parser.add_argument("--json", action="store_true", help="Output JSON only")

    args = parser.parse_args()

    project_dir = Path(args.project_dir) if args.project_dir else None
    result = check_lockfiles(project_dir)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"[INFO] Checking lock files in {result['project_dir']}")
        print()

        for lf in result["lockfiles"]:
            status = "[OK]" if lf["is_synced"] else "[WARN]"
            print(f"  {status} {lf['lock_file']}: {lf['message']}")

        print()
        print(result["summary"])

    return 0 if result["all_synced"] else 1


if __name__ == "__main__":
    sys.exit(main())
