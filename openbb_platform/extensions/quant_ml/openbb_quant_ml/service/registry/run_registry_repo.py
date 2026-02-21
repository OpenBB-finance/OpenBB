"""Read-side repository helpers for SQLite run registry."""

from __future__ import annotations

import sqlite3
from typing import Any

from openbb_quant_ml.service.constants import RUN_REGISTRY_DB_PATH
from openbb_quant_ml.service.registry.run_registry_db import ensure_registry_db


def get_run_meta(run_id: str) -> dict[str, Any] | None:
    """Read one run row by id from SQLite registry."""
    ensure_registry_db()
    conn = sqlite3.connect(RUN_REGISTRY_DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            """
            SELECT run_id, run_uid, model_name, created_at_utc, updated_at_utc,
                   status, stage, progress, error, artifact_root
            FROM runs
            WHERE run_id = :run_id
            """,
            {"run_id": run_id},
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        return None
    return {key: row[key] for key in row.keys()}


def get_latest_completed_run_id() -> str | None:
    """Return latest completed run id from SQLite registry."""
    ensure_registry_db()
    conn = sqlite3.connect(RUN_REGISTRY_DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        row = conn.execute(
            """
            SELECT run_id
            FROM runs
            WHERE status = 'completed'
            ORDER BY updated_at_utc DESC
            LIMIT 1
            """
        ).fetchone()
    finally:
        conn.close()
    if row is None:
        return None
    return str(row["run_id"])
