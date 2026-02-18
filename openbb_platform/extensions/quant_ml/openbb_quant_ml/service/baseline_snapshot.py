"""Create baseline snapshot from run artifacts (time_profile + metrics)."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime

from openbb_quant_ml.service.constants import ARTIFACT_ROOT
from openbb_quant_ml.service.storage import get_run_dir, load_json, read_registry, save_json


def _latest_completed_run_id() -> str | None:
    payload = read_registry()
    runs = payload.get("runs", {})
    if not isinstance(runs, dict):
        return None
    rows: list[tuple[str, str]] = []
    for run_id, row in runs.items():
        if not isinstance(row, dict):
            continue
        if str(row.get("status", "")).lower() != "completed":
            continue
        updated = str(row.get("updated_at") or row.get("created_at") or "")
        rows.append((updated, str(run_id)))
    if not rows:
        return None
    rows.sort(reverse=True)
    return rows[0][1]


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create quant baseline snapshot from one run.")
    parser.add_argument("--run-id", default=None, help="Run id (default: latest completed)")
    parser.add_argument("--period", default="1y", help="Period label for baseline metadata")
    parser.add_argument("--symbols-count", type=int, default=20, help="Universe size used for baseline run")
    parser.add_argument("--target-mode", default="next_open_to_close")
    parser.add_argument("--entry-price", default="next_open")
    parser.add_argument("--exit-price", default="close")
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    run_id = args.run_id or _latest_completed_run_id()
    if not run_id:
        print("No completed run found.")
        return 1

    run_dir = get_run_dir(run_id)
    if not run_dir.exists():
        print(f"Run directory not found: {run_id}")
        return 1

    time_profile = load_json(run_dir / "time_profile.json", default={})
    metrics = load_json(run_dir / "metrics.json", default={})
    if not isinstance(time_profile, dict):
        time_profile = {}
    if not isinstance(metrics, dict):
        metrics = {}

    timestamp = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    out_path = ARTIFACT_ROOT / "baselines" / f"baseline_{timestamp}.json"
    payload = {
        "run_id": run_id,
        "created_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "period": str(args.period),
        "symbols_count": int(args.symbols_count),
        "target_mode": str(args.target_mode),
        "entry_price": str(args.entry_price),
        "exit_price": str(args.exit_price),
        "time_profile": time_profile,
        "metrics": metrics,
    }
    save_json(out_path, payload)
    print(f"Baseline snapshot saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

