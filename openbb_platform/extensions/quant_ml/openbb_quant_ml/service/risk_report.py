"""Risk report builders for run artifacts."""

from __future__ import annotations

from typing import Any


def build_risk_summary(
    *,
    run_id: str,
    model_name: str,
    vol_ex_ante: float,
    cvar_95: float,
    risk_contribution_max: float,
    invalid_rebalance_count: int = 0,
) -> dict[str, Any]:
    """Build compact run-level risk summary payload."""
    return {
        "run_id": run_id,
        "model_name": model_name,
        "vol_ex_ante": float(vol_ex_ante),
        "cvar_95": float(cvar_95),
        "risk_contribution_max": float(risk_contribution_max),
        "invalid_rebalance_count": int(invalid_rebalance_count),
    }

