import { clearCachePrefix, getCachedOrFetch } from "./quantCache";
import { buildOpenBBRequestInit, buildOpenBBRequestUrl } from "./openbbBackend";
import type { FeatureActivation, FeatureActivationResult } from "../types/feature-activation";
import type {
  AlertsPayload,
  ArtifactSummaryPayload,
  BacktestRequestPayload,
  BacktestResponsePayload,
  WalkForwardBacktestRequestPayload,
  WalkForwardBacktestStatusPayload,
  WalkForwardBacktestSubmitPayload,
  DashboardHealthPayload,
  DashboardBootstrapPayload,
  DashboardMode,
  DataQualityHistoryPayload,
  DataQualityLatestPayload,
  ExecutionMode,
  ExecutionModePayload,
  ExecutionModeUpdateRequestPayload,
  FeatureImportancePayload,
  ICDecayPayload,
  ModelShapPayload,
  ModelICPayload,
  ModelName,
  ExperimentListPayload,
  ExperimentRunItemPayload,
  ModelRegistryEntryPayload,
  ModelRegistryHistoryPayload,
  ModelPerformancePayload,
  ModelRegimePayload,
  NotificationsHistoryPayload,
  OpsIssueQueuePayload,
  OpsStatusPayload,
  PerformanceRegimePayload,
  PortfolioPolicyPayload,
  RebalanceHistoryPayload,
  PromotedModelPayload,
  ExecutionOrderPreviewRequestPayload,
  ExecutionPreviewPayload,
  ExecutionSubmitPayload,
  ExecutionOrdersPayload,
  ExecutionFillsPayload,
  ExecutionPositionsPayload,
  ExecutionPnlPayload,
  RiskPretradeRequestPayload,
  RiskPretradePayload,
  RiskLimitsPayload,
  RiskEventsPayload,
  ReportsHistoryPayload,
  ReportsLatestPayload,
  PortfolioExposurePayload,
  PortfolioCurrentPayload,
  PortfolioRiskPayload,
  PredictionDistributionPayload,
  PredictionsLatestPayload,
  RunLatestConstraintsPayload,
  RunLatestMetaPayload,
  RunLatestExposuresPayload,
  RunLatestRiskPayload,
  RunSnapshotPayload,
  RunAuditPayload,
  RunConstraintsPayload,
  RunRiskPayload,
  RunExposuresPayload,
  RegimeCurrentPayload,
  RegimeHistoryPayload,
  RollingPerformancePayload,
  RunListPayload,
  RunStatusPayload,
  SignalsRequestPayload,
  SignalsResponsePayload,
  SnapshotProfile,
  TrainRequestPayload,
  TrainResponsePayload,
  UniverseResponse,
  UniverseListPayload,
  UniverseExclusionsPayload,
  UniverseResolvePayload,
  UniverseSnapshotPayload,
  SchedulerStatusPayload,
  SymbolContextPayload,
  TradingAlgorithmToggleRequestPayload,
  TradingAlgorithmValidationPayload,
  TradingAlgorithmValidateRequestPayload,
  TradingAlgorithmsPayload,
  TradingCycleRunPayload,
  TradingCycleRunRequestPayload,
  TradingEventsPayload,
  TradingExecutionModePayload,
  TradingFillsPayload,
  TradingOrdersPayload,
  TradingPerformancePayload,
  TradingPositionsPayload,
  TradingRiskPayload,
  TradingScanPayload,
  TradingSettingsPayload,
  TradingSettingsUpdatePayload,
  TradingStatusPayload,
  TradingSymbolDetailPayload,
  RunComparePayload,
  WorkspaceBriefPayload,
} from "../types/quant";
import {
  parseRunAudit,
  parseRunExposures,
  parseRunLatestConstraints,
  parseRunLatestMeta,
  parseRunRisk,
  parseRunSnapshot,
} from "./quantSchemas";

const QUANT_PREFIX = "/api/v1/quant_ml";
const DASHBOARD_CACHE_TTL_MS = 60_000;
const LIVE_CACHE_TTL_MS = 5_000;
const LEGACY_TRADING_ENDPOINT_TTL_MS = 60 * 60 * 1000;
const LOCAL_API_RETRY_BASE_MS = 150;

function buildFeatureActivation(featureName: string, available: boolean, detail?: string): FeatureActivation {
  return {
    featureName,
    available,
    detail: detail ?? null,
    lastCheckedAt: new Date().toISOString(),
  };
}

interface DashboardRequestOptions {
  mode?: DashboardMode;
  signal?: AbortSignal;
  snapshotProfile?: SnapshotProfile;
}

const MAX_RETRIES = 2;
const RETRY_BASE_MS = 500;

function isLoopbackBaseUrl(baseUrl: string): boolean {
  try {
    const parsed = new URL(baseUrl);
    const { hostname } = parsed;
    return (
      hostname === "127.0.0.1" ||
      hostname === "::1" ||
      hostname === "localhost" ||
      hostname.endsWith(".localhost")
    );
  } catch {
    return false;
  }
}

function getRetryPolicy(baseUrl: string): { retries: number; baseDelayMs: number } {
  if (isLoopbackBaseUrl(baseUrl)) {
    return {
      retries: import.meta.env.DEV ? 1 : 1,
      baseDelayMs: LOCAL_API_RETRY_BASE_MS,
    };
  }

  return {
    retries: MAX_RETRIES,
    baseDelayMs: RETRY_BASE_MS,
  };
}

function isRetryableError(response: Response | null, error: unknown): boolean {
  if (response) {
    return response.status === 503 || response.status === 502 || response.status === 504;
  }
  const msg = error instanceof Error ? error.message : String(error);
  return (
    msg.includes("Failed to fetch") ||
    msg.includes("NetworkError") ||
    msg.includes("network") ||
    msg.includes("ECONNRESET") ||
    msg.includes("ETIMEDOUT")
  );
}

async function requestJson<T>(baseUrl: string, path: string, init: RequestInit): Promise<T> {
  const retryPolicy = getRetryPolicy(baseUrl);
  let lastError: Error | null = null;
  let lastResponse: Response | null = null;

  for (let attempt = 0; attempt <= retryPolicy.retries; attempt++) {
    try {
      const response = await fetch(buildOpenBBRequestUrl(baseUrl, path), buildOpenBBRequestInit(init));
      lastResponse = response;

      if (!response.ok) {
        let detail = "";
        try {
          const payload = await response.json();
          detail = payload?.detail ? String(payload.detail) : "";
        } catch {
          detail = "";
        }
        const err = new Error(detail || `Request failed (${response.status})`);
        if (attempt < retryPolicy.retries && isRetryableError(response, null)) {
          const delayMs = retryPolicy.baseDelayMs * Math.pow(2, attempt);
          await new Promise((resolve) => setTimeout(resolve, delayMs));
          continue;
        }
        throw err;
      }
      return (await response.json()) as T;
    } catch (error) {
      lastError = error instanceof Error ? error : new Error(String(error));
      if (attempt < retryPolicy.retries && isRetryableError(lastResponse, error)) {
        const delayMs = retryPolicy.baseDelayMs * Math.pow(2, attempt);
        await new Promise((resolve) => setTimeout(resolve, delayMs));
        continue;
      }
      throw lastError;
    }
  }

  throw lastError ?? new Error("Request failed after retries");
}

async function requestJsonParsed<T>(
  baseUrl: string,
  path: string,
  init: RequestInit,
  parse: (payload: unknown) => T,
): Promise<T> {
  const payload = await requestJson<unknown>(baseUrl, path, init);
  return parse(payload);
}

function requestJsonCached<T>(
  cacheKey: string,
  baseUrl: string,
  path: string,
  init: RequestInit,
): Promise<T> {
  return getCachedOrFetch(cacheKey, DASHBOARD_CACHE_TTL_MS, () => requestJson<T>(baseUrl, path, init));
}

function requestJsonMaybeCached<T>(
  cacheKey: string,
  ttlMs: number,
  baseUrl: string,
  path: string,
  init: RequestInit,
): Promise<T> {
  if (ttlMs <= 0) {
    return requestJson<T>(baseUrl, path, init);
  }
  return getCachedOrFetch(cacheKey, ttlMs, () => requestJson<T>(baseUrl, path, init));
}

function ttlForMode(mode: DashboardMode): number {
  return mode === "live" ? LIVE_CACHE_TTL_MS : DASHBOARD_CACHE_TTL_MS;
}

function getLegacyTradingEndpointCacheKey(baseUrl: string, endpoint: string): string {
  return `quant-legacy-endpoint:${baseUrl}:${endpoint}`;
}

function isLegacyTradingEndpointCached(baseUrl: string, endpoint: string): boolean {
  try {
    const raw = sessionStorage.getItem(getLegacyTradingEndpointCacheKey(baseUrl, endpoint));
    if (!raw) return false;
    const expiresAt = Number(raw);
    if (!Number.isFinite(expiresAt) || expiresAt < Date.now()) {
      sessionStorage.removeItem(getLegacyTradingEndpointCacheKey(baseUrl, endpoint));
      return false;
    }
    return true;
  } catch {
    return false;
  }
}

function markLegacyTradingEndpoint(baseUrl: string, endpoint: string): void {
  try {
    sessionStorage.setItem(
      getLegacyTradingEndpointCacheKey(baseUrl, endpoint),
      String(Date.now() + LEGACY_TRADING_ENDPOINT_TTL_MS),
    );
  } catch {
    // Ignore storage failures and fall back to probing again later.
  }
}

function isLegacyTradingSettingsRouteError(error: unknown): boolean {
  const message = error instanceof Error ? error.message : String(error);
  return (
    message.includes("trading_settings_update") &&
    message.includes("ValidationError")
  );
}

function isLegacyTradingExecutionModeRouteError(error: unknown): boolean {
  const message = error instanceof Error ? error.message : String(error);
  return (
    message.includes("trading_execution_mode_update") &&
    message.includes("ValidationError")
  );
}

function createDefaultTradingSettingsPayload(): TradingSettingsPayload {
  return {
    version: "v1",
    tab_name: "Trading",
    mode: "paper",
    runtime_status: "stopped",
    universe_id: "default",
    schedule: {
      mode: "eod",
      scan_interval_minutes: 1440,
      timeframe: "1d",
    },
    scan: {
      lookback_days: 320,
      provider: "yfinance",
      max_workers: 8,
      max_data_delay_days: 5,
    },
    execution: {
      mode: "paper",
      auto_order: false,
      manual_approval: false,
      signal_generation: true,
      fill_policy: "close",
      slippage_bps: 2.0,
      commission_bps: 1.0,
    },
    account: {
      initial_cash: 1_000_000,
      position_size_mode: "percent",
      position_size_value: 0.05,
      max_concurrent_positions: 12,
      max_daily_new_entries: 5,
      max_daily_gross_entry: 250_000,
      max_order_notional: 150_000,
      reentry_cooldown_days: 5,
      max_daily_orders: 20,
    },
    risk: {
      max_position_weight: 0.10,
      max_sector_weight: 0.35,
      min_avg_dollar_volume: 2_500_000,
      max_atr_pct: 0.12,
      stop_loss_pct: 0.08,
      take_profit_pct: 0.15,
      trailing_stop_enabled: false,
      trailing_stop_pct: 0.05,
      daily_loss_limit: 35_000,
      portfolio_drawdown_limit: 0.15,
      capital_cap: 750_000,
      allow_duplicate_exposure: false,
    },
    strategies: {
      ema_cross: {
        enabled: true,
        params: {
          fast_span: 12,
          slow_span: 26,
          rsi_ceiling: 72,
        },
      },
      rsi_reversal: {
        enabled: true,
        params: {
          oversold: 30,
          rebound_level: 35,
          overbought_exit: 70,
        },
      },
      breakout_volume: {
        enabled: true,
        params: {
          lookback: 20,
          volume_multiple: 1.8,
          min_atr_pct: 0.01,
          max_atr_pct: 0.10,
        },
      },
    },
    custom_algorithms: {
      path: "openbb_quant_ml/algorithms",
      auto_pause_failure_threshold: 3,
      allowed_auto_order_statuses: ["active"],
      default_status: "sandbox",
      signal_only_dev: true,
      dry_run_default: true,
    },
    ui: {
      polling_ms: 5000,
      history_limit: 250,
    },
    built_in_strategies: [],
    custom_algorithm_records: [],
  };
}

export function invalidateQuantCaches(baseUrl: string, runId?: string, modelName?: ModelName): void {
  clearCachePrefix("dashboard-");
  clearCachePrefix("dashboard-bootstrap:");
  clearCachePrefix("portfolio-current:");
  clearCachePrefix("portfolio-rebalance-history:");
  clearCachePrefix("predictions-latest:");
  clearCachePrefix("model-performance:");

  if (runId && modelName) {
    clearCachePrefix(`dashboard-bootstrap:${baseUrl}:${runId}:${modelName}`);
    clearCachePrefix(`portfolio-current:${baseUrl}:${runId}:${modelName}`);
    clearCachePrefix(`portfolio-rebalance-history:${baseUrl}:${runId}:${modelName}`);
    clearCachePrefix(`predictions-latest:${baseUrl}:${runId}:${modelName}`);
    clearCachePrefix(`model-performance:${baseUrl}:${runId}`);
  }
}

export function fetchUniverse(baseUrl: string): Promise<UniverseResponse> {
  return requestJson<UniverseResponse>(baseUrl, `${QUANT_PREFIX}/universe`, {
    method: "GET",
  });
}

export function fetchUniverseList(baseUrl: string): Promise<UniverseListPayload> {
  return requestJson<UniverseListPayload>(baseUrl, `${QUANT_PREFIX}/universe/list`, {
    method: "GET",
  });
}

export async function fetchUniverseListWithActivation(
  baseUrl: string,
): Promise<FeatureActivationResult<UniverseListPayload>> {
  try {
    const data = await fetchUniverseList(baseUrl);
    return {
      activation: buildFeatureActivation("quant_ml", true),
      data,
    };
  } catch (error) {
    return {
      activation: buildFeatureActivation(
        "quant_ml",
        false,
        error instanceof Error ? error.message : "quant_ml extension unavailable",
      ),
    };
  }
}

export async function probeQuantMlActivation(baseUrl: string): Promise<FeatureActivation> {
  const result = await fetchUniverseListWithActivation(baseUrl);
  return result.activation;
}

export function resolveUniverse(
  baseUrl: string,
  universeId: string,
  mode = "train",
  includeSymbols = false,
): Promise<UniverseResolvePayload> {
  const query = new URLSearchParams({
    universe_id: universeId,
    mode,
    include_symbols: String(includeSymbols),
  });
  return requestJson<UniverseResolvePayload>(
    baseUrl,
    `${QUANT_PREFIX}/universe/resolve?${query.toString()}`,
    {
      method: "GET",
    },
  );
}

export function startTrain(baseUrl: string, payload: TrainRequestPayload): Promise<TrainResponsePayload> {
  return requestJson<TrainResponsePayload>(baseUrl, `${QUANT_PREFIX}/train`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function fetchRunStatus(baseUrl: string, runId: string): Promise<RunStatusPayload> {
  return requestJson<RunStatusPayload>(baseUrl, `${QUANT_PREFIX}/runs/${runId}`, {
    method: "GET",
  });
}

export function createRunLogStreamUrl(
  baseUrl: string,
  runId: string,
  pollIntervalSec = 1.0,
  maxSeconds = 600,
): string {
  const query = new URLSearchParams({
    poll_interval_sec: String(pollIntervalSec),
    max_seconds: String(maxSeconds),
  });
  return buildOpenBBRequestUrl(
    baseUrl,
    `${QUANT_PREFIX}/runs/${encodeURIComponent(runId)}/stream?${query.toString()}`,
  );
}

export function fetchRunsList(
  baseUrl: string,
  limit = 20,
  options: { completedFirst?: boolean; actionableOnly?: boolean } = {},
): Promise<RunListPayload> {
  const query = new URLSearchParams({
    limit: String(limit),
    completed_first: String(options.completedFirst ?? true),
    actionable_only: String(options.actionableOnly ?? false),
  });
  return requestJson<RunListPayload>(baseUrl, `${QUANT_PREFIX}/runs/list?${query.toString()}`, {
    method: "GET",
  });
}

export function createSignals(
  baseUrl: string,
  payload: SignalsRequestPayload,
): Promise<SignalsResponsePayload> {
  return requestJson<SignalsResponsePayload>(baseUrl, `${QUANT_PREFIX}/signals`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function runBacktest(
  baseUrl: string,
  payload: BacktestRequestPayload,
): Promise<BacktestResponsePayload> {
  return requestJson<BacktestResponsePayload>(baseUrl, `${QUANT_PREFIX}/backtest`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function fetchRunBacktest(
  baseUrl: string,
  runId: string,
  modelName: ModelName,
): Promise<BacktestResponsePayload> {
  const query = new URLSearchParams({ model_name: modelName });
  return requestJson<BacktestResponsePayload>(
    baseUrl,
    `${QUANT_PREFIX}/runs/${encodeURIComponent(runId)}/backtest?${query.toString()}`,
    { method: "GET" },
  );
}

export function runBacktestWalkforward(
  baseUrl: string,
  payload: WalkForwardBacktestRequestPayload,
): Promise<WalkForwardBacktestSubmitPayload> {
  return requestJson<WalkForwardBacktestSubmitPayload>(baseUrl, `${QUANT_PREFIX}/backtest/walkforward`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function fetchWalkforwardBacktestStatus(
  baseUrl: string,
  jobId: string,
): Promise<WalkForwardBacktestStatusPayload> {
  return requestJson<WalkForwardBacktestStatusPayload>(
    baseUrl,
    `${QUANT_PREFIX}/backtest/walkforward/${encodeURIComponent(jobId)}`,
    { method: "GET" },
  );
}

export function fetchPromotedModel(
  baseUrl: string,
  modelName: ModelName = "lgbm_ranker",
): Promise<PromotedModelPayload> {
  const query = new URLSearchParams({ model_name: modelName });
  return requestJson<PromotedModelPayload>(
    baseUrl,
    `${QUANT_PREFIX}/model/promoted?${query.toString()}`,
    { method: "GET" },
  );
}

export function fetchRunLatestMeta(
  baseUrl: string,
  modelName: ModelName = "lgbm_ranker",
  runId?: string,
): Promise<RunLatestMetaPayload> {
  const query = new URLSearchParams({ model_name: modelName });
  if (runId && runId.trim()) {
    query.set("run_id", runId.trim());
  }
  return requestJsonParsed<RunLatestMetaPayload>(
    baseUrl,
    `${QUANT_PREFIX}/run/latest/meta?${query.toString()}`,
    { method: "GET" },
    parseRunLatestMeta,
  );
}

export function fetchRunLatestRisk(
  baseUrl: string,
  modelName: ModelName = "lgbm_ranker",
  runId?: string,
  lookback = 126,
): Promise<RunLatestRiskPayload> {
  const query = new URLSearchParams({
    model_name: modelName,
    lookback: String(lookback),
  });
  if (runId && runId.trim()) {
    query.set("run_id", runId.trim());
  }
  return requestJsonParsed<RunLatestRiskPayload>(
    baseUrl,
    `${QUANT_PREFIX}/run/latest/risk?${query.toString()}`,
    { method: "GET" },
    parseRunRisk,
  );
}

export function fetchRunLatestExposures(
  baseUrl: string,
  modelName: ModelName = "lgbm_ranker",
  runId?: string,
): Promise<RunLatestExposuresPayload> {
  const query = new URLSearchParams({ model_name: modelName });
  if (runId && runId.trim()) {
    query.set("run_id", runId.trim());
  }
  return requestJsonParsed<RunLatestExposuresPayload>(
    baseUrl,
    `${QUANT_PREFIX}/run/latest/exposures?${query.toString()}`,
    { method: "GET" },
    parseRunExposures,
  );
}

export function fetchRunLatestConstraints(
  baseUrl: string,
  modelName: ModelName = "lgbm_ranker",
  runId?: string,
): Promise<RunLatestConstraintsPayload> {
  const query = new URLSearchParams({ model_name: modelName });
  if (runId && runId.trim()) {
    query.set("run_id", runId.trim());
  }
  return requestJsonParsed<RunLatestConstraintsPayload>(
    baseUrl,
    `${QUANT_PREFIX}/run/latest/constraints?${query.toString()}`,
    { method: "GET" },
    parseRunLatestConstraints,
  );
}

export function fetchRunSnapshot(
  baseUrl: string,
  runId: string,
  modelName: ModelName = "lgbm_ranker",
  options: { profile?: SnapshotProfile } = {},
): Promise<RunSnapshotPayload> {
  const query = new URLSearchParams({
    model_name: modelName,
    profile: options.profile ?? "full",
  });
  return requestJsonParsed<RunSnapshotPayload>(
    baseUrl,
    `${QUANT_PREFIX}/runs/${encodeURIComponent(runId)}/snapshot?${query.toString()}`,
    { method: "GET" },
    parseRunSnapshot,
  );
}

export function fetchRunRisk(
  baseUrl: string,
  runId: string,
  modelName: ModelName = "lgbm_ranker",
  lookback = 126,
): Promise<RunRiskPayload> {
  const query = new URLSearchParams({
    model_name: modelName,
    lookback: String(lookback),
  });
  return requestJsonParsed<RunRiskPayload>(
    baseUrl,
    `${QUANT_PREFIX}/runs/${encodeURIComponent(runId)}/risk?${query.toString()}`,
    { method: "GET" },
    parseRunRisk,
  );
}

export function fetchRunExposures(
  baseUrl: string,
  runId: string,
  modelName: ModelName = "lgbm_ranker",
): Promise<RunExposuresPayload> {
  const query = new URLSearchParams({ model_name: modelName });
  return requestJsonParsed<RunExposuresPayload>(
    baseUrl,
    `${QUANT_PREFIX}/runs/${encodeURIComponent(runId)}/exposures?${query.toString()}`,
    { method: "GET" },
    parseRunExposures,
  );
}

export function fetchRunConstraints(
  baseUrl: string,
  runId: string,
  modelName: ModelName = "lgbm_ranker",
): Promise<RunConstraintsPayload> {
  const query = new URLSearchParams({ model_name: modelName });
  return requestJsonParsed<RunConstraintsPayload>(
    baseUrl,
    `${QUANT_PREFIX}/runs/${encodeURIComponent(runId)}/constraints?${query.toString()}`,
    { method: "GET" },
    parseRunLatestConstraints,
  );
}

export function fetchRunAudit(
  baseUrl: string,
  runId: string,
  limit = 500,
): Promise<RunAuditPayload> {
  const query = new URLSearchParams({ limit: String(limit) });
  return requestJsonParsed<RunAuditPayload>(
    baseUrl,
    `${QUANT_PREFIX}/runs/${encodeURIComponent(runId)}/audit?${query.toString()}`,
    { method: "GET" },
    parseRunAudit,
  );
}

export function fetchArtifactSummary(
  baseUrl: string,
  runId: string,
  modelName: ModelName,
): Promise<ArtifactSummaryPayload> {
  const query = new URLSearchParams({ model_name: modelName });
  return requestJson<ArtifactSummaryPayload>(
    baseUrl,
    `${QUANT_PREFIX}/artifacts/${runId}/summary?${query.toString()}`,
    {
      method: "GET",
    },
  );
}

export function fetchModelPerformance(baseUrl: string, runId: string): Promise<ModelPerformancePayload> {
  const query = new URLSearchParams({ run_id: runId });
  return requestJsonCached<ModelPerformancePayload>(
    `model-performance:${baseUrl}:${runId}`,
    baseUrl,
    `${QUANT_PREFIX}/model/performance?${query.toString()}`,
    { method: "GET" },
  );
}

export function fetchModelIc(
  baseUrl: string,
  runId: string,
  modelName: ModelName,
  window = 6,
): Promise<ModelICPayload> {
  const query = new URLSearchParams({
    run_id: runId,
    model_name: modelName,
    window: String(window),
  });
  return requestJsonCached<ModelICPayload>(
    `model-ic:${baseUrl}:${runId}:${modelName}:${window}`,
    baseUrl,
    `${QUANT_PREFIX}/model/ic?${query.toString()}`,
    { method: "GET" },
  );
}

export function fetchModelRegime(
  baseUrl: string,
  runId: string,
  modelName: ModelName,
): Promise<ModelRegimePayload> {
  const query = new URLSearchParams({
    run_id: runId,
    model_name: modelName,
  });
  return requestJsonCached<ModelRegimePayload>(
    `model-regime:${baseUrl}:${runId}:${modelName}`,
    baseUrl,
    `${QUANT_PREFIX}/model/regime?${query.toString()}`,
    { method: "GET" },
  );
}

export function fetchPortfolioCurrent(
  baseUrl: string,
  runId: string,
  modelName: ModelName,
  useCache = false,
): Promise<PortfolioCurrentPayload> {
  const query = new URLSearchParams({
    run_id: runId,
    model_name: modelName,
  });
  const path = `${QUANT_PREFIX}/portfolio/current?${query.toString()}`;
  if (!useCache) {
    return requestJson<PortfolioCurrentPayload>(baseUrl, path, { method: "GET" });
  }
  return requestJsonCached<PortfolioCurrentPayload>(
    `portfolio-current:${baseUrl}:${runId}:${modelName}`,
    baseUrl,
    path,
    { method: "GET" },
  );
}

export function fetchRebalanceHistory(
  baseUrl: string,
  runId: string,
  modelName: ModelName,
  useCache = false,
): Promise<RebalanceHistoryPayload> {
  const query = new URLSearchParams({
    run_id: runId,
    model_name: modelName,
  });
  const path = `${QUANT_PREFIX}/portfolio/rebalance/history?${query.toString()}`;
  if (!useCache) {
    return requestJson<RebalanceHistoryPayload>(baseUrl, path, { method: "GET" });
  }
  return requestJsonCached<RebalanceHistoryPayload>(
    `portfolio-rebalance-history:${baseUrl}:${runId}:${modelName}`,
    baseUrl,
    path,
    { method: "GET" },
  );
}

export function fetchPortfolioPolicy(baseUrl: string): Promise<PortfolioPolicyPayload> {
  return requestJson<PortfolioPolicyPayload>(baseUrl, `${QUANT_PREFIX}/portfolio/policy`, { method: "GET" });
}

export function fetchUniverseSnapshot(baseUrl: string, runId: string): Promise<UniverseSnapshotPayload> {
  const query = new URLSearchParams({ run_id: runId });
  return requestJson<UniverseSnapshotPayload>(baseUrl, `${QUANT_PREFIX}/universe/snapshot?${query.toString()}`, {
    method: "GET",
  });
}

export function fetchUniverseExclusions(baseUrl: string, runId: string): Promise<UniverseExclusionsPayload> {
  const query = new URLSearchParams({ run_id: runId });
  return requestJson<UniverseExclusionsPayload>(baseUrl, `${QUANT_PREFIX}/universe/exclusions?${query.toString()}`, {
    method: "GET",
  });
}

export function fetchFeatureImportance(
  baseUrl: string,
  runId: string,
  modelName: ModelName,
): Promise<FeatureImportancePayload> {
  const query = new URLSearchParams({
    run_id: runId,
    model_name: modelName,
  });
  return requestJsonCached<FeatureImportancePayload>(
    `feature-importance:${baseUrl}:${runId}:${modelName}`,
    baseUrl,
    `${QUANT_PREFIX}/feature/importance?${query.toString()}`,
    { method: "GET" },
  );
}

export function fetchPredictionsLatest(
  baseUrl: string,
  runId: string,
  modelName: ModelName,
  topK = 20,
): Promise<PredictionsLatestPayload> {
  const query = new URLSearchParams({
    run_id: runId,
    model_name: modelName,
    top_k: String(topK),
  });
  return requestJsonCached<PredictionsLatestPayload>(
    `predictions-latest:${baseUrl}:${runId}:${modelName}:${topK}`,
    baseUrl,
    `${QUANT_PREFIX}/predictions/latest?${query.toString()}`,
    { method: "GET" },
  );
}

export function fetchDashboardHealth(
  baseUrl: string,
  runId?: string,
  modelName: ModelName = "lgbm_ranker",
  options: DashboardRequestOptions = {},
): Promise<DashboardHealthPayload> {
  const mode = options.mode ?? "backtest";
  const query = new URLSearchParams({ model_name: modelName, mode });
  if (runId && runId.trim()) {
    query.set("run_id", runId.trim());
  }
  return requestJsonMaybeCached<DashboardHealthPayload>(
    `dashboard-health:${baseUrl}:${runId ?? ""}:${modelName}:${mode}`,
    ttlForMode(mode),
    baseUrl,
    `${QUANT_PREFIX}/health?${query.toString()}`,
    { method: "GET", signal: options.signal },
  );
}

export function fetchDashboardBootstrap(
  baseUrl: string,
  runId?: string,
  modelName: ModelName = "lgbm_ranker",
  options: DashboardRequestOptions = {},
): Promise<DashboardBootstrapPayload> {
  const mode = options.mode ?? "backtest";
  const snapshotProfile = options.snapshotProfile ?? "core";
  const query = new URLSearchParams({
    model_name: modelName,
    mode,
    snapshot_profile: snapshotProfile,
  });
  if (runId && runId.trim()) {
    query.set("run_id", runId.trim());
  }
  return requestJsonMaybeCached<DashboardBootstrapPayload>(
    `dashboard-bootstrap:${baseUrl}:${runId ?? ""}:${modelName}:${mode}:${snapshotProfile}`,
    ttlForMode(mode),
    baseUrl,
    `${QUANT_PREFIX}/dashboard/bootstrap?${query.toString()}`,
    { method: "GET", signal: options.signal },
  );
}

export function fetchPerformanceRolling(
  baseUrl: string,
  runId: string,
  modelName: ModelName,
  windowShort = 63,
  windowLong = 126,
  options: DashboardRequestOptions = {},
): Promise<RollingPerformancePayload> {
  const mode = options.mode ?? "backtest";
  const query = new URLSearchParams({
    run_id: runId,
    model_name: modelName,
    window_short: String(windowShort),
    window_long: String(windowLong),
  });
  return requestJsonMaybeCached<RollingPerformancePayload>(
    `dashboard-rolling:${baseUrl}:${runId}:${modelName}:${windowShort}:${windowLong}:${mode}`,
    ttlForMode(mode),
    baseUrl,
    `${QUANT_PREFIX}/performance/rolling?${query.toString()}`,
    { method: "GET", signal: options.signal },
  );
}

export function fetchPerformanceRegime(
  baseUrl: string,
  runId: string,
  modelName: ModelName,
  options: DashboardRequestOptions = {},
): Promise<PerformanceRegimePayload> {
  const mode = options.mode ?? "backtest";
  const query = new URLSearchParams({
    run_id: runId,
    model_name: modelName,
  });
  return requestJsonMaybeCached<PerformanceRegimePayload>(
    `dashboard-regime-perf:${baseUrl}:${runId}:${modelName}:${mode}`,
    ttlForMode(mode),
    baseUrl,
    `${QUANT_PREFIX}/performance/regime?${query.toString()}`,
    { method: "GET", signal: options.signal },
  );
}

export function fetchPortfolioExposure(
  baseUrl: string,
  runId: string,
  modelName: ModelName,
  options: DashboardRequestOptions = {},
): Promise<PortfolioExposurePayload> {
  const mode = options.mode ?? "backtest";
  const query = new URLSearchParams({
    run_id: runId,
    model_name: modelName,
  });
  return requestJsonMaybeCached<PortfolioExposurePayload>(
    `dashboard-portfolio-exposure:${baseUrl}:${runId}:${modelName}:${mode}`,
    ttlForMode(mode),
    baseUrl,
    `${QUANT_PREFIX}/portfolio/exposure?${query.toString()}`,
    { method: "GET", signal: options.signal },
  );
}

export function fetchPortfolioRisk(
  baseUrl: string,
  runId: string,
  modelName: ModelName,
  lookback = 126,
  options: DashboardRequestOptions = {},
): Promise<PortfolioRiskPayload> {
  const mode = options.mode ?? "backtest";
  const query = new URLSearchParams({
    run_id: runId,
    model_name: modelName,
    lookback: String(lookback),
  });
  return requestJsonMaybeCached<PortfolioRiskPayload>(
    `dashboard-portfolio-risk:${baseUrl}:${runId}:${modelName}:${lookback}:${mode}`,
    ttlForMode(mode),
    baseUrl,
    `${QUANT_PREFIX}/portfolio/risk?${query.toString()}`,
    { method: "GET", signal: options.signal },
  );
}

export function fetchModelIcDecay(
  baseUrl: string,
  runId: string,
  modelName: ModelName,
  maxHorizon = 20,
  options: DashboardRequestOptions = {},
): Promise<ICDecayPayload> {
  const mode = options.mode ?? "backtest";
  const query = new URLSearchParams({
    run_id: runId,
    model_name: modelName,
    max_horizon: String(maxHorizon),
  });
  return requestJsonMaybeCached<ICDecayPayload>(
    `dashboard-ic-decay:${baseUrl}:${runId}:${modelName}:${maxHorizon}:${mode}`,
    ttlForMode(mode),
    baseUrl,
    `${QUANT_PREFIX}/model/ic_decay?${query.toString()}`,
    { method: "GET", signal: options.signal },
  );
}

export function fetchPredictionDistribution(
  baseUrl: string,
  runId: string,
  modelName: ModelName,
  bins = 30,
  options: DashboardRequestOptions = {},
): Promise<PredictionDistributionPayload> {
  const mode = options.mode ?? "backtest";
  const query = new URLSearchParams({
    run_id: runId,
    model_name: modelName,
    bins: String(bins),
  });
  return requestJsonMaybeCached<PredictionDistributionPayload>(
    `dashboard-pred-dist:${baseUrl}:${runId}:${modelName}:${bins}:${mode}`,
    ttlForMode(mode),
    baseUrl,
    `${QUANT_PREFIX}/model/prediction_distribution?${query.toString()}`,
    { method: "GET", signal: options.signal },
  );
}

export function fetchRegimeCurrent(
  baseUrl: string,
  runId: string,
  modelName: ModelName,
  options: DashboardRequestOptions = {},
): Promise<RegimeCurrentPayload> {
  const mode = options.mode ?? "backtest";
  const query = new URLSearchParams({
    run_id: runId,
    model_name: modelName,
  });
  return requestJsonMaybeCached<RegimeCurrentPayload>(
    `dashboard-regime-current:${baseUrl}:${runId}:${modelName}:${mode}`,
    ttlForMode(mode),
    baseUrl,
    `${QUANT_PREFIX}/regime/current?${query.toString()}`,
    { method: "GET", signal: options.signal },
  );
}

export function fetchRegimeHistory(
  baseUrl: string,
  runId: string,
  modelName: ModelName,
  options: DashboardRequestOptions = {},
): Promise<RegimeHistoryPayload> {
  const mode = options.mode ?? "backtest";
  const query = new URLSearchParams({
    run_id: runId,
    model_name: modelName,
  });
  return requestJsonMaybeCached<RegimeHistoryPayload>(
    `dashboard-regime-history:${baseUrl}:${runId}:${modelName}:${mode}`,
    ttlForMode(mode),
    baseUrl,
    `${QUANT_PREFIX}/regime/history?${query.toString()}`,
    { method: "GET", signal: options.signal },
  );
}

export function fetchAlertsCurrent(
  baseUrl: string,
  runId: string,
  modelName: ModelName,
  options: DashboardRequestOptions = {},
): Promise<AlertsPayload> {
  const mode = options.mode ?? "backtest";
  const query = new URLSearchParams({
    run_id: runId,
    model_name: modelName,
  });
  return requestJsonMaybeCached<AlertsPayload>(
    `dashboard-alerts-current:${baseUrl}:${runId}:${modelName}:${mode}`,
    ttlForMode(mode),
    baseUrl,
    `${QUANT_PREFIX}/alerts/current?${query.toString()}`,
    { method: "GET", signal: options.signal },
  );
}

export function fetchAlertsHistory(
  baseUrl: string,
  runId: string,
  modelName: ModelName,
  limit = 200,
  options: DashboardRequestOptions = {},
): Promise<AlertsPayload> {
  const mode = options.mode ?? "backtest";
  const query = new URLSearchParams({
    run_id: runId,
    model_name: modelName,
    limit: String(limit),
  });
  return requestJsonMaybeCached<AlertsPayload>(
    `dashboard-alerts-history:${baseUrl}:${runId}:${modelName}:${limit}:${mode}`,
    ttlForMode(mode),
    baseUrl,
    `${QUANT_PREFIX}/alerts/history?${query.toString()}`,
    { method: "GET", signal: options.signal },
  );
}

export function fetchModelShap(
  baseUrl: string,
  runId: string,
  modelName: ModelName,
  options: DashboardRequestOptions = {},
): Promise<ModelShapPayload> {
  const mode = options.mode ?? "backtest";
  const query = new URLSearchParams({
    run_id: runId,
    model_name: modelName,
  });
  return requestJsonMaybeCached<ModelShapPayload>(
    `dashboard-model-shap:${baseUrl}:${runId}:${modelName}:${mode}`,
    ttlForMode(mode),
    baseUrl,
    `${QUANT_PREFIX}/model/shap?${query.toString()}`,
    { method: "GET", signal: options.signal },
  );
}

export function previewExecutionOrders(
  baseUrl: string,
  payload: ExecutionOrderPreviewRequestPayload,
): Promise<ExecutionPreviewPayload> {
  return requestJson<ExecutionPreviewPayload>(baseUrl, `${QUANT_PREFIX}/execution/orders/preview`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function submitExecutionOrders(
  baseUrl: string,
  payload: ExecutionOrderPreviewRequestPayload,
): Promise<ExecutionSubmitPayload> {
  return requestJson<ExecutionSubmitPayload>(baseUrl, `${QUANT_PREFIX}/execution/orders/submit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function riskCheckPretrade(
  baseUrl: string,
  payload: RiskPretradeRequestPayload,
): Promise<RiskPretradePayload> {
  return requestJson<RiskPretradePayload>(baseUrl, `${QUANT_PREFIX}/risk/check/pretrade`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function fetchExecutionOrdersCurrent(
  baseUrl: string,
  runId: string,
  modelName: ModelName,
): Promise<ExecutionOrdersPayload> {
  const query = new URLSearchParams({ run_id: runId, model_name: modelName });
  return requestJson<ExecutionOrdersPayload>(baseUrl, `${QUANT_PREFIX}/execution/orders/current?${query.toString()}`, {
    method: "GET",
  });
}

export function fetchExecutionFillsHistory(
  baseUrl: string,
  runId: string,
  modelName: ModelName,
  limit = 200,
): Promise<ExecutionFillsPayload> {
  const query = new URLSearchParams({ run_id: runId, model_name: modelName, limit: String(limit) });
  return requestJson<ExecutionFillsPayload>(baseUrl, `${QUANT_PREFIX}/execution/fills/history?${query.toString()}`, {
    method: "GET",
  });
}

export function fetchExecutionPositionsCurrent(
  baseUrl: string,
  runId: string,
  modelName: ModelName,
): Promise<ExecutionPositionsPayload> {
  const query = new URLSearchParams({ run_id: runId, model_name: modelName });
  return requestJson<ExecutionPositionsPayload>(
    baseUrl,
    `${QUANT_PREFIX}/execution/positions/current?${query.toString()}`,
    { method: "GET" },
  );
}

export function fetchExecutionPnl(
  baseUrl: string,
  runId: string,
  modelName: ModelName,
): Promise<ExecutionPnlPayload> {
  const query = new URLSearchParams({ run_id: runId, model_name: modelName });
  return requestJson<ExecutionPnlPayload>(baseUrl, `${QUANT_PREFIX}/execution/pnl?${query.toString()}`, { method: "GET" });
}

export function fetchRiskLimits(
  baseUrl: string,
  runId: string,
  modelName: ModelName,
): Promise<RiskLimitsPayload> {
  const query = new URLSearchParams({ run_id: runId, model_name: modelName });
  return requestJson<RiskLimitsPayload>(baseUrl, `${QUANT_PREFIX}/risk/limits?${query.toString()}`, { method: "GET" });
}

export function fetchRiskEvents(
  baseUrl: string,
  runId: string,
  modelName: ModelName,
  limit = 200,
): Promise<RiskEventsPayload> {
  const query = new URLSearchParams({ run_id: runId, model_name: modelName, limit: String(limit) });
  return requestJson<RiskEventsPayload>(baseUrl, `${QUANT_PREFIX}/risk/events?${query.toString()}`, { method: "GET" });
}

export function fetchOpsStatus(baseUrl: string): Promise<OpsStatusPayload> {
  return requestJson<OpsStatusPayload>(baseUrl, `${QUANT_PREFIX}/ops/status`, { method: "GET" });
}

export function fetchOpsIssues(baseUrl: string, limit = 10): Promise<OpsIssueQueuePayload> {
  return requestJson<OpsIssueQueuePayload>(
    baseUrl,
    `${QUANT_PREFIX}/ops/issues?limit=${limit}`,
    { method: "GET" },
  );
}

export function fetchWorkspaceBrief(baseUrl: string): Promise<WorkspaceBriefPayload> {
  return requestJson<WorkspaceBriefPayload>(baseUrl, `${QUANT_PREFIX}/workspace/brief`, {
    method: "GET",
  });
}

export function fetchDataQualityLatest(
  baseUrl: string,
  runId?: string,
): Promise<DataQualityLatestPayload> {
  const query = new URLSearchParams();
  if (runId) {
    query.set("run_id", runId);
  }
  const suffix = query.size > 0 ? `?${query.toString()}` : "";
  return requestJson<DataQualityLatestPayload>(
    baseUrl,
    `${QUANT_PREFIX}/data-quality/latest${suffix}`,
    { method: "GET" },
  );
}

export function fetchDataQualityHistory(
  baseUrl: string,
  runId?: string,
  limit = 50,
): Promise<DataQualityHistoryPayload> {
  const query = new URLSearchParams({ limit: String(limit) });
  if (runId) {
    query.set("run_id", runId);
  }
  return requestJson<DataQualityHistoryPayload>(
    baseUrl,
    `${QUANT_PREFIX}/data-quality/history?${query.toString()}`,
    { method: "GET" },
  );
}

export function fetchExperimentList(baseUrl: string, limit = 50): Promise<ExperimentListPayload> {
  return requestJson<ExperimentListPayload>(
    baseUrl,
    `${QUANT_PREFIX}/experiments/list?limit=${limit}`,
    { method: "GET" },
  );
}

export function fetchExperimentDetail(baseUrl: string, runId: string): Promise<ExperimentRunItemPayload> {
  return requestJson<ExperimentRunItemPayload>(
    baseUrl,
    `${QUANT_PREFIX}/experiments/${runId}`,
    { method: "GET" },
  );
}

export function fetchRunsCompare(
  baseUrl: string,
  params?: { runIds?: string[]; limit?: number },
): Promise<RunComparePayload> {
  const query = new URLSearchParams();
  if (params?.runIds?.length) {
    query.set("run_ids", params.runIds.join(","));
  }
  if (params?.limit) {
    query.set("limit", String(params.limit));
  }
  const suffix = query.size > 0 ? `?${query.toString()}` : "";
  return requestJson<RunComparePayload>(baseUrl, `${QUANT_PREFIX}/runs/compare${suffix}`, {
    method: "GET",
  });
}

export function fetchModelRegistryChampion(
  baseUrl: string,
  modelName?: string,
): Promise<ModelRegistryEntryPayload> {
  const query = modelName ? `?model_name=${encodeURIComponent(modelName)}` : "";
  return requestJson<ModelRegistryEntryPayload>(
    baseUrl,
    `${QUANT_PREFIX}/model-registry/champion${query}`,
    { method: "GET" },
  );
}

export function fetchModelRegistryChallenger(
  baseUrl: string,
  modelName?: string,
): Promise<ModelRegistryEntryPayload> {
  const query = modelName ? `?model_name=${encodeURIComponent(modelName)}` : "";
  return requestJson<ModelRegistryEntryPayload>(
    baseUrl,
    `${QUANT_PREFIX}/model-registry/challenger${query}`,
    { method: "GET" },
  );
}

export function fetchModelRegistryHistory(
  baseUrl: string,
  modelName?: string,
  limit = 50,
): Promise<ModelRegistryHistoryPayload> {
  const query = new URLSearchParams({ limit: String(limit) });
  if (modelName) {
    query.set("model_name", modelName);
  }
  return requestJson<ModelRegistryHistoryPayload>(
    baseUrl,
    `${QUANT_PREFIX}/model-registry/history?${query.toString()}`,
    { method: "GET" },
  );
}

export function fetchReportsLatest(
  baseUrl: string,
  runId?: string,
  reportType?: string,
): Promise<ReportsLatestPayload> {
  const query = new URLSearchParams();
  if (runId) {
    query.set("run_id", runId);
  }
  if (reportType) {
    query.set("report_type", reportType);
  }
  const suffix = query.size > 0 ? `?${query.toString()}` : "";
  return requestJson<ReportsLatestPayload>(
    baseUrl,
    `${QUANT_PREFIX}/reports/latest${suffix}`,
    { method: "GET" },
  );
}

export function fetchReportsHistory(
  baseUrl: string,
  params?: { runId?: string; reportType?: string; limit?: number },
): Promise<ReportsHistoryPayload> {
  const query = new URLSearchParams({
    limit: String(params?.limit ?? 50),
  });
  if (params?.runId) {
    query.set("run_id", params.runId);
  }
  if (params?.reportType) {
    query.set("report_type", params.reportType);
  }
  return requestJson<ReportsHistoryPayload>(
    baseUrl,
    `${QUANT_PREFIX}/reports/history?${query.toString()}`,
    { method: "GET" },
  );
}

export function fetchNotificationsHistory(
  baseUrl: string,
  limit = 100,
): Promise<NotificationsHistoryPayload> {
  return requestJson<NotificationsHistoryPayload>(
    baseUrl,
    `${QUANT_PREFIX}/notifications/history?limit=${limit}`,
    { method: "GET" },
  );
}

export function fetchSchedulerStatus(baseUrl: string): Promise<SchedulerStatusPayload> {
  return requestJson<SchedulerStatusPayload>(
    baseUrl,
    `${QUANT_PREFIX}/scheduler/status`,
    { method: "GET" },
  );
}

export function fetchExecutionMode(
  baseUrl: string,
  runId: string,
  modelName: ModelName,
): Promise<ExecutionModePayload> {
  const query = new URLSearchParams({
    run_id: runId,
    model_name: modelName,
  });
  return requestJson<ExecutionModePayload>(
    baseUrl,
    `${QUANT_PREFIX}/execution/mode?${query.toString()}`,
    { method: "GET" },
  );
}

export function updateExecutionMode(
  baseUrl: string,
  payload: ExecutionModeUpdateRequestPayload,
): Promise<ExecutionModePayload> {
  return requestJson<ExecutionModePayload>(
    baseUrl,
    `${QUANT_PREFIX}/execution/mode/update`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    },
  );
}

export function fetchTradingStatus(baseUrl: string): Promise<TradingStatusPayload> {
  return requestJson<TradingStatusPayload>(
    baseUrl,
    `${QUANT_PREFIX}/trading/status`,
    { method: "GET" },
  );
}

export function fetchTradingSettings(baseUrl: string): Promise<TradingSettingsPayload> {
  if (isLegacyTradingEndpointCached(baseUrl, "trading-settings")) {
    return Promise.resolve(createDefaultTradingSettingsPayload());
  }
  return requestJson<TradingSettingsPayload>(
    baseUrl,
    `${QUANT_PREFIX}/trading/settings`,
    { method: "GET" },
  ).catch((error) => {
    if (isLegacyTradingSettingsRouteError(error)) {
      markLegacyTradingEndpoint(baseUrl, "trading-settings");
      return createDefaultTradingSettingsPayload();
    }
    throw error;
  });
}

export function updateTradingSettings(
  baseUrl: string,
  payload: TradingSettingsUpdatePayload,
): Promise<TradingSettingsPayload> {
  return requestJson<TradingSettingsPayload>(
    baseUrl,
    `${QUANT_PREFIX}/trading/settings/update`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    },
  );
}

export function runTradingCycle(
  baseUrl: string,
  payload: TradingCycleRunRequestPayload = {},
): Promise<TradingCycleRunPayload> {
  return requestJson<TradingCycleRunPayload>(
    baseUrl,
    `${QUANT_PREFIX}/trading/cycle/run`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    },
  );
}

export function fetchTradingScanLatest(
  baseUrl: string,
  limit = 200,
): Promise<TradingScanPayload> {
  return requestJson<TradingScanPayload>(
    baseUrl,
    `${QUANT_PREFIX}/trading/scan/latest?limit=${limit}`,
    { method: "GET" },
  );
}

export function fetchTradingScanHistory(
  baseUrl: string,
  limit = 250,
): Promise<TradingScanPayload> {
  return requestJson<TradingScanPayload>(
    baseUrl,
    `${QUANT_PREFIX}/trading/scan/history?limit=${limit}`,
    { method: "GET" },
  );
}

export function fetchTradingSymbolDetail(
  baseUrl: string,
  ticker: string,
): Promise<TradingSymbolDetailPayload> {
  return requestJson<TradingSymbolDetailPayload>(
    baseUrl,
    `${QUANT_PREFIX}/trading/symbol/${encodeURIComponent(ticker)}`,
    { method: "GET" },
  );
}

export function fetchSymbolContext(
  baseUrl: string,
  params: {
    symbol: string;
    source?: string;
    studyId?: string;
    runId?: string;
    signalId?: string;
    reportPath?: string;
  },
): Promise<SymbolContextPayload> {
  const query = new URLSearchParams({ symbol: params.symbol });
  if (params.source) query.set("source", params.source);
  if (params.studyId) query.set("study_id", params.studyId);
  if (params.runId) query.set("run_id", params.runId);
  if (params.signalId) query.set("signal_id", params.signalId);
  if (params.reportPath) query.set("report_path", params.reportPath);
  return requestJson<SymbolContextPayload>(
    baseUrl,
    `${QUANT_PREFIX}/symbol/context?${query.toString()}`,
    { method: "GET" },
  );
}

export function fetchTradingOrders(
  baseUrl: string,
  limit = 250,
): Promise<TradingOrdersPayload> {
  return requestJson<TradingOrdersPayload>(
    baseUrl,
    `${QUANT_PREFIX}/trading/orders?limit=${limit}`,
    { method: "GET" },
  );
}

export function approveTradingOrder(
  baseUrl: string,
  orderId: string,
): Promise<TradingOrdersPayload["items"][number]> {
  return requestJson<TradingOrdersPayload["items"][number]>(
    baseUrl,
    `${QUANT_PREFIX}/trading/orders/${encodeURIComponent(orderId)}/approve`,
    { method: "POST" },
  );
}

export function cancelTradingOrder(
  baseUrl: string,
  orderId: string,
): Promise<TradingOrdersPayload["items"][number]> {
  return requestJson<TradingOrdersPayload["items"][number]>(
    baseUrl,
    `${QUANT_PREFIX}/trading/orders/${encodeURIComponent(orderId)}/cancel`,
    { method: "POST" },
  );
}

export function fetchTradingFills(
  baseUrl: string,
  limit = 250,
): Promise<TradingFillsPayload> {
  return requestJson<TradingFillsPayload>(
    baseUrl,
    `${QUANT_PREFIX}/trading/fills?limit=${limit}`,
    { method: "GET" },
  );
}

export function fetchTradingPositions(baseUrl: string): Promise<TradingPositionsPayload> {
  return requestJson<TradingPositionsPayload>(
    baseUrl,
    `${QUANT_PREFIX}/trading/positions`,
    { method: "GET" },
  );
}

export function closeTradingPosition(
  baseUrl: string,
  ticker: string,
): Promise<TradingOrdersPayload["items"][number]> {
  return requestJson<TradingOrdersPayload["items"][number]>(
    baseUrl,
    `${QUANT_PREFIX}/trading/positions/${encodeURIComponent(ticker)}/close`,
    { method: "POST" },
  );
}

export function fetchTradingPerformance(baseUrl: string): Promise<TradingPerformancePayload> {
  return requestJson<TradingPerformancePayload>(
    baseUrl,
    `${QUANT_PREFIX}/trading/performance`,
    { method: "GET" },
  );
}

export function fetchTradingRisk(baseUrl: string): Promise<TradingRiskPayload> {
  return requestJson<TradingRiskPayload>(
    baseUrl,
    `${QUANT_PREFIX}/trading/risk`,
    { method: "GET" },
  );
}

export function fetchTradingEvents(
  baseUrl: string,
  limit = 250,
): Promise<TradingEventsPayload> {
  return requestJson<TradingEventsPayload>(
    baseUrl,
    `${QUANT_PREFIX}/trading/events?limit=${limit}`,
    { method: "GET" },
  );
}

export function fetchTradingAlgorithms(baseUrl: string): Promise<TradingAlgorithmsPayload> {
  return requestJson<TradingAlgorithmsPayload>(
    baseUrl,
    `${QUANT_PREFIX}/trading/algorithms`,
    { method: "GET" },
  );
}

export function toggleTradingAlgorithm(
  baseUrl: string,
  payload: TradingAlgorithmToggleRequestPayload,
): Promise<TradingAlgorithmsPayload> {
  return requestJson<TradingAlgorithmsPayload>(
    baseUrl,
    `${QUANT_PREFIX}/trading/algorithms/toggle`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    },
  );
}

export function validateTradingAlgorithm(
  baseUrl: string,
  payload: TradingAlgorithmValidateRequestPayload,
): Promise<TradingAlgorithmValidationPayload> {
  return requestJson<TradingAlgorithmValidationPayload>(
    baseUrl,
    `${QUANT_PREFIX}/trading/algorithms/validate`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    },
  );
}

export function fetchTradingExecutionMode(
  baseUrl: string,
): Promise<TradingExecutionModePayload> {
  if (isLegacyTradingEndpointCached(baseUrl, "trading-execution-mode")) {
    return fetchTradingStatus(baseUrl).then((status) => ({
      mode: status.mode ?? "paper",
      live_adapter_enabled: false,
      broker_ready: false,
      kill_switch: false,
      updated_at: status.last_order_at ?? status.last_scan_at ?? undefined,
    }));
  }
  return requestJson<TradingExecutionModePayload>(
    baseUrl,
    `${QUANT_PREFIX}/trading/execution/mode`,
    { method: "GET" },
  ).catch(async (error) => {
    if (isLegacyTradingExecutionModeRouteError(error)) {
      markLegacyTradingEndpoint(baseUrl, "trading-execution-mode");
      const status = await fetchTradingStatus(baseUrl);
      return {
        mode: status.mode ?? "paper",
        live_adapter_enabled: false,
        broker_ready: false,
        kill_switch: false,
        updated_at: status.last_order_at ?? status.last_scan_at ?? undefined,
      };
    }
    throw error;
  });
}

export function updateTradingExecutionMode(
  baseUrl: string,
  mode: ExecutionMode,
): Promise<TradingExecutionModePayload> {
  return requestJson<TradingExecutionModePayload>(
    baseUrl,
    `${QUANT_PREFIX}/trading/execution/mode/update`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ mode }),
    },
  );
}
