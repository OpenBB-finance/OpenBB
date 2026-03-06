"""Runtime promoted-model pointer helpers."""

from __future__ import annotations

import hashlib
from datetime import UTC, datetime
from typing import Any

import pandas as pd

from openbb_quant_ml.models import ModelName, PromotedModelResponse
from openbb_quant_ml.service.constants import PROMOTED_MODEL_PATH
from openbb_quant_ml.service.registry.run_registry_db import (
    get_model_alias,
    insert_promotion_event,
    list_model_versions,
    upsert_model_alias,
)
from openbb_quant_ml.service.signal_schema import infer_model_version
from openbb_quant_ml.service.storage import get_run_dir, load_json, save_json

_SUPPORTED_MODELS: tuple[ModelName, ...] = ("xgb_lstm", "lgbm_ranker")


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _normalize_model_name(model_name: str | None) -> ModelName:
    if model_name in _SUPPORTED_MODELS:
        return model_name
    return "lgbm_ranker"


def _prediction_paths(run_dir, model_name: ModelName) -> list:
    paths = [run_dir / f"predictions_{model_name}.parquet"]
    if model_name == "lgbm_ranker":
        paths.append(run_dir / "predictions.parquet")
    return paths


def _load_feature_hash(run_dir, model_name: ModelName) -> str | None:
    if model_name != "lgbm_ranker":
        return None
    meta = load_json(run_dir / "model_lgbm_ranker_meta.json", default={})
    if not isinstance(meta, dict):
        return None
    feature_columns = meta.get("feature_columns", [])
    if not isinstance(feature_columns, list):
        return None
    normalized = "|".join(
        str(item).strip() for item in feature_columns if str(item).strip()
    )
    if not normalized:
        return None
    return hashlib.sha1(normalized.encode("utf-8")).hexdigest()[:12]


def _load_as_of_date(run_dir, model_name: ModelName) -> str | None:
    infer_payload = load_json(run_dir / "inference_latest.json", default={})
    if isinstance(infer_payload, dict):
        as_of_date = str(infer_payload.get("as_of_date", "")).strip()
        if as_of_date:
            return as_of_date

    for path in _prediction_paths(run_dir, model_name):
        if not path.exists():
            continue
        frame = pd.read_parquet(path, columns=["date"])
        if frame.empty:
            continue
        latest = pd.Timestamp(pd.to_datetime(frame["date"]).max()).date().isoformat()
        return latest
    return None


def _has_required_artifacts(run_id: str, model_name: ModelName) -> bool:
    run_dir = get_run_dir(run_id)
    if not run_dir.exists():
        return False
    contract = load_json(
        run_dir / "artifacts" / "artifact_contract.json", default={}
    )
    if isinstance(contract, dict) and bool(contract.get("required_artifacts_ready", False)):
        return True
    has_predictions = any(
        path.exists() for path in _prediction_paths(run_dir, model_name)
    )
    if not has_predictions:
        return False
    if model_name == "lgbm_ranker":
        return (run_dir / "model_lgbm_ranker.pkl").exists() and (
            run_dir / "model_lgbm_ranker_meta.json"
        ).exists()
    return (run_dir / "model_xgb_xgb_lstm.json").exists()


def _latest_completed_run_id(model_name: ModelName) -> str | None:
    from openbb_quant_ml.service.storage import read_registry

    registry = read_registry()
    runs = registry.get("runs", {})
    if not isinstance(runs, dict):
        return None
    rows: list[tuple[str, str]] = []
    for run_id, payload in runs.items():
        if not isinstance(payload, dict):
            continue
        if str(payload.get("status", "")).lower() != "completed":
            continue
        updated = str(payload.get("updated_at") or payload.get("created_at") or "")
        rows.append((updated, str(run_id)))
    rows.sort(key=lambda item: item[0], reverse=True)
    for _, run_id in rows:
        if _has_required_artifacts(run_id, model_name):
            return run_id
    return None


def load_promoted_model_payload() -> dict[str, Any]:
    """Read persisted promoted model pointer payload."""
    payload = load_json(PROMOTED_MODEL_PATH, default={})
    return payload if isinstance(payload, dict) else {}


def set_promoted_model_pointer(
    *,
    run_id: str,
    model_name: str = "lgbm_ranker",
    as_of_date: str | None = None,
    feature_hash: str | None = None,
    source: str = "promote_candidate",
) -> dict[str, Any]:
    """Persist promoted model pointer payload."""
    normalized_model = _normalize_model_name(model_name)
    run_dir = get_run_dir(run_id)
    resolved_as_of = as_of_date or _load_as_of_date(run_dir, normalized_model)
    resolved_hash = feature_hash or _load_feature_hash(run_dir, normalized_model)
    payload = {
        "run_id": run_id,
        "model_name": normalized_model,
        "as_of_date": resolved_as_of,
        "feature_hash": resolved_hash,
        "model_version": None,
        "dataset_version": None,
        "feature_set_version": None,
        "metrics": {},
        "updated_at": _now_iso(),
        "source": source,
        "ready": _has_required_artifacts(run_id, normalized_model),
    }
    model_version = None
    dataset_version = None
    feature_set_version = None
    metrics = {}
    for row in list_model_versions(model_name=normalized_model, limit=200):
        if str(row.get("run_id", "")) != run_id:
            continue
        model_version = str(row.get("model_version", "")).strip() or None
        dataset_version = (
            str(row.get("dataset_version", "")).strip() or None
        )
        feature_set_version = (
            str(row.get("feature_set_version", "")).strip() or None
        )
        metrics_raw = row.get("metrics_json")
        metrics = metrics_raw if isinstance(metrics_raw, dict) else {}
        break
    if model_version is None:
        metrics_payload = load_json(
            get_run_dir(run_id) / f"metrics_{normalized_model}.json",
            default={},
        )
        if isinstance(metrics_payload, dict):
            model_version = infer_model_version(metrics_payload)
            metrics = (
                metrics_payload.get("metrics", {})
                if isinstance(metrics_payload.get("metrics"), dict)
                else {}
            )
    payload["model_version"] = model_version
    payload["dataset_version"] = dataset_version
    payload["feature_set_version"] = feature_set_version
    payload["metrics"] = metrics
    save_json(PROMOTED_MODEL_PATH, payload)
    previous = get_model_alias("champion")
    upsert_model_alias(
        alias="champion",
        run_id=run_id,
        model_name=normalized_model,
        model_version=model_version,
        source=source,
        updated_at_utc=str(payload["updated_at"]),
    )
    insert_promotion_event(
        run_id=run_id,
        model_name=normalized_model,
        previous_run_id=(
            str(previous.get("run_id")) if isinstance(previous, dict) else None
        ),
        previous_model_version=(
            str(previous.get("model_version"))
            if isinstance(previous, dict) and previous.get("model_version") is not None
            else None
        ),
        new_model_version=model_version,
        summary_json={"source": source},
        created_at_utc=str(payload["updated_at"]),
    )
    return payload


def get_promoted_model(model_name: str | None = None) -> dict[str, Any]:
    """Resolve promoted model pointer with registry fallback."""
    normalized_model = _normalize_model_name(model_name)
    pointer = load_promoted_model_payload()
    pointer_run_id = str(pointer.get("run_id", "")).strip()
    alias_row = get_model_alias("champion")
    if isinstance(alias_row, dict) and alias_row:
        alias_run_id = str(alias_row.get("run_id", "")).strip()
        if (
            pointer_run_id
            and pointer_run_id == alias_run_id
            and _has_required_artifacts(pointer_run_id, normalized_model)
        ):
            run_dir = get_run_dir(pointer_run_id)
            return {
                "run_id": pointer_run_id,
                "model_name": normalized_model,
                "as_of_date": pointer.get("as_of_date")
                or _load_as_of_date(run_dir, normalized_model),
                "feature_hash": pointer.get("feature_hash")
                or _load_feature_hash(run_dir, normalized_model),
                "updated_at": pointer.get("updated_at") or _now_iso(),
                "source": "runtime_pointer",
                "ready": True,
                "alias": "champion",
                "model_version": pointer.get("model_version"),
                "dataset_version": pointer.get("dataset_version"),
                "feature_set_version": pointer.get("feature_set_version"),
                "metrics": pointer.get("metrics", {}),
            }
        if alias_run_id and _has_required_artifacts(alias_run_id, normalized_model):
            run_dir = get_run_dir(alias_run_id)
            return {
                "run_id": alias_run_id,
                "model_name": normalized_model,
                "as_of_date": _load_as_of_date(run_dir, normalized_model),
                "feature_hash": _load_feature_hash(run_dir, normalized_model),
                "updated_at": str(alias_row.get("updated_at_utc") or _now_iso()),
                "source": str(alias_row.get("source") or "model_registry"),
                "ready": True,
                "alias": "champion",
                "model_version": (
                    str(alias_row.get("model_version"))
                    if alias_row.get("model_version") is not None
                    else None
                ),
                "dataset_version": None,
                "feature_set_version": None,
                "metrics": {},
            }

    if pointer_run_id and _has_required_artifacts(pointer_run_id, normalized_model):
        run_dir = get_run_dir(pointer_run_id)
        return {
            "run_id": pointer_run_id,
            "model_name": normalized_model,
            "as_of_date": pointer.get("as_of_date")
            or _load_as_of_date(run_dir, normalized_model),
            "feature_hash": pointer.get("feature_hash")
            or _load_feature_hash(run_dir, normalized_model),
            "updated_at": pointer.get("updated_at") or _now_iso(),
            "source": "runtime_pointer",
            "ready": True,
            "alias": "champion",
            "model_version": pointer.get("model_version"),
            "dataset_version": pointer.get("dataset_version"),
            "feature_set_version": pointer.get("feature_set_version"),
            "metrics": pointer.get("metrics", {}),
        }

    fallback_run_id = _latest_completed_run_id(normalized_model)
    if fallback_run_id:
        run_dir = get_run_dir(fallback_run_id)
        return {
            "run_id": fallback_run_id,
            "model_name": normalized_model,
            "as_of_date": _load_as_of_date(run_dir, normalized_model),
            "feature_hash": _load_feature_hash(run_dir, normalized_model),
            "updated_at": _now_iso(),
            "source": "fallback_registry",
            "ready": True,
            "alias": "champion",
            "model_version": None,
            "dataset_version": None,
            "feature_set_version": None,
            "metrics": {},
        }

    return {
        "run_id": None,
        "model_name": normalized_model,
        "as_of_date": None,
        "feature_hash": None,
        "updated_at": _now_iso(),
        "source": "fallback_registry",
        "ready": False,
        "alias": "champion",
        "model_version": None,
        "dataset_version": None,
        "feature_set_version": None,
        "metrics": {},
    }


def get_promoted_run_id(model_name: str | None = None) -> str | None:
    """Resolve promoted run id only."""
    payload = get_promoted_model(model_name=model_name)
    run_id = payload.get("run_id")
    return str(run_id) if run_id else None


def get_promoted_model_response(model_name: str | None = None) -> PromotedModelResponse:
    """Return typed promoted model payload."""
    return PromotedModelResponse(**get_promoted_model(model_name=model_name))
