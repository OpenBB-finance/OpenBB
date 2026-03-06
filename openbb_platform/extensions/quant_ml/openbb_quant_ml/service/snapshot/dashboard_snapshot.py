"""Builder for canonical dashboard snapshot payload."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import numpy as np

from openbb_quant_ml.models import DashboardSnapshotV2


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        casted = float(value)
    except (TypeError, ValueError):
        return default
    if np.isnan(casted) or np.isinf(casted):
        return default
    return casted


def build_dashboard_snapshot_v2(
    *,
    run_id: str,
    run_uid: str | None,
    model_name: str,
    snapshot_profile: str = "full",
    as_of_utc: str | None,
    metrics: dict[str, Any],
    exposure: dict[str, float],
    risk_contrib_top10: list[dict[str, float | str]],
    constraint_bindings: list[dict[str, Any]],
    ic_rolling: list[dict[str, float | str]],
    regime_current: dict[str, str] | None = None,
    alerts_current_count: int = 0,
    constraint_summary: dict[str, float | int] | None = None,
    artifact_summary: dict[str, Any] | None = None,
    model_performance: dict[str, Any] | None = None,
    run_latest_meta: dict[str, Any] | None = None,
) -> DashboardSnapshotV2:
    """Construct canonical `DashboardSnapshotV2` payload from raw components."""
    stamp = as_of_utc or datetime.now(UTC).replace(microsecond=0).isoformat()
    return DashboardSnapshotV2(
        run_id=run_id,
        run_uid=run_uid,
        model_name=model_name,  # type: ignore[arg-type]
        snapshot_profile=snapshot_profile,  # type: ignore[arg-type]
        as_of_utc=stamp,
        total_return=_safe_float(
            metrics.get("net_return", metrics.get("gross_return", 0.0)), default=0.0
        ),
        cagr=_safe_float(metrics.get("cagr"), default=0.0),
        sharpe=_safe_float(metrics.get("sharpe"), default=0.0),
        sortino=_safe_float(metrics.get("sortino"), default=0.0),
        max_drawdown=_safe_float(metrics.get("max_drawdown"), default=0.0),
        volatility=_safe_float(metrics.get("volatility"), default=0.0),
        turnover=_safe_float(metrics.get("turnover"), default=0.0),
        win_rate=_safe_float(metrics.get("hit_rate", metrics.get("win_rate", 0.0))),
        exposure=exposure,
        risk_contrib_top10=risk_contrib_top10,
        constraint_bindings=constraint_bindings,
        ic_rolling=ic_rolling,
        regime_current=regime_current or {},
        alerts_current_count=max(0, int(alerts_current_count)),
        constraint_summary=constraint_summary or {},
        artifact_summary=artifact_summary,
        model_performance=model_performance,
        run_latest_meta=run_latest_meta,
        currency="USD",
    )
