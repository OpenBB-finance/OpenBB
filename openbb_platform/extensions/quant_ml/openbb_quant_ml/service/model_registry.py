"""Champion/challenger model registry helpers."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from openbb_quant_ml.models import (
    ModelRegistryEntryResponse,
    ModelRegistryHistoryResponse,
)
from openbb_quant_ml.service.registry.run_registry_db import (
    get_model_alias,
    insert_model_version,
    insert_promotion_event,
    list_model_aliases,
    list_model_versions,
    upsert_model_alias,
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


def register_model_version(
    *,
    run_id: str,
    model_name: str,
    model_version: str,
    stage: str,
    artifact_uri: str | None,
    dataset_version: str | None,
    feature_set_version: str | None,
    metrics: dict[str, Any] | None,
    alias: str | None = None,
    source: str = "training",
) -> None:
    """Register one model artifact version."""
    insert_model_version(
        run_id=run_id,
        model_name=model_name,
        model_version=model_version,
        stage=stage,
        artifact_uri=artifact_uri,
        dataset_version=dataset_version,
        feature_set_version=feature_set_version,
        metrics_json=metrics,
        created_at_utc=_now_iso(),
    )
    if alias:
        upsert_model_alias(
            alias=alias,
            run_id=run_id,
            model_name=model_name,
            model_version=model_version,
            source=source,
            updated_at_utc=_now_iso(),
        )


def promote_model_version(
    *,
    run_id: str,
    model_name: str,
    model_version: str,
    summary: dict[str, Any] | None = None,
    source: str = "evaluation_gate",
) -> None:
    """Promote one registered model to the champion alias."""
    previous = get_model_alias("champion")
    upsert_model_alias(
        alias="champion",
        run_id=run_id,
        model_name=model_name,
        model_version=model_version,
        source=source,
        updated_at_utc=_now_iso(),
    )
    insert_promotion_event(
        run_id=run_id,
        model_name=model_name,
        previous_run_id=(
            str(previous.get("run_id")) if isinstance(previous, dict) else None
        ),
        previous_model_version=(
            str(previous.get("model_version"))
            if isinstance(previous, dict) and previous.get("model_version") is not None
            else None
        ),
        new_model_version=model_version,
        summary_json=summary or {},
        created_at_utc=_now_iso(),
    )


def _latest_version_for_run(
    run_id: str, model_name: str | None = None
) -> dict[str, Any] | None:
    rows = list_model_versions(model_name=model_name, limit=200)
    for row in rows:
        if str(row.get("run_id")) == str(run_id):
            return row
    return None


def _row_to_response(row: dict[str, Any], *, alias: str) -> ModelRegistryEntryResponse:
    return ModelRegistryEntryResponse(
        alias=alias,
        run_id=str(row.get("run_id")) if row.get("run_id") is not None else None,
        model_name=(
            str(row.get("model_name")) if row.get("model_name") is not None else None
        ),
        model_version=(
            str(row.get("model_version"))
            if row.get("model_version") is not None
            else None
        ),
        stage=str(row.get("stage")) if row.get("stage") is not None else None,
        artifact_uri=(
            str(row.get("artifact_uri")) if row.get("artifact_uri") is not None else None
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
        metrics=_parse_json(row.get("metrics_json")),
        source=str(row.get("source")) if row.get("source") is not None else None,
        updated_at=(
            str(row.get("updated_at_utc"))
            if row.get("updated_at_utc")
            else str(row.get("created_at_utc")) if row.get("created_at_utc") else None
        ),
    )


def get_model_registry_entry_response(
    alias: str, *, model_name: str | None = None
) -> ModelRegistryEntryResponse:
    """Return champion or challenger alias metadata."""
    row = get_model_alias(alias)
    if isinstance(row, dict) and row:
        latest = _latest_version_for_run(str(row.get("run_id", "")), model_name=model_name)
        merged = dict(row)
        if isinstance(latest, dict):
            merged.update(latest)
        return _row_to_response(merged, alias=alias)
    if alias == "challenger":
        latest_rows = list_model_versions(model_name=model_name, limit=1)
        if latest_rows:
            return _row_to_response(latest_rows[0], alias=alias)
    if alias == "champion":
        try:
            from openbb_quant_ml.service.runtime_pointer import get_promoted_model_response

            promoted = get_promoted_model_response(model_name=model_name)
            return ModelRegistryEntryResponse(
                alias=alias,
                run_id=promoted.run_id,
                model_name=promoted.model_name,
                model_version=promoted.model_version,
                dataset_version=promoted.dataset_version,
                feature_set_version=promoted.feature_set_version,
                metrics=promoted.metrics,
                source=promoted.source,
                updated_at=promoted.updated_at,
            )
        except Exception:
            pass
    return ModelRegistryEntryResponse(alias=alias, model_name=model_name)


def get_model_registry_history_response(
    *, model_name: str | None = None, limit: int = 50
) -> ModelRegistryHistoryResponse:
    """Return model version history."""
    rows = list_model_versions(model_name=model_name, limit=limit)
    alias_rows = {
        str(item.get("run_id")): str(item.get("alias"))
        for item in list_model_aliases(limit=50)
    }
    items = []
    for row in rows:
        alias = alias_rows.get(str(row.get("run_id")), str(row.get("stage", "version")))
        items.append(_row_to_response(row, alias=alias))
    return ModelRegistryHistoryResponse(items=items)
