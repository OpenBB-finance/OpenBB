"""Version metadata registry for raw/feature stores."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import threading
from typing import Any

import pandas as pd

from openbb_quant_ml.service.constants import (
    DATA_VERSION_PATH,
    FEATURE_VERSION_PATH,
    FEATURE_STORE_DIR,
    RAW_STORE_DIR,
    VERSIONS_DIR,
)
from openbb_quant_ml.service.storage import utc_now_iso

_REGISTRY_LOCK = threading.RLock()


def _ensure_paths() -> None:
    RAW_STORE_DIR.mkdir(parents=True, exist_ok=True)
    FEATURE_STORE_DIR.mkdir(parents=True, exist_ok=True)
    VERSIONS_DIR.mkdir(parents=True, exist_ok=True)


def _read_json(path: Path, default: dict[str, Any]) -> dict[str, Any]:
    if not path.exists():
        return default
    try:
        with path.open(encoding="utf-8") as file:
            payload = json.load(file)
    except (OSError, json.JSONDecodeError):
        return default
    if isinstance(payload, dict):
        return payload
    return default


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)


def _hash_frame(frame: pd.DataFrame, columns: list[str]) -> str:
    if frame.empty:
        return "empty"
    available = [col for col in columns if col in frame.columns]
    if not available:
        return "na"
    sample = frame[available].tail(min(len(frame), 500)).copy()
    sample = sample.replace([pd.NA], float("nan"))
    data = sample.to_csv(index=False).encode("utf-8", errors="ignore")
    return hashlib.sha256(data).hexdigest()[:16]


def compute_params_hash(payload: dict[str, Any]) -> str:
    serialized = json.dumps(payload, sort_keys=True, ensure_ascii=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]


def update_data_version(symbol: str, frame: pd.DataFrame, source: str = "yfinance") -> None:
    with _REGISTRY_LOCK:
        _ensure_paths()
        payload = _read_json(DATA_VERSION_PATH, {"symbols": {}, "updated_at": utc_now_iso()})
        symbols = payload.setdefault("symbols", {})
        last_date = None
        if not frame.empty and "date" in frame.columns:
            last_date = pd.Timestamp(pd.to_datetime(frame["date"]).max()).date().isoformat()
        symbols[str(symbol)] = {
            "symbol": str(symbol),
            "last_date": last_date,
            "rows": int(len(frame)),
            "source": source,
            "checksum": _hash_frame(frame, ["date", "open", "high", "low", "close", "volume"]),
            "updated_at": utc_now_iso(),
        }
        payload["updated_at"] = utc_now_iso()
        _write_json(DATA_VERSION_PATH, payload)


def update_feature_version(
    symbol: str,
    feature_set_id: str,
    params_hash: str,
    frame: pd.DataFrame,
) -> None:
    with _REGISTRY_LOCK:
        _ensure_paths()
        payload = _read_json(FEATURE_VERSION_PATH, {"features": {}, "updated_at": utc_now_iso()})
        features = payload.setdefault("features", {})
        key = f"{feature_set_id}:{symbol}"
        last_date = None
        if not frame.empty and "date" in frame.columns:
            last_date = pd.Timestamp(pd.to_datetime(frame["date"]).max()).date().isoformat()
        features[key] = {
            "symbol": str(symbol),
            "feature_set_id": str(feature_set_id),
            "params_hash": str(params_hash),
            "last_date": last_date,
            "rows": int(len(frame)),
            "checksum": _hash_frame(frame, ["date", "symbol", "target_return"]),
            "updated_at": utc_now_iso(),
        }
        payload["updated_at"] = utc_now_iso()
        _write_json(FEATURE_VERSION_PATH, payload)


def get_data_versions() -> dict[str, Any]:
    _ensure_paths()
    return _read_json(DATA_VERSION_PATH, {"symbols": {}, "updated_at": utc_now_iso()})


def get_feature_versions() -> dict[str, Any]:
    _ensure_paths()
    return _read_json(FEATURE_VERSION_PATH, {"features": {}, "updated_at": utc_now_iso()})


def get_feature_version(symbol: str, feature_set_id: str) -> dict[str, Any] | None:
    payload = get_feature_versions()
    key = f"{feature_set_id}:{symbol}"
    row = payload.get("features", {}).get(key)
    if isinstance(row, dict):
        return row
    return None
