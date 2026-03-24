export type TradingViewThemeMode = "light" | "dark";

export type TradingViewFinanceWidgetType =
  | "advanced-chart"
  | "symbol-info"
  | "company-profile"
  | "fundamental-data";

export type FinanceFundamentalsTab =
  | "overview"
  | "forecast"
  | "income-statement"
  | "balance-sheet"
  | "cash-flow";

export type FinanceStatementPeriod = "annual" | "quarterly";

export type FinanceStatementKind = "income" | "balance" | "cash";

export interface FinancePageSearch {
  symbol?: string;
}

export interface FinanceRecentSymbolItem {
  symbol: string;
  label: string;
}

export interface TradingViewWidgetConfig {
  widgetType: TradingViewFinanceWidgetType;
  symbol: string;
  theme: TradingViewThemeMode;
  scriptSrc: string;
  payload: Record<string, unknown>;
}

export interface TradingViewFinancialLink {
  label: string;
  href: string;
}

export interface FinanceSymbolSuggestion {
  symbol: string;
  source: "active" | "recent" | "popular" | "typed";
}

export interface FinanceStatementRecord {
  period_ending?: string | null;
  [key: string]: string | number | boolean | null | undefined;
}

export interface FinanceStatementEnvelope {
  results: FinanceStatementRecord[];
  provider?: string | null;
  extra?: {
    metadata?: {
      timestamp?: string | null;
    } | null;
  } | null;
}

export interface FinanceForecastConsensusRecord {
  symbol?: string | null;
  target_high?: number | null;
  target_low?: number | null;
  target_consensus?: number | null;
  target_median?: number | null;
  recommendation?: string | null;
  recommendation_mean?: number | null;
  number_of_analysts?: number | null;
  current_price?: number | null;
  currency?: string | null;
}

export interface FinanceForecastEnvelope {
  results: FinanceForecastConsensusRecord[];
  provider?: string | null;
  extra?: {
    metadata?: {
      timestamp?: string | null;
    } | null;
  } | null;
}
