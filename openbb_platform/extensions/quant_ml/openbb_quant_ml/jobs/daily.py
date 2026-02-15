"""Daily operational job."""

from __future__ import annotations

import time
from typing import Any, Callable

from openbb_quant_ml.jobs.logging import append_log, write_json
from openbb_quant_ml.jobs.state import JobState
from openbb_quant_ml.service.storage import read_registry
from openbb_quant_ml.jobs.steps import (
    backtest,
    build_features,
    build_signals,
    notify,
    predict,
    publish,
    update_macro_data,
    update_market_data,
)

StepFunc = Callable[[dict[str, Any]], dict[str, Any]]


def _latest_completed_run_id() -> str | None:
    payload = read_registry()
    runs = payload.get("runs", {})
    if not isinstance(runs, dict):
        return None
    candidates: list[tuple[str, str]] = []
    for run_id, row in runs.items():
        if not isinstance(row, dict):
            continue
        if str(row.get("status", "")).lower() != "completed":
            continue
        updated = str(row.get("updated_at") or row.get("created_at") or "")
        candidates.append((updated, str(run_id)))
    if not candidates:
        return None
    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates[0][1]


def _is_completed_run(run_id: str | None) -> bool:
    if not run_id:
        return False
    payload = read_registry()
    runs = payload.get("runs", {})
    if not isinstance(runs, dict):
        return False
    row = runs.get(str(run_id), {})
    return isinstance(row, dict) and str(row.get("status", "")).lower() == "completed"


def _run_step(
    run_dir,
    name: str,
    func: StepFunc,
    config: dict[str, Any],
    retries: int,
    backoff_sec: float,
) -> tuple[dict[str, Any], float]:
    last_exc: Exception | None = None
    started = time.perf_counter()
    for attempt in range(1, retries + 2):
        try:
            result = func(config)
            elapsed = float(time.perf_counter() - started)
            append_log(run_dir, "info", name, f"step completed (attempt={attempt})", {"result": result, "elapsed": elapsed})
            return result, elapsed
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            append_log(run_dir, "warning", name, f"step failed (attempt={attempt}): {exc}")
            if attempt < retries + 1:
                time.sleep(backoff_sec * attempt)
    raise RuntimeError(f"{name} failed after retries: {last_exc}") from last_exc


def run_daily(config: dict[str, Any], state: JobState, run_id: str, run_dir) -> None:
    """Execute daily job steps."""
    job_cfg = config.get("daily", {}) if isinstance(config, dict) else {}
    runtime_cfg = dict(job_cfg)
    configured_run = str(runtime_cfg.get("run_id") or "").strip()
    if configured_run:
        runtime_cfg["run_id"] = configured_run
    else:
        weekly_run = state.get("weekly.latest_run_id")
        runtime_cfg["run_id"] = weekly_run if _is_completed_run(weekly_run) else _latest_completed_run_id()
    runtime_cfg.setdefault("job", "daily")
    runtime_cfg["updated_at"] = run_id
    retries = int(job_cfg.get("retries", 1))
    backoff_sec = float(job_cfg.get("backoff_sec", 1.0))

    steps: list[tuple[str, StepFunc]] = [
        ("update_market_data", update_market_data.run),
        ("update_macro_data", update_macro_data.run),
        ("build_features_incremental", build_features.run),
        ("predict", predict.run),
        ("build_signals", build_signals.run),
        ("backtest_light", backtest.run),
        ("publish", publish.run),
        ("notify", notify.run),
    ]

    time_profile: dict[str, float] = {}
    for step_name, func in steps:
        result, elapsed = _run_step(run_dir, step_name, func, runtime_cfg, retries=retries, backoff_sec=backoff_sec)
        state.set(f"daily.{step_name}.last_success", run_id)
        state.set(f"daily.{step_name}.result", result)
        time_profile[step_name] = elapsed
    write_json(run_dir, "time_profile.json", time_profile)
