"""Scheduler configuration and health helpers."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import yaml

from openbb_quant_ml.models import SchedulerStatusResponse
from openbb_quant_ml.service.constants import ARTIFACT_ROOT, OPS_JOBS_PATH
from openbb_quant_ml.service.ops_policy import get_ops_policy
from openbb_quant_ml.service.storage import load_json


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _load_ops_jobs() -> dict[str, Any]:
    if not OPS_JOBS_PATH.exists():
        return {}
    try:
        parsed = yaml.safe_load(OPS_JOBS_PATH.read_text(encoding="utf-8")) or {}
    except Exception:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def get_scheduler_status_response() -> SchedulerStatusResponse:
    """Return scheduler configuration and last-known job state."""
    jobs_cfg = _load_ops_jobs()
    defaults = jobs_cfg.get("defaults", {}) if isinstance(jobs_cfg, dict) else {}
    policy = get_ops_policy()
    scheduler_cfg = policy.get("scheduler", {}) if isinstance(policy, dict) else {}
    expected_jobs = scheduler_cfg.get("expected_jobs", [])
    if not isinstance(expected_jobs, list):
        expected_jobs = ["daily", "weekly", "monthly"]
    job_state = load_json(ARTIFACT_ROOT / "jobs" / "job_state.json", default={})
    if not isinstance(job_state, dict):
        job_state = {}
    rows: list[dict[str, Any]] = []
    for job_name in expected_jobs:
        rows.append(
            {
                "job": str(job_name),
                "last_status": job_state.get(f"{job_name}.last_status"),
                "last_run_id": job_state.get(f"{job_name}.last_run_id"),
                "last_error": job_state.get(f"{job_name}.last_error"),
            }
        )
    try:
        from openbb_quant_ml.service.macro_service import get_regime_scheduler_status_response

        macro_scheduler = get_regime_scheduler_status_response().model_dump(mode="json")
    except Exception as exc:  # noqa: BLE001
        macro_scheduler = {"status": "unknown", "message": str(exc)}
    market_schedule = (
        defaults.get("market_schedule", {}) if isinstance(defaults, dict) else {}
    )
    return SchedulerStatusResponse(
        timezone=(
            str(defaults.get("timezone")) if isinstance(defaults, dict) else None
        ),
        market_schedule=(
            market_schedule if isinstance(market_schedule, dict) else {}
        ),
        expected_jobs=[str(item) for item in expected_jobs],
        jobs=rows,
        macro_scheduler=macro_scheduler,
        generated_at=_now_iso(),
    )
