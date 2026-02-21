"""Tests for SQLite run registry helpers."""

from __future__ import annotations

from pathlib import Path

from openbb_quant_ml.service.registry.run_registry_db import (
    append_run_event,
    ensure_registry_db,
    list_run_events,
    upsert_run_record,
)


def test_run_registry_db_upsert_and_events(monkeypatch, tmp_path: Path) -> None:
    db_path = tmp_path / "run_registry.sqlite3"
    monkeypatch.setattr(
        "openbb_quant_ml.service.registry.run_registry_db.RUN_REGISTRY_DB_PATH", db_path
    )

    ensure_registry_db()
    upsert_run_record(
        run_id="trn-260221-001",
        run_uid="2026-02-21_150233Z_ab12cd34",
        status="running",
        progress=10,
        stage="training",
        created_at_utc="2026-02-21T15:02:33+00:00",
        updated_at_utc="2026-02-21T15:05:33+00:00",
        artifact_root=str(tmp_path / "runs" / "trn-260221-001"),
    )
    append_run_event(
        run_id="trn-260221-001",
        event_type="run_created",
        payload={"stage": "queued"},
        created_at_utc="2026-02-21T15:02:33+00:00",
    )
    rows = list_run_events("trn-260221-001", limit=50)
    assert len(rows) == 1
    assert rows[0]["event_type"] == "run_created"
    assert rows[0]["payload"]["stage"] == "queued"
