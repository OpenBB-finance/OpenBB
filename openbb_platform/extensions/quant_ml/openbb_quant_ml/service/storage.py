"""Storage helpers for Quant ML artifacts and registry."""

from __future__ import annotations

import json
import os
from datetime import UTC, datetime
from pathlib import Path
from threading import RLock
from typing import Any
from uuid import uuid4

import pandas as pd

from openbb_quant_ml.service.constants import (
    ARTIFACT_ROOT,
    CACHE_DIR,
    INDEX_DIR,
    REGISTRY_PATH,
    RUNTIME_DIR,
    RUNS_DIR,
    WALKFORWARD_DIR,
)

_REGISTRY_LOCK = RLock()


def utc_now_iso() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def ensure_storage_dirs() -> None:
    """Ensure all required storage directories exist."""
    ARTIFACT_ROOT.mkdir(parents=True, exist_ok=True)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    WALKFORWARD_DIR.mkdir(parents=True, exist_ok=True)
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    if not REGISTRY_PATH.exists():
        save_json(REGISTRY_PATH, {"runs": {}})


def _atomic_replace(path: Path, payload_text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.parent / f".{path.name}.{os.getpid()}.{uuid4().hex}.tmp"
    tmp_path.write_text(payload_text, encoding="utf-8")
    tmp_path.replace(path)


def save_json(path: Path, payload: Any) -> None:
    """Write JSON payload to disk."""
    _atomic_replace(
        path,
        json.dumps(payload, ensure_ascii=False, indent=2),
    )


def save_parquet_atomic(
    path: Path, frame: pd.DataFrame, *, index: bool = False
) -> None:
    """Write parquet payload atomically via temporary file replace."""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.parent / f".{path.name}.{os.getpid()}.{uuid4().hex}.tmp"
    frame.to_parquet(tmp_path, index=index)
    tmp_path.replace(path)


def load_json(path: Path, default: Any) -> Any:
    """Load JSON payload from disk."""
    if not path.exists():
        return default
    with path.open(encoding="utf-8") as file:
        return json.load(file)


def get_run_dir(run_id: str) -> Path:
    """Return directory for a given run id."""
    return RUNS_DIR / run_id


def read_registry() -> dict[str, Any]:
    """Load run registry payload."""
    ensure_storage_dirs()
    with _REGISTRY_LOCK:
        payload = load_json(REGISTRY_PATH, {"runs": {}})
        if "runs" not in payload:
            payload["runs"] = {}
        return payload


def write_registry(payload: dict[str, Any]) -> None:
    """Persist run registry payload."""
    ensure_storage_dirs()
    with _REGISTRY_LOCK:
        save_json(REGISTRY_PATH, payload)


def list_run_artifacts(run_id: str) -> list[str]:
    """List file artifacts for a run."""
    run_dir = get_run_dir(run_id)
    if not run_dir.exists():
        return []
    return sorted(path.name for path in run_dir.iterdir() if path.is_file())
