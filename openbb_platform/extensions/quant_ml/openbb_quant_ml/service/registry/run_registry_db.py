"""SQLite storage for run registry and audit events."""

from __future__ import annotations

import json
import sqlite3
from collections.abc import Iterable
from contextlib import contextmanager
from pathlib import Path
from threading import RLock
from typing import Any

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
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS dataset_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT,
                dataset_name TEXT NOT NULL,
                layer TEXT NOT NULL,
                as_of_date TEXT NOT NULL,
                version TEXT NOT NULL,
                uri TEXT,
                row_count INTEGER,
                checksum TEXT,
                profile_json TEXT,
                metadata_json TEXT,
                created_at_utc TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS quality_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT,
                gate_name TEXT NOT NULL,
                qc_status TEXT NOT NULL,
                as_of_date TEXT,
                summary_json TEXT,
                report_path TEXT,
                created_at_utc TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS experiment_runs (
                run_id TEXT PRIMARY KEY,
                model_type TEXT,
                dataset_version TEXT,
                feature_set_version TEXT,
                hyperparameters_json TEXT,
                feature_set_json TEXT,
                performance_json TEXT,
                artifact_uri TEXT,
                status TEXT,
                created_at_utc TEXT NOT NULL,
                updated_at_utc TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS model_versions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                model_name TEXT NOT NULL,
                model_version TEXT NOT NULL,
                stage TEXT NOT NULL,
                artifact_uri TEXT,
                dataset_version TEXT,
                feature_set_version TEXT,
                metrics_json TEXT,
                created_at_utc TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS model_aliases (
                alias TEXT PRIMARY KEY,
                run_id TEXT NOT NULL,
                model_name TEXT NOT NULL,
                model_version TEXT,
                source TEXT,
                updated_at_utc TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS promotion_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT NOT NULL,
                model_name TEXT NOT NULL,
                previous_run_id TEXT,
                previous_model_version TEXT,
                new_model_version TEXT,
                summary_json TEXT,
                created_at_utc TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS notification_outbox (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT,
                event_type TEXT NOT NULL,
                channel TEXT NOT NULL,
                fingerprint TEXT NOT NULL,
                status TEXT NOT NULL,
                payload_json TEXT,
                attempts INTEGER NOT NULL DEFAULT 0,
                last_error TEXT,
                created_at_utc TEXT NOT NULL,
                updated_at_utc TEXT NOT NULL,
                delivered_at_utc TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS report_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT,
                report_type TEXT NOT NULL,
                report_path TEXT NOT NULL,
                status TEXT NOT NULL,
                summary_json TEXT,
                created_at_utc TEXT NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_dataset_snapshots_run ON dataset_snapshots(run_id, created_at_utc DESC)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_quality_runs_created ON quality_runs(created_at_utc DESC)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_model_versions_model ON model_versions(model_name, created_at_utc DESC)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_promotion_events_model ON promotion_events(model_name, created_at_utc DESC)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_notification_outbox_lookup ON notification_outbox(fingerprint, channel, created_at_utc DESC)"
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_report_runs_lookup ON report_runs(report_type, created_at_utc DESC)"
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


def upsert_dataset_snapshot(
    *,
    run_id: str | None,
    dataset_name: str,
    layer: str,
    as_of_date: str,
    version: str,
    uri: str | None,
    row_count: int | None,
    checksum: str | None,
    profile_json: dict[str, Any] | None,
    metadata_json: dict[str, Any] | None,
    created_at_utc: str,
) -> None:
    """Insert one dataset snapshot row."""
    ensure_registry_db()
    with _DB_LOCK, _connect() as conn:
        conn.execute(
            """
            INSERT INTO dataset_snapshots(
                run_id, dataset_name, layer, as_of_date, version, uri, row_count,
                checksum, profile_json, metadata_json, created_at_utc
            ) VALUES (
                :run_id, :dataset_name, :layer, :as_of_date, :version, :uri, :row_count,
                :checksum, :profile_json, :metadata_json, :created_at_utc
            )
            """,
            {
                "run_id": run_id,
                "dataset_name": dataset_name,
                "layer": layer,
                "as_of_date": as_of_date,
                "version": version,
                "uri": uri,
                "row_count": row_count,
                "checksum": checksum,
                "profile_json": json.dumps(profile_json or {}, ensure_ascii=False),
                "metadata_json": json.dumps(metadata_json or {}, ensure_ascii=False),
                "created_at_utc": created_at_utc,
            },
        )


def list_dataset_snapshots(
    *,
    run_id: str | None = None,
    dataset_name: str | None = None,
    layer: str | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """List dataset snapshot rows with optional filters."""
    ensure_registry_db()
    query = "SELECT * FROM dataset_snapshots"
    where: list[str] = []
    params: dict[str, Any] = {"limit": max(1, int(limit))}
    if run_id:
        where.append("run_id = :run_id")
        params["run_id"] = run_id
    if dataset_name:
        where.append("dataset_name = :dataset_name")
        params["dataset_name"] = dataset_name
    if layer:
        where.append("layer = :layer")
        params["layer"] = layer
    if where:
        query += " WHERE " + " AND ".join(where)
    query += " ORDER BY created_at_utc DESC LIMIT :limit"
    rows: list[dict[str, Any]] = []
    with _DB_LOCK, _connect() as conn:
        for row in conn.execute(query, params).fetchall():
            rows.append({key: row[key] for key in row.keys()})
    return rows


def insert_quality_run(
    *,
    run_id: str | None,
    gate_name: str,
    qc_status: str,
    as_of_date: str | None,
    summary_json: dict[str, Any] | None,
    report_path: str | None,
    created_at_utc: str,
) -> int:
    """Insert one data-quality run row."""
    ensure_registry_db()
    with _DB_LOCK, _connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO quality_runs(
                run_id, gate_name, qc_status, as_of_date, summary_json, report_path, created_at_utc
            ) VALUES (
                :run_id, :gate_name, :qc_status, :as_of_date, :summary_json, :report_path, :created_at_utc
            )
            """,
            {
                "run_id": run_id,
                "gate_name": gate_name,
                "qc_status": qc_status,
                "as_of_date": as_of_date,
                "summary_json": json.dumps(summary_json or {}, ensure_ascii=False),
                "report_path": report_path,
                "created_at_utc": created_at_utc,
            },
        )
        return int(cursor.lastrowid)


def list_quality_runs(*, run_id: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
    """List stored data-quality rows."""
    ensure_registry_db()
    query = """
        SELECT id, run_id, gate_name, qc_status, as_of_date, summary_json, report_path, created_at_utc
        FROM quality_runs
    """
    params: dict[str, Any] = {"limit": max(1, int(limit))}
    if run_id:
        query += " WHERE run_id = :run_id"
        params["run_id"] = run_id
    query += " ORDER BY created_at_utc DESC LIMIT :limit"
    rows: list[dict[str, Any]] = []
    with _DB_LOCK, _connect() as conn:
        for row in conn.execute(query, params).fetchall():
            try:
                summary = json.loads(str(row["summary_json"] or "{}"))
            except Exception:
                summary = {}
            rows.append(
                {
                    "id": int(row["id"]),
                    "run_id": row["run_id"],
                    "gate_name": str(row["gate_name"]),
                    "qc_status": str(row["qc_status"]),
                    "as_of_date": row["as_of_date"],
                    "summary": summary if isinstance(summary, dict) else {},
                    "report_path": row["report_path"],
                    "created_at_utc": str(row["created_at_utc"]),
                }
            )
    return rows


def upsert_experiment_run(
    *,
    run_id: str,
    model_type: str | None,
    dataset_version: str | None,
    feature_set_version: str | None,
    hyperparameters_json: dict[str, Any] | None,
    feature_set_json: dict[str, Any] | None,
    performance_json: dict[str, Any] | None,
    artifact_uri: str | None,
    status: str | None,
    created_at_utc: str,
    updated_at_utc: str,
) -> None:
    """Insert or update one experiment row."""
    ensure_registry_db()
    with _DB_LOCK, _connect() as conn:
        conn.execute(
            """
            INSERT INTO experiment_runs(
                run_id, model_type, dataset_version, feature_set_version,
                hyperparameters_json, feature_set_json, performance_json, artifact_uri,
                status, created_at_utc, updated_at_utc
            ) VALUES (
                :run_id, :model_type, :dataset_version, :feature_set_version,
                :hyperparameters_json, :feature_set_json, :performance_json, :artifact_uri,
                :status, :created_at_utc, :updated_at_utc
            )
            ON CONFLICT(run_id) DO UPDATE SET
                model_type=COALESCE(excluded.model_type, experiment_runs.model_type),
                dataset_version=COALESCE(excluded.dataset_version, experiment_runs.dataset_version),
                feature_set_version=COALESCE(excluded.feature_set_version, experiment_runs.feature_set_version),
                hyperparameters_json=COALESCE(excluded.hyperparameters_json, experiment_runs.hyperparameters_json),
                feature_set_json=COALESCE(excluded.feature_set_json, experiment_runs.feature_set_json),
                performance_json=COALESCE(excluded.performance_json, experiment_runs.performance_json),
                artifact_uri=COALESCE(excluded.artifact_uri, experiment_runs.artifact_uri),
                status=COALESCE(excluded.status, experiment_runs.status),
                updated_at_utc=excluded.updated_at_utc
            """,
            {
                "run_id": run_id,
                "model_type": model_type,
                "dataset_version": dataset_version,
                "feature_set_version": feature_set_version,
                "hyperparameters_json": json.dumps(hyperparameters_json or {}, ensure_ascii=False),
                "feature_set_json": json.dumps(feature_set_json or {}, ensure_ascii=False),
                "performance_json": json.dumps(performance_json or {}, ensure_ascii=False),
                "artifact_uri": artifact_uri,
                "status": status,
                "created_at_utc": created_at_utc,
                "updated_at_utc": updated_at_utc,
            },
        )


def get_experiment_run(run_id: str) -> dict[str, Any] | None:
    """Return one experiment row."""
    ensure_registry_db()
    with _DB_LOCK, _connect() as conn:
        row = conn.execute(
            """
            SELECT *
            FROM experiment_runs
            WHERE run_id = :run_id
            """,
            {"run_id": run_id},
        ).fetchone()
    if row is None:
        return None
    return {key: row[key] for key in row.keys()}


def list_experiment_runs(*, limit: int = 100) -> list[dict[str, Any]]:
    """Return experiment runs ordered by update time."""
    ensure_registry_db()
    rows: list[dict[str, Any]] = []
    with _DB_LOCK, _connect() as conn:
        cursor = conn.execute(
            """
            SELECT *
            FROM experiment_runs
            ORDER BY updated_at_utc DESC
            LIMIT :limit
            """,
            {"limit": max(1, int(limit))},
        )
        for row in cursor.fetchall():
            rows.append({key: row[key] for key in row.keys()})
    return rows


def insert_model_version(
    *,
    run_id: str,
    model_name: str,
    model_version: str,
    stage: str,
    artifact_uri: str | None,
    dataset_version: str | None,
    feature_set_version: str | None,
    metrics_json: dict[str, Any] | None,
    created_at_utc: str,
) -> None:
    """Insert one model-version row."""
    ensure_registry_db()
    with _DB_LOCK, _connect() as conn:
        conn.execute(
            """
            INSERT INTO model_versions(
                run_id, model_name, model_version, stage, artifact_uri,
                dataset_version, feature_set_version, metrics_json, created_at_utc
            ) VALUES (
                :run_id, :model_name, :model_version, :stage, :artifact_uri,
                :dataset_version, :feature_set_version, :metrics_json, :created_at_utc
            )
            """,
            {
                "run_id": run_id,
                "model_name": model_name,
                "model_version": model_version,
                "stage": stage,
                "artifact_uri": artifact_uri,
                "dataset_version": dataset_version,
                "feature_set_version": feature_set_version,
                "metrics_json": json.dumps(metrics_json or {}, ensure_ascii=False),
                "created_at_utc": created_at_utc,
            },
        )


def list_model_versions(*, model_name: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
    """List model versions."""
    ensure_registry_db()
    query = "SELECT * FROM model_versions"
    params: dict[str, Any] = {"limit": max(1, int(limit))}
    if model_name:
        query += " WHERE model_name = :model_name"
        params["model_name"] = model_name
    query += " ORDER BY created_at_utc DESC LIMIT :limit"
    rows: list[dict[str, Any]] = []
    with _DB_LOCK, _connect() as conn:
        for row in conn.execute(query, params).fetchall():
            rows.append({key: row[key] for key in row.keys()})
    return rows


def upsert_model_alias(
    *,
    alias: str,
    run_id: str,
    model_name: str,
    model_version: str | None,
    source: str | None,
    updated_at_utc: str,
) -> None:
    """Upsert one model alias row."""
    ensure_registry_db()
    with _DB_LOCK, _connect() as conn:
        conn.execute(
            """
            INSERT INTO model_aliases(alias, run_id, model_name, model_version, source, updated_at_utc)
            VALUES(:alias, :run_id, :model_name, :model_version, :source, :updated_at_utc)
            ON CONFLICT(alias) DO UPDATE SET
                run_id=excluded.run_id,
                model_name=excluded.model_name,
                model_version=excluded.model_version,
                source=excluded.source,
                updated_at_utc=excluded.updated_at_utc
            """,
            {
                "alias": alias,
                "run_id": run_id,
                "model_name": model_name,
                "model_version": model_version,
                "source": source,
                "updated_at_utc": updated_at_utc,
            },
        )


def get_model_alias(alias: str) -> dict[str, Any] | None:
    """Return one model alias row."""
    ensure_registry_db()
    with _DB_LOCK, _connect() as conn:
        row = conn.execute(
            "SELECT * FROM model_aliases WHERE alias = :alias",
            {"alias": alias},
        ).fetchone()
    if row is None:
        return None
    return {key: row[key] for key in row.keys()}


def list_model_aliases(*, limit: int = 50) -> list[dict[str, Any]]:
    """List model aliases ordered by freshness."""
    ensure_registry_db()
    rows: list[dict[str, Any]] = []
    with _DB_LOCK, _connect() as conn:
        for row in conn.execute(
            "SELECT * FROM model_aliases ORDER BY updated_at_utc DESC LIMIT :limit",
            {"limit": max(1, int(limit))},
        ).fetchall():
            rows.append({key: row[key] for key in row.keys()})
    return rows


def insert_promotion_event(
    *,
    run_id: str,
    model_name: str,
    previous_run_id: str | None,
    previous_model_version: str | None,
    new_model_version: str | None,
    summary_json: dict[str, Any] | None,
    created_at_utc: str,
) -> None:
    """Insert one promotion event."""
    ensure_registry_db()
    with _DB_LOCK, _connect() as conn:
        conn.execute(
            """
            INSERT INTO promotion_events(
                run_id, model_name, previous_run_id, previous_model_version, new_model_version,
                summary_json, created_at_utc
            ) VALUES (
                :run_id, :model_name, :previous_run_id, :previous_model_version, :new_model_version,
                :summary_json, :created_at_utc
            )
            """,
            {
                "run_id": run_id,
                "model_name": model_name,
                "previous_run_id": previous_run_id,
                "previous_model_version": previous_model_version,
                "new_model_version": new_model_version,
                "summary_json": json.dumps(summary_json or {}, ensure_ascii=False),
                "created_at_utc": created_at_utc,
            },
        )


def list_promotion_events(*, model_name: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
    """List promotion events."""
    ensure_registry_db()
    query = "SELECT * FROM promotion_events"
    params: dict[str, Any] = {"limit": max(1, int(limit))}
    if model_name:
        query += " WHERE model_name = :model_name"
        params["model_name"] = model_name
    query += " ORDER BY created_at_utc DESC LIMIT :limit"
    rows: list[dict[str, Any]] = []
    with _DB_LOCK, _connect() as conn:
        for row in conn.execute(query, params).fetchall():
            rows.append({key: row[key] for key in row.keys()})
    return rows


def enqueue_notification(
    *,
    run_id: str | None,
    event_type: str,
    channel: str,
    fingerprint: str,
    payload_json: dict[str, Any] | None,
    status: str,
    attempts: int,
    last_error: str | None,
    created_at_utc: str,
    updated_at_utc: str,
    delivered_at_utc: str | None = None,
) -> int:
    """Insert one outbox notification row."""
    ensure_registry_db()
    with _DB_LOCK, _connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO notification_outbox(
                run_id, event_type, channel, fingerprint, status, payload_json, attempts,
                last_error, created_at_utc, updated_at_utc, delivered_at_utc
            ) VALUES (
                :run_id, :event_type, :channel, :fingerprint, :status, :payload_json, :attempts,
                :last_error, :created_at_utc, :updated_at_utc, :delivered_at_utc
            )
            """,
            {
                "run_id": run_id,
                "event_type": event_type,
                "channel": channel,
                "fingerprint": fingerprint,
                "status": status,
                "payload_json": json.dumps(payload_json or {}, ensure_ascii=False),
                "attempts": max(0, int(attempts)),
                "last_error": last_error,
                "created_at_utc": created_at_utc,
                "updated_at_utc": updated_at_utc,
                "delivered_at_utc": delivered_at_utc,
            },
        )
        return int(cursor.lastrowid)


def update_notification_status(
    notification_id: int,
    *,
    status: str,
    attempts: int,
    updated_at_utc: str,
    last_error: str | None = None,
    delivered_at_utc: str | None = None,
) -> None:
    """Update one notification row."""
    ensure_registry_db()
    with _DB_LOCK, _connect() as conn:
        conn.execute(
            """
            UPDATE notification_outbox
            SET status = :status,
                attempts = :attempts,
                updated_at_utc = :updated_at_utc,
                last_error = :last_error,
                delivered_at_utc = :delivered_at_utc
            WHERE id = :notification_id
            """,
            {
                "status": status,
                "attempts": max(0, int(attempts)),
                "updated_at_utc": updated_at_utc,
                "last_error": last_error,
                "delivered_at_utc": delivered_at_utc,
                "notification_id": int(notification_id),
            },
        )


def find_recent_notification(
    *,
    fingerprint: str,
    channel: str,
    limit: int = 1,
) -> list[dict[str, Any]]:
    """Return recent notifications for dedupe lookups."""
    ensure_registry_db()
    rows: list[dict[str, Any]] = []
    with _DB_LOCK, _connect() as conn:
        cursor = conn.execute(
            """
            SELECT *
            FROM notification_outbox
            WHERE fingerprint = :fingerprint AND channel = :channel
            ORDER BY created_at_utc DESC
            LIMIT :limit
            """,
            {"fingerprint": fingerprint, "channel": channel, "limit": max(1, int(limit))},
        )
        for row in cursor.fetchall():
            rows.append({key: row[key] for key in row.keys()})
    return rows


def list_notifications(*, limit: int = 100) -> list[dict[str, Any]]:
    """List notification outbox rows."""
    ensure_registry_db()
    rows: list[dict[str, Any]] = []
    with _DB_LOCK, _connect() as conn:
        for row in conn.execute(
            """
            SELECT *
            FROM notification_outbox
            ORDER BY created_at_utc DESC
            LIMIT :limit
            """,
            {"limit": max(1, int(limit))},
        ).fetchall():
            rows.append({key: row[key] for key in row.keys()})
    return rows


def insert_report_run(
    *,
    run_id: str | None,
    report_type: str,
    report_path: str,
    status: str,
    summary_json: dict[str, Any] | None,
    created_at_utc: str,
) -> int:
    """Insert one report row."""
    ensure_registry_db()
    with _DB_LOCK, _connect() as conn:
        cursor = conn.execute(
            """
            INSERT INTO report_runs(run_id, report_type, report_path, status, summary_json, created_at_utc)
            VALUES(:run_id, :report_type, :report_path, :status, :summary_json, :created_at_utc)
            """,
            {
                "run_id": run_id,
                "report_type": report_type,
                "report_path": report_path,
                "status": status,
                "summary_json": json.dumps(summary_json or {}, ensure_ascii=False),
                "created_at_utc": created_at_utc,
            },
        )
        return int(cursor.lastrowid)


def list_report_runs(
    *,
    run_id: str | None = None,
    report_type: str | None = None,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """List report rows with optional filters."""
    ensure_registry_db()
    query = "SELECT * FROM report_runs"
    where: list[str] = []
    params: dict[str, Any] = {"limit": max(1, int(limit))}
    if run_id:
        where.append("run_id = :run_id")
        params["run_id"] = run_id
    if report_type:
        where.append("report_type = :report_type")
        params["report_type"] = report_type
    if where:
        query += " WHERE " + " AND ".join(where)
    query += " ORDER BY created_at_utc DESC LIMIT :limit"
    rows: list[dict[str, Any]] = []
    with _DB_LOCK, _connect() as conn:
        for row in conn.execute(query, params).fetchall():
            rows.append({key: row[key] for key in row.keys()})
    return rows
