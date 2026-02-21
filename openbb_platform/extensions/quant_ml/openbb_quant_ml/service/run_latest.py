"""Alias endpoints for latest run meta/risk/exposure/constraints."""

from __future__ import annotations

from typing import Any

import pandas as pd

from openbb_quant_ml.models import (
    ArtifactCompletenessItem,
    ConstraintBindingItem,
    ModelName,
    PortfolioExposureResponse,
    PortfolioRiskResponse,
    RunLatestConstraintsResponse,
    RunLatestMetaResponse,
)
from openbb_quant_ml.service.artifact_store import artifact_completeness, required_artifacts_ready
from openbb_quant_ml.service.constraints import summarize_constraint_bindings
from openbb_quant_ml.service.dashboard_metrics import (
    get_dashboard_health,
    get_portfolio_exposure,
    get_portfolio_risk,
)
from openbb_quant_ml.service.run_context import ensure_run_context
from openbb_quant_ml.service.storage import get_run_dir, load_json


def _normalize_model_name(model_name: str | None) -> ModelName:
    if model_name in {"lgbm_ranker", "xgb_lstm"}:
        return model_name
    return "lgbm_ranker"


def _resolve_run_id(run_id: str | None, model_name: ModelName) -> str | None:
    token = str(run_id or "").strip()
    if token:
        return token
    health = get_dashboard_health(run_id=None, model_name=model_name)
    resolved = str(health.resolved_run_id or health.latest_run_id or "").strip()
    return resolved or None


def _load_backtest_payload(run_id: str, model_name: ModelName) -> dict[str, Any]:
    run_dir = get_run_dir(run_id)
    candidates = [run_dir / f"backtest_{model_name}.json"]
    if model_name == "lgbm_ranker":
        candidates.append(run_dir / "backtest.json")
    for path in candidates:
        payload = load_json(path, default={})
        if isinstance(payload, dict) and payload:
            return payload
    return {}


def get_run_latest_meta(
    *, run_id: str | None = None, model_name: str | None = None
) -> RunLatestMetaResponse:
    """Return latest-run meta alias payload."""
    normalized_model = _normalize_model_name(model_name)
    resolved_run_id = _resolve_run_id(run_id, normalized_model)
    if not resolved_run_id:
        return RunLatestMetaResponse(
            run_id=None,
            model_name=normalized_model,
            status="insufficient_data",
            message="No available runs.",
        )

    run_dir = get_run_dir(resolved_run_id)
    context = ensure_run_context(run_dir, resolved_run_id)
    backtest = _load_backtest_payload(resolved_run_id, normalized_model)
    as_of_date = None
    period_weights = backtest.get("period_weights", [])
    if isinstance(period_weights, list) and period_weights:
        as_of_date = str(period_weights[-1].get("date", "")).strip() or None
    if not as_of_date:
        as_of_date = str(backtest.get("end_date", "")).strip() or None

    completeness_rows = [
        ArtifactCompletenessItem(**row)
        for row in artifact_completeness(resolved_run_id)
        if isinstance(row, dict)
    ]
    return RunLatestMetaResponse(
        run_id=resolved_run_id,
        run_uid=str(context.get("run_uid", "")).strip() or None,
        model_name=normalized_model,
        as_of_date=as_of_date,
        status="ok",
        artifact_contract_version=str(
            load_json(
                run_dir / "artifacts" / "artifact_contract.json", default={}
            ).get("artifact_contract_version", "")
        )
        or None,
        required_artifacts_ready=required_artifacts_ready(resolved_run_id),
        universe_stage_counts=(
            backtest.get("universe_stage_counts", {})
            if isinstance(backtest.get("universe_stage_counts", {}), dict)
            else {}
        ),
        artifact_completeness=completeness_rows,
    )


def get_run_latest_constraints(
    *, run_id: str | None = None, model_name: str | None = None
) -> RunLatestConstraintsResponse:
    """Return latest-run constraint binding summary."""
    normalized_model = _normalize_model_name(model_name)
    resolved_run_id = _resolve_run_id(run_id, normalized_model)
    if not resolved_run_id:
        return RunLatestConstraintsResponse(
            run_id="",
            model_name=normalized_model,
            status="insufficient_data",
            message="No available runs.",
        )

    run_dir = get_run_dir(resolved_run_id)
    path = run_dir / "artifacts" / "constraints_log.parquet"
    if not path.exists():
        return RunLatestConstraintsResponse(
            run_id=resolved_run_id,
            model_name=normalized_model,
            status="insufficient_data",
            message="constraints_log is unavailable",
        )
    frame = pd.read_parquet(path)
    summary = summarize_constraint_bindings(frame)
    rows = [
        ConstraintBindingItem(**row) for row in summary if isinstance(row, dict)
    ]
    liquidity_rows: list[dict[str, float | str]] = []
    if not frame.empty and "constraint_type" in frame.columns:
        liq = frame[
            frame["constraint_type"].astype(str).str.lower() == "liquidity_adv20"
        ].copy()
        if not liq.empty:
            liq["threshold"] = pd.to_numeric(liq.get("threshold"), errors="coerce").fillna(0.0)
            grouped = (
                liq.groupby("ticker", dropna=True)["threshold"].max().reset_index()
                .sort_values("threshold", ascending=False)
                .head(20)
            )
            for _, row in grouped.iterrows():
                liquidity_rows.append(
                    {
                        "symbol": str(row.get("ticker", "")).strip().upper(),
                        "adv_weight_cap": float(row.get("threshold", 0.0) or 0.0),
                    }
                )
    backtest = _load_backtest_payload(resolved_run_id, normalized_model)
    risk = get_portfolio_risk(
        run_id=resolved_run_id,
        model_name=normalized_model,
        lookback=126,
    )
    return RunLatestConstraintsResponse(
        run_id=resolved_run_id,
        model_name=normalized_model,
        status="ok",
        items=rows,
        liquidity_clip_ratio=float(backtest.get("liquidity_clip_ratio", 0.0) or 0.0),
        risk_contribution_max=float(backtest.get("risk_contribution_max", 0.0) or 0.0),
        top_risk_contribution=risk.position_risk_contrib_top10,
        liquidity_adv_top=liquidity_rows,
    )


def get_run_latest_risk(
    *, run_id: str | None = None, model_name: str | None = None, lookback: int = 126
) -> PortfolioRiskResponse:
    """Return latest-run risk alias payload."""
    normalized_model = _normalize_model_name(model_name)
    resolved_run_id = _resolve_run_id(run_id, normalized_model)
    if not resolved_run_id:
        return PortfolioRiskResponse(
            run_id="",
            model_name=normalized_model,
            status="insufficient_data",
            message="No available runs.",
        )
    return get_portfolio_risk(
        run_id=resolved_run_id,
        model_name=normalized_model,
        lookback=lookback,
    )


def get_run_latest_exposures(
    *, run_id: str | None = None, model_name: str | None = None
) -> PortfolioExposureResponse:
    """Return latest-run exposure alias payload."""
    normalized_model = _normalize_model_name(model_name)
    resolved_run_id = _resolve_run_id(run_id, normalized_model)
    if not resolved_run_id:
        return PortfolioExposureResponse(
            run_id="",
            model_name=normalized_model,
            status="insufficient_data",
            message="No available runs.",
        )
    return get_portfolio_exposure(
        run_id=resolved_run_id,
        model_name=normalized_model,
    )
