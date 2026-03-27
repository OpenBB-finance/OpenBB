"""Experiment registry helpers for quant ML runs."""

from __future__ import annotations

import importlib
import json
import logging
import os
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from openbb_quant_ml.models import ExperimentListResponse, ExperimentRunItemResponse
from openbb_quant_ml.service.registry.run_registry_db import (
    get_experiment_run,
    get_model_alias,
    list_experiment_runs,
    upsert_experiment_run,
)

LOGGER = logging.getLogger(__name__)
_MLFLOW_IMPORT_WARNING_EMITTED = False
_MLFLOW_DEFAULT_EXPERIMENT_NAME = "openbb-quant-ml"


@dataclass(frozen=True)
class MlflowTrackingConfig:
    experiment_name: str
    tracking_uri: str | None = None


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


def _is_truthy_env(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _get_mlflow_tracking_config() -> MlflowTrackingConfig | None:
    enabled_raw = str(os.getenv("OPENBB_QUANT_ML_MLFLOW_ENABLED", "")).strip()
    tracking_uri = (
        str(os.getenv("OPENBB_QUANT_ML_MLFLOW_TRACKING_URI", "")).strip()
        or str(os.getenv("MLFLOW_TRACKING_URI", "")).strip()
        or None
    )
    experiment_name = (
        str(os.getenv("OPENBB_QUANT_ML_MLFLOW_EXPERIMENT_NAME", "")).strip()
        or str(os.getenv("MLFLOW_EXPERIMENT_NAME", "")).strip()
        or _MLFLOW_DEFAULT_EXPERIMENT_NAME
    )
    if enabled_raw and not _is_truthy_env(enabled_raw):
        return None
    if not enabled_raw and not tracking_uri:
        return None
    return MlflowTrackingConfig(
        experiment_name=experiment_name,
        tracking_uri=tracking_uri,
    )


def _load_mlflow_module() -> Any | None:
    global _MLFLOW_IMPORT_WARNING_EMITTED
    try:
        return importlib.import_module("mlflow")
    except ModuleNotFoundError:
        if not _MLFLOW_IMPORT_WARNING_EMITTED:
            LOGGER.warning(
                "MLflow tracking is configured but the 'mlflow' package is not installed. "
                "SQLite experiment tracking will continue without MLflow sync."
            )
            _MLFLOW_IMPORT_WARNING_EMITTED = True
        return None


def _sanitize_mlflow_key(prefix: str, key: str) -> str:
    cleaned_key = re.sub(r"[^0-9A-Za-z_.-]+", "_", str(key).strip()) or "value"
    if prefix:
        return f"{prefix}.{cleaned_key}"
    return cleaned_key


def _collect_mlflow_params(payload: Any, *, prefix: str = "") -> dict[str, str]:
    params: dict[str, str] = {}
    if payload is None:
        return params
    if isinstance(payload, dict):
        for key in sorted(payload):
            params.update(
                _collect_mlflow_params(
                    payload[key],
                    prefix=_sanitize_mlflow_key(prefix, str(key)),
                )
            )
        return params
    if isinstance(payload, (list, tuple)):
        if prefix:
            params[prefix] = json.dumps(payload, sort_keys=True, default=str)
        return params
    if prefix:
        params[prefix] = str(payload)
    return params


def _collect_mlflow_metrics(payload: Any, *, prefix: str = "") -> dict[str, float]:
    metrics: dict[str, float] = {}
    if payload is None:
        return metrics
    if isinstance(payload, dict):
        for key in sorted(payload):
            metrics.update(
                _collect_mlflow_metrics(
                    payload[key],
                    prefix=_sanitize_mlflow_key(prefix, str(key)),
                )
            )
        return metrics
    if isinstance(payload, (list, tuple)):
        for index, item in enumerate(payload):
            metrics.update(
                _collect_mlflow_metrics(
                    item,
                    prefix=_sanitize_mlflow_key(prefix, str(index)),
                )
            )
        return metrics
    if isinstance(payload, bool):
        return metrics
    if isinstance(payload, (int, float)) and prefix:
        metrics[prefix] = float(payload)
    return metrics


def _get_or_create_mlflow_experiment(client: Any, experiment_name: str) -> str:
    experiment = client.get_experiment_by_name(experiment_name)
    if experiment is not None:
        return str(experiment.experiment_id)
    try:
        return str(client.create_experiment(experiment_name))
    except Exception:
        experiment = client.get_experiment_by_name(experiment_name)
        if experiment is None:
            raise
        return str(experiment.experiment_id)


def _get_or_create_mlflow_run(
    client: Any,
    *,
    experiment_id: str,
    run_id: str,
    model_type: str | None,
    status: str,
    artifact_uri: str | None,
) -> tuple[str, bool]:
    safe_run_id = str(run_id).replace("'", "")
    filter_string = f"tags.openbb_run_id = '{safe_run_id}'"
    for run in client.search_runs(
        experiment_ids=[experiment_id],
        filter_string=filter_string,
        max_results=1,
    ):
        return str(run.info.run_id), False
    created = client.create_run(
        experiment_id=experiment_id,
        tags={
            "mlflow.runName": run_id,
            "openbb_run_id": run_id,
            "status": status,
            "model_type": str(model_type or ""),
            "artifact_uri": str(artifact_uri or ""),
        },
    )
    return str(created.info.run_id), True


def _mlflow_terminal_status(status: str) -> str | None:
    normalized = str(status or "").strip().lower()
    if normalized == "completed":
        return "FINISHED"
    if normalized == "failed":
        return "FAILED"
    if normalized in {"cancelled", "canceled"}:
        return "KILLED"
    return None


def _sync_mlflow_experiment_run(
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
    config = _get_mlflow_tracking_config()
    if config is None:
        return
    mlflow = _load_mlflow_module()
    if mlflow is None:
        return
    try:
        client = (
            mlflow.tracking.MlflowClient(tracking_uri=config.tracking_uri)
            if config.tracking_uri
            else mlflow.tracking.MlflowClient()
        )
        experiment_id = _get_or_create_mlflow_experiment(
            client, config.experiment_name
        )
        mlflow_run_id, is_new_run = _get_or_create_mlflow_run(
            client,
            experiment_id=experiment_id,
            run_id=run_id,
            model_type=model_type,
            status=status,
            artifact_uri=artifact_uri,
        )
        if is_new_run:
            params = {
                "model_type": str(model_type or ""),
                "dataset_version": str(dataset_version or ""),
                "feature_set_version": str(feature_set_version or ""),
            }
            params.update(
                _collect_mlflow_params(hyperparameters, prefix="hyperparameters")
            )
            params.update(_collect_mlflow_params(feature_set, prefix="feature_set"))
            for key, value in params.items():
                client.log_param(mlflow_run_id, key, value)
        for key, value in _collect_mlflow_metrics(
            performance, prefix="performance"
        ).items():
            client.log_metric(mlflow_run_id, key, value)
        client.set_tag(mlflow_run_id, "status", status)
        if artifact_uri:
            client.set_tag(mlflow_run_id, "artifact_uri", artifact_uri)
        terminal_status = _mlflow_terminal_status(status)
        if terminal_status is not None:
            client.set_terminated(mlflow_run_id, status=terminal_status)
    except Exception:
        LOGGER.warning(
            "MLflow sync failed for experiment run %s.",
            run_id,
            exc_info=True,
        )


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
    _sync_mlflow_experiment_run(
        run_id=run_id,
        model_type=model_type,
        dataset_version=dataset_version,
        feature_set_version=feature_set_version,
        hyperparameters=hyperparameters,
        feature_set=feature_set,
        performance=performance,
        artifact_uri=artifact_uri,
        status=status,
    )


def _row_to_response(row: dict[str, Any]) -> ExperimentRunItemResponse:
    hyperparameters = _parse_json(row.get("hyperparameters_json"))
    feature_set = _parse_json(row.get("feature_set_json"))
    performance = _parse_json(row.get("performance_json"))
    macro_study_links = feature_set.get("macro_study_links", [])
    if not isinstance(macro_study_links, list):
        macro_study_links = []
    train_start = (
        feature_set.get("train_start")
        or hyperparameters.get("train_start")
        or hyperparameters.get("start_date")
    )
    train_end = (
        feature_set.get("train_end")
        or hyperparameters.get("train_end")
        or hyperparameters.get("end_date")
    )
    training_window = None
    if train_start and train_end:
        training_window = f"{train_start} -> {train_end}"
    champion = get_model_alias("champion") or {}
    challenger = get_model_alias("challenger") or {}
    promotion_state = "candidate"
    run_id = str(row.get("run_id", ""))
    if str(champion.get("run_id", "")) == run_id:
        promotion_state = "champion"
    elif str(challenger.get("run_id", "")) == run_id:
        promotion_state = "challenger"
    return ExperimentRunItemResponse(
        run_id=run_id,
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
        hyperparameters=hyperparameters,
        feature_set=feature_set,
        performance=performance,
        artifact_uri=(
            str(row.get("artifact_uri")) if row.get("artifact_uri") is not None else None
        ),
        status=str(row.get("status")) if row.get("status") is not None else None,
        macro_study_links=[str(item) for item in macro_study_links if str(item).strip()],
        as_of_policy=(
            str(feature_set.get("as_of_policy"))
            if feature_set.get("as_of_policy") is not None
            else None
        ),
        training_window=training_window,
        constraints_summary=(
            performance.get("constraints_summary")
            if isinstance(performance.get("constraints_summary"), dict)
            else {}
        ),
        promotion_state=promotion_state,
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
