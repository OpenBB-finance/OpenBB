"""Audit log adapter for run registry."""

from __future__ import annotations

from typing import Any

from openbb_quant_ml.service.registry.run_registry_db import append_run_event
from openbb_quant_ml.service.storage import utc_now_iso


def append_audit_event(
    run_id: str,
    *,
    event_type: str,
    severity: str = "info",
    payload: dict[str, Any] | None = None,
) -> None:
    """Append one run audit event into SQLite registry."""
    append_run_event(
        run_id=run_id,
        event_type=event_type,
        severity=severity,
        payload=payload or {},
        created_at_utc=utc_now_iso(),
    )
