"""Daily operational job."""

from __future__ import annotations

import time
from collections.abc import Callable
from datetime import UTC, date, datetime
from typing import Any

from openbb_quant_ml.jobs.logging import append_log, write_json
from openbb_quant_ml.jobs.state import JobState
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
from openbb_quant_ml.service.runtime_pointer import get_promoted_run_id
from openbb_quant_ml.service.storage import read_registry

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
            append_log(
                run_dir,
                "info",
                name,
                f"step completed (attempt={attempt})",
                {"result": result, "elapsed": elapsed},
            )
            return result, elapsed
        except Exception as exc:  # noqa: BLE001
            last_exc = exc
            append_log(
                run_dir, "warning", name, f"step failed (attempt={attempt}): {exc}"
            )
            if attempt < retries + 1:
                time.sleep(backoff_sec * attempt)
    raise RuntimeError(f"{name} failed after retries: {last_exc}") from last_exc


def _resolve_run_date(run_date: str | None) -> str:
    candidate = str(run_date or "").strip()
    try:
        return date.fromisoformat(candidate).isoformat()
    except ValueError:
        return date.today().isoformat()


def _resolve_operational_run_id(
    state: JobState, model_name: str | None = None
) -> str | None:
    promoted = get_promoted_run_id(model_name=model_name)
    if _is_completed_run(promoted):
        return promoted

    weekly_run = state.get("weekly.latest_run_id")
    if _is_completed_run(weekly_run):
        return weekly_run
    return _latest_completed_run_id()


def run_daily(
    config: dict[str, Any],
    state: JobState,
    run_id: str,
    run_dir,
    *,
    run_date: str,
) -> None:
    """Execute daily job steps."""
    defaults = config.get("defaults", {}) if isinstance(config, dict) else {}
    job_cfg = config.get("daily", {}) if isinstance(config, dict) else {}
    runtime_cfg: dict[str, Any] = {}
    if isinstance(defaults, dict):
        runtime_cfg.update(defaults)
    if isinstance(job_cfg, dict):
        runtime_cfg.update(job_cfg)
    configured_run = str(runtime_cfg.get("run_id") or "").strip()
    if configured_run:
        runtime_cfg["run_id"] = configured_run
    else:
        runtime_cfg["run_id"] = _resolve_operational_run_id(
            state,
            model_name=str(runtime_cfg.get("model_name", "lgbm_ranker")),
        )
    runtime_cfg.setdefault("job", "daily")
    runtime_cfg["updated_at"] = run_id
    runtime_cfg["_job_run_dir"] = str(run_dir)
    retries = int(runtime_cfg.get("retries", 1))
    backoff_sec = float(runtime_cfg.get("backoff_sec", 1.0))
    run_date_token = _resolve_run_date(run_date)

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

    time_profile: dict[str, Any] = {}
    for step_name, func in steps:
        step_started_at = datetime.now(UTC).replace(microsecond=0).isoformat()
        append_log(run_dir, "info", step_name, "step started")
        last_success_date = str(
            state.get(f"daily.{step_name}.last_success_date", "") or ""
        )
        if last_success_date == run_date_token:
            append_log(
                run_dir,
                "info",
                step_name,
                f"step skipped (already successful for {run_date_token})",
            )
            time_profile[step_name] = {
                "started_at": step_started_at,
                "finished_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
                "elapsed_sec": 0.0,
                "status": "skipped",
            }
            continue
        try:
            result, elapsed = _run_step(
                run_dir,
                step_name,
                func,
                runtime_cfg,
                retries=retries,
                backoff_sec=backoff_sec,
            )
        except RuntimeError:
            can_fallback = step_name in {"predict", "build_signals", "backtest_light"}
            current_run_id = str(runtime_cfg.get("run_id") or "").strip()
            fallback_run_id = _resolve_operational_run_id(
                state,
                model_name=str(runtime_cfg.get("model_name", "lgbm_ranker")),
            )
            if (
                not can_fallback
                or not fallback_run_id
                or fallback_run_id == current_run_id
            ):
                raise
            append_log(
                run_dir,
                "warning",
                step_name,
                f"retrying with fallback run_id={fallback_run_id}",
                {"previous_run_id": current_run_id},
            )
            runtime_cfg["run_id"] = fallback_run_id
            result, elapsed = _run_step(
                run_dir,
                step_name,
                func,
                runtime_cfg,
                retries=0,
                backoff_sec=backoff_sec,
            )
        state.set(f"daily.{step_name}.last_success", run_id)
        state.set(f"daily.{step_name}.last_success_date", run_date_token)
        state.set(f"daily.{step_name}.result", result)
        time_profile[step_name] = {
            "started_at": step_started_at,
            "finished_at": datetime.now(UTC).replace(microsecond=0).isoformat(),
            "elapsed_sec": float(elapsed),
            "status": "ok",
        }
    write_json(run_dir, "time_profile.json", time_profile)
