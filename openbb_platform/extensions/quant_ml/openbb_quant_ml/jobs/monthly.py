"""Monthly universe/policy refresh job."""

from __future__ import annotations

import time
from typing import Any, Callable

from openbb_quant_ml.jobs.logging import append_log, write_json
from openbb_quant_ml.jobs.state import JobState
from openbb_quant_ml.jobs.steps import (
    backfill_if_needed,
    build_features,
    db_maintenance,
    evaluate,
    notify,
    publish,
    rebuild_universe,
    stress_test,
    train_models,
)

StepFunc = Callable[[dict[str, Any]], dict[str, Any]]


def _run_step(run_dir, name: str, func: StepFunc, config: dict[str, Any]) -> tuple[dict[str, Any], float]:
    started = time.perf_counter()
    result = func(config)
    elapsed = float(time.perf_counter() - started)
    append_log(run_dir, "info", name, "step completed", {"result": result, "elapsed": elapsed})
    return result, elapsed


def run_monthly(config: dict[str, Any], state: JobState, run_id: str, run_dir) -> None:
    """Execute monthly job steps."""
    job_cfg = config.get("monthly", {}) if isinstance(config, dict) else {}
    runtime_cfg = dict(job_cfg)
    runtime_cfg.setdefault("job", "monthly")
    runtime_cfg["updated_at"] = run_id

    steps: list[tuple[str, StepFunc]] = [
        ("rebuild_universe", rebuild_universe.run),
        ("backfill_if_needed", backfill_if_needed.run),
        ("rebuild_features_for_changed_universe", build_features.run),
        ("train_models_full", train_models.run),
        ("evaluate", evaluate.run),
        ("stress_test", stress_test.run),
        ("db_maintenance", db_maintenance.run),
        ("publish", publish.run),
        ("notify", notify.run),
    ]

    time_profile: dict[str, float] = {}
    for step_name, func in steps:
        result, elapsed = _run_step(run_dir, step_name, func, runtime_cfg)
        if step_name == "train_models_full" and isinstance(result, dict) and result.get("run_id"):
            runtime_cfg["run_id"] = str(result["run_id"])
            state.set("monthly.latest_run_id", str(result["run_id"]))
        state.set(f"monthly.{step_name}.last_success", run_id)
        state.set(f"monthly.{step_name}.result", result)
        time_profile[step_name] = elapsed
    write_json(run_dir, "time_profile.json", time_profile)
