#!/usr/bin/env python3
"""Initialize a new pipeline run."""

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path


def get_state_file() -> Path:
    """Get the path to the state file."""
    # Look for state directory relative to script location
    script_dir = Path(__file__).resolve().parent
    # Go up to plugin root: scripts -> state-management -> skills -> .claude -> preflight
    plugin_root = script_dir.parent.parent.parent.parent
    state_dir = plugin_root / "state"
    state_dir.mkdir(parents=True, exist_ok=True)
    return state_dir / "pipeline_state.json"


def init_pipeline(target_package: str = "", target_version: str = "") -> dict:
    """Initialize a new pipeline state."""
    pipeline_id = str(uuid.uuid4())[:8]
    now = datetime.now(timezone.utc).isoformat()

    state = {
        "pipeline_id": pipeline_id,
        "started_at": now,
        "current_gate": None,
        "target_package": target_package,
        "target_version": target_version,
        "gates": {
            "lint-test": {"status": "PENDING"},
            "coverage": {"status": "PENDING"},
            "cross-platform": {"status": "PENDING"},
            "python-matrix": {"status": "PENDING"},
            "security": {"status": "PENDING"},
            "api-compat": {"status": "PENDING"},
            "packaging": {"status": "PENDING"},
            "github-pr": {"status": "PENDING"},
        },
    }

    return state


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Initialize a new pipeline run")
    parser.add_argument("--target-package", default="", help="Package name")
    parser.add_argument("--target-version", default="", help="Package version")
    args = parser.parse_args()

    state = init_pipeline(args.target_package, args.target_version)
    state_file = get_state_file()

    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

    # Output result
    result = {
        "status": "OK",
        "pipeline_id": state["pipeline_id"],
        "state_file": str(state_file),
        "message": f"Pipeline {state['pipeline_id']} initialized",
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
