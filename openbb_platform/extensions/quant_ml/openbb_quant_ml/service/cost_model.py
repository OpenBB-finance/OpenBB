"""Trading cost model helpers."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class TransactionCostModel:
    """Transaction cost model with fixed and ADV-scaled impact components."""

    commission_bps: float = 5.0
    spread_bps: float = 3.0
    market_impact_bps: float = 2.0

    def compute_cost(self, weight_delta: float, adv_ratio: float = 0.0) -> float:
        """Return normalized portfolio cost for a single weight change."""
        fixed = (float(self.commission_bps) + float(self.spread_bps)) * 1e-4
        impact = float(self.market_impact_bps) * 1e-4 * float(
            np.sqrt(max(float(adv_ratio), 0.0))
        )
        return (fixed + impact) * abs(float(weight_delta))


def estimate_roundtrip_cost(
    turnover: float,
    *,
    cost_bps: float,
    slippage_bps: float,
    participation_impact_bps: float = 0.0,
    fee_bps: float = 0.0,
) -> float:
    """Estimate daily portfolio cost from turnover and bps assumptions."""
    model = TransactionCostModel(
        commission_bps=float(cost_bps) + float(fee_bps),
        spread_bps=float(slippage_bps),
        market_impact_bps=float(participation_impact_bps),
    )
    return model.compute_cost(weight_delta=max(0.0, float(turnover)), adv_ratio=1.0)
