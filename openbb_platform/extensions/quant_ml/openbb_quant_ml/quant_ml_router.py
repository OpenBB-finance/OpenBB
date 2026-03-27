"""Quant ML Router."""

import asyncio
import json
import logging
from collections import deque
from datetime import date
from threading import Lock, RLock
from time import monotonic
from typing import Any

from cachetools import cached
from fastapi import HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from openbb_core.app.router import Router

from openbb_quant_ml.macro_models import MacroSeriesResponse
from openbb_quant_ml.macro_router import router as macro_router
from openbb_quant_ml.models import (
    AlertsResponse,
    ArtifactSummaryResponse,
    BacktestRequest,
    BacktestResponse,
    DashboardBootstrapResponse,
    DashboardHealthResponse,
    DashboardSnapshotV2,
    DataQualityHistoryResponse,
    DataQualityLatestResponse,
    ExecutionFillsResponse,
    ExecutionModeResponse,
    ExecutionModeUpdateRequest,
    ExecutionOrderPreviewRequest,
    ExecutionOrdersResponse,
    ExecutionPnlResponse,
    ExecutionPositionsResponse,
    ExecutionPreviewResponse,
    ExecutionSubmitResponse,
    ExperimentListResponse,
    ExperimentRunItemResponse,
    FeatureImportanceResponse,
    ICDecayResponse,
    ModelICResponse,
    ModelName,
    ModelPerformanceResponse,
    ModelRegimeResponse,
    ModelRegistryEntryResponse,
    ModelRegistryHistoryResponse,
    ModelShapResponse,
    NotificationsHistoryResponse,
    OpsIssueQueueResponse,
    OpsStatusResponse,
    PerformanceRegimeResponse,
    PortfolioCurrentResponse,
    PortfolioExposureResponse,
    PortfolioPolicyResponse,
    PortfolioRiskResponse,
    PredictionDistributionResponse,
    PredictionsLatestResponse,
    PromotedModelResponse,
    RebalanceHistoryResponse,
    RegimeCurrentResponse,
    RegimeHistoryResponse,
    ReportsHistoryResponse,
    ReportsLatestResponse,
    RiskEventsResponse,
    RiskLimitsResponse,
    RiskPretradeRequest,
    RiskPretradeResponse,
    RollingPerformanceResponse,
    RunAuditResponse,
    RunCompareResponse,
    RunLatestConstraintsResponse,
    RunLatestMetaResponse,
    RunListResponse,
    RunStatusResponse,
    SchedulerStatusResponse,
    SignalRequest,
    SignalResponse,
    SnapshotProfile,
    TradingAlgorithmsResponse,
    TradingAlgorithmToggleRequest,
    TradingAlgorithmValidateRequest,
    TradingAlgorithmValidationResponse,
    TradingCycleRunRequest,
    TradingCycleRunResponse,
    TradingEventsResponse,
    TradingExecutionModeResponse,
    TradingExecutionModeUpdateRequest,
    TradingFillsResponse,
    TradingOrderItemResponse,
    TradingOrdersResponse,
    TradingPerformanceResponse,
    TradingPositionsResponse,
    TradingRiskResponse,
    TradingScanHistoryResponse,
    TradingScanResponse,
    TradingSettingsResponse,
    TradingSettingsUpdateRequest,
    TradingStatusResponse,
    TradingSymbolDetailResponse,
    TrainRequest,
    TrainResponse,
    UniverseExclusionsResponse,
    UniverseListResponse,
    UniverseResolveResponse,
    UniverseResponse,
    UniverseSnapshotResponse,
    WorkspaceBriefResponse,
    SymbolContextResponse,
    WalkForwardBacktestRequest,
    WalkForwardBacktestStatusResponse,
    WalkForwardBacktestSubmitResponse,
)
from openbb_quant_ml.service import (
    approve_trading_order_payload,
    build_signals,
    cancel_trading_order_payload,
    close_trading_position_payload,
    get_alerts_current,
    get_alerts_history,
    get_backtest_result,
    get_dashboard_health,
    get_data_quality_history_response,
    get_execution_fills_history,
    get_execution_mode_response,
    get_execution_orders_current,
    get_execution_pnl,
    get_execution_positions_current,
    get_experiment_detail_response,
    get_experiment_list_response,
    get_feature_importance,
    get_latest_data_quality_response,
    get_market_ratio_response,
    get_market_rolling_corr_response,
    get_model_ic,
    get_model_ic_decay,
    get_model_performance,
    get_model_regime,
    get_model_registry_entry_response,
    get_model_registry_history_response,
    get_model_shap,
    get_notifications_history_response,
    get_ops_issue_queue_response,
    get_ops_status_response,
    get_performance_regime,
    get_performance_rolling,
    get_portfolio_current,
    get_portfolio_exposure,
    get_portfolio_policy_response,
    get_portfolio_risk,
    get_prediction_distribution,
    get_predictions_latest,
    get_promoted_model_response,
    get_rebalance_history,
    get_regime_current,
    get_regime_history,
    get_reports_history_response,
    get_reports_latest_response,
    get_run_compare_response,
    get_risk_events,
    get_risk_limits,
    get_run,
    get_run_audit,
    get_run_constraints,
    get_run_exposures,
    get_run_latest_constraints,
    get_run_latest_exposures,
    get_run_latest_meta,
    get_run_latest_risk,
    get_run_risk,
    get_run_snapshot,
    get_runs_list,
    get_scheduler_status_response,
    get_symbol_context_response,
    get_summary,
    get_trading_algorithms_payload,
    get_trading_events_payload,
    get_trading_execution_mode_payload,
    get_trading_fills_payload,
    get_trading_latest_scan_payload,
    get_trading_orders_payload,
    get_trading_performance_payload,
    get_trading_positions_payload,
    get_trading_risk_payload,
    get_trading_scan_history_payload,
    get_trading_settings_payload,
    get_trading_status_payload,
    get_trading_symbol_detail_payload,
    get_universe,
    get_universe_exclusions,
    get_universe_snapshot,
    get_workspace_brief_response,
    get_walkforward_backtest_status,
    preview_execution_orders,
    risk_check_pretrade,
    run_backtest_for_run,
    run_trading_cycle,
    set_execution_mode,
    set_trading_execution_mode_payload,
    submit_execution_orders,
    submit_training,
    submit_walkforward_backtest,
    toggle_trading_algorithm_payload,
    update_trading_settings_payload,
    validate_trading_algorithm_payload,
)
from openbb_quant_ml.service.runtime_cache import build_runtime_ttl_cache
from openbb_quant_ml.service.universe import (
    get_symbols_for_universe,
    get_universe_count_hint,
    get_universe_file_path,
    get_universe_minimum_required,
    get_universe_size_status,
    list_universe_ids,
    universe_file_exists,
)
from openbb_quant_ml.service.universe_policy import get_legacy_universe_meta

router = Router(prefix="", description="ML/DL based Quant Lab backend extension")
router.include_router(macro_router)

try:
    from limits import parse as parse_rate_limit
    from slowapi import Limiter
    from slowapi.util import get_remote_address
except Exception:  # noqa: BLE001
    Limiter = None
    get_remote_address = None
    parse_rate_limit = None

_TRAIN_RATE_LIMIT_WINDOW_SEC = 60.0
_TRAIN_RATE_LIMIT_MAX_REQUESTS = 5
_TRAIN_RATE_LIMIT_LABEL = "5/minute"
_TRAIN_RATE_BUCKETS: dict[str, deque[float]] = {}
_TRAIN_RATE_LOCK = Lock()
_TRAIN_RATE_LIMIT_ITEM: Any | None = None
_SLOWAPI_LIMITER: Any | None = None

_RUN_SNAPSHOT_CACHE = build_runtime_ttl_cache(
    namespace="quant:runs:snapshot", maxsize=128, ttl=600
)
_RUN_BACKTEST_CACHE = build_runtime_ttl_cache(
    namespace="quant:runs:backtest", maxsize=128, ttl=600
)
_HEALTH_CACHE = build_runtime_ttl_cache(
    namespace="quant:dashboard:health", maxsize=256, ttl=5
)
_DASHBOARD_BOOTSTRAP_CACHE = build_runtime_ttl_cache(
    namespace="quant:dashboard:bootstrap", maxsize=256, ttl=5
)
_PERFORMANCE_ROLLING_CACHE = build_runtime_ttl_cache(
    namespace="quant:performance:rolling", maxsize=256, ttl=15
)
_PERFORMANCE_REGIME_CACHE = build_runtime_ttl_cache(
    namespace="quant:performance:regime", maxsize=256, ttl=15
)
_MODEL_IC_DECAY_CACHE = build_runtime_ttl_cache(
    namespace="quant:model:ic-decay", maxsize=256, ttl=300
)
_RUN_LATEST_META_CACHE = build_runtime_ttl_cache(
    namespace="quant:runs:latest-meta", maxsize=256, ttl=10
)
_REGIME_CURRENT_CACHE = build_runtime_ttl_cache(
    namespace="quant:regime:current", maxsize=256, ttl=30
)
_REGIME_HISTORY_CACHE = build_runtime_ttl_cache(
    namespace="quant:regime:history", maxsize=256, ttl=30
)
_ALERTS_CURRENT_CACHE = build_runtime_ttl_cache(
    namespace="quant:alerts:current", maxsize=256, ttl=15
)
_READ_CACHE_LOCK = RLock()
_LOGGER = logging.getLogger(__name__)


def _invalidate_read_caches() -> None:
    with _READ_CACHE_LOCK:
        _RUN_SNAPSHOT_CACHE.clear()
        _RUN_BACKTEST_CACHE.clear()
        _HEALTH_CACHE.clear()
        _DASHBOARD_BOOTSTRAP_CACHE.clear()
        _PERFORMANCE_ROLLING_CACHE.clear()
        _PERFORMANCE_REGIME_CACHE.clear()
        _MODEL_IC_DECAY_CACHE.clear()
        _RUN_LATEST_META_CACHE.clear()
        _REGIME_CURRENT_CACHE.clear()
        _REGIME_HISTORY_CACHE.clear()
        _ALERTS_CURRENT_CACHE.clear()

if Limiter is not None and parse_rate_limit is not None and get_remote_address is not None:
    try:
        _SLOWAPI_LIMITER = Limiter(key_func=get_remote_address, enabled=True)
        _TRAIN_RATE_LIMIT_ITEM = parse_rate_limit(_TRAIN_RATE_LIMIT_LABEL)
    except Exception:  # noqa: BLE001
        _SLOWAPI_LIMITER = None
        _TRAIN_RATE_LIMIT_ITEM = None


def _now_monotonic() -> float:
    return monotonic()


def _client_key(http_request: Request | None) -> str:
    if (
        http_request is not None
        and getattr(http_request, "client", None) is not None
        and getattr(http_request.client, "host", None) is not None
    ):
        return str(http_request.client.host)
    return "local"


def _enforce_train_rate_limit(http_request: Request | None) -> None:
    key = _client_key(http_request)
    if _SLOWAPI_LIMITER is not None and _TRAIN_RATE_LIMIT_ITEM is not None:
        if not bool(_SLOWAPI_LIMITER.limiter.hit(_TRAIN_RATE_LIMIT_ITEM, key)):
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded for /train ({_TRAIN_RATE_LIMIT_LABEL}).",
            )
        return

    now_ts = _now_monotonic()
    with _TRAIN_RATE_LOCK:
        bucket = _TRAIN_RATE_BUCKETS.setdefault(key, deque())
        while bucket and (now_ts - bucket[0]) > _TRAIN_RATE_LIMIT_WINDOW_SEC:
            bucket.popleft()
        if len(bucket) >= _TRAIN_RATE_LIMIT_MAX_REQUESTS:
            raise HTTPException(
                status_code=429,
                detail=f"Rate limit exceeded for /train ({_TRAIN_RATE_LIMIT_LABEL}).",
            )
        bucket.append(now_ts)


@router.command(methods=["GET"])
def universe() -> UniverseResponse:
    """Return active universe configuration."""
    return get_universe()


@router.command(methods=["GET"], path="/universe/list")
def universe_list() -> UniverseListResponse:
    """Return discoverable universe identifiers from local universe files."""
    rows = []
    for universe_id in list_universe_ids():
        file_path = get_universe_file_path(universe_id)
        has_file = universe_file_exists(universe_id)
        rows.append(
            {
                "id": universe_id,
                "has_file": has_file,
                "path": str(file_path) if file_path else None,
                "count_hint": int(get_universe_count_hint(universe_id)),
                "minimum_required": int(get_universe_minimum_required(universe_id)),
            }
        )
    return UniverseListResponse(universes=rows)


@router.command(methods=["GET"], path="/universe/resolve")
def universe_resolve(
    universe_id: str = Query(...),
    mode: str = Query("train"),
    include_symbols: bool = Query(False),
) -> UniverseResolveResponse:
    """Resolve one universe id into symbol count and optional symbol list."""
    key = str(universe_id).strip()
    available = ", ".join(list_universe_ids())
    if not key:
        raise HTTPException(
            status_code=400,
            detail=(
                "invalid_or_empty_universe_id: <empty>; "
                f"available_universe_id: {available}; "
                "hint: run refresh_universes"
            ),
        )
    symbols = get_symbols_for_universe(key)
    if not symbols:
        raise HTTPException(
            status_code=400,
            detail=(
                f"invalid_or_empty_universe_id: {key}; "
                f"available_universe_id: {available}; "
                f"hint: populate openbb_quant_ml/universe/{key}.csv "
                "or run refresh_universes"
            ),
        )
    actual_count, minimum_required, meets_minimum = get_universe_size_status(
        key, symbols
    )
    if not meets_minimum:
        raise HTTPException(
            status_code=400,
            detail=(
                f"invalid_or_undersized_universe_id: {key}; "
                f"actual_count: {actual_count}; "
                f"minimum_required: {minimum_required}; "
                "hint: run refresh_universes --all --no-validate"
            ),
        )

    response = UniverseResolveResponse(
        universe_id=key,
        mode=mode,
        count=actual_count,
        minimum_required=minimum_required,
        meets_minimum=meets_minimum,
        **get_legacy_universe_meta(key),
    )
    if include_symbols:
        response.symbols = symbols
    return response


@router.command(methods=["POST"])
def train(
    request: TrainRequest, http_request: Request
) -> TrainResponse:
    """Queue asynchronous model training."""
    try:
        _enforce_train_rate_limit(http_request)
        response = submit_training(request)
        _invalidate_read_caches()
        return response
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/runs/list")
def runs_list(
    limit: int = Query(default=20, ge=1, le=200),
    completed_first: bool = Query(default=True),
    actionable_only: bool = Query(default=False),
) -> RunListResponse:
    """Return recent runs with optional completed-first/actionable filtering."""
    return get_runs_list(
        limit=limit,
        completed_first=completed_first,
        actionable_only=actionable_only,
    )


@router.command(methods=["GET"], path="/runs/compare")
def runs_compare(
    run_ids: str | None = None,
    limit: int = Query(default=5, ge=2, le=20),
) -> RunCompareResponse:
    """Return a compact comparison payload for recent strategy runs."""
    selected = [item.strip() for item in str(run_ids or "").split(",") if item.strip()]
    return get_run_compare_response(run_ids=selected or None, limit=limit)


@router.command(methods=["GET"], path="/runs/{run_id}")
def run_status(run_id: str) -> RunStatusResponse:
    """Get run status."""
    try:
        return get_run(run_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/runs/{run_id}/stream")
async def run_log_stream(
    run_id: str,
    request: Request,
    poll_interval_sec: float = Query(default=1.0, ge=0.5, le=10.0),
    max_seconds: int = Query(default=600, ge=30, le=7200),
) -> dict[str, object]:
    """Stream run status/log updates as Server-Sent Events (SSE)."""
    try:
        get_run(run_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    async def event_gen():
        started_at = _now_monotonic()
        sent_count = 0
        last_status: tuple[str, str, int] | None = None
        try:
            yield f"event: ready\ndata: {json.dumps({'run_id': run_id})}\n\n"
            while True:
                if await request.is_disconnected():
                    break

                try:
                    status = get_run(run_id)
                except ValueError as exc:
                    payload = {"type": "error", "message": str(exc)}
                    yield f"event: error\ndata: {json.dumps(payload)}\n\n"
                    break

                logs = list(status.logs_tail or [])
                if sent_count > len(logs):
                    sent_count = 0
                for line in logs[sent_count:]:
                    payload = {
                        "type": "log",
                        "run_id": run_id,
                        "status": status.status,
                        "stage": status.stage,
                        "line": str(line),
                    }
                    yield f"data: {json.dumps(payload)}\n\n"
                sent_count = len(logs)

                current_status = (
                    str(status.status),
                    str(status.stage),
                    int(status.progress),
                )
                if current_status != last_status:
                    last_status = current_status
                    payload = {
                        "type": "status",
                        "run_id": run_id,
                        "status": status.status,
                        "stage": status.stage,
                        "progress": int(status.progress),
                    }
                    yield f"event: status\ndata: {json.dumps(payload)}\n\n"

                if status.status in {"completed", "failed"}:
                    payload = {"type": "done", "run_id": run_id, "status": status.status}
                    yield f"event: done\ndata: {json.dumps(payload)}\n\n"
                    break

                if (_now_monotonic() - started_at) >= float(max_seconds):
                    payload = {
                        "type": "timeout",
                        "run_id": run_id,
                        "max_seconds": int(max_seconds),
                    }
                    yield f"event: timeout\ndata: {json.dumps(payload)}\n\n"
                    break

                if await request.is_disconnected():
                    break
                try:
                    await asyncio.sleep(float(poll_interval_sec))
                except asyncio.CancelledError:
                    break
        except asyncio.CancelledError:
            return

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@router.command(methods=["GET"], path="/runs/{run_id}/snapshot")
@cached(cache=_RUN_SNAPSHOT_CACHE, lock=_READ_CACHE_LOCK)
def run_snapshot(
    run_id: str,
    model_name: ModelName = "lgbm_ranker",
    profile: SnapshotProfile = "full",
) -> DashboardSnapshotV2:
    """Return canonical run-scoped dashboard snapshot payload."""
    try:
        return get_run_snapshot(run_id=run_id, model_name=model_name, profile=profile)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/runs/{run_id}/backtest")
@cached(cache=_RUN_BACKTEST_CACHE, lock=_READ_CACHE_LOCK)
def run_backtest_result(
    run_id: str, model_name: ModelName = "lgbm_ranker"
) -> BacktestResponse:
    """Return canonical run-scoped backtest payload."""
    try:
        return get_backtest_result(run_id=run_id, model_name=model_name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/runs/{run_id}/risk")
def run_risk(
    run_id: str, model_name: ModelName = "lgbm_ranker", lookback: int = 126
) -> PortfolioRiskResponse:
    """Return canonical run-scoped risk payload."""
    try:
        return get_run_risk(run_id=run_id, model_name=model_name, lookback=lookback)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/runs/{run_id}/exposures")
def run_exposures(
    run_id: str, model_name: ModelName = "lgbm_ranker"
) -> PortfolioExposureResponse:
    """Return canonical run-scoped exposure payload."""
    try:
        return get_run_exposures(run_id=run_id, model_name=model_name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/runs/{run_id}/constraints")
def run_constraints(
    run_id: str, model_name: ModelName = "lgbm_ranker"
) -> RunLatestConstraintsResponse:
    """Return canonical run-scoped constraints payload."""
    try:
        return get_run_constraints(run_id=run_id, model_name=model_name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/runs/{run_id}/audit")
def run_audit(run_id: str, limit: int = 500) -> RunAuditResponse:
    """Return run-scoped audit trail payload."""
    return get_run_audit(run_id=run_id, limit=limit)


@router.command(methods=["POST"])
def signals(request: SignalRequest) -> SignalResponse:
    """Generate signals from a completed training run."""
    try:
        response = build_signals(request)
        _invalidate_read_caches()
        return response
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.command(methods=["POST"])
def backtest(request: BacktestRequest) -> BacktestResponse:
    """Run backtest with mean-variance monthly optimization."""
    try:
        response = run_backtest_for_run(request)
        _invalidate_read_caches()
        return response
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.command(methods=["POST"], path="/backtest/walkforward")
def backtest_walkforward(
    request: WalkForwardBacktestRequest,
) -> WalkForwardBacktestSubmitResponse:
    """Queue asynchronous walk-forward backtest."""
    try:
        response = submit_walkforward_backtest(request)
        _invalidate_read_caches()
        return response
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/backtest/walkforward/{job_id}")
def backtest_walkforward_status(job_id: str) -> WalkForwardBacktestStatusResponse:
    """Get walk-forward backtest status."""
    response = get_walkforward_backtest_status(job_id)
    if response.status == "not_found":
        raise HTTPException(status_code=404, detail=response.message or "not found")
    return response


@router.command(methods=["GET"], path="/artifacts/{run_id}/summary")
def artifacts_summary(
    run_id: str, model_name: ModelName = "lgbm_ranker"
) -> ArtifactSummaryResponse:
    """Return run artifact summary."""
    try:
        return get_summary(run_id, model_name=model_name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/model/performance")
def model_performance(run_id: str) -> ModelPerformanceResponse:
    """Return model comparison summary."""
    try:
        return get_model_performance(run_id=run_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/model/ic")
def model_ic(
    run_id: str, model_name: ModelName = "lgbm_ranker", window: int = 6
) -> ModelICResponse:
    """Return model IC series."""
    try:
        return get_model_ic(run_id=run_id, model_name=model_name, window=window)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/model/regime")
def model_regime(
    run_id: str, model_name: ModelName = "lgbm_ranker"
) -> ModelRegimeResponse:
    """Return regime performance breakdown."""
    try:
        return get_model_regime(run_id=run_id, model_name=model_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/portfolio/current")
def portfolio_current(
    run_id: str, model_name: ModelName = "lgbm_ranker"
) -> PortfolioCurrentResponse:
    """Return latest portfolio allocations and rationale."""
    try:
        return get_portfolio_current(run_id=run_id, model_name=model_name)
    except ValueError as exc:
        detail = str(exc)
        if "Run backtest first" in detail:
            raise HTTPException(status_code=409, detail=detail) from exc
        raise HTTPException(status_code=404, detail=detail) from exc


@router.command(methods=["GET"], path="/portfolio/rebalance/history")
def portfolio_rebalance_history(
    run_id: str, model_name: ModelName = "lgbm_ranker"
) -> RebalanceHistoryResponse:
    """Return rebalance timeline (added/sold/turnover) for a run/model."""
    try:
        return get_rebalance_history(run_id=run_id, model_name=model_name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/portfolio/policy")
def portfolio_policy() -> PortfolioPolicyResponse:
    """Return enforced portfolio policy constants."""
    return get_portfolio_policy_response()


@router.command(methods=["GET"], path="/model/promoted")
def model_promoted(model_name: ModelName = "lgbm_ranker") -> PromotedModelResponse:
    """Return promoted model pointer payload."""
    return get_promoted_model_response(model_name=model_name)


@router.command(methods=["GET"], path="/run/latest/meta")
@cached(cache=_RUN_LATEST_META_CACHE, lock=_READ_CACHE_LOCK)
def run_latest_meta(
    run_id: str | None = None, model_name: ModelName = "lgbm_ranker"
) -> RunLatestMetaResponse:
    """Return latest run metadata alias payload."""
    try:
        return get_run_latest_meta(run_id=run_id, model_name=model_name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/run/latest/risk")
def run_latest_risk(
    run_id: str | None = None,
    model_name: ModelName = "lgbm_ranker",
    lookback: int = 126,
) -> PortfolioRiskResponse:
    """Return latest run portfolio risk alias payload."""
    return get_run_latest_risk(run_id=run_id, model_name=model_name, lookback=lookback)


@router.command(methods=["GET"], path="/run/latest/exposures")
def run_latest_exposures(
    run_id: str | None = None, model_name: ModelName = "lgbm_ranker"
) -> PortfolioExposureResponse:
    """Return latest run portfolio exposures alias payload."""
    return get_run_latest_exposures(run_id=run_id, model_name=model_name)


@router.command(methods=["GET"], path="/run/latest/constraints")
def run_latest_constraints(
    run_id: str | None = None, model_name: ModelName = "lgbm_ranker"
) -> RunLatestConstraintsResponse:
    """Return latest run constraint binding summary alias payload."""
    return get_run_latest_constraints(run_id=run_id, model_name=model_name)


@router.command(methods=["GET"], path="/universe/snapshot")
def universe_snapshot(run_id: str) -> UniverseSnapshotResponse:
    """Return latest U0/U1/U2 snapshot for a run."""
    try:
        return get_universe_snapshot(run_id=run_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/universe/exclusions")
def universe_exclusions(run_id: str) -> UniverseExclusionsResponse:
    """Return latest exclusion rows for a run."""
    try:
        return UniverseExclusionsResponse(
            run_id=run_id,
            items=get_universe_exclusions(run_id=run_id),
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/feature/importance")
def feature_importance(
    run_id: str, model_name: ModelName = "lgbm_ranker"
) -> FeatureImportanceResponse:
    """Return feature importance for a trained model."""
    try:
        return get_feature_importance(run_id=run_id, model_name=model_name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/predictions/latest")
def predictions_latest(
    run_id: str,
    model_name: ModelName = "lgbm_ranker",
    top_k: int = 20,
) -> PredictionsLatestResponse:
    """Return latest prediction table."""
    try:
        return get_predictions_latest(run_id=run_id, model_name=model_name, top_k=top_k)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/health")
@cached(cache=_HEALTH_CACHE, lock=_READ_CACHE_LOCK)
def health(
    run_id: str | None = None,
    model_name: ModelName = "lgbm_ranker",
    mode: str | None = None,
) -> DashboardHealthResponse:
    """Return dashboard health and run resolution metadata."""
    return get_dashboard_health(run_id=run_id, model_name=model_name, mode=mode)


@router.command(methods=["GET"], path="/workspace/brief")
def workspace_brief() -> WorkspaceBriefResponse:
    """Return the aggregated workspace brief payload."""
    return get_workspace_brief_response()


@router.command(methods=["GET"], path="/dashboard/bootstrap")
def dashboard_bootstrap(
    run_id: str | None = None,
    model_name: ModelName = "lgbm_ranker",
    mode: str | None = None,
    snapshot_profile: SnapshotProfile = "core",
) -> DashboardBootstrapResponse:
    """Return dashboard bootstrap payload in one request."""
    started_at = monotonic()
    cache_key = (
        (str(run_id).strip() if run_id else ""),
        str(model_name),
        (str(mode).strip() if mode else ""),
        str(snapshot_profile),
    )
    with _READ_CACHE_LOCK:
        cached_payload = _DASHBOARD_BOOTSTRAP_CACHE.get(cache_key)
    if isinstance(cached_payload, DashboardBootstrapResponse):
        elapsed_ms = int((monotonic() - started_at) * 1000)
        _LOGGER.info(
            "dashboard_bootstrap profile=%s cache_hit=true elapsed_ms=%d run_id=%s model=%s mode=%s",
            snapshot_profile,
            elapsed_ms,
            run_id or "",
            model_name,
            mode or "",
        )
        return cached_payload

    health_payload_raw = get_dashboard_health(
        run_id=run_id, model_name=model_name, mode=mode
    )
    health_payload = (
        health_payload_raw
        if isinstance(health_payload_raw, DashboardHealthResponse)
        else DashboardHealthResponse(**health_payload_raw)
    )
    resolved_run_id = str(
        health_payload.resolved_run_id or health_payload.latest_run_id or ""
    ).strip()
    snapshot_payload: DashboardSnapshotV2 | None = None
    if resolved_run_id:
        try:
            snapshot_payload = run_snapshot(
                run_id=resolved_run_id,
                model_name=model_name,
                profile=snapshot_profile,
            )
        except HTTPException as exc:
            _LOGGER.warning(
                "dashboard_bootstrap snapshot missing; returning health-only. run_id=%s model=%s profile=%s detail=%s",
                resolved_run_id,
                model_name,
                snapshot_profile,
                str(exc.detail),
            )
            snapshot_payload = None
    response = DashboardBootstrapResponse(
        snapshot_profile=snapshot_profile,
        health=health_payload,
        snapshot=snapshot_payload,
    )
    with _READ_CACHE_LOCK:
        _DASHBOARD_BOOTSTRAP_CACHE[cache_key] = response
    elapsed_ms = int((monotonic() - started_at) * 1000)
    _LOGGER.info(
        "dashboard_bootstrap profile=%s cache_hit=false elapsed_ms=%d run_id=%s model=%s mode=%s",
        snapshot_profile,
        elapsed_ms,
        run_id or resolved_run_id,
        model_name,
        mode or "",
    )
    return response


@router.command(methods=["GET"], path="/ops/status")
def ops_status() -> OpsStatusResponse:
    """Return operational jobs/cache/run/macro status summary."""
    return get_ops_status_response()


@router.command(methods=["GET"], path="/data-quality/latest")
def data_quality_latest(run_id: str | None = None) -> DataQualityLatestResponse:
    """Return the latest QC gate result."""
    return get_latest_data_quality_response(run_id=run_id)


@router.command(methods=["GET"], path="/data-quality/history")
def data_quality_history(
    run_id: str | None = None, limit: int = 50
) -> DataQualityHistoryResponse:
    """Return QC history for one run or globally."""
    return get_data_quality_history_response(run_id=run_id, limit=limit)


@router.command(methods=["GET"], path="/experiments/list")
def experiments_list(limit: int = 50) -> ExperimentListResponse:
    """Return tracked experiment runs."""
    return get_experiment_list_response(limit=limit)


@router.command(methods=["GET"], path="/experiments/{run_id}")
def experiment_get(run_id: str) -> ExperimentRunItemResponse:
    """Return one tracked experiment run."""
    return get_experiment_detail_response(run_id)


@router.command(methods=["GET"], path="/model-registry/champion")
def model_registry_champion(
    model_name: str | None = None,
) -> ModelRegistryEntryResponse:
    """Return the champion alias entry."""
    return get_model_registry_entry_response("champion", model_name=model_name)


@router.command(methods=["GET"], path="/model-registry/challenger")
def model_registry_challenger(
    model_name: str | None = None,
) -> ModelRegistryEntryResponse:
    """Return the challenger alias entry."""
    return get_model_registry_entry_response("challenger", model_name=model_name)


@router.command(methods=["GET"], path="/model-registry/history")
def model_registry_history(
    model_name: str | None = None, limit: int = 50
) -> ModelRegistryHistoryResponse:
    """Return model registry history."""
    return get_model_registry_history_response(model_name=model_name, limit=limit)


@router.command(methods=["GET"], path="/reports/latest")
def reports_latest(
    run_id: str | None = None, report_type: str | None = None
) -> ReportsLatestResponse:
    """Return the latest generated report."""
    return get_reports_latest_response(run_id=run_id, report_type=report_type)


@router.command(methods=["GET"], path="/reports/history")
def reports_history(
    run_id: str | None = None, report_type: str | None = None, limit: int = 50
) -> ReportsHistoryResponse:
    """Return generated report history."""
    return get_reports_history_response(
        run_id=run_id,
        report_type=report_type,
        limit=limit,
    )


@router.command(methods=["GET"], path="/ops/issues")
def ops_issues(limit: int = Query(default=10, ge=1, le=100)) -> OpsIssueQueueResponse:
    """Return the current human-readable ops issue queue."""
    return get_ops_issue_queue_response(limit=limit)


@router.command(methods=["GET"], path="/symbol/context")
def symbol_context(
    symbol: str,
    source: str | None = None,
    study_id: str | None = None,
    run_id: str | None = None,
    signal_id: str | None = None,
    report_path: str | None = None,
) -> SymbolContextResponse:
    """Return the shared Symbol Lab context payload."""
    return get_symbol_context_response(
        symbol=symbol,
        source=source,
        study_id=study_id,
        run_id=run_id,
        signal_id=signal_id,
        report_path=report_path,
    )


@router.command(methods=["GET"], path="/notifications/history")
def notifications_history(limit: int = 100) -> NotificationsHistoryResponse:
    """Return notification outbox history."""
    return get_notifications_history_response(limit=limit)


@router.command(methods=["GET"], path="/scheduler/status")
def scheduler_status() -> SchedulerStatusResponse:
    """Return scheduler configuration and health."""
    return get_scheduler_status_response()


@router.command(methods=["GET"], path="/trading/status")
def trading_status() -> TradingStatusResponse:
    """Return high-level trading runtime status."""
    return TradingStatusResponse(**get_trading_status_payload())


@router.command(methods=["GET"], path="/trading/settings")
def trading_settings() -> TradingSettingsResponse:
    """Return trading runtime settings and registries."""
    return TradingSettingsResponse(**get_trading_settings_payload())


@router.command(methods=["POST"], path="/trading/settings/update")
def trading_settings_update(
    request: TradingSettingsUpdateRequest,
) -> TradingSettingsResponse:
    """Persist trading runtime settings updates."""
    payload = request.model_dump(exclude_none=True)
    return TradingSettingsResponse(**update_trading_settings_payload(payload))


@router.command(methods=["POST"], path="/trading/cycle/run")
def trading_cycle_run(request: TradingCycleRunRequest) -> TradingCycleRunResponse:
    """Run one trading scan/execution cycle."""
    try:
        payload = run_trading_cycle(auto_execute=request.auto_execute)
        return TradingCycleRunResponse(**payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/trading/scan/latest")
def trading_scan_latest(limit: int = Query(default=200, ge=1, le=1000)) -> TradingScanResponse:
    """Return latest trading scan rows."""
    return TradingScanResponse(**get_trading_latest_scan_payload(limit=limit))


@router.command(methods=["GET"], path="/trading/scan/history")
def trading_scan_history(limit: int = Query(default=250, ge=1, le=2000)) -> TradingScanHistoryResponse:
    """Return trading scan history."""
    return TradingScanHistoryResponse(**get_trading_scan_history_payload(limit=limit))


@router.command(methods=["GET"], path="/trading/symbol/{ticker}")
def trading_symbol_detail(ticker: str) -> TradingSymbolDetailResponse:
    """Return one symbol detail payload for the trading tab."""
    try:
        payload = get_trading_symbol_detail_payload(ticker)
        context = get_symbol_context_response(symbol=ticker)
        payload["related_studies"] = context.linked_studies
        payload["related_runs"] = context.related_runs
        payload["latest_report_ids"] = [
            int(item.id) for item in context.attached_reports if item.id is not None
        ]
        return TradingSymbolDetailResponse(**payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/trading/orders")
def trading_orders(limit: int = Query(default=250, ge=1, le=2000)) -> TradingOrdersResponse:
    """Return trading order history."""
    return TradingOrdersResponse(**get_trading_orders_payload(limit=limit))


@router.command(methods=["POST"], path="/trading/orders/{order_id}/approve")
def trading_order_approve(order_id: str) -> TradingOrderItemResponse:
    """Approve and submit one pending paper order."""
    try:
        return TradingOrderItemResponse(**approve_trading_order_payload(order_id))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["POST"], path="/trading/orders/{order_id}/cancel")
def trading_order_cancel(order_id: str) -> TradingOrderItemResponse:
    """Cancel one pending paper order."""
    try:
        return TradingOrderItemResponse(**cancel_trading_order_payload(order_id))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/trading/fills")
def trading_fills(limit: int = Query(default=250, ge=1, le=2000)) -> TradingFillsResponse:
    """Return paper fill history."""
    return TradingFillsResponse(**get_trading_fills_payload(limit=limit))


@router.command(methods=["GET"], path="/trading/positions")
def trading_positions() -> TradingPositionsResponse:
    """Return current open positions."""
    return TradingPositionsResponse(**get_trading_positions_payload())


@router.command(methods=["POST"], path="/trading/positions/{ticker}/close")
def trading_position_close(ticker: str) -> TradingOrderItemResponse:
    """Force close one open paper position."""
    try:
        return TradingOrderItemResponse(**close_trading_position_payload(ticker))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/trading/performance")
def trading_performance() -> TradingPerformanceResponse:
    """Return paper-trading performance snapshot."""
    return TradingPerformanceResponse(**get_trading_performance_payload())


@router.command(methods=["GET"], path="/trading/risk")
def trading_risk() -> TradingRiskResponse:
    """Return trading risk limits and recent risk events."""
    return TradingRiskResponse(**get_trading_risk_payload())


@router.command(methods=["GET"], path="/trading/events")
def trading_events(limit: int = Query(default=250, ge=1, le=2000)) -> TradingEventsResponse:
    """Return trading audit/event history."""
    return TradingEventsResponse(**get_trading_events_payload(limit=limit))


@router.command(methods=["GET"], path="/trading/algorithms")
def trading_algorithms() -> TradingAlgorithmsResponse:
    """Return custom algorithm registry rows."""
    return TradingAlgorithmsResponse(**get_trading_algorithms_payload())


@router.command(methods=["POST"], path="/trading/algorithms/toggle")
def trading_algorithms_toggle(
    request: TradingAlgorithmToggleRequest,
) -> TradingAlgorithmsResponse:
    """Update one custom algorithm runtime state."""
    payload = toggle_trading_algorithm_payload(
        name=request.name,
        version=request.version,
        active=request.active,
        sandbox_mode=request.sandbox_mode,
        signal_only=request.signal_only,
        status=request.status,
    )
    return TradingAlgorithmsResponse(**payload)


@router.command(methods=["POST"], path="/trading/algorithms/validate")
def trading_algorithms_validate(
    request: TradingAlgorithmValidateRequest,
) -> TradingAlgorithmValidationResponse:
    """Validate one custom algorithm against a sample input frame."""
    try:
        return TradingAlgorithmValidationResponse(
            **validate_trading_algorithm_payload(request.name, request.version)
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/trading/execution/mode")
def trading_execution_mode() -> TradingExecutionModeResponse:
    """Return trading runtime execution mode."""
    return TradingExecutionModeResponse(**get_trading_execution_mode_payload())


@router.command(methods=["POST"], path="/trading/execution/mode/update")
def trading_execution_mode_update(
    request: TradingExecutionModeUpdateRequest,
) -> TradingExecutionModeResponse:
    """Update trading runtime execution mode."""
    return TradingExecutionModeResponse(
        **set_trading_execution_mode_payload(request.mode)
    )


@router.command(methods=["GET"], path="/performance/rolling")
@cached(cache=_PERFORMANCE_ROLLING_CACHE, lock=_READ_CACHE_LOCK)
def performance_rolling(
    run_id: str,
    model_name: ModelName = "lgbm_ranker",
    window_short: int = 63,
    window_long: int = 126,
) -> RollingPerformanceResponse:
    """Return rolling strategy performance timeseries."""
    try:
        return get_performance_rolling(
            run_id=run_id,
            model_name=model_name,
            window_short=window_short,
            window_long=window_long,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/performance/regime")
@cached(cache=_PERFORMANCE_REGIME_CACHE, lock=_READ_CACHE_LOCK)
def performance_regime(
    run_id: str, model_name: ModelName = "lgbm_ranker"
) -> PerformanceRegimeResponse:
    """Return regime breakdown for strategy performance."""
    try:
        return get_performance_regime(run_id=run_id, model_name=model_name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/portfolio/exposure")
def portfolio_exposure(
    run_id: str, model_name: ModelName = "lgbm_ranker"
) -> PortfolioExposureResponse:
    """Return portfolio exposure decomposition."""
    try:
        return get_portfolio_exposure(run_id=run_id, model_name=model_name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/portfolio/risk")
def portfolio_risk(
    run_id: str,
    model_name: ModelName = "lgbm_ranker",
    lookback: int = 126,
) -> PortfolioRiskResponse:
    """Return portfolio risk decomposition."""
    try:
        return get_portfolio_risk(
            run_id=run_id, model_name=model_name, lookback=lookback
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/model/ic_decay")
@cached(cache=_MODEL_IC_DECAY_CACHE, lock=_READ_CACHE_LOCK)
def model_ic_decay(
    run_id: str,
    model_name: ModelName = "lgbm_ranker",
    max_horizon: int = 20,
) -> ICDecayResponse:
    """Return IC decay across horizons."""
    try:
        return get_model_ic_decay(
            run_id=run_id, model_name=model_name, max_horizon=max_horizon
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/model/shap")
def model_shap(run_id: str, model_name: ModelName = "lgbm_ranker") -> ModelShapResponse:
    """Return SHAP payload (phase-2 placeholder)."""
    try:
        return get_model_shap(run_id=run_id, model_name=model_name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/model/prediction_distribution")
def prediction_distribution(
    run_id: str,
    model_name: ModelName = "lgbm_ranker",
    bins: int = 30,
) -> PredictionDistributionResponse:
    """Return latest prediction distribution and decile spread."""
    try:
        return get_prediction_distribution(
            run_id=run_id, model_name=model_name, bins=bins
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/regime/current")
@cached(cache=_REGIME_CURRENT_CACHE, lock=_READ_CACHE_LOCK)
def regime_current(
    run_id: str, model_name: ModelName = "lgbm_ranker"
) -> RegimeCurrentResponse:
    """Return current regime state."""
    try:
        return get_regime_current(run_id=run_id, model_name=model_name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/regime/history")
@cached(cache=_REGIME_HISTORY_CACHE, lock=_READ_CACHE_LOCK)
def regime_history(
    run_id: str, model_name: ModelName = "lgbm_ranker"
) -> RegimeHistoryResponse:
    """Return regime history timeline."""
    try:
        return get_regime_history(run_id=run_id, model_name=model_name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/alerts/current")
@cached(cache=_ALERTS_CURRENT_CACHE, lock=_READ_CACHE_LOCK)
def alerts_current(
    run_id: str, model_name: ModelName = "lgbm_ranker"
) -> AlertsResponse:
    """Return current strategy alerts."""
    try:
        return get_alerts_current(run_id=run_id, model_name=model_name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/alerts/history")
def alerts_history(
    run_id: str, model_name: ModelName = "lgbm_ranker", limit: int = 200
) -> AlertsResponse:
    """Return strategy alerts history."""
    try:
        return get_alerts_history(run_id=run_id, model_name=model_name, limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["POST"], path="/execution/orders/preview")
def execution_orders_preview(
    request: ExecutionOrderPreviewRequest,
) -> ExecutionPreviewResponse:
    """Preview paper execution orders for latest target portfolio."""
    try:
        return preview_execution_orders(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/execution/mode")
def execution_mode(
    run_id: str, model_name: ModelName = "lgbm_ranker"
) -> ExecutionModeResponse:
    """Return execution mode for one run/model."""
    return get_execution_mode_response(run_id, model_name)


@router.command(methods=["POST"], path="/execution/mode/update")
def execution_mode_update(
    request: ExecutionModeUpdateRequest,
) -> ExecutionModeResponse:
    """Persist execution mode for one run/model."""
    response = set_execution_mode(request)
    _invalidate_read_caches()
    return response


@router.command(methods=["POST"], path="/execution/orders/submit")
def execution_orders_submit(
    request: ExecutionOrderPreviewRequest,
) -> ExecutionSubmitResponse:
    """Submit paper execution orders and generate fills."""
    try:
        return submit_execution_orders(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/execution/orders/current")
def execution_orders_current(
    run_id: str, model_name: ModelName = "lgbm_ranker"
) -> ExecutionOrdersResponse:
    """Return current paper execution order snapshot."""
    return get_execution_orders_current(run_id=run_id, model_name=model_name)


@router.command(methods=["GET"], path="/execution/fills/history")
def execution_fills_history(
    run_id: str,
    model_name: ModelName = "lgbm_ranker",
    limit: int = 200,
) -> ExecutionFillsResponse:
    """Return paper execution fills history."""
    return get_execution_fills_history(
        run_id=run_id, model_name=model_name, limit=limit
    )


@router.command(methods=["GET"], path="/execution/positions/current")
def execution_positions_current(
    run_id: str, model_name: ModelName = "lgbm_ranker"
) -> ExecutionPositionsResponse:
    """Return current paper execution positions."""
    return get_execution_positions_current(run_id=run_id, model_name=model_name)


@router.command(methods=["GET"], path="/execution/pnl")
def execution_pnl(
    run_id: str, model_name: ModelName = "lgbm_ranker"
) -> ExecutionPnlResponse:
    """Return paper execution PnL."""
    return get_execution_pnl(run_id=run_id, model_name=model_name)


@router.command(methods=["GET"], path="/risk/limits")
def risk_limits(
    run_id: str, model_name: ModelName = "lgbm_ranker"
) -> RiskLimitsResponse:
    """Return risk limits and kill-switch state."""
    return get_risk_limits(run_id=run_id, model_name=model_name)


@router.command(methods=["POST"], path="/risk/check/pretrade")
def risk_check_pretrade_route(request: RiskPretradeRequest) -> RiskPretradeResponse:
    """Run pre-trade risk checks and persist events."""
    try:
        return risk_check_pretrade(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/risk/events")
def risk_events(
    run_id: str, model_name: ModelName = "lgbm_ranker", limit: int = 200
) -> RiskEventsResponse:
    """Return stored risk events."""
    return get_risk_events(run_id=run_id, model_name=model_name, limit=limit)


@router.command(methods=["GET"], path="/market/ratio")
def market_ratio(
    lhs: str,
    rhs: str,
    start: date | None = None,
    end: date | None = None,
    freq: str = "D",
    fill: str = "ffill",
) -> MacroSeriesResponse:
    """Return aligned ratio series lhs/rhs."""
    try:
        return get_market_ratio_response(
            lhs=lhs, rhs=rhs, start=start, end=end, freq=freq, fill=fill
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/market/rolling_corr")
def market_rolling_corr(
    x: str,
    y: str,
    window: int = 60,
    start: date | None = None,
    end: date | None = None,
    freq: str = "D",
    fill: str = "ffill",
) -> MacroSeriesResponse:
    """Return rolling correlation series for selected assets."""
    try:
        return get_market_rolling_corr_response(
            x=x,
            y=y,
            window=window,
            start=start,
            end=end,
            freq=freq,
            fill=fill,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# ---------------------------------------------------------------------------
# Finance: News & Watchlist
# ---------------------------------------------------------------------------


@router.command(methods=["GET"], path="/finance/news")
def get_finance_news(
    symbol: str = Query(..., description="Ticker symbol, e.g. IBM"),
    days: int = Query(7, ge=1, le=30, description="Lookback window in days"),
    limit: int = Query(30, ge=1, le=100, description="Max news items"),
) -> dict[str, Any]:
    """Return recent news articles for a single stock symbol."""
    from openbb_quant_ml.service.finance_news import get_stock_news  # noqa: PLC0415

    return get_stock_news(symbol=symbol.upper(), days=days, limit=limit)


@router.command(methods=["GET"], path="/finance/market_news")
def get_finance_market_news(
    limit: int = Query(20, ge=1, le=50, description="Max items"),
) -> dict[str, Any]:
    """Return broad market news from major indices."""
    from openbb_quant_ml.service.finance_news import get_market_news  # noqa: PLC0415

    return get_market_news(limit=limit)


@router.command(methods=["GET"], path="/finance/watchlist")
def get_finance_watchlist() -> dict[str, Any]:
    """Return the full watchlist with groups and tickers."""
    from openbb_quant_ml.service.watchlist_store import get_watchlist  # noqa: PLC0415

    return get_watchlist()


@router.command(methods=["POST"], path="/finance/watchlist")
def update_finance_watchlist(
    action: str = Query(..., description="One of: add_group, remove_group, add_ticker, remove_ticker, reorder"),
    group_name: str = Query("Default Watchlist", description="Target group name"),
    symbol: str = Query("", description="Ticker symbol (for add/remove ticker)"),
    ordered_symbols: str = Query("", description="Comma-separated ordered symbols (for reorder)"),
) -> dict[str, Any]:
    """Mutate the watchlist. Action determines the operation."""
    from openbb_quant_ml.service.watchlist_store import (  # noqa: PLC0415
        add_group,
        add_ticker,
        remove_group,
        remove_ticker,
        reorder_tickers,
    )

    if action == "add_group":
        return add_group(group_name)
    if action == "remove_group":
        return remove_group(group_name)
    if action == "add_ticker":
        if not symbol.strip():
            raise HTTPException(status_code=400, detail="symbol is required for add_ticker")
        return add_ticker(group_name, symbol.strip())
    if action == "remove_ticker":
        if not symbol.strip():
            raise HTTPException(status_code=400, detail="symbol is required for remove_ticker")
        return remove_ticker(group_name, symbol.strip())
    if action == "reorder":
        symbols_list = [s.strip() for s in ordered_symbols.split(",") if s.strip()]
        return reorder_tickers(group_name, symbols_list)
    raise HTTPException(status_code=400, detail=f"Unknown action: {action}")

@router.command(methods=["GET"], path="/finance/statement")
def get_finance_statement_proxy(
    kind: str = Query(..., description="income, balance, or cash"),
    symbol: str = Query(...),
    period: str = Query("annual"),
    limit: int = Query(4)
) -> dict[str, Any]:
    """Proxy fundamental statement fetch using internal SDK."""
    from openbb_quant_ml.service.finance_fundamentals import get_statement  # noqa: PLC0415
    res = get_statement(kind, symbol, period, limit)
    if "detail" in res:
        raise HTTPException(status_code=400, detail=res["detail"])
    return res

@router.command(methods=["GET"], path="/finance/forecast")
def get_finance_forecast_proxy(
    symbol: str = Query(...)
) -> dict[str, Any]:
    """Proxy analyst consensus forecast using internal SDK."""
    from openbb_quant_ml.service.finance_fundamentals import get_forecast  # noqa: PLC0415
    res = get_forecast(symbol)
    if "detail" in res:
        raise HTTPException(status_code=400, detail=res["detail"])
    return res
