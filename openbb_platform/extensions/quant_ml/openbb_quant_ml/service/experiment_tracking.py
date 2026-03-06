"""Experiment registry helpers for quant ML runs."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from openbb_quant_ml.models import ExperimentListResponse, ExperimentRunItemResponse
from openbb_quant_ml.service.registry.run_registry_db import (
    get_experiment_run,
    list_experiment_runs,
    upsert_experiment_run,
)


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _parse_json(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    if isinstance(value, str) and value.strip():
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, dict) else {}
    return {}


def register_experiment_run(
    *,
    run_id: str,
    model_type: str | None,
    dataset_version: str | None,
    feature_set_version: str | None,
    hyperparameters: dict[str, Any] | None,
    feature_set: dict[str, Any] | None,
    performance: dict[str, Any] | None,
    artifact_uri: str | None,
    status: str,
) -> None:
    """Insert or update one experiment row."""
    existing = get_experiment_run(run_id)
    created_at = (
        str(existing.get("created_at_utc"))
        if isinstance(existing, dict) and existing.get("created_at_utc")
        else _now_iso()
    )
    upsert_experiment_run(
        run_id=run_id,
        model_type=model_type,
        dataset_version=dataset_version,
        feature_set_version=feature_set_version,
        hyperparameters_json=hyperparameters,
        feature_set_json=feature_set,
        performance_json=performance,
        artifact_uri=artifact_uri,
        status=status,
        created_at_utc=created_at,
        updated_at_utc=_now_iso(),
    )


def _row_to_response(row: dict[str, Any]) -> ExperimentRunItemResponse:
    return ExperimentRunItemResponse(
        run_id=str(row.get("run_id", "")),
        model_type=(
            str(row.get("model_type")) if row.get("model_type") is not None else None
        ),
        dataset_version=(
            str(row.get("dataset_version"))
            if row.get("dataset_version") is not None
            else None
        ),
        feature_set_version=(
            str(row.get("feature_set_version"))
            if row.get("feature_set_version") is not None
            else None
        ),
        hyperparameters=_parse_json(row.get("hyperparameters_json")),
        feature_set=_parse_json(row.get("feature_set_json")),
        performance=_parse_json(row.get("performance_json")),
        artifact_uri=(
            str(row.get("artifact_uri")) if row.get("artifact_uri") is not None else None
        ),
        status=str(row.get("status")) if row.get("status") is not None else None,
        created_at=(
            str(row.get("created_at_utc")) if row.get("created_at_utc") else None
        ),
        updated_at=(
            str(row.get("updated_at_utc")) if row.get("updated_at_utc") else None
        ),
    )


def get_experiment_detail_response(run_id: str) -> ExperimentRunItemResponse:
    """Return one experiment row."""
    row = get_experiment_run(run_id)
    if not row:
        return ExperimentRunItemResponse(run_id=run_id)
    return _row_to_response(row)


def get_experiment_list_response(*, limit: int = 50) -> ExperimentListResponse:
    """Return recent experiment rows."""
    rows = list_experiment_runs(limit=limit)
    return ExperimentListResponse(items=[_row_to_response(row) for row in rows])
