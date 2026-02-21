"""Liquidity-cap helpers."""

from __future__ import annotations


def adv20_weight_cap(
    adv20_usd: float, nav: float, *, max_adv_participation: float = 0.05
) -> float:
    """Return max portfolio weight by ADV participation."""
    nav_safe = max(float(nav), 1e-9)
    adv_safe = max(float(adv20_usd), 0.0)
    return max(0.0, (float(max_adv_participation) * adv_safe) / nav_safe)

