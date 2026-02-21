"""As-of integrity guard helpers."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any


def build_asof_manifest(
    *,
    rebalance_dates: list[date],
    fundamentals_lag_days: int = 60,
    market_cutoff: str = "T-1_close",
) -> dict[str, Any]:
    """Build as-of policy manifest for one backtest run."""
    windows: list[dict[str, str]] = []
    for rebalance_date in rebalance_dates:
        cutoff = rebalance_date - timedelta(days=1)
        windows.append(
            {
                "rebalance_date": rebalance_date.isoformat(),
                "market_data_cutoff": cutoff.isoformat(),
                "shares_float_cutoff": cutoff.isoformat(),
                "fundamentals_max_date": (rebalance_date - timedelta(days=fundamentals_lag_days)).isoformat(),
            }
        )
    return {
        "policy": {
            "market_data_cutoff": market_cutoff,
            "shares_float_cutoff": "T-1",
            "fundamentals_lag_days": int(fundamentals_lag_days),
            "prohibit_future_data": True,
        },
        "windows": windows,
    }


def validate_walkforward_train_windows(train_windows: list[dict[str, str]]) -> None:
    """Raise when walk-forward uses future training windows."""
    for row in train_windows:
        rebalance = str(row.get("rebalance_date", "")).strip()
        train_until = str(row.get("train_until", "")).strip()
        if not rebalance or not train_until:
            continue
        if train_until >= rebalance:
            raise ValueError("asof_integrity_violation")

