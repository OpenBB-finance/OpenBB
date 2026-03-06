export type TrainRunStatus = "queued" | "running" | "completed" | "failed";
export type SignalSide = "buy" | "hold" | "sell";
export const MODEL_NAMES = ["xgb_lstm", "lgbm_ranker", "catboost_ranker"] as const;
export type ModelName = (typeof MODEL_NAMES)[number];
export type PortfolioMode = "long_only" | "long_short";
export type MuMapping = "z_score" | "quantile_mean_return" | "ic_vol_scaled";
export type TargetMode = "close_to_close" | "close_to_next_open" | "next_open_to_close";
export type EntryPriceMode = "next_open" | "close";
export type ExitPriceMode = "close" | "next_open";
export type CloseToNextOpenHorizonPolicy = "fixed_1" | "use_h";
export type ModelChoice = "lgbm_only" | "xgb_only" | "catboost_only" | "dual";
export type DashboardMode = "live" | "backtest";
export type SnapshotProfile = "core" | "full";
export type WorkflowRunStatus = "queued" | "running" | "completed" | "failed" | "unknown";
export type WalkForwardJobStatus = "queued" | "running" | "completed" | "failed" | "not_found";
export type PurgingMode =
  | "legacy_month_cutoff"
  | "strict_label_overlap"
  | "purged_group_kfold";
export type HPOObjectiveMetric = "val_ic" | "validation_mse";
export type OptimizerMode = "mv" | "cvar" | "sharpe" | "risk_parity";
export type MVOptimizerEngine = "legacy_slsqp" | "cvxpy" | "auto";
export type QCStatus = "NORMAL" | "WARNING" | "CRITICAL";
export type ExecutionMode = "paper" | "shadow_live" | "live_adapter";
export type CovarianceMethod =
  | "sample"
  | "ewma"
  | "ledoit_wolf"
  | "ewma_shrink"
  | "stat_factor_pca";
export type AlphaMappingMode = "legacy_score" | "ic_vol_scaled";

export interface UniverseAsset {
  symbol: string;
  category: string;
}

export interface UniverseResponse {
  version: string;
  assets: UniverseAsset[];
}

export interface UniverseListItemPayload {
  id: string;
  has_file: boolean;
  path?: string | null;
  count_hint: number;
  minimum_required?: number;
}

export interface UniverseListPayload {
  universes: UniverseListItemPayload[];
}

export interface UniverseResolvePayload {
  universe_id: string;
  mode: string;
  count: number;
  minimum_required?: number;
  meets_minimum?: boolean;
  symbols?: string[] | null;
  deprecated?: boolean;
  replacement_id?: string | null;
  sunset_date?: string | null;
}

export interface DateRangeInput {
  start: string;
  end: string;
}

export interface ModelConfigInput {
  seq_len: number;
  xgb_n_estimators: number;
  xgb_max_depth: number;
  xgb_learning_rate: number;
  xgb_subsample: number;
  xgb_colsample_bytree: number;
  lstm_hidden_size: number;
  lstm_num_layers: number;
  lstm_dropout: number;
  lstm_epochs: number;
  lstm_batch_size: number;
  lstm_learning_rate: number;
  train_val_split: number;
}

export interface RankerConfigInput {
  objective: "rank_xendcg";
  metric: "ndcg";
  ndcg_eval_at: number[];
  learning_rate: number;
  n_estimators: number;
  num_leaves: number;
  min_data_in_leaf: number;
  subsample: number;
  colsample_bytree: number;
  reg_lambda: number;
  random_state: number;
  early_stopping_rounds: number;
  stacking_enabled?: boolean;
  stacking_alpha?: number;
}

export interface WalkForwardConfigInput {
  train_months: number;
  embargo_months: number;
  val_months: number;
  step_months: number;
  purging_mode?: PurgingMode;
  purged_n_splits?: number;
  purged_embargo_pct?: number;
}

export interface SignalConfigInput {
  theta_grid: number[];
  selection_metric: "val_sharpe";
}

export interface HPOConfigInput {
  enabled?: boolean;
  n_trials?: number;
  timeout_sec?: number;
  objective_metric?: HPOObjectiveMetric;
  random_state?: number;
}

export interface FeatureConfigInput {
  lags: number[];
  vol_windows: number[];
  momentum_windows: number[];
  include_rsi: boolean;
  include_macd: boolean;
  include_bollinger?: boolean;
  bollinger_windows?: number[];
  include_atr?: boolean;
  atr_windows?: number[];
  include_adx?: boolean;
  adx_windows?: number[];
  include_obv?: boolean;
  include_stochastic?: boolean;
  stochastic_k_period?: number;
  stochastic_d_period?: number;
  include_williams_r?: boolean;
  williams_r_period?: number;
  include_cci?: boolean;
  cci_period?: number;
  include_vwap_ratio?: boolean;
  vwap_window?: number;
  include_ichimoku_signal?: boolean;
  include_fundamentals?: boolean;
  include_sentiment?: boolean;
  include_regime_features: boolean;
  include_residual_momentum?: boolean;
  residual_momentum_windows?: number[];
}

export interface TrainRequestPayload {
  symbols?: string[];
  universe_id?: string;
  date_range: DateRangeInput;
  horizon_days: number;
  target_mode?: TargetMode;
  close_to_next_open_horizon_policy?: CloseToNextOpenHorizonPolicy;
  include_macro_features?: boolean;
  macro_feature_subset?: string[];
  provider?: string;
  fundamental_provider?: string;
  model_config: ModelConfigInput;
  feature_config: FeatureConfigInput;
  training_mode?: "single" | "dual_compare";
  model_set?: ModelName[];
  walk_forward_config?: WalkForwardConfigInput;
  ranker_config?: RankerConfigInput;
  signal_config?: SignalConfigInput;
  portfolio_mode?: PortfolioMode;
  mu_mapping?: MuMapping;
  quick_mode?: boolean;
  model_choice?: ModelChoice;
  early_stopping?: boolean;
  feature_pruning?: boolean;
  walk_forward_compact?: boolean;
  cross_sectional_sampling?: boolean;
  top_liquid_n?: number;
  enable_hpo?: boolean;
  hpo_n_trials?: number;
  hpo_config?: HPOConfigInput;
}

export interface TrainResponsePayload {
  run_id: string;
  status: TrainRunStatus;
  artifact_root: string;
  created_at: string;
}

export interface RunStatusPayload {
  run_id: string;
  run_uid?: string | null;
  status: TrainRunStatus;
  progress: number;
  stage: string;
  created_at: string;
  updated_at: string;
  last_heartbeat_at?: string | null;
  run_idle_minutes?: number | null;
  stale_timeout_minutes?: number | null;
  stale_reason?: string | null;
  logs_tail: string[];
  error?: string | null;
  artifact_contract_version?: string | null;
  required_artifacts_ready?: boolean | null;
  dataset_version?: string | null;
  feature_set_version?: string | null;
  qc_status?: QCStatus | null;
  report_urls?: string[];
  model_version?: string | null;
}

export interface RunListItemPayload {
  run_id: string;
  status: string;
  stage: string;
  created_at?: string | null;
  updated_at?: string | null;
  actionable_backtest?: boolean;
}

export interface RunListPayload {
  limit: number;
  runs: RunListItemPayload[];
}

export interface SignalItem {
  symbol: string;
  side: SignalSide;
  predicted_return: number;
  confidence: number;
  reason_codes: string[];
  z_score: number;
  predicted_xgb?: number | null;
  predicted_lstm?: number | null;
}

export interface SignalsResponsePayload {
  run_id: string;
  model_name: ModelName;
  as_of_date: string;
  signals: SignalItem[];
}

export interface SignalsRequestPayload {
  run_id: string;
  model_name: ModelName;
  as_of_date?: string;
  top_k: number;
  score_threshold: number;
  balanced_long_short?: boolean;
}

export interface BacktestConstraintsInput {
  max_weight: number;
  long_only: boolean;
  risk_aversion: number;
  lookback_days: number;
  optimizer_mode?: OptimizerMode;
  mv_optimizer_engine?: MVOptimizerEngine;
  optimizer_strict?: boolean;
  cvar_alpha?: number;
  cvar_lambda?: number;
  scenario_lookback_days?: number;
  cov_method?: CovarianceMethod;
  cov_ewma_halflife?: number;
  cov_shrinkage?: number;
  cov_pca_components?: number;
  cov_pca_idio_floor?: number;
  alpha_mapping_mode?: AlphaMappingMode;
  ic_lookback_days?: number;
  ic_ewma_halflife?: number;
  ic_clip_min?: number;
  ic_clip_max?: number;
  ic_fallback?: number;
  alpha_ema_halflife_days?: number;
  trigger_rebalance_enabled?: boolean;
  trigger_threshold_bps?: number;
  trigger_cost_multiplier?: number;
  commission_bps?: number;
  half_spread_bps?: number;
  impact_k?: number;
  borrow_bps?: number;
  turnover_penalty_mode?: "none" | "l1" | "l2";
  turnover_penalty?: number;
  turnover_limit?: number;
  gross_exposure_max?: number;
  net_exposure_min?: number;
  net_exposure_max?: number;
  sector_max_weight?: number;
  min_bond_weight?: number;
  execution_cash_buffer?: number;
}

export interface BacktestRequestPayload {
  run_id: string;
  model_name: ModelName;
  start: string;
  end: string;
  rebalance: "monthly";
  constraints: BacktestConstraintsInput;
  cost_bps: number;
  slippage_bps?: number;
  entry_price?: EntryPriceMode;
  exit_price?: ExitPriceMode;
  portfolio_mode?: PortfolioMode;
  mu_mapping?: MuMapping;
}

export interface WalkForwardBacktestRequestPayload {
  run_id: string;
  model_name: ModelName;
  start: string;
  end: string;
  rebalance: "monthly";
  constraints: BacktestConstraintsInput;
  cost_bps: number;
  slippage_bps?: number;
  entry_price?: EntryPriceMode;
  exit_price?: ExitPriceMode;
  portfolio_mode?: PortfolioMode;
  regime_policy?: "fixed" | "mixed";
  min_history_days?: number;
}

export interface BacktestMetrics {
  cagr: number;
  sharpe: number;
  sortino?: number;
  calmar?: number;
  omega?: number;
  max_consecutive_loss_days?: number;
  max_drawdown: number;
  volatility: number;
  turnover: number;
  cvar_95?: number;
}

export interface MonthlyReturnPoint {
  year: number;
  month: number;
  return: number;
}

export interface EquityCurvePoint {
  date: string;
  equity: number;
  daily_return: number;
}

export interface BenchmarkCurvePoint {
  date: string;
  benchmark: number;
}

export interface PeriodWeightsPoint {
  date: string;
  weights: Record<string, number>;
}

export interface WeightDeltaItem {
  symbol: string;
  delta: number;
}

export interface RebalanceHistoryItem {
  date: string;
  previous_date?: string | null;
  added: string[];
  sold: string[];
  top_weight_increases: WeightDeltaItem[];
  top_weight_decreases: WeightDeltaItem[];
  turnover: number;
  binding_constraints: string[];
  triggered?: boolean | null;
  trigger_reason?: string | null;
  utility_gain?: number | null;
  estimated_trigger_cost?: number | null;
  forced_rebalance?: boolean | null;
  ic_hat?: number | null;
}

export interface BacktestResponsePayload {
  run_id: string;
  run_uid?: string | null;
  model_name: ModelName;
  start_date: string;
  end_date: string;
  base_index: number;
  benchmark_symbol: string;
  metrics: BacktestMetrics;
  equity_curve: EquityCurvePoint[];
  benchmark_curve: BenchmarkCurvePoint[];
  monthly_returns?: MonthlyReturnPoint[];
  period_weights: PeriodWeightsPoint[];
  effective_constraints?: Record<string, number | boolean | string | null>;
  cash_weight?: number;
  rebalance_history_summary?: RebalanceHistoryItem[];
  constraint_violations?: Array<Record<string, unknown>>;
  liquidity_clip_ratio?: number;
  risk_contribution_max?: number;
  universe_stage_counts?: Record<string, number>;
  weights_target_available?: boolean;
  weights_final_available?: boolean;
  constraint_binding_summary?: Array<{
    constraint_type: string;
    binding_count: number;
    binding_ratio: number;
  }>;
  artifact_contract_version?: string | null;
  required_artifacts_ready?: boolean;
  dataset_version?: string | null;
  feature_set_version?: string | null;
  qc_status?: QCStatus | null;
  regime_label?: string | null;
  regime_policy_applied?: Record<string, unknown>;
  report_urls?: string[];
  execution_mode?: ExecutionMode;
  model_version?: string | null;
}

export interface WalkForwardBacktestSubmitPayload {
  job_id: string;
  status: WalkForwardJobStatus;
  run_id: string;
  model_name: ModelName;
  created_at: string;
}

export interface WalkForwardBacktestStatusPayload {
  job_id: string;
  status: WalkForwardJobStatus;
  run_id: string;
  model_name: ModelName;
  created_at?: string | null;
  updated_at?: string | null;
  artifact_root?: string | null;
  progress: number;
  metrics?: BacktestMetrics | null;
  message?: string | null;
  train_windows: Array<{ rebalance_date: string; train_until: string }>;
}

export interface ArtifactSummaryPayload {
  run_id: string;
  model_name: ModelName;
  model_meta: Record<string, unknown>;
  latest_validation_error?: number | null;
  feature_importance: Array<{ feature: string; importance: number }>;
  params: Record<string, unknown>;
  available_artifacts: string[];
}

export interface ModelPerformanceItem {
  model_name: ModelName;
  train_ic?: number | null;
  val_ic?: number | null;
  ndcg?: number | null;
  sharpe?: number | null;
  max_dd?: number | null;
  turnover?: number | null;
  hit_rate?: number | null;
  backend?: string | null;
  primary_backend?: string | null;
  stacked_v1?: boolean;
  regime_performance?: Record<string, number | string | null>;
}

export interface ModelPerformancePayload {
  run_id: string;
  models: ModelPerformanceItem[];
}

export interface ModelICPoint {
  date: string;
  ic: number;
  rolling_ic?: number | null;
}

export interface ModelICPayload {
  run_id: string;
  model_name: ModelName;
  window: number;
  points: ModelICPoint[];
}

export interface ModelRegimePayload {
  run_id: string;
  model_name: ModelName;
  regimes: Record<string, Record<string, number>>;
}

export interface PortfolioSymbolWeightItem {
  symbol: string;
  weight: number;
  category: string;
  name?: string | null;
  market?: string | null;
  sector_l1?: string | null;
  category_l2?: string | null;
}

export interface AssetClassWeightItem {
  category: string;
  weight: number;
}

export interface PortfolioRationalePayload {
  summary_lines: string[];
  constraints_applied: Record<string, number | boolean>;
}

export interface PortfolioCurrentPayload {
  run_id: string;
  model_name: ModelName;
  as_of_date?: string | null;
  total_weight: number;
  symbol_weights: PortfolioSymbolWeightItem[];
  asset_class_weights: AssetClassWeightItem[];
  asset_class_weights_l1?: AssetClassWeightItem[];
  rationale: PortfolioRationalePayload;
  last_rebalance_trades?: RebalanceHistoryItem | null;
  last_rebalance_turnover?: number;
  dataset_version?: string | null;
  feature_set_version?: string | null;
  qc_status?: QCStatus | null;
  regime_label?: string | null;
  regime_policy_applied?: Record<string, unknown>;
  report_urls?: string[];
  execution_mode?: ExecutionMode;
  model_version?: string | null;
}

export interface RebalanceHistoryPayload {
  run_id: string;
  model_name: ModelName;
  items: RebalanceHistoryItem[];
}

export interface UniverseExclusionItemPayload {
  symbol: string;
  stage: "u0" | "u1" | "u2";
  reasons: string[];
  as_of_date?: string | null;
  company_id?: string | null;
}

export interface UniverseSnapshotPayload {
  run_id: string;
  as_of_date: string;
  universe_id: string;
  stage_counts: Record<string, number>;
  u0_symbols: string[];
  u1_symbols: string[];
  u2_symbols: string[];
  excluded: UniverseExclusionItemPayload[];
}

export interface UniverseExclusionsPayload {
  run_id: string;
  items: UniverseExclusionItemPayload[];
}

export interface PortfolioPolicyPayload {
  template: string;
  single_name_max_abs_weight: number;
  small_universe_policy: string;
  sector_concentration_max: number;
  turnover_max: number;
  gross_exposure_max: number;
  net_exposure_abs_max: number;
  min_bond_weight?: number;
  execution_cash_buffer?: number;
  cash_symbol: string;
  cash_category: string;
}

export interface PromotedModelPayload {
  run_id?: string | null;
  model_name: ModelName;
  as_of_date?: string | null;
  feature_hash?: string | null;
  updated_at?: string | null;
  source: string;
  ready: boolean;
  alias?: string;
  model_version?: string | null;
  dataset_version?: string | null;
  feature_set_version?: string | null;
  metrics?: Record<string, unknown>;
}

export interface FeatureImportancePayload {
  run_id: string;
  model_name: ModelName;
  items: Array<{ feature?: string; importance?: number }>;
}

export interface PredictionsLatestPayload {
  run_id: string;
  model_name: ModelName;
  as_of_date: string;
  predictions: Array<Record<string, unknown>>;
}

export type DashboardPayloadStatus = "ok" | "insufficient_data" | "not_found";

export interface DashboardHealthPayload {
  run_id?: string | null;
  model_name?: ModelName | null;
  status: DashboardPayloadStatus;
  message?: string | null;
  backend_connected: boolean;
  backend_source: string;
  backend_detail: string;
  latest_run_id?: string | null;
  resolved_run_id?: string | null;
  promoted_run_id?: string | null;
  pretrain_ready?: boolean;
  cache_warm_ratio?: number;
  mode_supported: DashboardMode[];
  data_timestamp?: string | null;
  latest_market_date?: string | null;
  staleness_days?: number;
  disk_free_gb?: number;
  data_freshness_days?: number | null;
  last_successful_run_at?: string | null;
  fred_api_status?: "ok" | "degraded" | "unavailable";
  recommended_portfolio_mode?: PortfolioMode;
  universe_size: number;
  cost_bps: number;
  cash_exposure: number;
  gross_exposure: number;
  net_exposure: number;
  strategy_health: Record<string, number>;
  workflow_state?: WorkflowStatePayload;
}

export interface DashboardBootstrapPayload {
  snapshot_profile: SnapshotProfile;
  health: DashboardHealthPayload;
  snapshot: RunSnapshotPayload | null;
}

export interface WorkflowArtifactsReadyPayload {
  predictions: boolean;
  signals: boolean;
  backtest: boolean;
  portfolio_current: boolean;
}

export interface WorkflowStatePayload {
  run_status: WorkflowRunStatus;
  run_stage: string;
  run_progress: number;
  artifacts_ready: WorkflowArtifactsReadyPayload;
  updated_at?: string | null;
}

export interface QuantSessionState {
  run_id: string;
  model_name: ModelName;
  mode: DashboardMode;
  run_status: WorkflowRunStatus;
  run_stage: string;
  run_progress: number;
  artifacts_ready: WorkflowArtifactsReadyPayload;
  data_timestamp?: string | null;
  updated_at?: string | null;
}

export interface TimeSeriesPoint {
  date: string;
  value: number;
}

export interface ExposureTimeSeriesPoint {
  date: string;
  cash: number;
  gross: number;
  net: number;
}

export interface RollingPerformancePayload {
  run_id: string;
  model_name: ModelName;
  status: DashboardPayloadStatus;
  message?: string | null;
  window_short: number;
  window_long: number;
  cumulative_return: TimeSeriesPoint[];
  rolling_sharpe_3m: TimeSeriesPoint[];
  rolling_sharpe_6m: TimeSeriesPoint[];
  rolling_ic_3m: TimeSeriesPoint[];
  rolling_ic_6m: TimeSeriesPoint[];
  rolling_maxdd: TimeSeriesPoint[];
  turnover_ts: TimeSeriesPoint[];
  exposure_ts: ExposureTimeSeriesPoint[];
}

export interface RegimePerformanceStats {
  count: number;
  mean_return: number;
  sharpe: number;
  ic: number;
  turnover: number;
}

export interface RegimeMatrixPoint {
  trend_regime: string;
  vol_regime: string;
  count: number;
  sharpe: number;
  mean_return: number;
  ic: number;
}

export interface PerformanceRegimePayload {
  run_id: string;
  model_name: ModelName;
  status: DashboardPayloadStatus;
  message?: string | null;
  trend_regime_perf: Record<string, RegimePerformanceStats>;
  vol_regime_perf: Record<string, RegimePerformanceStats>;
  liquidity_regime_perf: Record<string, RegimePerformanceStats>;
  matrix_2d: RegimeMatrixPoint[];
}

export interface PortfolioPositionItem {
  symbol: string;
  weight: number;
}

export interface PortfolioExposurePayload {
  run_id: string;
  model_name: ModelName;
  status: DashboardPayloadStatus;
  message?: string | null;
  sector_exposure: AssetClassWeightItem[];
  factor_exposure: Record<string, number>;
  beta_spy: number;
  beta_qqq: number;
  duration_estimate: number;
  top10_long: PortfolioPositionItem[];
  top10_short: PortfolioPositionItem[];
}

export interface PortfolioRiskContributionItem {
  symbol: string;
  contribution: number;
}

export interface PortfolioRiskPayload {
  run_id: string;
  model_name: ModelName;
  status: DashboardPayloadStatus;
  message?: string | null;
  vol_ex_ante: number;
  cvar_95: number;
  position_risk_contrib_top5: PortfolioRiskContributionItem[];
  position_risk_contrib_top10?: PortfolioRiskContributionItem[];
  position_return_contrib_top5: PortfolioRiskContributionItem[];
  worst5_positions: PortfolioRiskContributionItem[];
  factor_exposure?: Record<string, number>;
  stress_test?: Record<string, number>;
}

export interface ConstraintBindingItemPayload {
  constraint_type: string;
  binding_count: number;
  binding_ratio: number;
}

export interface ArtifactCompletenessItemPayload {
  artifact: string;
  ready: boolean;
  path?: string | null;
}

export interface RunLatestMetaPayload {
  run_id?: string | null;
  run_uid?: string | null;
  model_name: ModelName;
  as_of_date?: string | null;
  status: DashboardPayloadStatus;
  artifact_contract_version?: string | null;
  required_artifacts_ready: boolean;
  universe_stage_counts: Record<string, number>;
  artifact_completeness: ArtifactCompletenessItemPayload[];
  message?: string | null;
}

export interface RunLatestConstraintsPayload {
  run_id: string;
  model_name: ModelName;
  status: DashboardPayloadStatus;
  message?: string | null;
  items: ConstraintBindingItemPayload[];
  liquidity_clip_ratio: number;
  risk_contribution_max: number;
  top_risk_contribution: PortfolioRiskContributionItem[];
  liquidity_adv_top: Array<{ symbol: string; adv_weight_cap: number }>;
}

export type RunLatestRiskPayload = PortfolioRiskPayload;
export type RunLatestExposuresPayload = PortfolioExposurePayload;

export interface TrainResultV2Payload {
  run_id: string;
  run_uid?: string | null;
  model_name: ModelName;
  universe_hash?: string | null;
  feature_hash?: string | null;
  config_hash?: string | null;
  train_start_utc?: string | null;
  train_end_utc?: string | null;
  validation_metrics: Record<string, number>;
  artifact_uri?: string | null;
  data_version?: string | null;
  feature_version?: string | null;
  currency: string;
}

export interface BacktestResultV2Payload {
  run_id: string;
  run_uid?: string | null;
  model_name: ModelName;
  equity_base: number;
  equity_curve: Array<Record<string, string | number>>;
  returns_decimal: Array<Record<string, string | number>>;
  cumulative_returns: Array<Record<string, string | number>>;
  drawdown: Array<Record<string, string | number>>;
  gross_exposure: Array<Record<string, string | number>>;
  net_exposure: Array<Record<string, string | number>>;
  positions: Array<Record<string, string | number>>;
  trades: Array<Record<string, string | number>>;
  turnover: Array<Record<string, string | number>>;
  metrics: Record<string, number>;
  asof_manifest: Record<string, unknown>;
  currency: string;
}

export interface WalkForwardFoldV2Payload {
  fold_id: string;
  train_period: Record<string, string>;
  test_period: Record<string, string>;
  fold_metrics: Record<string, number>;
  fold_equity: Array<Record<string, string | number>>;
  asof_manifest_hash?: string | null;
}

export interface WalkForwardResultV2Payload {
  run_id: string;
  run_uid?: string | null;
  model_name: ModelName;
  folds: WalkForwardFoldV2Payload[];
  aggregate_metrics: Record<string, number>;
  train_window_integrity: boolean;
  currency: string;
}

export interface ExecutionStateV2Payload {
  run_id: string;
  model_name: ModelName;
  portfolio_value: number;
  cash: number;
  positions_weight: Array<Record<string, string | number>>;
  positions_quantity: Array<Record<string, string | number>>;
  exposure: Record<string, number>;
  risk_metrics: Record<string, number>;
  last_rebalance_time_utc?: string | null;
  orders: Array<Record<string, string | number>>;
  fills: Array<Record<string, string | number>>;
  kill_switch: boolean;
  currency: string;
}

export interface DashboardSnapshotV2Payload {
  run_id: string;
  run_uid?: string | null;
  model_name: ModelName;
  snapshot_profile?: SnapshotProfile;
  as_of_utc: string;
  total_return: number;
  cagr: number;
  sharpe: number;
  sortino: number;
  max_drawdown: number;
  volatility: number;
  turnover: number;
  win_rate: number;
  exposure: Record<string, number>;
  risk_contrib_top10: PortfolioRiskContributionItem[];
  constraint_bindings: ConstraintBindingItemPayload[];
  ic_rolling: Array<Record<string, string | number>>;
  regime_current?: Record<string, string>;
  alerts_current_count?: number;
  constraint_summary?: Record<string, number>;
  artifact_summary?: ArtifactSummaryPayload | null;
  model_performance?: ModelPerformancePayload | null;
  run_latest_meta?: RunLatestMetaPayload | null;
  currency: string;
}

export interface RunAuditEventPayload {
  id?: number | null;
  run_id: string;
  event_type: string;
  severity: "info" | "warning" | "critical";
  payload: Record<string, unknown>;
  created_at_utc: string;
}

export interface RunAuditPayload {
  run_id: string;
  status: DashboardPayloadStatus;
  message?: string | null;
  events: RunAuditEventPayload[];
}

export type RunSnapshotPayload = DashboardSnapshotV2Payload;
export type RunConstraintsPayload = RunLatestConstraintsPayload;
export type RunRiskPayload = PortfolioRiskPayload;
export type RunExposuresPayload = PortfolioExposurePayload;

export interface ICDecayPoint {
  horizon: number;
  ic: number;
}

export interface ICDecayPayload {
  run_id: string;
  model_name: ModelName;
  status: DashboardPayloadStatus;
  message?: string | null;
  max_horizon: number;
  ic_decay: ICDecayPoint[];
  ic_t_stat: number;
}

export interface PredictionHistogramBin {
  bin_left: number;
  bin_right: number;
  count: number;
}

export interface PredictionDistributionPayload {
  run_id: string;
  model_name: ModelName;
  status: DashboardPayloadStatus;
  message?: string | null;
  bins: number;
  histogram: PredictionHistogramBin[];
  top_decile_mean: number;
  bottom_decile_mean: number;
  decile_spread_ts: Array<{ date: string; spread: number }>;
}

export interface RegimeCurrentPayload {
  run_id: string;
  model_name: ModelName;
  status: DashboardPayloadStatus;
  message?: string | null;
  trend_regime: string;
  vol_regime: string;
  liquidity_regime: string;
  vix_level: number;
  breadth: number;
  spx_distance_200ma: number;
}

export interface RegimeHistoryPoint {
  date: string;
  trend_regime: string;
  vol_regime: string;
  liquidity_regime: string;
  vix_level: number;
  breadth: number;
  spx_distance_200ma: number;
}

export interface RegimeHistoryPayload {
  run_id: string;
  model_name: ModelName;
  status: DashboardPayloadStatus;
  message?: string | null;
  history: RegimeHistoryPoint[];
  regime_transition_stats: Record<string, number>;
}

export interface AlertItem {
  rule_id: string;
  severity: "info" | "warning" | "critical";
  triggered_at: string;
  message: string;
  value: number;
}

export interface AlertsPayload {
  run_id: string;
  model_name: ModelName;
  status: DashboardPayloadStatus;
  message?: string | null;
  alerts: AlertItem[];
}

export interface ModelShapPayload {
  run_id: string;
  model_name: ModelName;
  status: DashboardPayloadStatus;
  message?: string | null;
  summary_points: Array<Record<string, string | number>>;
  dependence_top3: Array<Record<string, string | number>>;
  feature_stability_ts: Array<Record<string, string | number>>;
}

export interface ExecutionOrderPreviewRequestPayload {
  run_id: string;
  model_name: ModelName;
  slippage_bps?: number;
  cost_bps?: number;
  nav?: number;
  idempotency_key?: string;
}

export interface ExecutionModeUpdateRequestPayload {
  run_id: string;
  model_name: ModelName;
  mode: ExecutionMode;
}

export interface ExecutionOrderItemPayload {
  order_id: string;
  symbol: string;
  side: "buy" | "sell";
  quantity: number;
  current_weight: number;
  target_weight: number;
  est_price: number;
  est_notional: number;
  status: "preview" | "submitted" | "filled" | "rejected";
}

export interface ExecutionPreviewPayload {
  run_id: string;
  model_name: ModelName;
  status: DashboardPayloadStatus;
  message?: string | null;
  as_of_date?: string | null;
  nav: number;
  orders: ExecutionOrderItemPayload[];
  estimated_turnover: number;
  execution_mode?: ExecutionMode;
}

export interface ExecutionSubmitPayload {
  run_id: string;
  model_name: ModelName;
  status: DashboardPayloadStatus;
  message?: string | null;
  submitted_at?: string | null;
  orders: ExecutionOrderItemPayload[];
  fills_count: number;
  cash_after: number;
  nav_after: number;
  kill_switch: boolean;
  execution_mode?: ExecutionMode;
}

export interface ExecutionOrdersPayload {
  run_id: string;
  model_name: ModelName;
  status: DashboardPayloadStatus;
  message?: string | null;
  orders: ExecutionOrderItemPayload[];
  execution_mode?: ExecutionMode;
}

export interface ExecutionFillsPayload {
  run_id: string;
  model_name: ModelName;
  status: DashboardPayloadStatus;
  message?: string | null;
  fills: Array<Record<string, string | number>>;
  execution_mode?: ExecutionMode;
}

export interface ExecutionPositionsPayload {
  run_id: string;
  model_name: ModelName;
  status: DashboardPayloadStatus;
  message?: string | null;
  as_of_date?: string | null;
  positions: Array<Record<string, string | number>>;
  cash: number;
  gross_exposure: number;
  net_exposure: number;
  execution_mode?: ExecutionMode;
}

export interface ExecutionPnlPayload {
  run_id: string;
  model_name: ModelName;
  status: DashboardPayloadStatus;
  message?: string | null;
  as_of_date?: string | null;
  realized_pnl: number;
  unrealized_pnl: number;
  total_pnl: number;
  return_pct: number;
  execution_mode?: ExecutionMode;
}

export interface RiskPretradeRequestPayload {
  run_id: string;
  model_name: ModelName;
  turnover_limit?: number;
}

export interface RiskViolationItemPayload {
  rule_id: string;
  severity: "info" | "warning" | "critical";
  value: number;
  limit: number;
  message: string;
}

export interface RiskPretradePayload {
  run_id: string;
  model_name: ModelName;
  status: DashboardPayloadStatus;
  passed: boolean;
  kill_switch: boolean;
  violations: RiskViolationItemPayload[];
  execution_mode?: ExecutionMode;
}

export interface RiskLimitsPayload {
  run_id: string;
  model_name: ModelName;
  status: DashboardPayloadStatus;
  limits: Record<string, number>;
  kill_switch: boolean;
  execution_mode?: ExecutionMode;
}

export interface RiskEventsPayload {
  run_id: string;
  model_name: ModelName;
  status: DashboardPayloadStatus;
  message?: string | null;
  events: Array<Record<string, string | number>>;
}

export interface OpsJobStatePayload {
  job: "daily" | "weekly" | "monthly";
  last_status: string;
  last_run_id?: string | null;
  last_error?: string | null;
  steps: Record<string, Record<string, unknown>>;
}

export interface OpsStatusPayload {
  status: DashboardPayloadStatus;
  message?: string | null;
  generated_at?: string | null;
  jobs: OpsJobStatePayload[];
  latest_publish: Record<string, unknown>;
  versions: Record<string, unknown>;
  latest_runs: Array<Record<string, unknown>>;
  macro_health: Record<string, unknown>;
  latest_training_run_id?: string | null;
  latest_daily_infer_date?: string | null;
  walkforward_queue_depth?: number;
  active_job_locks?: Array<Record<string, unknown>>;
  lock_health?: Record<string, string>;
  stale_policy?: Record<string, unknown>;
  data_quality?: Record<string, unknown>;
  reports?: Array<Record<string, unknown>>;
  model_registry?: Record<string, unknown>;
  scheduler?: Record<string, unknown>;
  notification_failures?: Array<Record<string, unknown>>;
  execution_mode?: Record<string, unknown>;
}

export interface DataQualityCheckPayload {
  check: string;
  severity: QCStatus;
  value?: string | number | null;
  threshold?: string | number | null;
  message?: string | null;
  details?: Record<string, unknown>;
}

export interface DataQualityLatestPayload {
  run_id?: string | null;
  gate_name?: string | null;
  qc_status: QCStatus;
  as_of_date?: string | null;
  created_at?: string | null;
  checks: DataQualityCheckPayload[];
  summary: Record<string, unknown>;
  report_path?: string | null;
}

export interface DataQualityHistoryPayload {
  items: DataQualityLatestPayload[];
}

export interface ExperimentRunItemPayload {
  run_id: string;
  model_type?: string | null;
  dataset_version?: string | null;
  feature_set_version?: string | null;
  hyperparameters: Record<string, unknown>;
  feature_set: Record<string, unknown>;
  performance: Record<string, unknown>;
  artifact_uri?: string | null;
  status?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface ExperimentListPayload {
  items: ExperimentRunItemPayload[];
}

export interface ModelRegistryEntryPayload {
  alias: string;
  run_id?: string | null;
  model_name?: string | null;
  model_version?: string | null;
  stage?: string | null;
  artifact_uri?: string | null;
  dataset_version?: string | null;
  feature_set_version?: string | null;
  metrics: Record<string, unknown>;
  source?: string | null;
  updated_at?: string | null;
}

export interface ModelRegistryHistoryPayload {
  items: ModelRegistryEntryPayload[];
}

export interface ReportRunItemPayload {
  run_id?: string | null;
  report_type: string;
  report_path: string;
  status: string;
  created_at?: string | null;
  summary: Record<string, unknown>;
}

export interface ReportsLatestPayload {
  item?: ReportRunItemPayload | null;
}

export interface ReportsHistoryPayload {
  items: ReportRunItemPayload[];
}

export interface NotificationItemPayload {
  id: number;
  run_id?: string | null;
  event_type: string;
  channel: string;
  fingerprint: string;
  status: string;
  payload: Record<string, unknown>;
  attempts: number;
  last_error?: string | null;
  created_at?: string | null;
  updated_at?: string | null;
  delivered_at?: string | null;
}

export interface NotificationsHistoryPayload {
  items: NotificationItemPayload[];
}

export interface SchedulerStatusPayload {
  timezone?: string | null;
  market_schedule: Record<string, unknown>;
  expected_jobs: string[];
  jobs: Array<Record<string, unknown>>;
  macro_scheduler: Record<string, unknown>;
  generated_at?: string | null;
}

export interface ExecutionModePayload {
  run_id: string;
  model_name: ModelName;
  mode: ExecutionMode;
  live_adapter_enabled: boolean;
  broker_ready: boolean;
  kill_switch: boolean;
  updated_at?: string | null;
}

export interface BackendService {
  id: string;
  name: string;
  command: string;
  status: "running" | "stopped" | "starting" | "stopping" | "error";
  url?: string;
}

export interface BackendResolution {
  baseUrl: string;
  source: "running-service-url" | "command-parse" | "fallback" | "web-dev-fallback" | "stored-url" | "fallback-recovery";
  connected: boolean;
  detail: string;
}

export type TradingRuntimeStatus = "running" | "paused" | "stopped";
export type TradingOrderStatus =
  | "pending"
  | "submitted"
  | "filled"
  | "partially_filled"
  | "cancelled"
  | "rejected";
export type TradingAlgorithmStatus =
  | "draft"
  | "dev"
  | "sandbox"
  | "validated"
  | "active"
  | "paused"
  | "deprecated";

export interface TradingStatusPayload {
  mode: ExecutionMode;
  runtime_status: TradingRuntimeStatus;
  last_scan_at?: string | null;
  last_order_at?: string | null;
  active_strategy_count: number;
  watchlist_size: number;
  open_position_count: number;
  today_signal_count: number;
  today_order_count: number;
  today_realized_pnl: number;
  cumulative_pnl: number;
  intraday_drawdown: number;
  used_capital: number;
  available_cash: number;
  report_urls?: string[];
  execution_mode?: ExecutionMode;
  model_version?: string | null;
}

export interface TradingStrategyConfigPayload {
  name: string;
  version: string;
  description?: string | null;
  enabled: boolean;
  parameters: Record<string, unknown>;
}

export interface TradingAlgorithmRecordPayload {
  name: string;
  version: string;
  status: TradingAlgorithmStatus;
  active: boolean;
  sandbox_mode: boolean;
  signal_only: boolean;
  description?: string | null;
  parameters: Record<string, unknown>;
  required_columns: string[];
  validation_result: Record<string, unknown>;
  recent_run_result: Record<string, unknown>;
  recent_error?: string | null;
  performance_summary: Record<string, unknown>;
  last_run_at?: string | null;
  created_at?: string | null;
  modified_at?: string | null;
}

export interface TradingSettingsPayload {
  version: string;
  tab_name?: string;
  mode: ExecutionMode;
  runtime_status: TradingRuntimeStatus;
  universe_id: string;
  schedule: Record<string, unknown>;
  scan: Record<string, unknown>;
  execution: Record<string, unknown>;
  account: Record<string, unknown>;
  risk: Record<string, unknown>;
  strategies: Record<string, unknown>;
  custom_algorithms: Record<string, unknown>;
  ui: Record<string, unknown>;
  built_in_strategies: TradingStrategyConfigPayload[];
  custom_algorithm_records: TradingAlgorithmRecordPayload[];
}

export interface TradingSettingsUpdatePayload {
  version?: string;
  mode?: ExecutionMode;
  runtime_status?: TradingRuntimeStatus;
  universe_id?: string;
  schedule?: Record<string, unknown>;
  scan?: Record<string, unknown>;
  execution?: Record<string, unknown>;
  account?: Record<string, unknown>;
  risk?: Record<string, unknown>;
  strategies?: Record<string, unknown>;
  custom_algorithms?: Record<string, unknown>;
  ui?: Record<string, unknown>;
}

export interface TradingCycleRunRequestPayload {
  auto_execute?: boolean;
}

export interface TradingCycleRunPayload {
  cycle_id: string;
  status: string;
  signal_count?: number;
  order_count?: number;
  fill_count?: number;
  skipped_symbols?: string[];
  report_path?: string | null;
  status_payload?: TradingStatusPayload | null;
}

export interface TradingSignalItemPayload {
  signal_id?: string | null;
  timestamp: string;
  ticker: string;
  name?: string | null;
  current_price: number;
  signal?: string | null;
  signal_type: string;
  side: string;
  strategy_name: string;
  algorithm_version?: string | null;
  signal_strength: number;
  entry_score: number;
  priority: number;
  confidence?: number;
  rsi: number;
  macd_hist: number;
  ma_relation: number;
  volume_change_pct: number;
  atr: number;
  recent_return: number;
  recommended_action: string;
  position_held: boolean;
  risk_check_status: string;
  risk_reason_codes: string[];
  reason?: string | null;
  sector?: string | null;
}

export interface TradingScanPayload {
  generated_at?: string | null;
  cycle_id?: string | null;
  signal_count: number;
  items: TradingSignalItemPayload[];
}

export interface TradingSymbolDetailPayload {
  ticker: string;
  series: Array<Record<string, unknown>>;
  signals: TradingSignalItemPayload[];
  orders: TradingOrderItemPayload[];
  position?: Record<string, unknown> | null;
  explanation?: string | null;
}

export interface TradingOrderItemPayload {
  order_id: string;
  created_at?: string | null;
  ticker: string;
  strategy_name: string;
  algorithm_version?: string | null;
  status: TradingOrderStatus;
  side: string;
  signal_type?: string | null;
  quantity: number;
  requested_price: number;
  filled_price?: number | null;
  notional: number;
  stop_loss?: number | null;
  take_profit?: number | null;
  trailing_stop?: number | null;
  reason?: string | null;
  metadata: Record<string, unknown>;
}

export interface TradingOrdersPayload {
  items: TradingOrderItemPayload[];
}

export interface TradingFillsPayload {
  items: Array<Record<string, unknown>>;
}

export interface TradingPositionsPayload {
  mode: ExecutionMode;
  items: Array<Record<string, unknown>>;
}

export interface TradingPerformancePayload {
  as_of_date?: string | null;
  generated_at?: string | null;
  equity?: number;
  cash?: number;
  used_capital?: number;
  realized_pnl?: number;
  unrealized_pnl?: number;
  total_pnl?: number;
  cumulative_return?: number;
  daily_return?: number;
  weekly_return?: number;
  monthly_return?: number;
  win_rate?: number;
  avg_win?: number;
  avg_loss?: number;
  profit_factor?: number;
  sharpe?: number;
  sortino?: number;
  max_drawdown?: number;
  turnover?: number;
  avg_holding_period?: number;
  strategy_contribution?: Record<string, number>;
  ticker_contribution?: Record<string, number>;
  equity_curve: Array<{ date: string; value: number }>;
  drawdown_curve: Array<{ date: string; value: number }>;
  daily_pnl: Array<{ date: string; value: number }>;
}

export interface TradingRiskPayload {
  generated_at?: string | null;
  limits: Record<string, unknown>;
  events: Array<Record<string, unknown>>;
}

export interface TradingEventsPayload {
  items: Array<Record<string, unknown>>;
}

export interface TradingAlgorithmsPayload {
  items: TradingAlgorithmRecordPayload[];
}

export interface TradingAlgorithmToggleRequestPayload {
  name: string;
  version?: string;
  active?: boolean;
  sandbox_mode?: boolean;
  signal_only?: boolean;
  status?: TradingAlgorithmStatus;
}

export interface TradingAlgorithmValidateRequestPayload {
  name: string;
  version?: string;
}

export interface TradingAlgorithmValidationPayload {
  name: string;
  version: string;
  status: string;
  passed: boolean;
  summary: Record<string, unknown>;
  checks: Array<Record<string, unknown>>;
  report_path?: string | null;
  created_at?: string | null;
}

export interface TradingExecutionModePayload {
  mode: ExecutionMode;
  live_adapter_enabled: boolean;
  broker_ready: boolean;
  kill_switch: boolean;
  updated_at?: string | null;
}
