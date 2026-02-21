"""Trading cost model helpers."""

from __future__ import annotations


def estimate_roundtrip_cost(
    turnover: float,
    *,
    cost_bps: float,
    slippage_bps: float,
    participation_impact_bps: float = 0.0,
    fee_bps: float = 0.0,
) -> float:
    """Estimate daily cost from turnover and basis-point assumptions."""
    bps_total = (
        float(cost_bps)
        + float(slippage_bps)
        + float(participation_impact_bps)
        + float(fee_bps)
    )
    return max(0.0, float(turnover)) * (bps_total / 10_000.0)

