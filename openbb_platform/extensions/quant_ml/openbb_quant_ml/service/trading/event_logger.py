"""Trading event logging and notifications."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import pandas as pd

from openbb_quant_ml.service.notification_center import dispatch_notification
from openbb_quant_ml.service.trading.registry import insert_trading_event
from openbb_quant_ml.service.trading.storage import (
    append_frame,
    event_history_path,
)


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def log_trading_event(
    *,
    cycle_id: str | None,
    event_type: str,
    ticker: str | None,
    strategy: str | None,
    status: str | None,
    message: str,
    metadata: dict[str, Any] | None = None,
    notify: bool = False,
    severity: str = "info",
) -> None:
    """Persist one trading event and optionally send a notification."""
    created_at = _now_iso()
    row = {
        "timestamp": created_at,
        "cycle_id": cycle_id,
        "event_type": event_type,
        "ticker": ticker or "",
        "strategy": strategy or "",
        "status": status or "",
        "message": message,
        "metadata": metadata or {},
    }
    append_frame(event_history_path(), pd.DataFrame([row]))
    insert_trading_event(
        cycle_id=cycle_id,
        event_type=event_type,
        ticker=ticker,
        strategy_name=strategy,
        status=status,
        message=message,
        metadata=metadata,
        created_at_utc=created_at,
    )
    if notify:
        dispatch_notification(
            run_id=cycle_id,
            event_type=f"trading.{event_type}",
            title=f"Trading: {event_type}",
            body=message,
            severity=severity,
            extra_payload=metadata,
        )
