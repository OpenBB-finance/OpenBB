import { MODEL_NAMES } from "../types/quant";
import type {
  ModelConfigInput,
  ModelName,
  PortfolioPolicyPayload,
  RankerConfigInput,
  UniverseAsset,
  UniverseListItemPayload,
  WalkForwardConfigInput,
} from "../types/quant";

export type UniverseProfileId = "all" | "aggressive" | "defensive" | "custom";
export type UniverseSetId = "default" | "global_core_equity";
export type SpeedPresetId = "turbo" | "fast" | "standard" | "thorough";
export type RunStreamState =
  | "idle"
  | "connecting"
  | "ready"
  | "streaming"
  | "fallback"
  | "done"
  | "timeout"
  | "error";

export interface UniverseProfile {
  id: Exclude<UniverseProfileId, "custom">;
  label: string;
  description: string;
}

export interface UniverseSetOption {
  id: UniverseSetId;
  label: string;
  countHint?: number;
  hasFile?: boolean;
  minimumRequired?: number;
}

export interface UniverseResolveState {
  status: "idle" | "loading" | "ok" | "error";
  message: string | null;
  count: number | null;
  minimumRequired: number;
  meetsMinimum: boolean;
}

export interface SpeedPreset {
  id: SpeedPresetId;
  label: string;
  description: string;
  estimatedTime: string;
  modelConfig: ModelConfigInput;
  walkForward: WalkForwardConfigInput;
  rankerConfig: RankerConfigInput;
  quickMode: boolean;
  featurePruning: boolean;
  walkForwardCompact: boolean;
  datePeriodYears: number;
  featureLags: number[];
  thetaGrid: number[];
}

export const PROFILE_LIST: UniverseProfile[] = [
  { id: "all", label: "All", description: "Use every symbol in universe." },
  {
    id: "aggressive",
    label: "Aggressive",
    description: "Equity/sector/factor-focused basket.",
  },
  {
    id: "defensive",
    label: "Defensive",
    description: "Bonds, commodities, and defensive assets.",
  },
];

export const UNIVERSE_SET_OPTIONS_DEFAULT: UniverseSetOption[] = [
  { id: "default", label: "Default (manual symbols)" },
  {
    id: "global_core_equity",
    label: "Global Core Equity (U0/U1/U2)",
    minimumRequired: 1200,
  },
];

const UNIVERSE_SET_API_ID: Record<UniverseSetId, string> = {
  default: "default",
  global_core_equity: "all_in_one",
};

export const VALID_MODEL_NAMES: ModelName[] = [...MODEL_NAMES];

export function toApiUniverseId(id: UniverseSetId): string {
  return UNIVERSE_SET_API_ID[id] ?? id;
}

function isUniverseSetId(value: string): value is UniverseSetId {
  return UNIVERSE_SET_OPTIONS_DEFAULT.some((option) => option.id === value);
}

export function mergeUniverseSetOptions(
  items: UniverseListItemPayload[],
): UniverseSetOption[] {
  const byId = new Map<UniverseSetId, UniverseSetOption>(
    UNIVERSE_SET_OPTIONS_DEFAULT.map((option) => [option.id, option]),
  );

  for (const item of items) {
    let mappedId: UniverseSetId | null = null;
    if (isUniverseSetId(item.id)) {
      mappedId = item.id;
    } else if (item.id === "all_in_one") {
      mappedId = "global_core_equity";
    }
    if (!mappedId) {
      continue;
    }
    const base = byId.get(mappedId);
    if (!base) {
      continue;
    }
    byId.set(mappedId, {
      ...base,
      countHint: item.count_hint,
      hasFile: item.has_file,
      minimumRequired: item.minimum_required ?? base.minimumRequired,
    });
  }

  return UNIVERSE_SET_OPTIONS_DEFAULT.map(
    (option) => byId.get(option.id) ?? option,
  );
}

const AGGRESSIVE_CATEGORIES = new Set([
  "korea_index",
  "korea_etf",
  "us_index",
  "us_equity_etf",
  "us_tech_index",
  "us_tech_etf",
  "us_sector_etf",
  "semiconductor_etf",
  "software_etf",
  "global_equity_etf",
  "developed_market_etf",
  "emerging_market_etf",
  "factor_etf",
  "us_large_cap_equity",
  "ai_semiconductor_equity",
  "kospi200_constituent",
]);

const DEFENSIVE_CATEGORIES = new Set([
  "bond_etf",
  "cash_proxy",
  "commodity_etf",
  "reit_etf",
  "currency_etf",
]);

export const todayIso = new Date().toISOString().slice(0, 10);
export const fiveYearsAgoIso = (() => {
  const base = new Date();
  base.setFullYear(base.getFullYear() - 5);
  return base.toISOString().slice(0, 10);
})();

export const SPEED_PRESETS: Record<SpeedPresetId, SpeedPreset> = {
  turbo: {
    id: "turbo",
    label: "Turbo",
    description: "Minimal data + lightweight model for rapid prototyping.",
    estimatedTime: "~2-5m",
    modelConfig: {
      seq_len: 30,
      xgb_n_estimators: 150,
      xgb_max_depth: 3,
      xgb_learning_rate: 0.05,
      xgb_subsample: 0.8,
      xgb_colsample_bytree: 0.8,
      lstm_hidden_size: 32,
      lstm_num_layers: 1,
      lstm_dropout: 0.1,
      lstm_epochs: 10,
      lstm_batch_size: 256,
      lstm_learning_rate: 0.002,
      train_val_split: 0.8,
    },
    walkForward: {
      train_months: 18,
      embargo_months: 1,
      val_months: 1,
      step_months: 3,
      purging_mode: "legacy_month_cutoff",
      purged_n_splits: 5,
      purged_embargo_pct: 0.01,
    },
    rankerConfig: {
      objective: "rank_xendcg",
      metric: "ndcg",
      ndcg_eval_at: [5, 10],
      learning_rate: 0.05,
      n_estimators: 1500,
      num_leaves: 31,
      min_data_in_leaf: 500,
      subsample: 0.7,
      colsample_bytree: 0.7,
      reg_lambda: 15.0,
      random_state: 42,
      early_stopping_rounds: 100,
      stacking_enabled: false,
      stacking_alpha: 1.0,
    },
    quickMode: true,
    featurePruning: true,
    walkForwardCompact: true,
    datePeriodYears: 2,
    featureLags: [1, 3, 5, 10],
    thetaGrid: [1.0],
  },
  fast: {
    id: "fast",
    label: "Fast",
    description: "3y dataset + compact walk-forward for frequent iteration.",
    estimatedTime: "~5-15m",
    modelConfig: {
      seq_len: 40,
      xgb_n_estimators: 250,
      xgb_max_depth: 4,
      xgb_learning_rate: 0.04,
      xgb_subsample: 0.85,
      xgb_colsample_bytree: 0.85,
      lstm_hidden_size: 48,
      lstm_num_layers: 2,
      lstm_dropout: 0.1,
      lstm_epochs: 15,
      lstm_batch_size: 256,
      lstm_learning_rate: 0.001,
      train_val_split: 0.8,
    },
    walkForward: {
      train_months: 24,
      embargo_months: 1,
      val_months: 1,
      step_months: 2,
      purging_mode: "legacy_month_cutoff",
      purged_n_splits: 5,
      purged_embargo_pct: 0.01,
    },
    rankerConfig: {
      objective: "rank_xendcg",
      metric: "ndcg",
      ndcg_eval_at: [5, 10, 20],
      learning_rate: 0.04,
      n_estimators: 3000,
      num_leaves: 47,
      min_data_in_leaf: 400,
      subsample: 0.8,
      colsample_bytree: 0.8,
      reg_lambda: 12.0,
      random_state: 42,
      early_stopping_rounds: 150,
      stacking_enabled: false,
      stacking_alpha: 1.0,
    },
    quickMode: true,
    featurePruning: true,
    walkForwardCompact: true,
    datePeriodYears: 3,
    featureLags: [1, 2, 5, 10, 20],
    thetaGrid: [0.8, 1.0, 1.2],
  },
  standard: {
    id: "standard",
    label: "Standard",
    description: "5y dataset + full walk-forward with balanced defaults.",
    estimatedTime: "~15-40m",
    modelConfig: {
      seq_len: 60,
      xgb_n_estimators: 400,
      xgb_max_depth: 4,
      xgb_learning_rate: 0.03,
      xgb_subsample: 0.9,
      xgb_colsample_bytree: 0.9,
      lstm_hidden_size: 64,
      lstm_num_layers: 2,
      lstm_dropout: 0.1,
      lstm_epochs: 30,
      lstm_batch_size: 128,
      lstm_learning_rate: 0.001,
      train_val_split: 0.8,
    },
    walkForward: {
      train_months: 36,
      embargo_months: 1,
      val_months: 1,
      step_months: 1,
      purging_mode: "legacy_month_cutoff",
      purged_n_splits: 5,
      purged_embargo_pct: 0.01,
    },
    rankerConfig: {
      objective: "rank_xendcg",
      metric: "ndcg",
      ndcg_eval_at: [5, 10, 20],
      learning_rate: 0.03,
      n_estimators: 6000,
      num_leaves: 63,
      min_data_in_leaf: 300,
      subsample: 0.8,
      colsample_bytree: 0.8,
      reg_lambda: 10.0,
      random_state: 42,
      early_stopping_rounds: 200,
      stacking_enabled: false,
      stacking_alpha: 1.0,
    },
    quickMode: false,
    featurePruning: false,
    walkForwardCompact: false,
    datePeriodYears: 5,
    featureLags: [1, 2, 3, 5, 10, 20],
    thetaGrid: [0.8, 1.0, 1.2, 1.5],
  },
  thorough: {
    id: "thorough",
    label: "Thorough",
    description: "7y dataset + HPO + full features for final production runs.",
    estimatedTime: "~40m-2h",
    modelConfig: {
      seq_len: 90,
      xgb_n_estimators: 600,
      xgb_max_depth: 5,
      xgb_learning_rate: 0.02,
      xgb_subsample: 0.9,
      xgb_colsample_bytree: 0.9,
      lstm_hidden_size: 128,
      lstm_num_layers: 3,
      lstm_dropout: 0.15,
      lstm_epochs: 50,
      lstm_batch_size: 64,
      lstm_learning_rate: 0.0005,
      train_val_split: 0.8,
    },
    walkForward: {
      train_months: 48,
      embargo_months: 1,
      val_months: 1,
      step_months: 1,
      purging_mode: "legacy_month_cutoff",
      purged_n_splits: 5,
      purged_embargo_pct: 0.01,
    },
    rankerConfig: {
      objective: "rank_xendcg",
      metric: "ndcg",
      ndcg_eval_at: [5, 10, 20],
      learning_rate: 0.02,
      n_estimators: 8000,
      num_leaves: 63,
      min_data_in_leaf: 200,
      subsample: 0.85,
      colsample_bytree: 0.85,
      reg_lambda: 8.0,
      random_state: 42,
      early_stopping_rounds: 300,
      stacking_enabled: true,
      stacking_alpha: 1.0,
    },
    quickMode: false,
    featurePruning: false,
    walkForwardCompact: false,
    datePeriodYears: 7,
    featureLags: [1, 2, 3, 5, 10, 20, 60],
    thetaGrid: [0.6, 0.8, 1.0, 1.2, 1.5, 2.0],
  },
};

export const defaultModelConfig = SPEED_PRESETS.standard.modelConfig;

export const DEFAULT_PORTFOLIO_POLICY: PortfolioPolicyPayload = {
  template: "diversified_long_only",
  single_name_max_abs_weight: 0.06,
  small_universe_policy: "cash_buffer",
  sector_concentration_max: 0.35,
  turnover_max: 1.0,
  gross_exposure_max: 1.0,
  net_exposure_abs_max: 1.0,
  cash_symbol: "CASH",
  cash_category: "cash_proxy",
};

export function toBacktestErrorMessage(error: unknown): string {
  const msg = error instanceof Error ? error.message : String(error);
  if (/run is not completed/i.test(msg))
    return "선택한 Run이 완료(completed) 상태가 아닙니다. Recent Runs에서 completed 항목을 선택하세요.";
  if (/run not found/i.test(msg))
    return "Run ID를 찾을 수 없습니다. Recent Runs에서 다시 선택하거나 Run ID를 확인하세요.";
  if (/selected model artifacts are not ready/i.test(msg))
    return "선택한 모델 아티팩트가 준비되지 않았습니다. 시그널 재생성 후 다시 시도하세요.";
  if (/not completed/i.test(msg)) return "Training is not completed yet.";
  if (/prediction.*not found/i.test(msg))
    return "Prediction artifact is missing. Run Generate Signals first.";
  if (/no trading days/i.test(msg))
    return "No trading days in selected date range. Check Start/End date.";
  if (/do not overlap/i.test(msg))
    return "Prediction dates and price dates do not overlap.";
  if (/no overlapping symbols/i.test(msg))
    return "Prediction symbols and price symbols do not overlap.";
  if (/market data.*missing/i.test(msg))
    return "Market data files are missing. Re-run training.";
  if (/empty/i.test(msg) && /prediction/i.test(msg))
    return "Prediction dataset is empty. Re-generate signals.";
  if (/no price data/i.test(msg))
    return "No price data available. Re-run training.";
  return msg;
}

export function parseSymbolsText(text: string): string[] {
  const seen = new Set<string>();
  const parsed: string[] = [];
  const items = text
    .split(/[\s,;]+/)
    .map((item) => item.trim())
    .filter(Boolean);

  for (const item of items) {
    const normalized = item.toUpperCase();
    if (!seen.has(normalized)) {
      seen.add(normalized);
      parsed.push(normalized);
    }
  }

  return parsed;
}

export function formatSymbolsForTextarea(symbols: string[], perLine = 6): string {
  if (symbols.length === 0) {
    return "";
  }
  const lines: string[] = [];
  for (let idx = 0; idx < symbols.length; idx += perLine) {
    lines.push(symbols.slice(idx, idx + perLine).join(", "));
  }
  return lines.join("\n");
}

export function symbolsByProfile(
  assets: UniverseAsset[],
  profileId: UniverseProfileId,
): string[] {
  if (profileId === "all" || profileId === "custom") {
    return assets.map((asset) => asset.symbol);
  }

  if (profileId === "aggressive") {
    return assets
      .filter((asset) => AGGRESSIVE_CATEGORIES.has(asset.category))
      .map((asset) => asset.symbol);
  }

  return assets
    .filter((asset) => DEFENSIVE_CATEGORIES.has(asset.category))
    .map((asset) => asset.symbol);
}

export function profileLabel(profileId: UniverseProfileId): string {
  if (profileId === "custom") {
    return "Custom";
  }
  return (
    PROFILE_LIST.find((profile) => profile.id === profileId)?.label ?? "Custom"
  );
}
