"""Pydantic models for the Quant ML extension."""

from __future__ import annotations

from datetime import date
from typing import Any, Literal

from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
    model_validator,
)

TrainRunStatus = Literal["queued", "running", "completed", "failed"]
SignalSide = Literal["buy", "hold", "sell"]
ModelName = Literal["xgb_lstm", "lgbm_ranker", "catboost_ranker"]
PortfolioMode = Literal["long_only", "long_short"]
MuMapping = Literal["z_score", "quantile_mean_return", "ic_vol_scaled"]
TargetMode = Literal["close_to_close", "close_to_next_open", "next_open_to_close"]
EntryPriceMode = Literal["next_open", "close", "vwap_proxy"]
ExitPriceMode = Literal["close", "next_open", "next_close", "vwap_proxy"]
CloseToNextOpenHorizonPolicy = Literal["fixed_1", "use_h"]
ModelChoice = Literal["lgbm_only", "xgb_only", "catboost_only", "dual"]
DashboardMode = Literal["live", "backtest"]
SnapshotProfile = Literal["core", "full"]
DashboardPayloadStatus = Literal["ok", "insufficient_data", "not_found"]
WorkflowRunStatus = Literal["queued", "running", "completed", "failed", "unknown"]
WalkForwardJobStatus = Literal["queued", "running", "completed", "failed", "not_found"]
PurgingMode = Literal[
    "legacy_month_cutoff",
    "strict_label_overlap",
    "purged_group_kfold",
]
HPOObjectiveMetric = Literal["val_ic", "validation_mse"]
OptimizerMode = Literal["mv", "cvar", "sharpe", "risk_parity"]
SignalSelectionMode = Literal["z_threshold", "quantile"]
RiskVolMethod = Literal["ewma", "std"]
CovarianceMethod = Literal[
    "sample", "ewma", "ledoit_wolf", "ewma_shrink", "stat_factor_pca"
]
TurnoverPenaltyMode = Literal["none", "l1", "l2"]
MVOptimizerEngine = Literal["legacy_slsqp", "cvxpy", "auto"]
AlphaMappingMode = Literal["legacy_score", "ic_vol_scaled"]
QCStatus = Literal["NORMAL", "WARNING", "CRITICAL"]
ExecutionMode = Literal["paper", "shadow_live", "live_adapter"]


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
    purged_n_splits: int = Field(default=5, ge=2, le=24)
    purged_embargo_pct: float = Field(default=0.01, ge=0.0, le=0.5)


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
    include_stochastic: bool = False
    stochastic_k_period: int = Field(default=14, ge=5, le=120)
    stochastic_d_period: int = Field(default=3, ge=2, le=30)
    include_williams_r: bool = False
    williams_r_period: int = Field(default=14, ge=5, le=120)
    include_cci: bool = False
    cci_period: int = Field(default=20, ge=5, le=120)
    include_vwap_ratio: bool = False
    vwap_window: int = Field(default=20, ge=5, le=252)
    include_ichimoku_signal: bool = False
    include_fundamentals: bool = False
    include_sentiment: bool = False
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
    provider: str = "yfinance"
    fundamental_provider: str | None = None
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
    enable_hpo: bool | None = None
    hpo_n_trials: int | None = Field(default=None, ge=1, le=500)
    hpo_config: HPOConfig = Field(default_factory=HPOConfig)

    @field_validator("symbols")
    @classmethod
    def validate_symbol_limit(cls, symbols: list[str] | None):  # noqa: ANN001
        """Limit symbols count to prevent oversized training requests."""
        if symbols is None:
            return symbols
        if len(symbols) > 5000:
            raise ValueError("Maximum 5000 symbols allowed per training request")
        return symbols

    @model_validator(mode="after")
    def apply_hpo_legacy_fields(self) -> TrainRequest:
        """Map legacy HPO fields into the canonical hpo_config object."""
        if self.enable_hpo is not None:
            self.hpo_config.enabled = bool(self.enable_hpo)
        if self.hpo_n_trials is not None:
            self.hpo_config.n_trials = int(self.hpo_n_trials)
        return self


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
    dataset_version: str | None = None
    feature_set_version: str | None = None
    qc_status: QCStatus | None = None
    report_urls: list[str] = Field(default_factory=list)
    model_version: str | None = None


class RunListItem(BaseModel):
    """Recent run item for list endpoints."""

    run_id: str
    status: str = "unknown"
    stage: str = ""
    created_at: str | None = None
    updated_at: str | None = None
    actionable_backtest: bool = False


class RunListResponse(BaseModel):
    """Recent run list payload."""

    limit: int = 20
    runs: list[RunListItem] = Field(default_factory=list)


class SignalRequest(BaseModel):
    """Signal generation request."""

    run_id: str
    model_name: ModelName = "lgbm_ranker"
    as_of_date: date | None = None
    top_k: int = Field(default=20, ge=1, le=200)
    score_threshold: float = Field(default=0.5, ge=0, le=5.0)
    balanced_long_short: bool = False
    selection_mode: SignalSelectionMode = "quantile"
    q_long: float = Field(default=0.10, gt=0.0, le=0.5)
    q_short: float = Field(default=0.10, gt=0.0, le=0.5)
    use_hysteresis: bool = True
    entry_q_long: float = Field(default=0.10, gt=0.0, le=0.5)
    exit_q_long: float = Field(default=0.30, gt=0.0, le=1.0)
    entry_q_short: float = Field(default=0.10, gt=0.0, le=0.5)
    exit_q_short: float = Field(default=0.30, gt=0.0, le=1.0)
    min_hold_periods: int = Field(default=1, ge=0, le=12)
    liquidity_filter_enabled: bool = True
    min_adv_usd: float = Field(default=5_000_000.0, ge=0.0)
    min_price: float = Field(default=2.0, ge=0.0)
    winsorize_pct: float = Field(default=0.01, ge=0.0, le=0.2)
    use_robust_zscore: bool = True
    use_rank_gaussianization: bool = True
    neutralize_sector: bool = True
    neutralize_size: bool = True
    neutralize_beta: bool = False
    risk_scale_enabled: bool = True
    risk_vol_lookback: int = Field(default=60, ge=5, le=756)
    risk_vol_method: RiskVolMethod = "ewma"
    confidence_sizing_enabled: bool = True
    confidence_disagreement_scale: float = Field(default=1.0, gt=0.0, le=1000.0)


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
    mv_optimizer_engine: MVOptimizerEngine = "legacy_slsqp"
    optimizer_strict: bool = False
    cvar_alpha: float = Field(default=0.05, gt=0.0, lt=1.0)
    cvar_lambda: float = Field(default=3.0, gt=0.0, le=100.0)
    scenario_lookback_days: int = Field(default=252, ge=60, le=2520)
    cov_method: CovarianceMethod = "ewma_shrink"
    cov_ewma_halflife: int = Field(default=42, ge=2, le=252)
    cov_shrinkage: float = Field(default=0.15, ge=0.0, le=1.0)
    cov_pca_components: int = Field(default=10, ge=1, le=256)
    cov_pca_idio_floor: float = Field(default=1e-6, gt=0.0, le=1.0)
    commission_bps: float | None = Field(default=None, ge=0.0, le=1000.0)
    half_spread_bps: float | None = Field(default=None, ge=0.0, le=1000.0)
    impact_k: float = Field(default=10.0, ge=0.0, le=1000.0)
    borrow_bps: float = Field(default=100.0, ge=0.0, le=5000.0)
    turnover_penalty_mode: TurnoverPenaltyMode = "l2"
    turnover_penalty: float = Field(default=5.0, ge=0.0, le=10000.0)
    turnover_limit: float = Field(default=1.0, ge=0.0, le=10.0)
    gross_exposure_max: float = Field(default=1.5, ge=0.0, le=5.0)
    net_exposure_min: float = Field(default=-0.2, ge=-5.0, le=5.0)
    net_exposure_max: float = Field(default=1.0, ge=-5.0, le=5.0)
    sector_max_weight: float = Field(default=0.35, ge=0.0, le=1.0)
    sector_neutral: bool = False
    beta_neutral: bool = False
    beta_tolerance: float = Field(default=0.05, ge=0.0, le=1.0)
    min_bond_weight: float = Field(default=0.0, ge=0.0, le=1.0)
    target_vol: float | None = Field(default=None, ge=0.0, le=5.0)
    execution_cash_buffer: float = Field(default=0.0, ge=0.0, le=1.0)
    target_vol_lookback_days: int = Field(default=63, ge=20, le=2520)
    alpha_mapping_mode: AlphaMappingMode = "legacy_score"
    ic_lookback_days: int = Field(default=252, ge=20, le=2520)
    ic_ewma_halflife: int = Field(default=63, ge=2, le=2520)
    ic_clip_min: float = Field(default=-0.2, ge=-1.0, le=1.0)
    ic_clip_max: float = Field(default=0.2, ge=-1.0, le=1.0)
    ic_fallback: float = Field(default=0.03, ge=-1.0, le=1.0)
    alpha_ema_halflife_days: int = Field(default=0, ge=0, le=2520)
    trigger_rebalance_enabled: bool = False
    trigger_threshold_bps: float = Field(default=10.0, ge=0.0, le=5000.0)
    trigger_cost_multiplier: float = Field(default=1.0, ge=0.0, le=100.0)
    holding_period_days: int = Field(default=-1, ge=-1, le=252)
    leakage_guard: bool = True
    defensive_bucket_enabled: bool = False
    defensive_floor_mode: Literal["regime", "fixed"] = "regime"
    defensive_floor_fixed: float = Field(default=0.30, ge=0.0, le=1.0)
    defensive_floor_low: float | None = Field(default=None, ge=0.0, le=1.0)
    defensive_floor_mid: float | None = Field(default=None, ge=0.0, le=1.0)
    defensive_floor_high: float | None = Field(default=None, ge=0.0, le=1.0)
    defensive_floor_risk_off: float | None = Field(default=None, ge=0.0, le=1.0)
    defensive_risk_off_drawdown: float | None = Field(default=None, ge=0.0, le=1.0)
    defensive_postcheck_enabled: bool = True
    defensive_postcheck_cvar_limit: float | None = Field(default=None, ge=-5.0, le=5.0)
    defensive_postcheck_vol_limit: float | None = Field(default=None, ge=0.0, le=5.0)


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
    sortino: float = 0.0
    calmar: float = 0.0
    omega: float = 0.0
    max_consecutive_loss_days: int = 0
    max_drawdown: float
    volatility: float
    turnover: float
    annual_turnover: float = 0.0
    monthly_turnover: float = 0.0
    cvar_95: float = 0.0
    gross_return: float = 0.0
    total_cost: float = 0.0
    total_commission: float = 0.0
    total_spread_cost: float = 0.0
    total_impact_cost: float = 0.0
    total_borrow_cost: float = 0.0
    net_return: float = 0.0
    gross_exposure_avg: float = 0.0
    net_exposure_avg: float = 0.0
    long_exposure_avg: float = 0.0
    short_exposure_avg: float = 0.0
    ic_mean: float = 0.0
    ic_ir: float = 0.0
    rank_ic_mean: float = 0.0
    rank_ic_ir: float = 0.0


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
    triggered: bool | None = None
    trigger_reason: str | None = None
    utility_gain: float | None = None
    estimated_trigger_cost: float | None = None
    forced_rebalance: bool | None = None
    ic_hat: float | None = None
    defensive_floor_target: float | None = None
    defensive_weight_realized: float | None = None
    defensive_core_weight: float | None = None
    defensive_credit_weight: float | None = None
    risk_weight_realized: float | None = None
    postcheck_iterations: int | None = None
    postcheck_vol_ex_ante: float | None = None
    postcheck_cvar_ex_ante: float | None = None
    postcheck_actions: list[str] = Field(default_factory=list)


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
    monthly_returns: list[dict[str, float | int | str]] = Field(default_factory=list)
    period_weights: list[PeriodWeight]
    cost_breakdown: list[dict[str, float | str]] = Field(default_factory=list)
    consistency_checks: dict[str, float | bool] = Field(default_factory=dict)
    regime_mode_by_period: list[dict[str, str]] = Field(default_factory=list)
    effective_constraints: dict[str, float | bool | str | int | None] = Field(
        default_factory=dict
    )
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
    dataset_version: str | None = None
    feature_set_version: str | None = None
    qc_status: QCStatus | None = None
    regime_label: str | None = None
    regime_policy_applied: dict[str, Any] = Field(default_factory=dict)
    report_urls: list[str] = Field(default_factory=list)
    execution_mode: ExecutionMode = "paper"
    model_version: str | None = None


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
    dataset_version: str | None = None
    feature_set_version: str | None = None
    qc_status: QCStatus | None = None
    regime_label: str | None = None
    regime_policy_applied: dict[str, Any] = Field(default_factory=dict)
    report_urls: list[str] = Field(default_factory=list)
    execution_mode: ExecutionMode = "paper"
    model_version: str | None = None


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
    single_name_max_abs_weight: float = 0.06
    small_universe_policy: str = "cash_buffer"
    sector_concentration_max: float = 0.35
    turnover_max: float = 1.0
    gross_exposure_max: float = 1.0
    net_exposure_abs_max: float = 1.0
    min_bond_weight: float = 0.0
    execution_cash_buffer: float = 0.0
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
    alias: str = "champion"
    model_version: str | None = None
    dataset_version: str | None = None
    feature_set_version: str | None = None
    metrics: dict[str, Any] = Field(default_factory=dict)


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
    disk_free_gb: float = 0.0
    data_freshness_days: int | None = None
    last_successful_run_at: str | None = None
    fred_api_status: Literal["ok", "degraded", "unavailable"] = "unavailable"
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
    idempotency_key: str | None = None


class ExecutionModeUpdateRequest(BaseModel):
    """Execution mode update request."""

    run_id: str
    model_name: ModelName = "lgbm_ranker"
    mode: ExecutionMode = "paper"


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


class ExecutionBlockingConstraintItem(BaseModel):
    """Human-readable blocking item for execution workflows."""

    rule_id: str | None = None
    severity: str | None = None
    message: str | None = None
    reason: str
    target_route: str | None = None
    target_search: dict[str, str] = Field(default_factory=dict)


class OrderRationaleResponse(BaseModel):
    """Narrative execution rationale payload."""

    signal_rationale: str = ""
    macro_backdrop: str = ""
    risk_check_result: str = ""
    expected_turnover_cost: str = ""
    blocking_constraints: list[ExecutionBlockingConstraintItem] = Field(
        default_factory=list
    )
    source_run_id: str | None = None
    source_study_ids: list[str] = Field(default_factory=list)


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
    estimated_cost: float = 0.0
    rationale: OrderRationaleResponse = Field(default_factory=OrderRationaleResponse)
    blocking_constraints: list[ExecutionBlockingConstraintItem] = Field(
        default_factory=list
    )
    execution_mode: ExecutionMode = "paper"


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
    execution_mode: ExecutionMode = "paper"


class ExecutionOrdersResponse(BaseModel):
    """Current paper execution orders payload."""

    run_id: str
    model_name: ModelName
    status: DashboardPayloadStatus = "ok"
    message: str | None = None
    orders: list[ExecutionOrderItem] = Field(default_factory=list)
    execution_mode: ExecutionMode = "paper"


class ExecutionFillsResponse(BaseModel):
    """Paper execution fills payload."""

    run_id: str
    model_name: ModelName
    status: DashboardPayloadStatus = "ok"
    message: str | None = None
    fills: list[dict[str, float | str]] = Field(default_factory=list)
    execution_mode: ExecutionMode = "paper"


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
    execution_mode: ExecutionMode = "paper"


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
    execution_mode: ExecutionMode = "paper"


class RiskLimitsResponse(BaseModel):
    """Risk limits payload."""

    run_id: str
    model_name: ModelName
    status: DashboardPayloadStatus = "ok"
    limits: dict[str, float] = Field(default_factory=dict)
    kill_switch: bool = False
    execution_mode: ExecutionMode = "paper"


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
    blocking_summary: str | None = None
    execution_mode: ExecutionMode = "paper"


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
    data_quality: dict[str, Any] = Field(default_factory=dict)
    reports: list[dict[str, Any]] = Field(default_factory=list)
    model_registry: dict[str, Any] = Field(default_factory=dict)
    scheduler: dict[str, Any] = Field(default_factory=dict)
    notification_failures: list[dict[str, Any]] = Field(default_factory=list)
    execution_mode: dict[str, Any] = Field(default_factory=dict)


class WorkspaceActionItemResponse(BaseModel):
    """Action queue item for the workspace brief."""

    id: str
    title: str
    detail: str
    target_route: str
    target_search: dict[str, str] = Field(default_factory=dict)


class WorkspaceMacroStudyCardResponse(BaseModel):
    """Active macro study summary."""

    study_id: str | None = None
    name: str | None = None
    objective: str | None = None
    conclusion_summary: str | None = None
    linked_assets: list[str] = Field(default_factory=list)
    latest_feature_export: str | None = None
    latest_attached_report: str | None = None


class WorkspaceStrategyCandidateResponse(BaseModel):
    """Strategy candidate summary."""

    run_id: str | None = None
    model_name: str | None = None
    as_of_date: str | None = None
    feature_lineage: list[str] = Field(default_factory=list)
    promotion_readiness: str = "not_ready"
    training_window: str | None = None
    macro_study_links: list[str] = Field(default_factory=list)


class WorkspacePortfolioContributorResponse(BaseModel):
    """Top portfolio risk contributor."""

    symbol: str
    contribution: float = 0.0


class WorkspacePortfolioSnapshotResponse(BaseModel):
    """Portfolio risk summary."""

    run_id: str | None = None
    model_name: str | None = None
    vol_ex_ante: float = 0.0
    cvar_95: float = 0.0
    top_risk_contributors: list[WorkspacePortfolioContributorResponse] = Field(
        default_factory=list
    )
    blocked_constraints: list[str] = Field(default_factory=list)


class WorkspaceLatestReportResponse(BaseModel):
    """Latest report card summary."""

    report_id: int | None = None
    title: str | None = None
    report_type: str | None = None
    report_path: str | None = None
    created_at: str | None = None


class WorkspaceBriefResponse(BaseModel):
    """Aggregated workspace brief payload."""

    status: DashboardPayloadStatus = "ok"
    message: str | None = None
    generated_at: str | None = None
    active_macro_study: WorkspaceMacroStudyCardResponse = Field(
        default_factory=WorkspaceMacroStudyCardResponse
    )
    current_strategy_candidate: WorkspaceStrategyCandidateResponse = Field(
        default_factory=WorkspaceStrategyCandidateResponse
    )
    portfolio_snapshot: WorkspacePortfolioSnapshotResponse = Field(
        default_factory=WorkspacePortfolioSnapshotResponse
    )
    ops_issue_queue: list["OpsIssueItemResponse"] = Field(default_factory=list)
    latest_report: WorkspaceLatestReportResponse = Field(
        default_factory=WorkspaceLatestReportResponse
    )
    pending_actions: list[WorkspaceActionItemResponse] = Field(default_factory=list)


class DataQualityCheckResult(BaseModel):
    """One data quality check result."""

    check: str
    severity: QCStatus = "NORMAL"
    value: float | int | str | None = None
    threshold: float | int | str | None = None
    message: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class DataQualityLatestResponse(BaseModel):
    """Latest data quality payload."""

    run_id: str | None = None
    gate_name: str | None = None
    qc_status: QCStatus = "NORMAL"
    as_of_date: str | None = None
    created_at: str | None = None
    checks: list[DataQualityCheckResult] = Field(default_factory=list)
    summary: dict[str, Any] = Field(default_factory=dict)
    report_path: str | None = None


class DataQualityHistoryResponse(BaseModel):
    """Historical data quality payload."""

    items: list[DataQualityLatestResponse] = Field(default_factory=list)


class ExperimentRunItemResponse(BaseModel):
    """Experiment registry row."""

    run_id: str
    model_type: str | None = None
    dataset_version: str | None = None
    feature_set_version: str | None = None
    hyperparameters: dict[str, Any] = Field(default_factory=dict)
    feature_set: dict[str, Any] = Field(default_factory=dict)
    performance: dict[str, Any] = Field(default_factory=dict)
    artifact_uri: str | None = None
    status: str | None = None
    macro_study_links: list[str] = Field(default_factory=list)
    as_of_policy: str | None = None
    training_window: str | None = None
    constraints_summary: dict[str, Any] = Field(default_factory=dict)
    promotion_state: str | None = None
    created_at: str | None = None
    updated_at: str | None = None


class ExperimentListResponse(BaseModel):
    """Experiment list payload."""

    items: list[ExperimentRunItemResponse] = Field(default_factory=list)


class ModelRegistryEntryResponse(BaseModel):
    """One model registry entry."""

    alias: str
    run_id: str | None = None
    model_name: str | None = None
    model_version: str | None = None
    stage: str | None = None
    artifact_uri: str | None = None
    dataset_version: str | None = None
    feature_set_version: str | None = None
    metrics: dict[str, Any] = Field(default_factory=dict)
    source: str | None = None
    updated_at: str | None = None


class ModelRegistryHistoryResponse(BaseModel):
    """Model registry history payload."""

    items: list[ModelRegistryEntryResponse] = Field(default_factory=list)


class ReportRunItemResponse(BaseModel):
    """One generated report row."""

    id: int | None = None
    run_id: str | None = None
    report_type: str
    report_path: str
    status: str = "created"
    created_at: str | None = None
    title: str | None = None
    symbols: list[str] = Field(default_factory=list)
    summary: dict[str, Any] = Field(default_factory=dict)


class RunCompareItemResponse(BaseModel):
    """Strategy run comparison row."""

    run_id: str
    model_name: str | None = None
    training_window: str | None = None
    feature_set_version: str | None = None
    macro_study_links: list[str] = Field(default_factory=list)
    metrics: dict[str, Any] = Field(default_factory=dict)
    constraints_summary: dict[str, Any] = Field(default_factory=dict)
    promotion_state: str | None = None


class RunCompareResponse(BaseModel):
    """Run comparison payload."""

    items: list[RunCompareItemResponse] = Field(default_factory=list)


class OpsIssueItemResponse(BaseModel):
    """Human-readable ops issue row."""

    id: str
    severity: Literal["critical", "warning", "info"] = "info"
    title: str
    impact: str
    suggested_action: str
    target_route: str
    target_search: dict[str, str] = Field(default_factory=dict)
    source: str | None = None
    status: str = "open"


class OpsIssueQueueResponse(BaseModel):
    """Ops issue queue payload."""

    items: list[OpsIssueItemResponse] = Field(default_factory=list)


class ReportsLatestResponse(BaseModel):
    """Latest report payload."""

    item: ReportRunItemResponse | None = None


class ReportsHistoryResponse(BaseModel):
    """Historical report payload."""

    items: list[ReportRunItemResponse] = Field(default_factory=list)


class NotificationItemResponse(BaseModel):
    """Notification outbox row."""

    id: int
    run_id: str | None = None
    event_type: str
    channel: str
    fingerprint: str
    status: str
    payload: dict[str, Any] = Field(default_factory=dict)
    attempts: int = 0
    last_error: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    delivered_at: str | None = None


class NotificationsHistoryResponse(BaseModel):
    """Notification history payload."""

    items: list[NotificationItemResponse] = Field(default_factory=list)


class SchedulerStatusResponse(BaseModel):
    """Scheduler configuration and health payload."""

    timezone: str | None = None
    market_schedule: dict[str, Any] = Field(default_factory=dict)
    expected_jobs: list[str] = Field(default_factory=list)
    jobs: list[dict[str, Any]] = Field(default_factory=list)
    macro_scheduler: dict[str, Any] = Field(default_factory=dict)
    generated_at: str | None = None


class ExecutionModeResponse(BaseModel):
    """Execution mode payload."""

    run_id: str
    model_name: ModelName
    mode: ExecutionMode = "paper"
    live_adapter_enabled: bool = False
    broker_ready: bool = False
    kill_switch: bool = False
    updated_at: str | None = None


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
    snapshot_profile: SnapshotProfile = "full"
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
    regime_current: dict[str, str] = Field(default_factory=dict)
    alerts_current_count: int = 0
    constraint_summary: dict[str, float | int] = Field(default_factory=dict)
    artifact_summary: ArtifactSummaryResponse | None = None
    model_performance: ModelPerformanceResponse | None = None
    run_latest_meta: RunLatestMetaResponse | None = None
    currency: str = "USD"


class DashboardBootstrapResponse(BaseModel):
    """Dashboard bootstrap payload: health + snapshot in one call."""

    snapshot_profile: SnapshotProfile = "core"
    health: DashboardHealthResponse
    snapshot: DashboardSnapshotV2 | None = None


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


TradingRuntimeStatus = Literal["running", "paused", "stopped"]
TradingOrderStatus = Literal[
    "pending",
    "submitted",
    "filled",
    "partially_filled",
    "cancelled",
    "rejected",
]
TradingAlgorithmStatus = Literal[
    "draft",
    "dev",
    "sandbox",
    "validated",
    "active",
    "paused",
    "deprecated",
]


class TradingStatusResponse(BaseModel):
    """High-level trading console status payload."""

    mode: ExecutionMode = "paper"
    runtime_status: TradingRuntimeStatus = "stopped"
    last_scan_at: str | None = None
    last_order_at: str | None = None
    active_strategy_count: int = 0
    watchlist_size: int = 0
    open_position_count: int = 0
    today_signal_count: int = 0
    today_order_count: int = 0
    today_realized_pnl: float = 0.0
    cumulative_pnl: float = 0.0
    intraday_drawdown: float = 0.0
    used_capital: float = 0.0
    available_cash: float = 0.0
    report_urls: list[str] = Field(default_factory=list)
    execution_mode: ExecutionMode = "paper"
    model_version: str | None = None


class TradingStrategyConfigItemResponse(BaseModel):
    """One built-in strategy config row."""

    name: str
    version: str
    description: str | None = None
    enabled: bool = False
    parameters: dict[str, Any] = Field(default_factory=dict)


class TradingAlgorithmRecordResponse(BaseModel):
    """One custom algorithm registry row."""

    name: str
    version: str
    status: TradingAlgorithmStatus = "draft"
    active: bool = False
    sandbox_mode: bool = True
    signal_only: bool = True
    description: str | None = None
    parameters: dict[str, Any] = Field(default_factory=dict)
    required_columns: list[str] = Field(default_factory=list)
    validation_result: dict[str, Any] = Field(default_factory=dict)
    recent_run_result: dict[str, Any] = Field(default_factory=dict)
    recent_error: str | None = None
    performance_summary: dict[str, Any] = Field(default_factory=dict)
    last_run_at: str | None = None
    created_at: str | None = None
    modified_at: str | None = None


class TradingSettingsResponse(BaseModel):
    """Trading runtime settings payload."""

    version: str = "v1"
    tab_name: str = "Trading"
    mode: ExecutionMode = "paper"
    runtime_status: TradingRuntimeStatus = "stopped"
    universe_id: str = "default"
    schedule: dict[str, Any] = Field(default_factory=dict)
    scan: dict[str, Any] = Field(default_factory=dict)
    execution: dict[str, Any] = Field(default_factory=dict)
    account: dict[str, Any] = Field(default_factory=dict)
    risk: dict[str, Any] = Field(default_factory=dict)
    strategies: dict[str, Any] = Field(default_factory=dict)
    custom_algorithms: dict[str, Any] = Field(default_factory=dict)
    ui: dict[str, Any] = Field(default_factory=dict)
    built_in_strategies: list[TradingStrategyConfigItemResponse] = Field(default_factory=list)
    custom_algorithm_records: list[TradingAlgorithmRecordResponse] = Field(default_factory=list)


class TradingSettingsUpdateRequest(BaseModel):
    """Partial trading settings update request."""

    version: str | None = None
    mode: ExecutionMode | None = None
    runtime_status: TradingRuntimeStatus | None = None
    universe_id: str | None = None
    schedule: dict[str, Any] | None = None
    scan: dict[str, Any] | None = None
    execution: dict[str, Any] | None = None
    account: dict[str, Any] | None = None
    risk: dict[str, Any] | None = None
    strategies: dict[str, Any] | None = None
    custom_algorithms: dict[str, Any] | None = None
    ui: dict[str, Any] | None = None


class TradingCycleRunRequest(BaseModel):
    """Trading cycle execution request."""

    auto_execute: bool | None = None


class TradingCycleRunResponse(BaseModel):
    """Trading cycle execution result."""

    cycle_id: str
    status: str
    signal_count: int = 0
    order_count: int = 0
    fill_count: int = 0
    skipped_symbols: list[str] = Field(default_factory=list)
    report_path: str | None = None
    status_payload: TradingStatusResponse | None = None


class TradingSignalItemResponse(BaseModel):
    """One normalized signal row for the trading UI."""

    signal_id: str | None = None
    timestamp: str
    ticker: str
    name: str | None = None
    current_price: float = 0.0
    signal: str | None = None
    signal_type: str
    side: str
    strategy_name: str
    algorithm_version: str | None = None
    signal_strength: float = 0.0
    entry_score: float = 0.0
    priority: float = 0.0
    confidence: float = 0.0
    rsi: float = 0.0
    macd_hist: float = 0.0
    ma_relation: float = 0.0
    volume_change_pct: float = 0.0
    atr: float = 0.0
    recent_return: float = 0.0
    recommended_action: str = "Hold"
    position_held: bool = False
    risk_check_status: str = "UNKNOWN"
    risk_reason_codes: list[str] = Field(default_factory=list)
    reason: str | None = None
    sector: str | None = None


class TradingScanResponse(BaseModel):
    """Latest trading scan payload."""

    generated_at: str | None = None
    cycle_id: str | None = None
    signal_count: int = 0
    items: list[TradingSignalItemResponse] = Field(default_factory=list)


class TradingScanHistoryResponse(BaseModel):
    """Historical trading scan rows."""

    items: list[TradingSignalItemResponse] = Field(default_factory=list)


class TradingSymbolDetailResponse(BaseModel):
    """Symbol detail panel payload."""

    ticker: str
    series: list[dict[str, Any]] = Field(default_factory=list)
    signals: list[TradingSignalItemResponse] = Field(default_factory=list)
    orders: list[dict[str, Any]] = Field(default_factory=list)
    position: dict[str, Any] | None = None
    explanation: str | None = None
    related_studies: list[dict[str, Any]] = Field(default_factory=list)
    related_runs: list[dict[str, Any]] = Field(default_factory=list)
    latest_report_ids: list[int] = Field(default_factory=list)


class SymbolContextLinkResponse(BaseModel):
    """Back-link or related reference for Symbol Lab."""

    label: str
    target_route: str
    target_search: dict[str, str] = Field(default_factory=dict)


class SymbolContextResponse(BaseModel):
    """Cross-workflow Symbol Lab context payload."""

    symbol: str
    source: str | None = None
    linked_studies: list[dict[str, Any]] = Field(default_factory=list)
    related_runs: list[dict[str, Any]] = Field(default_factory=list)
    latest_signal: dict[str, Any] | None = None
    latest_order: dict[str, Any] | None = None
    latest_position: dict[str, Any] | None = None
    attached_reports: list[ReportRunItemResponse] = Field(default_factory=list)
    back_links: list[SymbolContextLinkResponse] = Field(default_factory=list)


class TradingOrderItemResponse(BaseModel):
    """One paper-trading order row."""

    order_id: str
    created_at: str | None = None
    ticker: str
    strategy_name: str
    algorithm_version: str | None = None
    status: TradingOrderStatus = "pending"
    side: str
    signal_type: str | None = None
    quantity: float = 0.0
    requested_price: float = 0.0
    filled_price: float | None = None
    notional: float = 0.0
    stop_loss: float | None = None
    take_profit: float | None = None
    trailing_stop: float | None = None
    reason: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class TradingOrdersResponse(BaseModel):
    """Trading order history payload."""

    items: list[TradingOrderItemResponse] = Field(default_factory=list)


class TradingFillsResponse(BaseModel):
    """Trading fill history payload."""

    items: list[dict[str, Any]] = Field(default_factory=list)


class TradingPositionsResponse(BaseModel):
    """Open position payload."""

    mode: ExecutionMode = "paper"
    items: list[dict[str, Any]] = Field(default_factory=list)


class TradingPerformanceResponse(BaseModel):
    """Paper-trading performance payload."""

    as_of_date: str | None = None
    generated_at: str | None = None
    equity: float = 0.0
    cash: float = 0.0
    used_capital: float = 0.0
    realized_pnl: float = 0.0
    unrealized_pnl: float = 0.0
    total_pnl: float = 0.0
    cumulative_return: float = 0.0
    daily_return: float = 0.0
    weekly_return: float = 0.0
    monthly_return: float = 0.0
    win_rate: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    profit_factor: float = 0.0
    sharpe: float = 0.0
    sortino: float = 0.0
    max_drawdown: float = 0.0
    turnover: float = 0.0
    avg_holding_period: float = 0.0
    strategy_contribution: dict[str, float] = Field(default_factory=dict)
    ticker_contribution: dict[str, float] = Field(default_factory=dict)
    equity_curve: list[dict[str, Any]] = Field(default_factory=list)
    drawdown_curve: list[dict[str, Any]] = Field(default_factory=list)
    daily_pnl: list[dict[str, Any]] = Field(default_factory=list)


class TradingRiskResponse(BaseModel):
    """Trading risk status payload."""

    generated_at: str | None = None
    limits: dict[str, Any] = Field(default_factory=dict)
    events: list[dict[str, Any]] = Field(default_factory=list)


class TradingEventsResponse(BaseModel):
    """Trading audit log payload."""

    items: list[dict[str, Any]] = Field(default_factory=list)


class TradingAlgorithmsResponse(BaseModel):
    """Trading custom algorithm registry payload."""

    items: list[TradingAlgorithmRecordResponse] = Field(default_factory=list)


class TradingAlgorithmToggleRequest(BaseModel):
    """Algorithm toggle request."""

    name: str
    version: str | None = None
    active: bool | None = None
    sandbox_mode: bool | None = None
    signal_only: bool | None = None
    status: TradingAlgorithmStatus | None = None


class TradingAlgorithmValidateRequest(BaseModel):
    """Algorithm validation request."""

    name: str
    version: str | None = None


class TradingAlgorithmValidationResponse(BaseModel):
    """Algorithm validation result."""

    name: str
    version: str
    status: str
    passed: bool
    summary: dict[str, Any] = Field(default_factory=dict)
    checks: list[dict[str, Any]] = Field(default_factory=list)
    report_path: str | None = None
    created_at: str | None = None


class TradingExecutionModeResponse(BaseModel):
    """Trading execution mode payload."""

    mode: ExecutionMode = "paper"
    live_adapter_enabled: bool = False
    broker_ready: bool = False
    kill_switch: bool = False
    updated_at: str | None = None


class TradingExecutionModeUpdateRequest(BaseModel):
    """Trading execution mode update request."""

    mode: ExecutionMode = "paper"
