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
    SnapshotProfile,
)
from openbb_quant_ml.service.dashboard_metrics import (
    get_alerts_current,
    get_performance_rolling,
    get_portfolio_exposure,
    get_portfolio_risk,
    get_regime_current,
)
from openbb_quant_ml.service.pipeline import (
    get_model_performance,
    get_summary,
)
from openbb_quant_ml.service.registry.run_registry_db import list_run_events
from openbb_quant_ml.service.run_context import ensure_run_context
from openbb_quant_ml.service.run_latest import (
    get_run_latest_constraints,
    get_run_latest_meta,
)
from openbb_quant_ml.service.snapshot.dashboard_snapshot import (
    build_dashboard_snapshot_v2,
)
from openbb_quant_ml.service.storage import get_run_dir, load_json, read_registry

_SUPPORTED_MODELS: tuple[ModelName, ...] = ("lgbm_ranker", "xgb_lstm", "catboost_ranker")


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


def get_run_snapshot(
    run_id: str,
    model_name: str | None = None,
    profile: SnapshotProfile = "full",
) -> DashboardSnapshotV2:
    """Build canonical `DashboardSnapshotV2` for one explicit run."""
    normalized_model = _normalize_model_name(model_name)
    normalized_profile: SnapshotProfile = "core" if profile == "core" else "full"
    run_dir = get_run_dir(run_id)
    if not run_dir.exists():
        raise ValueError(f"Run not found: {run_id}")
    backtest = _load_backtest_payload(run_dir, normalized_model)
    metrics = (
        backtest.get("metrics", {})
        if isinstance(backtest.get("metrics", {}), dict)
        else {}
    )
    exposure = {}
    risk_contrib_top10 = []
    ic_rolling = []
    regime_current: dict[str, str] = {}
    alerts_current_count = 0

    if normalized_profile == "full":
        rolling = get_performance_rolling(
            run_id=run_id,
            model_name=normalized_model,
            window_short=63,
            window_long=126,
        )
        risk = get_portfolio_risk(
            run_id=run_id, model_name=normalized_model, lookback=126
        )
        exposures = get_portfolio_exposure(run_id=run_id, model_name=normalized_model)
        ic_rolling = (
            rolling.rolling_ic_3m if isinstance(rolling.rolling_ic_3m, list) else []
        )
        risk_contrib_top10 = risk.position_risk_contrib_top10
        exposure = _extract_exposure(exposures)
        try:
            regime = get_regime_current(run_id=run_id, model_name=normalized_model)
            regime_current = {
                "trend_regime": str(regime.trend_regime),
                "vol_regime": str(regime.vol_regime),
                "liquidity_regime": str(regime.liquidity_regime),
            }
        except Exception:  # noqa: BLE001
            regime_current = {}
        try:
            alerts = get_alerts_current(run_id=run_id, model_name=normalized_model)
            alerts_current_count = len(alerts.alerts or [])
        except Exception:  # noqa: BLE001
            alerts_current_count = 0
    run_context = ensure_run_context(run_dir, run_id)
    constraint_rows = backtest.get("constraint_binding_summary", [])
    if not isinstance(constraint_rows, list):
        constraint_rows = []
    binding_total = 0
    binding_ratio_sum = 0.0
    for row in constraint_rows:
        if not isinstance(row, dict):
            continue
        try:
            binding_total += int(row.get("binding_count", 0))
        except Exception:  # noqa: BLE001
            binding_total += 0
        try:
            binding_ratio_sum += float(row.get("binding_ratio", 0.0))
        except Exception:  # noqa: BLE001
            binding_ratio_sum += 0.0
    constraint_summary = {
        "binding_rows": int(len(constraint_rows)),
        "binding_total": int(binding_total),
        "binding_ratio_sum": float(binding_ratio_sum),
    }
    try:
        artifact_summary = get_summary(run_id=run_id, model_name=normalized_model)
        artifact_summary_payload: dict[str, Any] | None = artifact_summary.model_dump(
            mode="json"
        )
    except Exception:  # noqa: BLE001
        artifact_summary_payload = None
    try:
        model_performance = get_model_performance(run_id=run_id)
        model_performance_payload: dict[str, Any] | None = model_performance.model_dump(
            mode="json"
        )
    except Exception:  # noqa: BLE001
        model_performance_payload = None
    try:
        run_latest_meta = get_run_latest_meta(run_id=run_id, model_name=normalized_model)
        run_latest_meta_payload: dict[str, Any] | None = run_latest_meta.model_dump(
            mode="json"
        )
    except Exception:  # noqa: BLE001
        run_latest_meta_payload = None
    return build_dashboard_snapshot_v2(
        run_id=run_id,
        run_uid=(str(run_context.get("run_uid", "")).strip() or None),
        model_name=normalized_model,
        snapshot_profile=normalized_profile,
        as_of_utc=_resolve_as_of_utc(backtest),
        metrics=metrics,
        exposure=exposure,
        risk_contrib_top10=risk_contrib_top10,
        constraint_bindings=constraint_rows,
        ic_rolling=ic_rolling,
        regime_current=regime_current,
        alerts_current_count=alerts_current_count,
        constraint_summary=constraint_summary,
        artifact_summary=artifact_summary_payload,
        model_performance=model_performance_payload,
        run_latest_meta=run_latest_meta_payload,
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
