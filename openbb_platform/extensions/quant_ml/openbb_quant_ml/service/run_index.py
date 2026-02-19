"""Run index helpers for fast latest-run lookup."""

from __future__ import annotations

from typing import Any

from openbb_quant_ml.service.constants import RUNS_INDEX_PATH
from openbb_quant_ml.service.storage import (
    get_run_dir,
    load_json,
    read_registry,
    save_json,
)


def _empty_index() -> dict[str, Any]:
    return {
        "latest_run_id": None,
        "latest_training_run_id": None,
        "runs": {},
    }


def _sort_value(row: dict[str, Any]) -> str:
    return str(row.get("updated_at") or row.get("created_at") or "")


def _artifact_flags(run_id: str) -> dict[str, bool]:
    run_dir = get_run_dir(run_id)
    if not run_dir.exists():
        return {
            "predictions": False,
            "metrics": False,
            "backtest": False,
            "model": False,
            "meta": False,
        }
    files = {path.name for path in run_dir.iterdir() if path.is_file()}
    return {
        "predictions": any(name.startswith("predictions") for name in files),
        "metrics": any(name.startswith("metrics") for name in files),
        "backtest": any(name.startswith("backtest") for name in files),
        "model": any(
            name.startswith("model_") and not name.endswith("_meta.json")
            for name in files
        ),
        "meta": any(name.endswith("_meta.json") for name in files),
    }


def load_runs_index() -> dict[str, Any]:
    """Load runs index payload."""
    payload = load_json(RUNS_INDEX_PATH, default=_empty_index())
    if not isinstance(payload, dict):
        return _empty_index()
    runs = payload.get("runs")
    if not isinstance(runs, dict):
        payload["runs"] = {}
    payload.setdefault("latest_run_id", None)
    payload.setdefault("latest_training_run_id", None)
    return payload


def _recompute_latest_fields(payload: dict[str, Any]) -> None:
    runs = payload.get("runs", {})
    if not isinstance(runs, dict) or not runs:
        payload["latest_run_id"] = None
        payload["latest_training_run_id"] = None
        return
    sorted_rows = sorted(
        (
            (run_id, row if isinstance(row, dict) else {})
            for run_id, row in runs.items()
        ),
        key=lambda item: _sort_value(item[1]),
        reverse=True,
    )
    payload["latest_run_id"] = sorted_rows[0][0]

    latest_training = None
    for run_id, row in sorted_rows:
        if str(row.get("status", "")).lower() != "completed":
            continue
        flags = row.get("artifacts", {})
        if isinstance(flags, dict) and bool(flags.get("predictions")):
            latest_training = run_id
            break
    payload["latest_training_run_id"] = latest_training


def save_runs_index(payload: dict[str, Any]) -> None:
    """Persist runs index payload."""
    _recompute_latest_fields(payload)
    save_json(RUNS_INDEX_PATH, payload)


def rebuild_runs_index() -> dict[str, Any]:
    """Rebuild full runs index from registry and run directories."""
    registry = read_registry()
    runs = registry.get("runs", {})
    payload = _empty_index()
    rows: dict[str, Any] = {}
    if isinstance(runs, dict):
        for run_id, row in runs.items():
            if not isinstance(row, dict):
                continue
            run_key = str(run_id)
            rows[run_key] = {
                "status": str(row.get("status", "unknown")),
                "stage": str(row.get("stage", "")),
                "created_at": row.get("created_at"),
                "updated_at": row.get("updated_at"),
                "artifacts": _artifact_flags(run_key),
            }
    payload["runs"] = rows
    save_runs_index(payload)
    return payload


def upsert_run_index_entry(
    run_id: str,
    *,
    status: str | None = None,
    stage: str | None = None,
    created_at: str | None = None,
    updated_at: str | None = None,
) -> None:
    """Upsert one run row in index payload."""
    payload = load_runs_index()
    runs = payload.setdefault("runs", {})
    if not isinstance(runs, dict):
        payload["runs"] = {}
        runs = payload["runs"]
    row = runs.setdefault(run_id, {})
    if not isinstance(row, dict):
        row = {}
        runs[run_id] = row

    if status is not None:
        row["status"] = str(status)
    if stage is not None:
        row["stage"] = str(stage)
    if created_at is not None:
        row["created_at"] = created_at
    if updated_at is not None:
        row["updated_at"] = updated_at
    row["artifacts"] = _artifact_flags(run_id)
    save_runs_index(payload)


def get_latest_run_id_from_index() -> str | None:
    """Return latest run id from index payload."""
    payload = load_runs_index()
    latest = payload.get("latest_run_id")
    return str(latest) if latest else None


def get_latest_training_run_id_from_index() -> str | None:
    """Return latest completed training run id from index payload."""
    payload = load_runs_index()
    latest = payload.get("latest_training_run_id")
    return str(latest) if latest else None


def list_latest_runs_from_index(limit: int = 10) -> list[dict[str, Any]]:
    """Return latest run rows from index payload."""
    payload = load_runs_index()
    runs = payload.get("runs", {})
    if not isinstance(runs, dict):
        return []
    rows = [
        {
            "run_id": str(run_id),
            "status": str(row.get("status", "unknown")),
            "stage": str(row.get("stage", "")),
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
        }
        for run_id, row in runs.items()
        if isinstance(row, dict)
    ]
    rows.sort(
        key=lambda item: str(item.get("updated_at") or item.get("created_at") or ""),
        reverse=True,
    )
    return rows[: max(1, int(limit))]
