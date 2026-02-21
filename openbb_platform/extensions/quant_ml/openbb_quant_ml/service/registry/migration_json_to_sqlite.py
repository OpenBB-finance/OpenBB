"""Migrate legacy JSON run registry into SQLite."""

from __future__ import annotations

from typing import Any

from openbb_quant_ml.service.registry.run_registry_db import (
    ensure_registry_db,
    upsert_run_record,
)
from openbb_quant_ml.service.storage import read_registry


def migrate_json_registry_to_sqlite() -> dict[str, Any]:
    """Migrate `registry.json` rows to SQLite runs table."""
    ensure_registry_db()
    payload = read_registry()
    runs = payload.get("runs", {})
    if not isinstance(runs, dict):
        return {"migrated": 0, "skipped": 0}
    migrated = 0
    skipped = 0
    for run_id, row in runs.items():
        if not isinstance(row, dict):
            skipped += 1
            continue
        upsert_run_record(
            run_id=str(run_id),
            run_uid=(str(row.get("run_uid", "")).strip() or None),
            status=str(row.get("status", "unknown")),
            progress=int(row.get("progress", 0) or 0),
            stage=str(row.get("stage", "unknown")),
            created_at_utc=str(row.get("created_at", "")),
            updated_at_utc=str(row.get("updated_at", "")),
            error=(str(row.get("error", "")).strip() or None),
            artifact_root=(str(row.get("artifact_root", "")).strip() or None),
        )
        migrated += 1
    return {"migrated": migrated, "skipped": skipped}
