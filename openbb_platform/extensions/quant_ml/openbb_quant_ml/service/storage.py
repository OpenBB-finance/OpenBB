"""Storage helpers for Quant ML artifacts and registry."""

from __future__ import annotations

import json
import os
import time
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
    RUNS_DIR,
    RUNTIME_DIR,
    WALKFORWARD_DIR,
)

_REGISTRY_LOCK = RLock()
_REGISTRY_STATS_PATH = ARTIFACT_ROOT / "registry_write_stats.json"
_REGISTRY_WRITE_STATS: dict[str, int] = {
    "atomic_replace_retries": 0,
    "fallback_writes": 0,
}


def _persist_registry_stats() -> None:
    _REGISTRY_STATS_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        _REGISTRY_STATS_PATH.write_text(
            json.dumps(_REGISTRY_WRITE_STATS, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except OSError:
        pass


def _load_registry_stats() -> None:
    if not _REGISTRY_STATS_PATH.exists():
        return
    try:
        payload = json.loads(_REGISTRY_STATS_PATH.read_text(encoding="utf-8"))
    except Exception:
        return
    if not isinstance(payload, dict):
        return
    for key in ("atomic_replace_retries", "fallback_writes"):
        try:
            _REGISTRY_WRITE_STATS[key] = int(payload.get(key, 0))
        except (TypeError, ValueError):
            _REGISTRY_WRITE_STATS[key] = 0


def _bump_registry_stat(name: str, delta: int = 1) -> None:
    with _REGISTRY_LOCK:
        _REGISTRY_WRITE_STATS[name] = int(_REGISTRY_WRITE_STATS.get(name, 0)) + int(
            delta
        )
        _persist_registry_stats()


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
    _load_registry_stats()


def _atomic_replace(path: Path, payload_text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    last_exc: Exception | None = None
    for attempt in range(6):
        tmp_path = path.parent / f".{path.name}.{os.getpid()}.{uuid4().hex}.tmp"
        try:
            tmp_path.write_text(payload_text, encoding="utf-8")
            os.replace(tmp_path, path)
            return
        except (PermissionError, OSError) as exc:
            last_exc = exc
            _bump_registry_stat("atomic_replace_retries", 1)
            try:
                if tmp_path.exists():
                    tmp_path.unlink()
            except OSError:
                pass
            time.sleep(0.05 * (attempt + 1))

    # Final fallback for transient file-lock environments (Windows AV/indexing).
    # This sacrifices atomicity but keeps the registry writable for live jobs.
    try:
        path.write_text(payload_text, encoding="utf-8")
        _bump_registry_stat("fallback_writes", 1)
        return
    except OSError:
        if last_exc is not None:
            raise last_exc
        raise


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


def get_registry_write_stats() -> dict[str, int]:
    """Return registry write contention/fallback counters."""
    ensure_storage_dirs()
    with _REGISTRY_LOCK:
        return dict(_REGISTRY_WRITE_STATS)
