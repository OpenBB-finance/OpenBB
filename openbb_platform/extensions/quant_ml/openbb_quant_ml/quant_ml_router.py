"""Quant ML Router."""

from datetime import date

from fastapi import HTTPException
from openbb_core.app.router import Router

from openbb_quant_ml.macro_models import MacroSeriesResponse
from openbb_quant_ml.macro_router import router as macro_router
from openbb_quant_ml.models import (
    AlertsResponse,
    ArtifactSummaryResponse,
    BacktestRequest,
    BacktestResponse,
    DashboardHealthResponse,
    FeatureImportanceResponse,
    ICDecayResponse,
    ExecutionFillsResponse,
    ExecutionOrdersResponse,
    ExecutionPnlResponse,
    ExecutionPositionsResponse,
    ExecutionOrderPreviewRequest,
    ExecutionPreviewResponse,
    ExecutionSubmitResponse,
    ModelICResponse,
    ModelName,
    ModelPerformanceResponse,
    ModelRegimeResponse,
    ModelShapResponse,
    PerformanceRegimeResponse,
    PortfolioExposureResponse,
    PortfolioRiskResponse,
    PortfolioCurrentResponse,
    PredictionDistributionResponse,
    PredictionsLatestResponse,
    RegimeCurrentResponse,
    RegimeHistoryResponse,
    RiskEventsResponse,
    RiskLimitsResponse,
    RiskPretradeRequest,
    RiskPretradeResponse,
    RollingPerformanceResponse,
    RunStatusResponse,
    SignalRequest,
    SignalResponse,
    TrainRequest,
    TrainResponse,
    UniverseResponse,
)
from openbb_quant_ml.service import (
    build_signals,
    get_market_ratio_response,
    get_market_rolling_corr_response,
    get_alerts_current,
    get_alerts_history,
    get_dashboard_health,
    get_feature_importance,
    get_execution_fills_history,
    get_execution_orders_current,
    get_execution_pnl,
    get_execution_positions_current,
    get_model_ic,
    get_model_ic_decay,
    get_model_shap,
    get_model_performance,
    get_model_regime,
    get_performance_regime,
    get_performance_rolling,
    get_portfolio_current,
    get_portfolio_exposure,
    get_portfolio_risk,
    get_prediction_distribution,
    get_regime_current,
    get_regime_history,
    get_predictions_latest,
    get_risk_events,
    get_risk_limits,
    get_run,
    get_summary,
    get_universe,
    run_backtest_for_run,
    preview_execution_orders,
    risk_check_pretrade,
    submit_execution_orders,
    submit_training,
)

router = Router(prefix="", description="ML/DL based Quant Lab backend extension")
router.include_router(macro_router)


@router.command(methods=["GET"])
def universe() -> UniverseResponse:
    """Return active universe configuration."""
    return get_universe()


@router.command(methods=["POST"])
def train(request: TrainRequest) -> TrainResponse:
    """Queue asynchronous model training."""
    try:
        return submit_training(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/runs/{run_id}")
def run_status(run_id: str) -> RunStatusResponse:
    """Get run status."""
    try:
        return get_run(run_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["POST"])
def signals(request: SignalRequest) -> SignalResponse:
    """Generate signals from a completed training run."""
    try:
        return build_signals(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.command(methods=["POST"])
def backtest(request: BacktestRequest) -> BacktestResponse:
    """Run backtest with mean-variance monthly optimization."""
    try:
        return run_backtest_for_run(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/artifacts/{run_id}/summary")
def artifacts_summary(run_id: str, model_name: ModelName = "lgbm_ranker") -> ArtifactSummaryResponse:
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
def model_ic(run_id: str, model_name: ModelName = "lgbm_ranker", window: int = 6) -> ModelICResponse:
    """Return model IC series."""
    try:
        return get_model_ic(run_id=run_id, model_name=model_name, window=window)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/model/regime")
def model_regime(run_id: str, model_name: ModelName = "lgbm_ranker") -> ModelRegimeResponse:
    """Return regime performance breakdown."""
    try:
        return get_model_regime(run_id=run_id, model_name=model_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/portfolio/current")
def portfolio_current(run_id: str, model_name: ModelName = "lgbm_ranker") -> PortfolioCurrentResponse:
    """Return latest portfolio allocations and rationale."""
    try:
        return get_portfolio_current(run_id=run_id, model_name=model_name)
    except ValueError as exc:
        detail = str(exc)
        if "Run backtest first" in detail:
            raise HTTPException(status_code=409, detail=detail) from exc
        raise HTTPException(status_code=404, detail=detail) from exc


@router.command(methods=["GET"], path="/feature/importance")
def feature_importance(run_id: str, model_name: ModelName = "lgbm_ranker") -> FeatureImportanceResponse:
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
def health(run_id: str | None = None, model_name: ModelName = "lgbm_ranker") -> DashboardHealthResponse:
    """Return dashboard health and run resolution metadata."""
    return get_dashboard_health(run_id=run_id, model_name=model_name)


@router.command(methods=["GET"], path="/performance/rolling")
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
def performance_regime(run_id: str, model_name: ModelName = "lgbm_ranker") -> PerformanceRegimeResponse:
    """Return regime breakdown for strategy performance."""
    try:
        return get_performance_regime(run_id=run_id, model_name=model_name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/portfolio/exposure")
def portfolio_exposure(run_id: str, model_name: ModelName = "lgbm_ranker") -> PortfolioExposureResponse:
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
        return get_portfolio_risk(run_id=run_id, model_name=model_name, lookback=lookback)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/model/ic_decay")
def model_ic_decay(
    run_id: str,
    model_name: ModelName = "lgbm_ranker",
    max_horizon: int = 20,
) -> ICDecayResponse:
    """Return IC decay across horizons."""
    try:
        return get_model_ic_decay(run_id=run_id, model_name=model_name, max_horizon=max_horizon)
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
        return get_prediction_distribution(run_id=run_id, model_name=model_name, bins=bins)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/regime/current")
def regime_current(run_id: str, model_name: ModelName = "lgbm_ranker") -> RegimeCurrentResponse:
    """Return current regime state."""
    try:
        return get_regime_current(run_id=run_id, model_name=model_name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/regime/history")
def regime_history(run_id: str, model_name: ModelName = "lgbm_ranker") -> RegimeHistoryResponse:
    """Return regime history timeline."""
    try:
        return get_regime_history(run_id=run_id, model_name=model_name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/alerts/current")
def alerts_current(run_id: str, model_name: ModelName = "lgbm_ranker") -> AlertsResponse:
    """Return current strategy alerts."""
    try:
        return get_alerts_current(run_id=run_id, model_name=model_name)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/alerts/history")
def alerts_history(run_id: str, model_name: ModelName = "lgbm_ranker", limit: int = 200) -> AlertsResponse:
    """Return strategy alerts history."""
    try:
        return get_alerts_history(run_id=run_id, model_name=model_name, limit=limit)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.command(methods=["POST"], path="/execution/orders/preview")
def execution_orders_preview(request: ExecutionOrderPreviewRequest) -> ExecutionPreviewResponse:
    """Preview paper execution orders for latest target portfolio."""
    try:
        return preview_execution_orders(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.command(methods=["POST"], path="/execution/orders/submit")
def execution_orders_submit(request: ExecutionOrderPreviewRequest) -> ExecutionSubmitResponse:
    """Submit paper execution orders and generate fills."""
    try:
        return submit_execution_orders(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.command(methods=["GET"], path="/execution/orders/current")
def execution_orders_current(run_id: str, model_name: ModelName = "lgbm_ranker") -> ExecutionOrdersResponse:
    """Return current paper execution order snapshot."""
    return get_execution_orders_current(run_id=run_id, model_name=model_name)


@router.command(methods=["GET"], path="/execution/fills/history")
def execution_fills_history(
    run_id: str,
    model_name: ModelName = "lgbm_ranker",
    limit: int = 200,
) -> ExecutionFillsResponse:
    """Return paper execution fills history."""
    return get_execution_fills_history(run_id=run_id, model_name=model_name, limit=limit)


@router.command(methods=["GET"], path="/execution/positions/current")
def execution_positions_current(run_id: str, model_name: ModelName = "lgbm_ranker") -> ExecutionPositionsResponse:
    """Return current paper execution positions."""
    return get_execution_positions_current(run_id=run_id, model_name=model_name)


@router.command(methods=["GET"], path="/execution/pnl")
def execution_pnl(run_id: str, model_name: ModelName = "lgbm_ranker") -> ExecutionPnlResponse:
    """Return paper execution PnL."""
    return get_execution_pnl(run_id=run_id, model_name=model_name)


@router.command(methods=["GET"], path="/risk/limits")
def risk_limits(run_id: str, model_name: ModelName = "lgbm_ranker") -> RiskLimitsResponse:
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
def risk_events(run_id: str, model_name: ModelName = "lgbm_ranker", limit: int = 200) -> RiskEventsResponse:
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
        return get_market_ratio_response(lhs=lhs, rhs=rhs, start=start, end=end, freq=freq, fill=fill)
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
