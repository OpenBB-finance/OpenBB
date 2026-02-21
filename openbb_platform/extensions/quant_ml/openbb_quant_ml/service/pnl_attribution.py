"""PnL attribution builders."""

from __future__ import annotations

from typing import Any

import pandas as pd


def build_pnl_attribution(cost_breakdown: list[dict[str, Any]]) -> pd.DataFrame:
    """Build gross/cost/net attribution frame."""
    if not cost_breakdown:
        return pd.DataFrame(
            columns=["date", "gross_return", "trading_cost", "net_return"]
        )
    frame = pd.DataFrame(cost_breakdown).copy()
    for col in ("gross_return", "trading_cost", "net_return"):
        frame[col] = pd.to_numeric(frame.get(col), errors="coerce").fillna(0.0)
    frame["date"] = frame.get("date", "").astype(str)
    return frame[["date", "gross_return", "trading_cost", "net_return"]]

