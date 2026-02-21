"""Execution capacity estimators."""

from __future__ import annotations


def position_value_cap_from_adv20(
    adv20_usd: float, *, max_adv_participation: float = 0.05
) -> float:
    """Return max position value from ADV20 participation policy."""
    return max(0.0, float(max_adv_participation) * max(0.0, float(adv20_usd)))

