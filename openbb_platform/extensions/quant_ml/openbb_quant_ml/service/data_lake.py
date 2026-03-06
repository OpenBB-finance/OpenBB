"""Parquet lake helpers for bronze/silver/gold datasets."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd

from openbb_quant_ml.service.constants import (
    LAKE_BRONZE_DIR,
    LAKE_GOLD_DIR,
    LAKE_SILVER_DIR,
)
from openbb_quant_ml.service.storage import save_json, save_parquet_atomic, utc_now_iso

_LAYER_DIRS = {
    "bronze": LAKE_BRONZE_DIR,
    "silver": LAKE_SILVER_DIR,
    "gold": LAKE_GOLD_DIR,
}


def _safe_token(value: str) -> str:
    return "".join(
        ch if ch.isalnum() or ch in {"_", "-", "="} else "_" for ch in str(value).strip()
    )


def _frame_signature(frame: pd.DataFrame) -> str:
    if frame.empty:
        return "empty"
    sample = frame.tail(min(len(frame), 500)).copy()
    sample.columns = [str(col) for col in sample.columns]
    payload = sample.to_csv(index=False).encode("utf-8", errors="ignore")
    return hashlib.sha256(payload).hexdigest()[:16]


def _frame_profile(frame: pd.DataFrame) -> dict[str, Any]:
    numeric = frame.select_dtypes(include=["number"]).replace([pd.NA], float("nan"))
    profile: dict[str, Any] = {
        "rows": int(len(frame)),
        "columns": [str(col) for col in frame.columns],
        "numeric_summary": {},
    }
    for column in numeric.columns:
        series = pd.to_numeric(numeric[column], errors="coerce")
        if series.empty:
            continue
        profile["numeric_summary"][str(column)] = {
            "mean": None if series.dropna().empty else float(series.mean()),
            "std": None if series.dropna().empty else float(series.std(ddof=0) or 0.0),
            "missing_ratio": float(series.isna().mean()),
        }
    return profile


def compute_dataset_version(
    frame: pd.DataFrame,
    *,
    dataset: str,
    as_of_date: str,
    source: str | None = None,
) -> str:
    """Return stable dataset version token for one frame snapshot."""
    base = {
        "dataset": str(dataset),
        "as_of_date": str(as_of_date),
        "source": str(source or ""),
        "signature": _frame_signature(frame),
        "rows": int(len(frame)),
        "columns": [str(col) for col in frame.columns],
    }
    encoded = json.dumps(base, ensure_ascii=True, sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()[:16]


def get_layer_dir(layer: str) -> Path:
    """Return the configured directory for one lake layer."""
    normalized = str(layer or "").strip().lower()
    if normalized not in _LAYER_DIRS:
        raise ValueError(f"Unsupported lake layer: {layer}")
    return _LAYER_DIRS[normalized]


def write_lake_dataset(
    *,
    layer: str,
    dataset: str,
    frame: pd.DataFrame,
    as_of_date: str,
    version: str | None = None,
    source: str | None = None,
    run_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Write one snapshot under the canonical parquet lake."""
    layer_dir = get_layer_dir(layer)
    dataset_token = _safe_token(dataset)
    as_of_token = _safe_token(as_of_date)
    resolved_version = str(version or compute_dataset_version(frame, dataset=dataset, as_of_date=as_of_date, source=source))
    snapshot_dir = (
        layer_dir
        / f"dataset={dataset_token}"
        / f"as_of_date={as_of_token}"
        / f"version={_safe_token(resolved_version)}"
    )
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    data_path = snapshot_dir / "data.parquet"
    meta_path = snapshot_dir / "meta.json"
    latest_meta_path = layer_dir / f"dataset={dataset_token}" / "_latest.json"
    save_parquet_atomic(data_path, frame, index=False)
    payload = {
        "layer": str(layer).lower(),
        "dataset": dataset_token,
        "as_of_date": as_of_date,
        "version": resolved_version,
        "source": source,
        "run_id": run_id,
        "path": str(data_path),
        "created_at_utc": utc_now_iso(),
        "profile": _frame_profile(frame),
        "metadata": metadata or {},
    }
    save_json(meta_path, payload)
    save_json(latest_meta_path, payload)
    return payload


def load_latest_lake_meta(layer: str, dataset: str) -> dict[str, Any]:
    """Load the latest snapshot metadata for one layer+dataset."""
    layer_dir = get_layer_dir(layer)
    dataset_token = _safe_token(dataset)
    latest_meta_path = layer_dir / f"dataset={dataset_token}" / "_latest.json"
    if not latest_meta_path.exists():
        return {}
    try:
        payload = json.loads(latest_meta_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def load_previous_lake_meta(
    layer: str,
    dataset: str,
    *,
    exclude_version: str | None = None,
) -> dict[str, Any]:
    """Return the most recent lake meta that is not the current version."""
    layer_dir = get_layer_dir(layer)
    dataset_token = _safe_token(dataset)
    base_dir = layer_dir / f"dataset={dataset_token}"
    if not base_dir.exists():
        return {}
    rows: list[tuple[str, dict[str, Any]]] = []
    for meta_path in base_dir.glob("as_of_date=*/version=*/meta.json"):
        try:
            payload = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(payload, dict):
            continue
        version = str(payload.get("version", "")).strip()
        if exclude_version and version == exclude_version:
            continue
        created_at = str(payload.get("created_at_utc", "")).strip()
        rows.append((created_at, payload))
    rows.sort(key=lambda item: item[0], reverse=True)
    return rows[0][1] if rows else {}
