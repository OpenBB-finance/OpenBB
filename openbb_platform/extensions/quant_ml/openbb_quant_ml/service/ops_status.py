"""Operational status aggregation for jobs, cache versions, and macro health."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from openbb_quant_ml.models import OpsJobStateResponse, OpsStatusResponse
from openbb_quant_ml.service.cache_registry import (
    get_data_versions,
    get_feature_versions,
)
from openbb_quant_ml.service.constants import ARTIFACT_ROOT, WALKFORWARD_JOBS_PATH
from openbb_quant_ml.service.run_index import (
    get_latest_training_run_id_from_index,
    list_latest_runs_from_index,
    rebuild_runs_index,
)
from openbb_quant_ml.service.storage import get_run_dir, load_json, read_registry


def _build_job_state(payload: dict[str, Any], job: str) -> OpsJobStateResponse:
    prefix = f"{job}."
    steps: dict[str, dict[str, Any]] = {}
    for key, value in payload.items():
        if not isinstance(key, str) or not key.startswith(prefix):
            continue
        rest = key[len(prefix) :]
        if "." not in rest:
            continue
        step_name, field_name = rest.split(".", 1)
        if step_name in {"last_run_id", "last_status", "last_error"}:
            continue
        row = steps.setdefault(step_name, {})
        row[field_name] = value

    return OpsJobStateResponse(
        job=job,  # type: ignore[arg-type]
        last_status=str(payload.get(f"{job}.last_status", "unknown")),
        last_run_id=payload.get(f"{job}.last_run_id"),
        last_error=payload.get(f"{job}.last_error"),
        steps=steps,
    )


def _latest_runs(limit: int = 10) -> list[dict[str, Any]]:
    indexed = list_latest_runs_from_index(limit=limit)
    if indexed:
        return indexed

    registry = read_registry()
    runs = registry.get("runs", {})
    if not isinstance(runs, dict):
        return []
    rows: list[dict[str, Any]] = []
    for run_id, row in runs.items():
        if not isinstance(row, dict):
            continue
        rows.append(
            {
                "run_id": str(run_id),
                "status": str(row.get("status", "unknown")),
                "stage": str(row.get("stage", "")),
                "created_at": row.get("created_at"),
                "updated_at": row.get("updated_at"),
            }
        )
    rows.sort(
        key=lambda item: str(item.get("updated_at") or item.get("created_at") or ""),
        reverse=True,
    )
    return rows[: max(1, int(limit))]


def _latest_daily_infer_date(job_state: dict[str, Any]) -> str | None:
    result = job_state.get("daily.predict.result", {})
    if isinstance(result, dict):
        as_of_date = str(result.get("as_of_date", "")).strip()
        if as_of_date:
            return as_of_date

    latest_daily_run_id = str(job_state.get("daily.last_run_id", "")).strip()
    if not latest_daily_run_id:
        return None
    infer_path = get_run_dir(latest_daily_run_id) / "inference_latest.json"
    payload = load_json(infer_path, default={})
    if not isinstance(payload, dict):
        return None
    as_of_date = str(payload.get("as_of_date", "")).strip()
    return as_of_date or None


def _walkforward_queue_depth() -> int:
    payload = load_json(WALKFORWARD_JOBS_PATH, default={})
    if not isinstance(payload, dict):
        return 0
    jobs = payload.get("jobs", {})
    if not isinstance(jobs, dict):
        return 0
    depth = 0
    for row in jobs.values():
        if not isinstance(row, dict):
            continue
        status = str(row.get("status", "")).lower()
        if status in {"queued", "running"}:
            depth += 1
    return depth


def get_ops_status_response() -> OpsStatusResponse:
    """Return aggregated ops health payload for UI monitoring."""
    jobs_state_path = ARTIFACT_ROOT / "jobs" / "job_state.json"
    latest_publish_path = ARTIFACT_ROOT / "jobs" / "latest_publish.json"

    job_state = load_json(jobs_state_path, default={})
    if not isinstance(job_state, dict):
        job_state = {}

    job_rows = [
        _build_job_state(job_state, "daily"),
        _build_job_state(job_state, "weekly"),
        _build_job_state(job_state, "monthly"),
    ]
    rebuild_runs_index()

    latest_publish = load_json(latest_publish_path, default={})
    if not isinstance(latest_publish, dict):
        latest_publish = {}

    try:
        from openbb_quant_ml.service.macro_service import get_health_response

        macro_health = get_health_response().model_dump()
    except Exception as exc:  # noqa: BLE001
        macro_health = {
            "status": "insufficient_data",
            "message": str(exc),
        }

    status = "ok"
    message: str | None = None
    if any(job.last_status == "failed" for job in job_rows):
        status = "insufficient_data"
        message = "One or more scheduled jobs failed. Check jobs.latest error fields."
    elif str(macro_health.get("status")) != "ok":
        status = "insufficient_data"
        message = "Macro subsystem is not fully healthy."

    return OpsStatusResponse(
        status=status,  # type: ignore[arg-type]
        message=message,
        generated_at=datetime.now(UTC).replace(microsecond=0).isoformat(),
        jobs=job_rows,
        latest_publish=latest_publish,
        versions={
            "data": get_data_versions(),
            "features": get_feature_versions(),
        },
        latest_runs=_latest_runs(limit=10),
        macro_health=macro_health,
        latest_training_run_id=get_latest_training_run_id_from_index(),
        latest_daily_infer_date=_latest_daily_infer_date(job_state),
        walkforward_queue_depth=_walkforward_queue_depth(),
    )
