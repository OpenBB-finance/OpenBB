export type MacroStatus = "ok" | "insufficient_data" | "not_found" | "error";
export type MacroFreq = "native" | "D" | "W" | "M" | "Q";
export type MacroFill = "ffill" | "interpolate" | "none";

export interface MacroDataPoint {
  date: string;
  value: number;
}

export interface MacroSeriesMeta {
  key: string;
  title?: string | null;
  units?: string | null;
  frequency?: string | null;
  source: string;
  transform: string;
  lag_applied?: string | null;
  warning?: string | null;
}

export interface MacroSeriesStats {
  last?: number | null;
  change_1m?: number | null;
  change_3m?: number | null;
  z?: number | null;
  percentile_5y?: number | null;
}

export interface MacroSeriesResponse {
  meta: MacroSeriesMeta;
  data: MacroDataPoint[];
  stats: MacroSeriesStats;
  status: MacroStatus;
  message?: string | null;
}

export interface MacroSeriesMultiResponse {
  status: MacroStatus;
  message?: string | null;
  series: Record<string, MacroSeriesResponse>;
}

export interface MacroPresetSeries {
  id: string;
  axis: "left" | "right" | "bottom";
  meta: MacroSeriesMeta;
  data: MacroDataPoint[];
  stats: MacroSeriesStats;
}

export interface MacroEventItem {
  date: string;
  event_type: string;
  details: Record<string, string | number>;
}

export interface MacroPresetResponse {
  status: MacroStatus;
  message?: string | null;
  preset_id: string;
  inputs: Record<string, string | number | boolean>;
  series: MacroPresetSeries[];
  events: MacroEventItem[];
}

export interface MacroCatalogItem {
  id: string;
  source: string;
  series_id: string;
  title?: string | null;
  frequency?: string | null;
  units?: string | null;
  domain?: string | null;
  default_transform: string;
  publish_lag: number;
  notes?: string | null;
  active: boolean;
}

export interface MacroCatalogResponse {
  status: MacroStatus;
  message?: string | null;
  items: MacroCatalogItem[];
}

export interface MacroExpressionRequest {
  expr: string;
  start?: string;
  end?: string;
  freq?: MacroFreq;
  fill?: MacroFill;
  transform?: string;
}

export interface MacroExpressionResponse extends MacroSeriesResponse {
  dependencies: string[];
}

export interface MacroDerivedItem {
  derived_id: string;
  expression: string;
  dependencies: string[];
  default_transform: string;
  created_at?: string | null;
  updated_at?: string | null;
  is_favorite: boolean;
}

export interface MacroDerivedResponse {
  status: MacroStatus;
  message?: string | null;
  items: MacroDerivedItem[];
}

export interface MacroRegimePoint {
  date: string;
  risk_on_score: number;
  inflation_score: number;
  growth_score: number;
  liquidity_score: number;
  credit_stress_score: number;
}

export interface MacroRegimeResponse {
  status: MacroStatus;
  message?: string | null;
  data: MacroRegimePoint[];
  latest?: MacroRegimePoint | null;
}

export interface MacroRegimeStateResponse {
  status: MacroStatus;
  message?: string | null;
  date?: string | null;
  inflation_up: boolean;
  growth_down: boolean;
  risk_off_proxy: boolean;
}

export interface RegimeTransitionItem {
  date: string;
  axis: string;
  from_score: number;
  to_score: number;
  delta: number;
  direction: "rising" | "falling";
  severity: "minor" | "major";
}

export interface RegimeLabelPoint {
  date: string;
  label: string;
}

export interface RegimeTransitionResponse {
  status: MacroStatus;
  message?: string | null;
  transitions: RegimeTransitionItem[];
  regime_label_history: RegimeLabelPoint[];
}

export interface HmmRegimePoint {
  date: string;
  state: number;
  label: string;
  probability: number[];
}

export interface HmmRegimePayload {
  status: MacroStatus;
  message?: string | null;
  states: HmmRegimePoint[];
  state_meta: Record<string, Record<string, string | number>>;
}

export interface RegimeSchedulerStatus {
  running: boolean;
  last_market_refresh?: string | null;
  last_fred_update?: string | null;
  next_market_refresh?: string | null;
  next_fred_update?: string | null;
}

export interface RegimeRefreshResponse {
  status: string;
}

export interface RegimeStreamEvent {
  event_type: "scores_update" | "transition" | "alert" | "error";
  timestamp: string;
  data: Record<string, unknown>;
  label?: string | null;
  from_label?: string | null;
  to_label?: string | null;
}

export type MacroCycleLevel =
  | "expansion"
  | "late_expansion"
  | "transition"
  | "slowdown"
  | "contraction";

export interface MacroCycleLevelSnapshot {
  score: number;
  level: MacroCycleLevel;
  delta_4w: number;
  as_of: string | null;
  stale_days: number | null;
  risk_off_proxy: boolean;
  growth_down: boolean;
  inflation_up: boolean;
  action_hint: "aggressive" | "neutral" | "defensive";
}

export interface MacroAlertItem {
  rule_id: string;
  severity: "info" | "warning" | "critical";
  triggered_at: string;
  message: string;
  value: number;
  threshold: number;
  context: Record<string, string | number>;
}

export interface MacroAlertsResponse {
  status: MacroStatus;
  message?: string | null;
  current: MacroAlertItem[];
  history: MacroAlertItem[];
}

export interface MacroHealthObsStats {
  total_series_in_catalog: number;
  total_series_with_obs: number;
  last_obs_date_global?: string | null;
  last_fetched_at_global?: string | null;
}

export interface MacroHealthFeatureStats {
  total_feature_rows: number;
  last_feature_date?: string | null;
  feature_names_present: string[];
}

export interface MacroHealthResponse {
  status: MacroStatus;
  message?: string | null;
  fred_api_key_configured: boolean;
  macro_db_path: string;
  obs_stats: MacroHealthObsStats;
  feature_stats: MacroHealthFeatureStats;
  warnings: string[];
}

export interface MacroUpdateResponse {
  status: MacroStatus;
  message?: string | null;
  updated_series: string[];
}
