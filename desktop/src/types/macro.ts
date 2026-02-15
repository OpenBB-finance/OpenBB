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

export interface MacroUpdateResponse {
  status: MacroStatus;
  message?: string | null;
  updated_series: string[];
}
