"""Artifact contract helpers for institutional run outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from openbb_quant_ml.service.run_context import ensure_run_context
from openbb_quant_ml.service.storage import get_run_dir, save_json, save_parquet_atomic

ARTIFACT_CONTRACT_VERSION = "v1"

REQUIRED_ARTIFACTS: tuple[str, ...] = (
    "universe.parquet",
    "exclusions.parquet",
    "signals.parquet",
    "weights_target.parquet",
    "weights_final.parquet",
    "constraints_log.parquet",
    "trades.parquet",
    "costs.parquet",
    "returns_daily.parquet",
    "risk_summary.parquet",
    "exposures_sector.parquet",
    "report.html",
)


def get_artifacts_dir(run_id: str) -> Path:
    """Return contract artifact directory for one run."""
    out = get_run_dir(run_id) / "artifacts"
    out.mkdir(parents=True, exist_ok=True)
    return out


def _target_path(run_id: str, name: str) -> Path:
    return get_artifacts_dir(run_id) / str(name).strip()


def write_parquet(run_id: str, name: str, frame: pd.DataFrame) -> Path:
    """Write a parquet artifact under artifacts/."""
    path = _target_path(run_id, name)
    save_parquet_atomic(path, frame, index=False)
    return path


def write_json(run_id: str, name: str, payload: dict[str, Any]) -> Path:
    """Write a json artifact under artifacts/."""
    path = _target_path(run_id, name)
    save_json(path, payload)
    return path


def write_text(run_id: str, name: str, text: str) -> Path:
    """Write plain text artifact."""
    path = _target_path(run_id, name)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def artifact_completeness(run_id: str) -> list[dict[str, Any]]:
    """Return required artifact readiness rows."""
    base = get_artifacts_dir(run_id)
    rows: list[dict[str, Any]] = []
    for name in REQUIRED_ARTIFACTS:
        path = base / name
        rows.append(
            {
                "artifact": name,
                "ready": bool(path.exists()),
                "path": str(path),
            }
        )
    return rows


def required_artifacts_ready(run_id: str) -> bool:
    """Return True when all required artifacts exist."""
    return all(bool(row.get("ready", False)) for row in artifact_completeness(run_id))


def write_contract_manifest(run_id: str) -> dict[str, Any]:
    """Persist contract manifest with run context metadata."""
    run_dir = get_run_dir(run_id)
    context = ensure_run_context(run_dir, run_id)
    payload = {
        "run_id": run_id,
        "run_uid": context.get("run_uid"),
        "artifact_contract_version": ARTIFACT_CONTRACT_VERSION,
        "required_artifacts": list(REQUIRED_ARTIFACTS),
        "completeness": artifact_completeness(run_id),
        "required_artifacts_ready": required_artifacts_ready(run_id),
    }
    write_json(run_id, "artifact_contract.json", payload)
    return payload

