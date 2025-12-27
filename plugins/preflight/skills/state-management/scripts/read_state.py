#!/usr/bin/env python3
"""Read current pipeline state."""

import argparse
import json
import sys
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
        return {
            "status": "ERROR",
            "message": "No pipeline initialized. Run init_pipeline.py first.",
            "state_file": str(state_file),
        }

    with open(state_file, "r", encoding="utf-8") as f:
        return json.load(f)


def format_summary(state: dict) -> str:
    """Format state as human-readable summary."""
    if state.get("status") == "ERROR":
        return f"[ERROR] {state.get('message', 'Unknown error')}"

    lines = [
        f"Pipeline: {state.get('pipeline_id', 'unknown')}",
        f"Started: {state.get('started_at', 'unknown')}",
        f"Package: {state.get('target_package', 'N/A')} {state.get('target_version', '')}".strip(),
        "",
        "Gates:",
    ]

    gate_order = [
        "lint-test",
        "coverage",
        "cross-platform",
        "python-matrix",
        "security",
        "api-compat",
        "packaging",
        "github-pr",
    ]

    for i, gate_name in enumerate(gate_order, 1):
        gate = state.get("gates", {}).get(gate_name, {})
        status = gate.get("status", "PENDING")
        duration = gate.get("duration_seconds", "")
        duration_str = f" ({duration:.1f}s)" if duration else ""

        # Status indicators (ASCII only)
        if status == "PASS":
            indicator = "[PASS]"
        elif status == "FAIL":
            indicator = "[FAIL]"
        elif status == "RUNNING":
            indicator = "[....]"
        else:
            indicator = "[    ]"

        lines.append(f"  {i}. {gate_name:16} {indicator}{duration_str}")

    return "\n".join(lines)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Read pipeline state")
    parser.add_argument("--gate", help="Get status of specific gate only")
    parser.add_argument(
        "--format",
        choices=["json", "summary"],
        default="json",
        help="Output format",
    )
    args = parser.parse_args()

    state = read_state()

    # If specific gate requested
    if args.gate and state.get("status") != "ERROR":
        gate_status = state.get("gates", {}).get(args.gate)
        if gate_status:
            state = {"gate": args.gate, **gate_status}
        else:
            state = {"status": "ERROR", "message": f"Unknown gate: {args.gate}"}

    # Output
    if args.format == "summary":
        print(format_summary(state))
    else:
        print(json.dumps(state, indent=2))

    return 0


if __name__ == "__main__":
    sys.exit(main())
