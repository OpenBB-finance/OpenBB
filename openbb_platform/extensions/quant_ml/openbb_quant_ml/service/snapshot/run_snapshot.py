"""Canonical run-scoped snapshot/risk/exposure/constraints/audit services."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from openbb_quant_ml.models import (
    DashboardSnapshotV2,
    ModelName,
    PortfolioExposureResponse,
    PortfolioRiskResponse,
    RunAuditEventItem,
    RunAuditResponse,
    RunLatestConstraintsResponse,
)
from openbb_quant_ml.service.dashboard_metrics import (
    get_performance_rolling,
    get_portfolio_exposure,
    get_portfolio_risk,
)
from openbb_quant_ml.service.registry.run_registry_db import list_run_events
from openbb_quant_ml.service.run_context import ensure_run_context
from openbb_quant_ml.service.run_latest import get_run_latest_constraints
from openbb_quant_ml.service.snapshot.dashboard_snapshot import (
    build_dashboard_snapshot_v2,
)
from openbb_quant_ml.service.storage import get_run_dir, load_json, read_registry

_SUPPORTED_MODELS: tuple[ModelName, ...] = ("lgbm_ranker", "xgb_lstm")


def _normalize_model_name(model_name: str | None) -> ModelName:
    if model_name in _SUPPORTED_MODELS:
        return model_name
    return "lgbm_ranker"


def _load_backtest_payload(run_dir: Path, model_name: ModelName) -> dict[str, Any]:
    candidates = [run_dir / f"backtest_{model_name}.json"]
    if model_name == "lgbm_ranker":
        candidates.append(run_dir / "backtest.json")
    for path in candidates:
        payload = load_json(path, default={})
        if isinstance(payload, dict) and payload:
            return payload
    return {}


def _resolve_as_of_utc(backtest: dict[str, Any]) -> str:
    curve = backtest.get("equity_curve", [])
    if isinstance(curve, list) and curve:
        latest = curve[-1]
        if isinstance(latest, dict) and latest.get("date"):
            return (
                datetime.fromisoformat(str(latest["date"]) + "T00:00:00+00:00")
                .replace(microsecond=0)
                .isoformat()
            )
    return datetime.now(UTC).replace(microsecond=0).isoformat()


def _extract_exposure(payload: PortfolioExposureResponse) -> dict[str, float]:
    out: dict[str, float] = {}
    for item in payload.sector_exposure:
        key = str(item.category).strip().lower() or "other"
        out[key] = float(item.weight)
    return out


def get_run_snapshot(run_id: str, model_name: str | None = None) -> DashboardSnapshotV2:
    """Build canonical `DashboardSnapshotV2` for one explicit run."""
    normalized_model = _normalize_model_name(model_name)
    run_dir = get_run_dir(run_id)
    if not run_dir.exists():
        raise ValueError(f"Run not found: {run_id}")
    backtest = _load_backtest_payload(run_dir, normalized_model)
    metrics = (
        backtest.get("metrics", {})
        if isinstance(backtest.get("metrics", {}), dict)
        else {}
    )
    rolling = get_performance_rolling(
        run_id=run_id,
        model_name=normalized_model,
        window_short=63,
        window_long=126,
    )
    risk = get_portfolio_risk(run_id=run_id, model_name=normalized_model, lookback=126)
    exposures = get_portfolio_exposure(run_id=run_id, model_name=normalized_model)
    run_context = ensure_run_context(run_dir, run_id)
    constraint_rows = backtest.get("constraint_binding_summary", [])
    if not isinstance(constraint_rows, list):
        constraint_rows = []
    ic_rolling = (
        rolling.rolling_ic_3m if isinstance(rolling.rolling_ic_3m, list) else []
    )
    return build_dashboard_snapshot_v2(
        run_id=run_id,
        run_uid=(str(run_context.get("run_uid", "")).strip() or None),
        model_name=normalized_model,
        as_of_utc=_resolve_as_of_utc(backtest),
        metrics=metrics,
        exposure=_extract_exposure(exposures),
        risk_contrib_top10=risk.position_risk_contrib_top10,
        constraint_bindings=constraint_rows,
        ic_rolling=ic_rolling,
    )


def get_run_risk(
    run_id: str, *, model_name: str | None = None, lookback: int = 126
) -> PortfolioRiskResponse:
    """Return risk payload for explicit run id."""
    normalized_model = _normalize_model_name(model_name)
    return get_portfolio_risk(
        run_id=run_id,
        model_name=normalized_model,
        lookback=lookback,
    )


def get_run_exposures(
    run_id: str, *, model_name: str | None = None
) -> PortfolioExposureResponse:
    """Return exposure payload for explicit run id."""
    normalized_model = _normalize_model_name(model_name)
    return get_portfolio_exposure(run_id=run_id, model_name=normalized_model)


def get_run_constraints(
    run_id: str, *, model_name: str | None = None
) -> RunLatestConstraintsResponse:
    """Return constraint payload for explicit run id."""
    normalized_model = _normalize_model_name(model_name)
    return get_run_latest_constraints(run_id=run_id, model_name=normalized_model)


def get_run_audit(run_id: str, *, limit: int = 500) -> RunAuditResponse:
    """Return audit event trail for explicit run id."""
    run_dir = get_run_dir(run_id)
    if not run_dir.exists():
        return RunAuditResponse(
            run_id=run_id,
            status="not_found",
            message=f"Run not found: {run_id}",
            events=[],
        )
    rows = list_run_events(run_id, limit=limit)
    if not rows:
        registry = read_registry()
        runs = registry.get("runs", {}) if isinstance(registry, dict) else {}
        state = runs.get(run_id, {}) if isinstance(runs, dict) else {}
        logs_tail = state.get("logs_tail", []) if isinstance(state, dict) else []
        fallback_rows: list[dict[str, Any]] = []
        if isinstance(logs_tail, list):
            for idx, line in enumerate(logs_tail[-max(1, min(limit, 100)) :], start=1):
                fallback_rows.append(
                    {
                        "id": idx,
                        "run_id": run_id,
                        "event_type": "legacy_log_tail",
                        "severity": "info",
                        "payload": {"message": str(line)},
                        "created_at_utc": str(
                            state.get("updated_at")
                            or datetime.now(UTC).replace(microsecond=0).isoformat()
                        ),
                    }
                )
        rows = fallback_rows
    return RunAuditResponse(
        run_id=run_id,
        status="ok",
        events=[RunAuditEventItem(**row) for row in rows],
    )
