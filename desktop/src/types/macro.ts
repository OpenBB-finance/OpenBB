export type MacroStatus = "ok" | "insufficient_data" | "not_found" | "error";
export type MacroFreq = "native" | "D" | "W" | "M" | "Q";
export type MacroFill = "ffill" | "interpolate" | "none";
export type MacroViewMode = "explorer" | "compare" | "relationship" | "release" | "report";
export type MacroNormalizeMode = "raw" | "index100" | "zscore" | "yoy" | "percentile_5y";

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
  tags: string[];
  last_obs?: string | null;
  stale_days?: number | null;
  release_frequency?: string | null;
  default_view: MacroViewMode;
  vintage_available: boolean;
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

export interface MacroStudySeriesSpec {
  key: string;
  alias?: string | null;
  transform_chain: string[];
  freq: MacroFreq;
  fill: MacroFill;
  axis: "left" | "right";
  normalize_mode: MacroNormalizeMode;
  lag_mode?: string | null;
  display_style: "line" | "area" | "bar" | "scatter";
}

export interface MacroViewSpec {
  view_id: string;
  mode: MacroViewMode;
  title?: string | null;
  layout: Record<string, unknown>;
}

export interface MacroConclusionPayload {
  summary: string;
  thesis: string;
  risk_cases: string[];
  action_bias: string;
  confidence?: number | null;
  next_checks: string[];
}

export interface StudyReportAttachment {
  report_id?: string | null;
  title?: string | null;
  report_path: string;
  created_at?: string | null;
  source_run_id?: string | null;
  symbols: string[];
}

export interface MacroStudyPayload {
  id?: string | null;
  name: string;
  objective: string;
  series_specs: MacroStudySeriesSpec[];
  view_specs: MacroViewSpec[];
  notes: string;
  conclusion: MacroConclusionPayload;
  linked_assets: string[];
  linked_feature_set_id?: string | null;
  linked_reports?: StudyReportAttachment[];
  created_at?: string | null;
  updated_at?: string | null;
}

export interface MacroStudiesResponse {
  status: MacroStatus;
  message?: string | null;
  items: MacroStudyPayload[];
}

export interface MacroCompareResponse {
  status: MacroStatus;
  message?: string | null;
  normalization: MacroNormalizeMode;
  series: Record<string, MacroSeriesResponse>;
}

export interface MacroLeadLagPoint {
  lag: number;
  correlation: number;
}

export interface MacroLeadLagResponse {
  status: MacroStatus;
  message?: string | null;
  lhs: string;
  rhs: string;
  best_lag: number;
  best_correlation: number;
  table: MacroLeadLagPoint[];
  rolling_corr: MacroDataPoint[];
}

export interface MacroScatterPoint {
  date: string;
  x: number;
  y: number;
}

export interface MacroScatterResponse {
  status: MacroStatus;
  message?: string | null;
  lhs: string;
  rhs: string;
  correlation?: number | null;
  slope?: number | null;
  intercept?: number | null;
  points: MacroScatterPoint[];
}

export interface MacroVintagePoint {
  date: string;
  value: number;
  realtime_start?: string | null;
  realtime_end?: string | null;
  fetched_at?: string | null;
}

export interface MacroVintageResponse {
  status: MacroStatus;
  message?: string | null;
  key: string;
  as_of_date?: string | null;
  latest: MacroDataPoint[];
  as_of: MacroDataPoint[];
  revisions: MacroVintagePoint[];
  revision_delta?: number | null;
}

export interface MacroReleaseCalendarItem {
  key: string;
  title?: string | null;
  domain?: string | null;
  release_frequency?: string | null;
  last_obs?: string | null;
  stale_days?: number | null;
  estimated_next_release?: string | null;
  vintage_available: boolean;
}

export interface MacroReleaseCalendarResponse {
  status: MacroStatus;
  message?: string | null;
  items: MacroReleaseCalendarItem[];
}

export interface MacroReportResponse {
  status: MacroStatus;
  message?: string | null;
  study_id?: string | null;
  report_path?: string | null;
  generated_at?: string | null;
}

export interface MacroFeatureExportItem {
  feature_name: string;
  source_study_id: string;
  key: string;
  transform_chain: string[];
  lag_rule?: string | null;
  as_of_policy: string;
}

export interface MacroFeatureExportResponse {
  status: MacroStatus;
  message?: string | null;
  study_id?: string | null;
  artifact_path?: string | null;
  exported_at?: string | null;
  items: MacroFeatureExportItem[];
}
