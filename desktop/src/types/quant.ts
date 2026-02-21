export type TrainRunStatus = "queued" | "running" | "completed" | "failed";
export type SignalSide = "buy" | "hold" | "sell";
export type ModelName = "xgb_lstm" | "lgbm_ranker";
export type PortfolioMode = "long_only" | "long_short";
export type MuMapping = "z_score" | "quantile_mean_return";
export type TargetMode = "close_to_close" | "close_to_next_open" | "next_open_to_close";
export type EntryPriceMode = "next_open" | "close";
export type ExitPriceMode = "close" | "next_open";
export type CloseToNextOpenHorizonPolicy = "fixed_1" | "use_h";
export type ModelChoice = "lgbm_only" | "xgb_only" | "dual";
export type DashboardMode = "live" | "backtest";
export type WorkflowRunStatus = "queued" | "running" | "completed" | "failed" | "unknown";
export type WalkForwardJobStatus = "queued" | "running" | "completed" | "failed" | "not_found";

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
}

export interface WalkForwardConfigInput {
  train_months: number;
  embargo_months: number;
  val_months: number;
  step_months: number;
}

export interface SignalConfigInput {
  theta_grid: number[];
  selection_metric: "val_sharpe";
}

export interface FeatureConfigInput {
  lags: number[];
  vol_windows: number[];
  momentum_windows: number[];
  include_rsi: boolean;
  include_macd: boolean;
  include_regime_features: boolean;
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
}

export interface TrainResponsePayload {
  run_id: string;
  status: TrainRunStatus;
  artifact_root: string;
  created_at: string;
}

export interface RunStatusPayload {
  run_id: string;
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
}

export interface BacktestConstraintsInput {
  max_weight: number;
  long_only: boolean;
  risk_aversion: number;
  lookback_days: number;
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
  max_drawdown: number;
  volatility: number;
  turnover: number;
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

export interface BacktestResponsePayload {
  run_id: string;
  model_name: ModelName;
  start_date: string;
  end_date: string;
  base_index: number;
  benchmark_symbol: string;
  metrics: BacktestMetrics;
  equity_curve: EquityCurvePoint[];
  benchmark_curve: BenchmarkCurvePoint[];
  period_weights: PeriodWeightsPoint[];
  effective_constraints?: Record<string, number | boolean>;
  cash_weight?: number;
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
}

export interface PortfolioPolicyPayload {
  template: string;
  single_name_max_abs_weight: number;
  small_universe_policy: string;
  sector_concentration_max: number;
  turnover_max: number;
  gross_exposure_max: number;
  net_exposure_abs_max: number;
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
  universe_size: number;
  cost_bps: number;
  cash_exposure: number;
  gross_exposure: number;
  net_exposure: number;
  strategy_health: Record<string, number>;
  workflow_state?: WorkflowStatePayload;
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
  position_return_contrib_top5: PortfolioRiskContributionItem[];
  worst5_positions: PortfolioRiskContributionItem[];
}

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
}

export interface ExecutionOrdersPayload {
  run_id: string;
  model_name: ModelName;
  status: DashboardPayloadStatus;
  message?: string | null;
  orders: ExecutionOrderItemPayload[];
}

export interface ExecutionFillsPayload {
  run_id: string;
  model_name: ModelName;
  status: DashboardPayloadStatus;
  message?: string | null;
  fills: Array<Record<string, string | number>>;
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
}

export interface RiskLimitsPayload {
  run_id: string;
  model_name: ModelName;
  status: DashboardPayloadStatus;
  limits: Record<string, number>;
  kill_switch: boolean;
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
  source: "running-service-url" | "command-parse" | "fallback" | "web-dev-fallback";
  connected: boolean;
  detail: string;
}
