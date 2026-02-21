"""Risk-contribution helpers."""

from __future__ import annotations

import numpy as np


def compute_risk_contribution(
    weights: np.ndarray, cov: np.ndarray, *, epsilon: float = 1e-9
) -> np.ndarray:
    """Compute contribution to portfolio volatility."""
    port_var = float(weights @ cov @ weights)
    port_vol = float(np.sqrt(max(port_var, epsilon)))
    marginal = cov @ weights
    rc = weights * marginal / max(port_vol, epsilon)
    return np.nan_to_num(rc, nan=0.0, posinf=0.0, neginf=0.0)

