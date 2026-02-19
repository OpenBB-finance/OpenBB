"""CLI entrypoint for daily/weekly/monthly operational jobs."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml

from openbb_quant_ml.jobs.daily import run_daily
from openbb_quant_ml.jobs.lock import job_lock
from openbb_quant_ml.jobs.logging import append_log, create_run_dir, write_json
from openbb_quant_ml.jobs.monthly import run_monthly
from openbb_quant_ml.jobs.state import JobState
from openbb_quant_ml.jobs.weekly import run_weekly


def _load_config(path: str) -> dict[str, Any]:
    cfg_path = Path(path)
    if not cfg_path.exists():
        return {}
    with cfg_path.open(encoding="utf-8") as file:
        payload = yaml.safe_load(file) or {}
    return payload if isinstance(payload, dict) else {}


def _resolve_runtime_config(config: dict[str, Any], job_name: str) -> dict[str, Any]:
    runtime_cfg: dict[str, Any] = {}
    defaults = config.get("defaults", {}) if isinstance(config, dict) else {}
    if isinstance(defaults, dict):
        runtime_cfg.update(defaults)
    job_cfg = config.get(job_name, {}) if isinstance(config, dict) else {}
    if isinstance(job_cfg, dict):
        runtime_cfg.update(job_cfg)
    return runtime_cfg


def main() -> int:
    parser = argparse.ArgumentParser(description="Quant ML operational jobs CLI.")
    parser.add_argument("job", choices=["daily", "weekly", "monthly"])
    parser.add_argument("--config", required=True)
    args = parser.parse_args()

    cfg = _load_config(args.config)
    runtime_cfg = _resolve_runtime_config(cfg, args.job)
    run_id_scheme = str(runtime_cfg.get("run_id_scheme", "compact_v1"))
    timezone = str(runtime_cfg.get("timezone", "Asia/Seoul"))
    run_id, run_dir, run_date = create_run_dir(
        args.job,
        run_id_scheme=run_id_scheme,
        timezone=timezone,
    )
    state = JobState.load()

    try:
        with job_lock(args.job):
            append_log(run_dir, "info", "job", f"job started: {args.job}")
            if args.job == "daily":
                run_daily(cfg, state, run_id, run_dir, run_date=run_date)
            elif args.job == "weekly":
                run_weekly(cfg, state, run_id, run_dir)
            else:
                run_monthly(cfg, state, run_id, run_dir)
            state.set(f"{args.job}.last_run_id", run_id)
            state.set(f"{args.job}.last_status", "ok")
            state.delete(f"{args.job}.last_error")
            state.save()
            write_json(run_dir, "config_used.json", cfg)
            append_log(run_dir, "info", "job", "job completed")
            return 0
    except Exception as exc:  # noqa: BLE001
        append_log(run_dir, "error", "job", f"job failed: {exc}")
        state.set(f"{args.job}.last_run_id", run_id)
        state.set(f"{args.job}.last_status", "failed")
        state.set(f"{args.job}.last_error", str(exc))
        state.save()
        write_json(run_dir, "config_used.json", cfg)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
