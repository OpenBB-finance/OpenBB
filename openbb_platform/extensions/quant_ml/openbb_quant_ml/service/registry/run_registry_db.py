"""SQLite storage for run registry and audit events."""

from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from threading import RLock
from typing import Any, Iterable

from openbb_quant_ml.service.constants import RUN_REGISTRY_DB_PATH

_DB_LOCK = RLock()


@contextmanager
def _connect(path: Path | None = None) -> Iterable[sqlite3.Connection]:
    db_path = path or RUN_REGISTRY_DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def ensure_registry_db() -> None:
    """Create run-registry tables when missing."""
    with _DB_LOCK, _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS runs (
                run_id TEXT PRIMARY KEY,
                run_uid TEXT,
                model_name TEXT,
                universe_hash TEXT,
                feature_hash TEXT,
                data_version TEXT,
                created_at_utc TEXT,
                updated_at_utc TEXT,
                status TEXT,
                parent_run_id TEXT,
                stage TEXT,
                progress INTEGER,
                error TEXT,
                artifact_root TEXT,
                config_json TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS run_artifacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                artifact_name TEXT NOT NULL,
                uri TEXT,
                checksum TEXT,
                row_count INTEGER,
                created_at_utc TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS run_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                metric_key TEXT NOT NULL,
                metric_value REAL,
                unit TEXT,
                as_of_utc TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS run_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                payload_json TEXT,
                created_at_utc TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_run_events_run_id ON run_events(run_id, created_at_utc)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_runs_updated ON runs(updated_at_utc DESC)"
        )


def upsert_run_record(
    *,
    run_id: str,
    run_uid: str | None,
    status: str,
    progress: int,
    stage: str,
    created_at_utc: str,
    updated_at_utc: str,
    error: str | None = None,
    artifact_root: str | None = None,
    model_name: str | None = None,
    universe_hash: str | None = None,
    feature_hash: str | None = None,
    data_version: str | None = None,
    parent_run_id: str | None = None,
    config_json: dict[str, Any] | None = None,
) -> None:
    """Insert or update one run row."""
    ensure_registry_db()
    payload = json.dumps(config_json or {}, ensure_ascii=False)
    with _DB_LOCK, _connect() as conn:
        conn.execute(
            """
            INSERT INTO runs(
                run_id, run_uid, model_name, universe_hash, feature_hash, data_version,
                created_at_utc, updated_at_utc, status, parent_run_id, stage,
                progress, error, artifact_root, config_json
            ) VALUES (
                :run_id, :run_uid, :model_name, :universe_hash, :feature_hash, :data_version,
                :created_at_utc, :updated_at_utc, :status, :parent_run_id, :stage,
                :progress, :error, :artifact_root, :config_json
            )
            ON CONFLICT(run_id) DO UPDATE SET
                run_uid=excluded.run_uid,
                model_name=COALESCE(excluded.model_name, runs.model_name),
                universe_hash=COALESCE(excluded.universe_hash, runs.universe_hash),
                feature_hash=COALESCE(excluded.feature_hash, runs.feature_hash),
                data_version=COALESCE(excluded.data_version, runs.data_version),
                updated_at_utc=excluded.updated_at_utc,
                status=excluded.status,
                parent_run_id=COALESCE(excluded.parent_run_id, runs.parent_run_id),
                stage=excluded.stage,
                progress=excluded.progress,
                error=excluded.error,
                artifact_root=COALESCE(excluded.artifact_root, runs.artifact_root),
                config_json=COALESCE(excluded.config_json, runs.config_json)
            """,
            {
                "run_id": run_id,
                "run_uid": run_uid,
                "model_name": model_name,
                "universe_hash": universe_hash,
                "feature_hash": feature_hash,
                "data_version": data_version,
                "created_at_utc": created_at_utc,
                "updated_at_utc": updated_at_utc,
                "status": status,
                "parent_run_id": parent_run_id,
                "stage": stage,
                "progress": int(progress),
                "error": error,
                "artifact_root": artifact_root,
                "config_json": payload,
            },
        )


def append_run_event(
    *,
    run_id: str,
    event_type: str,
    severity: str = "info",
    payload: dict[str, Any] | None = None,
    created_at_utc: str,
) -> None:
    """Append one audit event row."""
    ensure_registry_db()
    with _DB_LOCK, _connect() as conn:
        conn.execute(
            """
            INSERT INTO run_events(run_id, event_type, severity, payload_json, created_at_utc)
            VALUES(:run_id, :event_type, :severity, :payload_json, :created_at_utc)
            """,
            {
                "run_id": run_id,
                "event_type": event_type,
                "severity": severity,
                "payload_json": json.dumps(payload or {}, ensure_ascii=False),
                "created_at_utc": created_at_utc,
            },
        )


def list_run_events(run_id: str, *, limit: int = 500) -> list[dict[str, Any]]:
    """List audit events for one run id."""
    ensure_registry_db()
    rows: list[dict[str, Any]] = []
    with _DB_LOCK, _connect() as conn:
        cursor = conn.execute(
            """
            SELECT id, run_id, event_type, severity, payload_json, created_at_utc
            FROM run_events
            WHERE run_id = :run_id
            ORDER BY id DESC
            LIMIT :limit
            """,
            {"run_id": run_id, "limit": max(1, int(limit))},
        )
        for row in cursor.fetchall():
            payload = {}
            try:
                payload = json.loads(str(row["payload_json"] or "{}"))
            except Exception:
                payload = {}
            rows.append(
                {
                    "id": int(row["id"]),
                    "run_id": str(row["run_id"]),
                    "event_type": str(row["event_type"]),
                    "severity": str(row["severity"] or "info"),
                    "payload": payload if isinstance(payload, dict) else {},
                    "created_at_utc": str(row["created_at_utc"]),
                }
            )
    rows.reverse()
    return rows
