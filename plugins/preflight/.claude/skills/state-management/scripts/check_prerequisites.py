#!/usr/bin/env python3
"""Check if prerequisites are met for a gate."""

import argparse
import json
import sys
from pathlib import Path


# Gate prerequisites mapping
PREREQUISITES = {
    "lint-test": [],
    "coverage": ["lint-test"],
    "cross-platform": ["lint-test", "coverage"],
    "python-matrix": ["lint-test", "coverage", "cross-platform"],
    "security": ["lint-test", "coverage", "cross-platform", "python-matrix"],
    "api-compat": [
        "lint-test",
        "coverage",
        "cross-platform",
        "python-matrix",
        "security",
    ],
    "packaging": [
        "lint-test",
        "coverage",
        "cross-platform",
        "python-matrix",
        "security",
        "api-compat",
    ],
    "github-pr": [
        "lint-test",
        "coverage",
        "cross-platform",
        "python-matrix",
        "security",
        "api-compat",
        "packaging",
    ],
}


def get_state_file() -> Path:
    """Get the path to the state file."""
    script_dir = Path(__file__).resolve().parent
    plugin_root = script_dir.parent.parent.parent.parent
    return plugin_root / "state" / "pipeline_state.json"


def read_state() -> dict:
    """Read the current pipeline state."""
    state_file = get_state_file()

    if not state_file.exists():
        return {}

    with open(state_file, "r", encoding="utf-8") as f:
        return json.load(f)


def check_prerequisites(gate: str) -> dict:
    """Check if all prerequisites are met for a gate."""
    if gate not in PREREQUISITES:
        return {
            "status": "ERROR",
            "can_run": False,
            "message": f"Unknown gate: {gate}",
            "valid_gates": list(PREREQUISITES.keys()),
        }

    required = PREREQUISITES[gate]

    # No prerequisites
    if not required:
        return {
            "status": "OK",
            "can_run": True,
            "gate": gate,
            "message": f"Gate {gate} has no prerequisites",
        }

    state = read_state()

    if not state:
        return {
            "status": "ERROR",
            "can_run": False,
            "message": "No pipeline initialized. Run init_pipeline.py first.",
        }

    gates = state.get("gates", {})

    passed = []
    failed = []
    pending = []

    for prereq in required:
        prereq_status = gates.get(prereq, {}).get("status", "PENDING")
        if prereq_status == "PASS":
            passed.append(prereq)
        elif prereq_status == "FAIL":
            failed.append(prereq)
        else:
            pending.append(prereq)

    can_run = len(passed) == len(required)

    if can_run:
        return {
            "status": "OK",
            "can_run": True,
            "gate": gate,
            "message": f"All {len(required)} prerequisites passed",
            "passed": passed,
        }
    else:
        blocking = failed + pending
        return {
            "status": "BLOCKED",
            "can_run": False,
            "gate": gate,
            "message": f"Cannot run {gate}: {len(blocking)} prerequisite(s) not passed",
            "blocking": blocking,
            "failed": failed,
            "pending": pending,
            "passed": passed,
        }


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Check gate prerequisites")
    parser.add_argument("gate", help="Gate to check prerequisites for")
    args = parser.parse_args()

    result = check_prerequisites(args.gate)
    print(json.dumps(result, indent=2))

    # Exit code: 0 if can run, 1 if blocked
    return 0 if result.get("can_run", False) else 1


if __name__ == "__main__":
    sys.exit(main())
