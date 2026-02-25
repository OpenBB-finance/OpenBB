"""Pydantic models for the Quant ML extension."""

from __future__ import annotations

from datetime import date
from typing import Any, Literal

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator

TrainRunStatus = Literal["queued", "running", "completed", "failed"]
SignalSide = Literal["buy", "hold", "sell"]
ModelName = Literal["xgb_lstm", "lgbm_ranker", "catboost_ranker"]
PortfolioMode = Literal["long_only", "long_short"]
MuMapping = Literal["z_score", "quantile_mean_return"]
TargetMode = Literal["close_to_close", "close_to_next_open", "next_open_to_close"]
EntryPriceMode = Literal["next_open", "close"]
ExitPriceMode = Literal["close", "next_open"]
CloseToNextOpenHorizonPolicy = Literal["fixed_1", "use_h"]
ModelChoice = Literal["lgbm_only", "xgb_only", "catboost_only", "dual"]
DashboardMode = Literal["live", "backtest"]
DashboardPayloadStatus = Literal["ok", "insufficient_data", "not_found"]
WorkflowRunStatus = Literal["queued", "running", "completed", "failed", "unknown"]
WalkForwardJobStatus = Literal["queued", "running", "completed", "failed", "not_found"]
PurgingMode = Literal["legacy_month_cutoff", "strict_label_overlap"]
HPOObjectiveMetric = Literal["val_ic", "validation_mse"]
OptimizerMode = Literal["mv", "cvar"]


class DateRange(BaseModel):
    """Date range model."""

    model_config = ConfigDict(populate_by_name=True)

    start_date: date = Field(validation_alias=AliasChoices("start_date", "start"))
    end_date: date = Field(validation_alias=AliasChoices("end_date", "end"))

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, end_date: date, info):  # noqa: ANN001
        """Validate end date is after start date."""
        start_date = info.data.get("start_date")
        if start_date and end_date <= start_date:
            raise ValueError("end_date must be after start_date")
        return end_date


class ModelConfig(BaseModel):
    """Model configuration for hybrid baseline."""

    seq_len: int = Field(default=60, ge=20, le=240)
    xgb_n_estimators: int = Field(default=400, ge=50, le=2000)
    xgb_max_depth: int = Field(default=4, ge=2, le=10)
    xgb_learning_rate: float = Field(default=0.03, gt=0, le=0.5)
    xgb_subsample: float = Field(default=0.9, gt=0, le=1.0)
    xgb_colsample_bytree: float = Field(default=0.9, gt=0, le=1.0)
    lstm_hidden_size: int = Field(default=64, ge=16, le=256)
    lstm_num_layers: int = Field(default=2, ge=1, le=4)
    lstm_dropout: float = Field(default=0.1, ge=0, le=0.5)
    lstm_epochs: int = Field(default=30, ge=5, le=300)
    lstm_batch_size: int = Field(default=128, ge=16, le=4096)
    lstm_learning_rate: float = Field(default=0.001, gt=0, le=0.1)
    train_val_split: float = Field(default=0.8, gt=0.5, lt=0.95)


class RankerConfig(BaseModel):
    """Learning-to-rank model configuration."""

    objective: Literal["rank_xendcg"] = "rank_xendcg"
    metric: Literal["ndcg"] = "ndcg"
    ndcg_eval_at: list[int] = Field(default_factory=lambda: [5, 10, 20])
    learning_rate: float = Field(default=0.03, gt=0, le=0.5)
    n_estimators: int = Field(default=6000, ge=100, le=20000)
    num_leaves: int = Field(default=63, ge=2, le=512)
    min_data_in_leaf: int = Field(default=300, ge=10, le=10000)
    subsample: float = Field(default=0.8, gt=0, le=1.0)
    colsample_bytree: float = Field(default=0.8, gt=0, le=1.0)
    reg_lambda: float = Field(default=10.0, ge=0, le=1000)
    random_state: int = 42
    early_stopping_rounds: int = Field(default=200, ge=10, le=2000)
    stacking_enabled: bool = False
    stacking_alpha: float = Field(default=1.0, ge=0.0, le=100.0)


class WalkForwardConfig(BaseModel):
    """Walk-forward split configuration."""

    train_months: int = Field(default=36, ge=6, le=240)
    embargo_months: int = Field(default=1, ge=0, le=12)
    val_months: int = Field(default=1, ge=1, le=12)
    step_months: int = Field(default=1, ge=1, le=12)
    purging_mode: PurgingMode = "legacy_month_cutoff"


class HPOConfig(BaseModel):
    """Hyperparameter optimization configuration."""

    enabled: bool = False
    n_trials: int = Field(default=25, ge=1, le=500)
    timeout_sec: int = Field(default=1800, ge=30, le=86400)
    objective_metric: HPOObjectiveMetric = "val_ic"
    random_state: int = 42


class SignalConfig(BaseModel):
    """Signal threshold selection configuration."""

    theta_grid: list[float] = Field(default_factory=lambda: [0.8, 1.0, 1.2, 1.5])
    selection_metric: Literal["val_sharpe"] = "val_sharpe"


class FeatureConfig(BaseModel):
    """Feature engineering configuration."""

    lags: list[int] = Field(default_factory=lambda: [1, 2, 3, 5, 10, 20])
    vol_windows: list[int] = Field(default_factory=lambda: [5, 20])
    momentum_windows: list[int] = Field(default_factory=lambda: [5, 20])
    include_rsi: bool = True
    include_macd: bool = True
    include_bollinger: bool = False
    bollinger_windows: list[int] = Field(default_factory=lambda: [20])
    include_atr: bool = False
    atr_windows: list[int] = Field(default_factory=lambda: [14])
    include_adx: bool = False
    adx_windows: list[int] = Field(default_factory=lambda: [14])
    include_obv: bool = False
    include_regime_features: bool = True
    include_residual_momentum: bool = False
    residual_momentum_windows: list[int] = Field(default_factory=lambda: [20])


class TrainRequest(BaseModel):
    """Training request."""

    model_config = ConfigDict(populate_by_name=True)

    symbols: list[str] | None = None
    universe_id: str | None = None
    date_range: DateRange
    horizon_days: int = Field(default=1, ge=1, le=31)
    target_mode: TargetMode = "next_open_to_close"
    close_to_next_open_horizon_policy: CloseToNextOpenHorizonPolicy = "fixed_1"
    include_macro_features: bool = True
    macro_feature_subset: list[str] = Field(
        default_factory=lambda: ["z_252", "yoy", "mom_3", "slope"]
    )
    model_parameters: ModelConfig = Field(
        default_factory=ModelConfig,
        validation_alias=AliasChoices("model_config", "model_parameters"),
        serialization_alias="model_config",
    )
    feature_parameters: FeatureConfig = Field(
        default_factory=FeatureConfig,
        validation_alias=AliasChoices("feature_config", "feature_parameters"),
        serialization_alias="feature_config",
    )
    training_mode: Literal["single", "dual_compare"] = "dual_compare"
    model_set: list[ModelName] = Field(
        default_factory=lambda: ["xgb_lstm", "lgbm_ranker"]
    )
    walk_forward_config: WalkForwardConfig = Field(default_factory=WalkForwardConfig)
    ranker_config: RankerConfig = Field(default_factory=RankerConfig)
    signal_config: SignalConfig = Field(default_factory=SignalConfig)
    portfolio_mode: PortfolioMode = "long_only"
    mu_mapping: MuMapping = "quantile_mean_return"
    quick_mode: bool = False
    model_choice: ModelChoice = "dual"
    early_stopping: bool = True
    feature_pruning: bool = False
    walk_forward_compact: bool = False
    cross_sectional_sampling: bool = False
    top_liquid_n: int | None = Field(default=None, ge=50, le=5000)
    market_data_workers: int | None = Field(default=None, ge=1, le=32)
    hpo_config: HPOConfig = Field(default_factory=HPOConfig)


class TrainResponse(BaseModel):
    """Training response."""

    run_id: str
    status: TrainRunStatus
    artifact_root: str
    created_at: str


class RunStatusResponse(BaseModel):
    """Run status response."""

    run_id: str
    run_uid: str | None = None
    status: TrainRunStatus
    progress: int = Field(ge=0, le=100)
    stage: str
    created_at: str
    updated_at: str
    last_heartbeat_at: str | None = None
    run_idle_minutes: float | None = None
    stale_timeout_minutes: int | None = None
    stale_reason: str | None = None
    logs_tail: list[str]
    error: str | None = None
    artifact_contract_version: str | None = None
    required_artifacts_ready: bool | None = None


class SignalRequest(BaseModel):
    """Signal generation request."""

    run_id: str
    model_name: ModelName = "lgbm_ranker"
    as_of_date: date | None = None
    top_k: int = Field(default=20, ge=1, le=200)
    score_threshold: float = Field(default=0.5, ge=0, le=5.0)
    balanced_long_short: bool = False


class SignalItem(BaseModel):
    """Single signal item."""

    symbol: str
    side: SignalSide
    predicted_return: float
    confidence: float
    reason_codes: list[str]
    z_score: float
    predicted_xgb: float | None = None
    predicted_lstm: float | None = None


class SignalResponse(BaseModel):
    """Signal response payload."""

    run_id: str
    model_name: ModelName = "lgbm_ranker"
    as_of_date: str
    latest_market_date: str | None = None
    staleness_days: int = 0
    recommended_portfolio_mode: PortfolioMode = "long_only"
    regime_snapshot: dict[str, str] = Field(default_factory=dict)
    signals: list[SignalItem]


class BacktestConstraints(BaseModel):
    """Backtest constraints."""

    max_weight: float = Field(default=0.2, gt=0, le=1.0)
    long_only: bool = True
    risk_aversion: float = Field(default=3.0, gt=0, le=20.0)
    lookback_days: int = Field(default=126, ge=60, le=756)
    optimizer_mode: OptimizerMode = "mv"
    cvar_alpha: float = Field(default=0.05, gt=0.0, lt=1.0)
    cvar_lambda: float = Field(default=3.0, gt=0.0, le=100.0)
    scenario_lookback_days: int = Field(default=252, ge=60, le=2520)


class BacktestRequest(BaseModel):
    """Backtest request."""

    model_config = ConfigDict(populate_by_name=True)

    run_id: str
    model_name: ModelName = "lgbm_ranker"
    start_date: date = Field(validation_alias=AliasChoices("start_date", "start"))
    end_date: date = Field(validation_alias=AliasChoices("end_date", "end"))
    rebalance: Literal["monthly"] = "monthly"
    constraints: BacktestConstraints = Field(default_factory=BacktestConstraints)
    cost_bps: float = Field(default=10.0, ge=0, le=1000)
    slippage_bps: float = Field(default=2.0, ge=0, le=1000)
    entry_price: EntryPriceMode = "next_open"
    exit_price: ExitPriceMode = "close"
    portfolio_mode: PortfolioMode = "long_only"
    mu_mapping: MuMapping = "quantile_mean_return"
    regime_policy: Literal["fixed", "mixed"] = "mixed"

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, end_date: date, info):  # noqa: ANN001
        """Validate end date is after start date."""
        start_date = info.data.get("start_date")
        if start_date and end_date <= start_date:
            raise ValueError("end_date must be after start_date")
        return end_date


class WalkForwardBacktestRequest(BaseModel):
    """Walk-forward backtest request."""

    model_config = ConfigDict(populate_by_name=True)

    run_id: str
    model_name: ModelName = "lgbm_ranker"
    start_date: date = Field(validation_alias=AliasChoices("start_date", "start"))
    end_date: date = Field(validation_alias=AliasChoices("end_date", "end"))
    rebalance: Literal["monthly"] = "monthly"
    constraints: BacktestConstraints = Field(default_factory=BacktestConstraints)
    cost_bps: float = Field(default=10.0, ge=0, le=1000)
    slippage_bps: float = Field(default=2.0, ge=0, le=1000)
    entry_price: EntryPriceMode = "next_open"
    exit_price: ExitPriceMode = "close"
    portfolio_mode: PortfolioMode = "long_only"
    regime_policy: Literal["fixed", "mixed"] = "mixed"
    min_history_days: int = Field(default=126, ge=60, le=1260)

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, end_date: date, info):  # noqa: ANN001
        """Validate end date is after start date."""
        start_date = info.data.get("start_date")
        if start_date and end_date <= start_date:
            raise ValueError("end_date must be after start_date")
        return end_date


class BacktestMetrics(BaseModel):
    """Backtest metrics."""

    cagr: float
    sharpe: float
    max_drawdown: float
    volatility: float
    turnover: float
    cvar_95: float = 0.0
    gross_return: float = 0.0
    total_cost: float = 0.0
    net_return: float = 0.0


class EquityPoint(BaseModel):
    """Equity curve point."""

    date: str
    equity: float
    daily_return: float
    gross_return: float = 0.0
    trading_cost: float = 0.0


class BenchmarkPoint(BaseModel):
    """Benchmark curve point."""

    date: str
    benchmark: float


class PeriodWeight(BaseModel):
    """Weight snapshot for a rebalance period."""

    date: str
    weights: dict[str, float]


class WeightDeltaItem(BaseModel):
    """One symbol-level weight delta row for a rebalance period."""

    symbol: str
    delta: float


class RebalanceHistoryItem(BaseModel):
    """One rebalance transition summary."""

    date: str
    added: list[str] = Field(default_factory=list)
    sold: list[str] = Field(default_factory=list)
    top_weight_increases: list[WeightDeltaItem] = Field(default_factory=list)
    top_weight_decreases: list[WeightDeltaItem] = Field(default_factory=list)
    turnover: float = 0.0
    binding_constraints: list[str] = Field(default_factory=list)
    previous_date: str | None = None


class BacktestResponse(BaseModel):
    """Backtest response."""

    run_id: str
    run_uid: str | None = None
    model_name: ModelName = "lgbm_ranker"
    start_date: str
    end_date: str
    base_index: float = 100.0
    benchmark_symbol: str
    metrics: BacktestMetrics
    equity_curve: list[EquityPoint]
    benchmark_curve: list[BenchmarkPoint]
    period_weights: list[PeriodWeight]
    cost_breakdown: list[dict[str, float | str]] = Field(default_factory=list)
    consistency_checks: dict[str, float | bool] = Field(default_factory=dict)
    regime_mode_by_period: list[dict[str, str]] = Field(default_factory=list)
    effective_constraints: dict[str, float | bool] = Field(default_factory=dict)
    cash_weight: float = 0.0
    cost_bps: float = 10.0
    slippage_bps: float = 2.0
    entry_price: EntryPriceMode = "next_open"
    exit_price: ExitPriceMode = "close"
    rebalance_history_summary: list[RebalanceHistoryItem] = Field(default_factory=list)
    constraint_violations: list[dict[str, Any]] = Field(default_factory=list)
    liquidity_clip_ratio: float = 0.0
    risk_contribution_max: float = 0.0
    universe_stage_counts: dict[str, int] = Field(default_factory=dict)
    weights_target_available: bool = False
    weights_final_available: bool = False
    constraint_binding_summary: list[dict[str, Any]] = Field(default_factory=list)
    artifact_contract_version: str | None = None
    required_artifacts_ready: bool = False


class WalkForwardBacktestSubmitResponse(BaseModel):
    """Walk-forward backtest submit response."""

    job_id: str
    status: WalkForwardJobStatus = "queued"
    run_id: str
    model_name: ModelName = "lgbm_ranker"
    created_at: str


class WalkForwardBacktestStatusResponse(BaseModel):
    """Walk-forward backtest status response."""

    job_id: str
    status: WalkForwardJobStatus = "queued"
    run_id: str
    model_name: ModelName = "lgbm_ranker"
    created_at: str | None = None
    updated_at: str | None = None
    artifact_root: str | None = None
    progress: int = Field(default=0, ge=0, le=100)
    metrics: BacktestMetrics | None = None
    message: str | None = None
    train_windows: list[dict[str, str]] = Field(default_factory=list)


class ArtifactSummaryResponse(BaseModel):
    """Artifacts summary response."""

    run_id: str
    model_name: ModelName = "lgbm_ranker"
    model_meta: dict
    latest_validation_error: float | None = None
    feature_importance: list[dict]
    params: dict
    available_artifacts: list[str]


class UniverseAsset(BaseModel):
    """Universe asset description."""

    symbol: str
    category: str


class UniverseResponse(BaseModel):
    """Universe response."""

    version: str
    assets: list[UniverseAsset]


class ModelPerformanceItem(BaseModel):
    """Per-model performance summary."""

    model_name: ModelName
    train_ic: float | None = None
    val_ic: float | None = None
    ndcg: float | None = None
    sharpe: float | None = None
    max_dd: float | None = None
    turnover: float | None = None
    hit_rate: float | None = None
    backend: str | None = None
    primary_backend: str | None = None
    stacked_v1: bool = False
    regime_performance: dict[str, float | int | None] = Field(default_factory=dict)


class ModelPerformanceResponse(BaseModel):
    """Model comparison payload."""

    run_id: str
    models: list[ModelPerformanceItem]


class ModelICPoint(BaseModel):
    """IC curve point."""

    date: str
    ic: float
    rolling_ic: float | None = None


class ModelICResponse(BaseModel):
    """Model IC payload."""

    run_id: str
    model_name: ModelName
    window: int
    points: list[ModelICPoint]


class ModelRegimeResponse(BaseModel):
    """Regime performance payload."""

    run_id: str
    model_name: ModelName
    regimes: dict[str, dict[str, float | int]]


class PortfolioSymbolWeightItem(BaseModel):
    """Portfolio symbol weight row."""

    symbol: str
    weight: float
    category: str
    name: str | None = None
    market: str | None = None
    sector_l1: str | None = None
    category_l2: str = "other"


class AssetClassWeightItem(BaseModel):
    """Portfolio aggregated category weight row."""

    category: str
    weight: float


class PortfolioRationale(BaseModel):
    """Rationale payload."""

    summary_lines: list[str]
    constraints_applied: dict[str, float | bool]


class PortfolioCurrentResponse(BaseModel):
    """Current portfolio payload."""

    run_id: str
    model_name: ModelName
    as_of_date: str | None = None
    total_weight: float
    symbol_weights: list[PortfolioSymbolWeightItem]
    asset_class_weights: list[AssetClassWeightItem]
    asset_class_weights_l1: list[AssetClassWeightItem] = Field(default_factory=list)
    rationale: PortfolioRationale
    last_rebalance_trades: RebalanceHistoryItem | None = None
    last_rebalance_turnover: float = 0.0


class RebalanceHistoryResponse(BaseModel):
    """Backtest rebalance timeline payload."""

    run_id: str
    model_name: ModelName
    items: list[RebalanceHistoryItem] = Field(default_factory=list)


class UniverseExclusionItem(BaseModel):
    """One excluded symbol row from universe staging."""

    symbol: str
    stage: Literal["u0", "u1", "u2"]
    reasons: list[str] = Field(default_factory=list)
    as_of_date: str | None = None
    company_id: str | None = None


class UniverseSnapshotResponse(BaseModel):
    """Universe snapshot payload for one run/as-of date."""

    run_id: str
    as_of_date: str
    universe_id: str
    stage_counts: dict[str, int] = Field(default_factory=dict)
    u0_symbols: list[str] = Field(default_factory=list)
    u1_symbols: list[str] = Field(default_factory=list)
    u2_symbols: list[str] = Field(default_factory=list)
    excluded: list[UniverseExclusionItem] = Field(default_factory=list)


class UniverseExclusionsResponse(BaseModel):
    """Latest universe exclusion list payload."""

    run_id: str
    items: list[UniverseExclusionItem] = Field(default_factory=list)


class PortfolioPolicyResponse(BaseModel):
    """Portfolio hard-policy payload."""

    template: str = "diversified_long_only"
    single_name_max_abs_weight: float = 0.04
    small_universe_policy: str = "cash_buffer"
    sector_concentration_max: float = 0.35
    turnover_max: float = 0.8
    gross_exposure_max: float = 1.0
    net_exposure_abs_max: float = 1.0
    cash_symbol: str = "CASH"
    cash_category: str = "cash_proxy"


class PromotedModelResponse(BaseModel):
    """Runtime promoted model pointer payload."""

    run_id: str | None = None
    model_name: ModelName = "lgbm_ranker"
    as_of_date: str | None = None
    feature_hash: str | None = None
    updated_at: str | None = None
    source: str = "fallback_registry"
    ready: bool = False


class FeatureImportanceResponse(BaseModel):
    """Feature importance payload."""

    run_id: str
    model_name: ModelName
    items: list[dict]


class PredictionsLatestResponse(BaseModel):
    """Latest predictions payload."""

    run_id: str
    model_name: ModelName
    as_of_date: str
    predictions: list[dict]


class WorkflowArtifactsReady(BaseModel):
    """Workflow artifact readiness flags."""

    predictions: bool = False
    signals: bool = False
    backtest: bool = False
    portfolio_current: bool = False


class WorkflowState(BaseModel):
    """Workflow run state for Quant Lab and Dashboard synchronization."""

    run_status: WorkflowRunStatus = "unknown"
    run_stage: str = ""
    run_progress: int = Field(default=0, ge=0, le=100)
    artifacts_ready: WorkflowArtifactsReady = Field(
        default_factory=WorkflowArtifactsReady
    )
    updated_at: str | None = None


class DashboardHealthResponse(BaseModel):
    """Dashboard health payload."""

    run_id: str | None = None
    model_name: ModelName | None = None
    status: DashboardPayloadStatus = "ok"
    message: str | None = None
    backend_connected: bool = True
    backend_source: str = "quant_ml_api"
    backend_detail: str = "quant_ml_api_connected"
    latest_run_id: str | None = None
    resolved_run_id: str | None = None
    promoted_run_id: str | None = None
    pretrain_ready: bool = False
    cache_warm_ratio: float = 0.0
    mode_supported: list[DashboardMode] = Field(
        default_factory=lambda: ["live", "backtest"]
    )
    data_timestamp: str | None = None
    latest_market_date: str | None = None
    staleness_days: int = 0
    recommended_portfolio_mode: PortfolioMode = "long_only"
    universe_size: int = 0
    cost_bps: float = 10.0
    cash_exposure: float = 0.0
    gross_exposure: float = 0.0
    net_exposure: float = 0.0
    strategy_health: dict[str, float] = Field(default_factory=dict)
    workflow_state: WorkflowState = Field(default_factory=WorkflowState)


class RollingPerformanceResponse(BaseModel):
    """Rolling performance payload."""

    run_id: str
    model_name: ModelName
    status: DashboardPayloadStatus = "ok"
    message: str | None = None
    window_short: int = 63
    window_long: int = 126
    cumulative_return: list[dict[str, float | str]] = Field(default_factory=list)
    rolling_sharpe_3m: list[dict[str, float | str]] = Field(default_factory=list)
    rolling_sharpe_6m: list[dict[str, float | str]] = Field(default_factory=list)
    rolling_ic_3m: list[dict[str, float | str]] = Field(default_factory=list)
    rolling_ic_6m: list[dict[str, float | str]] = Field(default_factory=list)
    rolling_maxdd: list[dict[str, float | str]] = Field(default_factory=list)
    turnover_ts: list[dict[str, float | str]] = Field(default_factory=list)
    exposure_ts: list[dict[str, float | str]] = Field(default_factory=list)


class PerformanceRegimeResponse(BaseModel):
    """Regime performance payload for dashboard."""

    run_id: str
    model_name: ModelName
    status: DashboardPayloadStatus = "ok"
    message: str | None = None
    trend_regime_perf: dict[str, dict[str, float | int]] = Field(default_factory=dict)
    vol_regime_perf: dict[str, dict[str, float | int]] = Field(default_factory=dict)
    liquidity_regime_perf: dict[str, dict[str, float | int]] = Field(
        default_factory=dict
    )
    matrix_2d: list[dict[str, float | str | int]] = Field(default_factory=list)


class PortfolioExposureResponse(BaseModel):
    """Portfolio exposure payload."""

    run_id: str
    model_name: ModelName
    status: DashboardPayloadStatus = "ok"
    message: str | None = None
    sector_exposure: list[AssetClassWeightItem] = Field(default_factory=list)
    factor_exposure: dict[str, float] = Field(default_factory=dict)
    beta_spy: float = 0.0
    beta_qqq: float = 0.0
    duration_estimate: float = 0.0
    top10_long: list[dict[str, float | str]] = Field(default_factory=list)
    top10_short: list[dict[str, float | str]] = Field(default_factory=list)


class PortfolioRiskResponse(BaseModel):
    """Portfolio risk payload."""

    run_id: str
    model_name: ModelName
    status: DashboardPayloadStatus = "ok"
    message: str | None = None
    vol_ex_ante: float = 0.0
    cvar_95: float = 0.0
    position_risk_contrib_top5: list[dict[str, float | str]] = Field(
        default_factory=list
    )
    position_risk_contrib_top10: list[dict[str, float | str]] = Field(
        default_factory=list
    )
    position_return_contrib_top5: list[dict[str, float | str]] = Field(
        default_factory=list
    )
    worst5_positions: list[dict[str, float | str]] = Field(default_factory=list)
    factor_exposure: dict[str, float] = Field(default_factory=dict)
    stress_test: dict[str, float] = Field(default_factory=dict)


class ICDecayResponse(BaseModel):
    """IC decay payload."""

    run_id: str
    model_name: ModelName
    status: DashboardPayloadStatus = "ok"
    message: str | None = None
    max_horizon: int
    ic_decay: list[dict[str, float | int]] = Field(default_factory=list)
    ic_t_stat: float = 0.0


class PredictionDistributionResponse(BaseModel):
    """Prediction distribution payload."""

    run_id: str
    model_name: ModelName
    status: DashboardPayloadStatus = "ok"
    message: str | None = None
    bins: int = 30
    histogram: list[dict[str, float | int]] = Field(default_factory=list)
    top_decile_mean: float = 0.0
    bottom_decile_mean: float = 0.0
    decile_spread_ts: list[dict[str, float | str]] = Field(default_factory=list)


class RegimeCurrentResponse(BaseModel):
    """Current regime payload."""

    run_id: str
    model_name: ModelName
    status: DashboardPayloadStatus = "ok"
    message: str | None = None
    trend_regime: str = "sideways"
    vol_regime: str = "mid"
    liquidity_regime: str = "mid"
    vix_level: float = 0.0
    breadth: float = 0.0
    spx_distance_200ma: float = 0.0


class RegimeHistoryResponse(BaseModel):
    """Regime history payload."""

    run_id: str
    model_name: ModelName
    status: DashboardPayloadStatus = "ok"
    message: str | None = None
    history: list[dict[str, float | str | int]] = Field(default_factory=list)
    regime_transition_stats: dict[str, float | int] = Field(default_factory=dict)


class AlertItem(BaseModel):
    """Strategy alert item."""

    rule_id: str
    severity: Literal["info", "warning", "critical"]
    triggered_at: str
    message: str
    value: float


class AlertsResponse(BaseModel):
    """Current/history alerts payload."""

    run_id: str
    model_name: ModelName
    status: DashboardPayloadStatus = "ok"
    message: str | None = None
    alerts: list[AlertItem] = Field(default_factory=list)


class ExecutionOrderPreviewRequest(BaseModel):
    """Paper execution preview request."""

    run_id: str
    model_name: ModelName = "lgbm_ranker"
    slippage_bps: float = Field(default=2.0, ge=0.0, le=1000.0)
    cost_bps: float | None = Field(default=None, ge=0.0, le=1000.0)
    nav: float | None = Field(default=None, ge=1000.0)


class ExecutionOrderItem(BaseModel):
    """Execution order row."""

    order_id: str
    symbol: str
    side: Literal["buy", "sell"]
    quantity: float
    current_weight: float
    target_weight: float
    est_price: float
    est_notional: float
    status: Literal["preview", "submitted", "filled", "rejected"] = "preview"


class ExecutionPreviewResponse(BaseModel):
    """Paper execution preview payload."""

    run_id: str
    model_name: ModelName
    status: DashboardPayloadStatus = "ok"
    message: str | None = None
    as_of_date: str | None = None
    nav: float = 0.0
    orders: list[ExecutionOrderItem] = Field(default_factory=list)
    estimated_turnover: float = 0.0


class ExecutionSubmitResponse(BaseModel):
    """Paper execution submit payload."""

    run_id: str
    model_name: ModelName
    status: DashboardPayloadStatus = "ok"
    message: str | None = None
    submitted_at: str | None = None
    orders: list[ExecutionOrderItem] = Field(default_factory=list)
    fills_count: int = 0
    cash_after: float = 0.0
    nav_after: float = 0.0
    kill_switch: bool = False


class ExecutionOrdersResponse(BaseModel):
    """Current paper execution orders payload."""

    run_id: str
    model_name: ModelName
    status: DashboardPayloadStatus = "ok"
    message: str | None = None
    orders: list[ExecutionOrderItem] = Field(default_factory=list)


class ExecutionFillsResponse(BaseModel):
    """Paper execution fills payload."""

    run_id: str
    model_name: ModelName
    status: DashboardPayloadStatus = "ok"
    message: str | None = None
    fills: list[dict[str, float | str]] = Field(default_factory=list)


class ExecutionPositionsResponse(BaseModel):
    """Paper execution positions payload."""

    run_id: str
    model_name: ModelName
    status: DashboardPayloadStatus = "ok"
    message: str | None = None
    as_of_date: str | None = None
    positions: list[dict[str, float | str]] = Field(default_factory=list)
    cash: float = 0.0
    gross_exposure: float = 0.0
    net_exposure: float = 0.0


class ExecutionPnlResponse(BaseModel):
    """Paper execution PnL payload."""

    run_id: str
    model_name: ModelName
    status: DashboardPayloadStatus = "ok"
    message: str | None = None
    as_of_date: str | None = None
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    total_pnl: float = 0.0
    return_pct: float = 0.0


class RiskLimitsResponse(BaseModel):
    """Risk limits payload."""

    run_id: str
    model_name: ModelName
    status: DashboardPayloadStatus = "ok"
    limits: dict[str, float] = Field(default_factory=dict)
    kill_switch: bool = False


class RiskPretradeRequest(BaseModel):
    """Pre-trade risk check request."""

    run_id: str
    model_name: ModelName = "lgbm_ranker"
    turnover_limit: float = Field(default=1.0, ge=0.0, le=10.0)


class RiskViolationItem(BaseModel):
    """Risk violation row."""

    rule_id: str
    severity: Literal["info", "warning", "critical"]
    value: float
    limit: float
    message: str


class RiskPretradeResponse(BaseModel):
    """Pre-trade risk check response."""

    run_id: str
    model_name: ModelName
    status: DashboardPayloadStatus = "ok"
    passed: bool = True
    kill_switch: bool = False
    violations: list[RiskViolationItem] = Field(default_factory=list)


class RiskEventsResponse(BaseModel):
    """Risk events payload."""

    run_id: str
    model_name: ModelName
    status: DashboardPayloadStatus = "ok"
    message: str | None = None
    events: list[dict[str, float | str]] = Field(default_factory=list)


class ModelShapResponse(BaseModel):
    """SHAP payload (phase-2 compatible)."""

    run_id: str
    model_name: ModelName
    status: DashboardPayloadStatus = "insufficient_data"
    message: str | None = "SHAP endpoint is in phase-2 rollout."
    summary_points: list[dict[str, float | str]] = Field(default_factory=list)
    dependence_top3: list[dict[str, float | str]] = Field(default_factory=list)
    feature_stability_ts: list[dict[str, float | str]] = Field(default_factory=list)


class OpsJobStateResponse(BaseModel):
    """One job state summary from job_state.json."""

    job: Literal["daily", "weekly", "monthly"]
    last_status: str = "unknown"
    last_run_id: str | None = None
    last_error: str | None = None
    steps: dict[str, dict[str, Any]] = Field(default_factory=dict)


class OpsStatusResponse(BaseModel):
    """Operational status payload for /ops dashboard."""

    status: DashboardPayloadStatus = "ok"
    message: str | None = None
    generated_at: str | None = None
    jobs: list[OpsJobStateResponse] = Field(default_factory=list)
    latest_publish: dict[str, Any] = Field(default_factory=dict)
    versions: dict[str, Any] = Field(default_factory=dict)
    latest_runs: list[dict[str, Any]] = Field(default_factory=list)
    macro_health: dict[str, Any] = Field(default_factory=dict)
    latest_training_run_id: str | None = None
    latest_daily_infer_date: str | None = None
    walkforward_queue_depth: int = 0
    active_job_locks: list[dict[str, Any]] = Field(default_factory=list)
    lock_health: dict[str, str] = Field(default_factory=dict)
    stale_policy: dict[str, Any] = Field(default_factory=dict)


class UniverseListItemResponse(BaseModel):
    """Universe list row."""

    id: str
    has_file: bool = False
    path: str | None = None
    count_hint: int = 0
    minimum_required: int = 0


class UniverseListResponse(BaseModel):
    """Universe list payload."""

    universes: list[UniverseListItemResponse] = Field(default_factory=list)


class UniverseResolveResponse(BaseModel):
    """Universe resolve payload."""

    universe_id: str
    mode: str = "train"
    count: int = 0
    minimum_required: int = 0
    meets_minimum: bool = True
    symbols: list[str] | None = None
    deprecated: bool = False
    replacement_id: str | None = None
    sunset_date: str | None = None


class ConstraintBindingItem(BaseModel):
    """Constraint binding summary row."""

    constraint_type: str
    binding_count: int = 0
    binding_ratio: float = 0.0


class ArtifactCompletenessItem(BaseModel):
    """Artifact contract completeness row."""

    artifact: str
    ready: bool = False
    path: str | None = None


class RunLatestMetaResponse(BaseModel):
    """Latest run meta alias payload."""

    run_id: str | None = None
    run_uid: str | None = None
    model_name: ModelName = "lgbm_ranker"
    as_of_date: str | None = None
    status: DashboardPayloadStatus = "ok"
    artifact_contract_version: str | None = None
    required_artifacts_ready: bool = False
    universe_stage_counts: dict[str, int] = Field(default_factory=dict)
    artifact_completeness: list[ArtifactCompletenessItem] = Field(default_factory=list)
    message: str | None = None


class RunLatestConstraintsResponse(BaseModel):
    """Latest run constraints alias payload."""

    run_id: str
    model_name: ModelName = "lgbm_ranker"
    status: DashboardPayloadStatus = "ok"
    message: str | None = None
    items: list[ConstraintBindingItem] = Field(default_factory=list)
    liquidity_clip_ratio: float = 0.0
    risk_contribution_max: float = 0.0
    top_risk_contribution: list[dict[str, float | str]] = Field(default_factory=list)
    liquidity_adv_top: list[dict[str, float | str]] = Field(default_factory=list)


class TrainResultV2(BaseModel):
    """Canonical train result contract."""

    run_id: str
    run_uid: str | None = None
    model_name: ModelName = "lgbm_ranker"
    universe_hash: str | None = None
    feature_hash: str | None = None
    config_hash: str | None = None
    train_start_utc: str | None = None
    train_end_utc: str | None = None
    validation_metrics: dict[str, float] = Field(default_factory=dict)
    artifact_uri: str | None = None
    data_version: str | None = None
    feature_version: str | None = None
    currency: str = "USD"


class BacktestResultV2(BaseModel):
    """Canonical backtest result contract."""

    run_id: str
    run_uid: str | None = None
    model_name: ModelName = "lgbm_ranker"
    equity_base: float = 1.0
    equity_curve: list[dict[str, float | str]] = Field(default_factory=list)
    returns_decimal: list[dict[str, float | str]] = Field(default_factory=list)
    cumulative_returns: list[dict[str, float | str]] = Field(default_factory=list)
    drawdown: list[dict[str, float | str]] = Field(default_factory=list)
    gross_exposure: list[dict[str, float | str]] = Field(default_factory=list)
    net_exposure: list[dict[str, float | str]] = Field(default_factory=list)
    positions: list[dict[str, float | str]] = Field(default_factory=list)
    trades: list[dict[str, float | str]] = Field(default_factory=list)
    turnover: list[dict[str, float | str]] = Field(default_factory=list)
    metrics: dict[str, float] = Field(default_factory=dict)
    asof_manifest: dict[str, Any] = Field(default_factory=dict)
    currency: str = "USD"


class WalkForwardFoldV2(BaseModel):
    """Canonical one-fold walk-forward result."""

    fold_id: str
    train_period: dict[str, str] = Field(default_factory=dict)
    test_period: dict[str, str] = Field(default_factory=dict)
    fold_metrics: dict[str, float] = Field(default_factory=dict)
    fold_equity: list[dict[str, float | str]] = Field(default_factory=list)
    asof_manifest_hash: str | None = None


class WalkForwardResultV2(BaseModel):
    """Canonical walk-forward result contract."""

    run_id: str
    run_uid: str | None = None
    model_name: ModelName = "lgbm_ranker"
    folds: list[WalkForwardFoldV2] = Field(default_factory=list)
    aggregate_metrics: dict[str, float] = Field(default_factory=dict)
    train_window_integrity: bool = True
    currency: str = "USD"


class ExecutionStateV2(BaseModel):
    """Canonical execution state contract."""

    run_id: str
    model_name: ModelName = "lgbm_ranker"
    portfolio_value: float = 0.0
    cash: float = 0.0
    positions_weight: list[dict[str, float | str]] = Field(default_factory=list)
    positions_quantity: list[dict[str, float | str]] = Field(default_factory=list)
    exposure: dict[str, float] = Field(default_factory=dict)
    risk_metrics: dict[str, float] = Field(default_factory=dict)
    last_rebalance_time_utc: str | None = None
    orders: list[dict[str, float | str]] = Field(default_factory=list)
    fills: list[dict[str, float | str]] = Field(default_factory=list)
    kill_switch: bool = False
    currency: str = "USD"


class DashboardSnapshotV2(BaseModel):
    """Canonical dashboard snapshot contract."""

    run_id: str
    run_uid: str | None = None
    model_name: ModelName = "lgbm_ranker"
    as_of_utc: str
    total_return: float = 0.0
    cagr: float = 0.0
    sharpe: float = 0.0
    sortino: float = 0.0
    max_drawdown: float = 0.0
    volatility: float = 0.0
    turnover: float = 0.0
    win_rate: float = 0.0
    exposure: dict[str, float] = Field(default_factory=dict)
    risk_contrib_top10: list[dict[str, float | str]] = Field(default_factory=list)
    constraint_bindings: list[ConstraintBindingItem] = Field(default_factory=list)
    ic_rolling: list[dict[str, float | str]] = Field(default_factory=list)
    currency: str = "USD"


class RunAuditEventItem(BaseModel):
    """One run-level audit event."""

    id: int | None = None
    run_id: str
    event_type: str
    severity: Literal["info", "warning", "critical"] = "info"
    payload: dict[str, Any] = Field(default_factory=dict)
    created_at_utc: str


class RunAuditResponse(BaseModel):
    """Run audit log response payload."""

    run_id: str
    status: DashboardPayloadStatus = "ok"
    message: str | None = None
    events: list[RunAuditEventItem] = Field(default_factory=list)
