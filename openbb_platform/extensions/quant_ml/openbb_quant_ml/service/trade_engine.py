"""Trade-plan construction helpers."""

from __future__ import annotations

from typing import Any


def build_trade_plan(
    *,
    as_of_date: str,
    previous_weights: dict[str, float],
    target_weights: dict[str, float],
) -> list[dict[str, Any]]:
    """Build add/reduce/close plan from two weight maps."""
    rows: list[dict[str, Any]] = []
    symbols = sorted(set(previous_weights) | set(target_weights))
    for symbol in symbols:
        prev = float(previous_weights.get(symbol, 0.0) or 0.0)
        tgt = float(target_weights.get(symbol, 0.0) or 0.0)
        delta = tgt - prev
        if abs(delta) <= 1e-12:
            continue
        action = "buy" if delta > 0 else "sell"
        rows.append(
            {
                "date": str(as_of_date),
                "symbol": str(symbol),
                "action": action,
                "weight_before": prev,
                "weight_after": tgt,
                "weight_delta": delta,
            }
        )
    return rows

