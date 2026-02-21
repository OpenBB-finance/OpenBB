"""Serialization helpers for canonical V2 contracts."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import numpy as np
import pandas as pd


def ensure_iso8601_utc(value: Any) -> str:
    """Normalize timestamp-like values into ISO8601 UTC string."""
    if isinstance(value, datetime):
        stamp = value
    else:
        stamp = pd.Timestamp(value).to_pydatetime()
    if stamp.tzinfo is None:
        stamp = stamp.replace(tzinfo=UTC)
    else:
        stamp = stamp.astimezone(UTC)
    return stamp.replace(microsecond=0).isoformat()


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        casted = float(value)
    except (TypeError, ValueError):
        return default
    if np.isnan(casted) or np.isinf(casted):
        return default
    return casted


def ensure_decimal_series(
    rows: list[dict[str, Any]], *, key: str, date_key: str = "date"
) -> list[dict[str, float | str]]:
    """Project one numeric field into canonical `{timestamp_utc, value}` rows."""
    out: list[dict[str, float | str]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        if date_key not in row:
            continue
        out.append(
            {
                "timestamp_utc": ensure_iso8601_utc(row.get(date_key)),
                "value": _safe_float(row.get(key), default=0.0),
            }
        )
    return out
