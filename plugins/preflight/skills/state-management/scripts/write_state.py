#!/usr/bin/env python3
"""Write/update gate status in pipeline state."""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


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


def write_state(gate: str, status: str, details: dict | None = None) -> dict:
    """Update gate status in pipeline state."""
    state_file = get_state_file()
    state = read_state()

    if not state:
        return {
            "status": "ERROR",
            "message": "No pipeline initialized. Run init_pipeline.py first.",
        }

    valid_gates = [
        "lint-test",
        "coverage",
        "cross-platform",
        "python-matrix",
        "security",
        "api-compat",
        "packaging",
        "github-pr",
    ]

    if gate not in valid_gates:
        return {
            "status": "ERROR",
            "message": f"Unknown gate: {gate}. Valid gates: {', '.join(valid_gates)}",
        }

    valid_statuses = ["PASS", "FAIL", "RUNNING", "PENDING"]
    if status not in valid_statuses:
        return {
            "status": "ERROR",
            "message": f"Invalid status: {status}. Valid: {', '.join(valid_statuses)}",
        }

    now = datetime.now(timezone.utc).isoformat()

    # Get existing gate state
    gate_state = state.get("gates", {}).get(gate, {})

    # Update gate state
    if status == "RUNNING":
        gate_state["status"] = "RUNNING"
        gate_state["started_at"] = now
        state["current_gate"] = gate
    else:
        gate_state["status"] = status
        gate_state["completed_at"] = now

        # Calculate duration if we have started_at
        if "started_at" in gate_state:
            try:
                started = datetime.fromisoformat(gate_state["started_at"])
                completed = datetime.fromisoformat(now)
                gate_state["duration_seconds"] = (completed - started).total_seconds()
            except (ValueError, TypeError):
                pass

        if status == "FAIL":
            state["current_gate"] = gate  # Stay on failed gate

    if details:
        gate_state["details"] = details

    # Update state
    if "gates" not in state:
        state["gates"] = {}
    state["gates"][gate] = gate_state

    # Write back
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

    return {
        "status": "OK",
        "gate": gate,
        "gate_status": status,
        "message": f"Gate {gate} updated to {status}",
    }


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Update gate status")
    parser.add_argument("gate", help="Gate name")
    parser.add_argument("status", choices=["PASS", "FAIL", "RUNNING", "PENDING"])
    parser.add_argument("--details", help="JSON string with gate details")
    args = parser.parse_args()

    details = None
    if args.details:
        try:
            details = json.loads(args.details)
        except json.JSONDecodeError as e:
            result = {"status": "ERROR", "message": f"Invalid JSON in --details: {e}"}
            print(json.dumps(result, indent=2))
            return 1

    result = write_state(args.gate, args.status, details)
    print(json.dumps(result, indent=2))

    return 0 if result.get("status") == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
