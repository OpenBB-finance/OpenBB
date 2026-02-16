import { clearCachePrefix, getCachedOrFetch } from "./quantCache";
import type { FeatureActivation, FeatureActivationResult } from "../types/feature-activation";
import type {
  AlertsPayload,
  ArtifactSummaryPayload,
  BacktestRequestPayload,
  BacktestResponsePayload,
  DashboardHealthPayload,
  DashboardMode,
  FeatureImportancePayload,
  ICDecayPayload,
  ModelShapPayload,
  ModelICPayload,
  ModelName,
  ModelPerformancePayload,
  ModelRegimePayload,
  OpsStatusPayload,
  PerformanceRegimePayload,
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
  PortfolioExposurePayload,
  PortfolioCurrentPayload,
  PortfolioRiskPayload,
  PredictionDistributionPayload,
  PredictionsLatestPayload,
  RegimeCurrentPayload,
  RegimeHistoryPayload,
  RollingPerformancePayload,
  RunStatusPayload,
  SignalsRequestPayload,
  SignalsResponsePayload,
  TrainRequestPayload,
  TrainResponsePayload,
  UniverseResponse,
  UniverseListPayload,
  UniverseResolvePayload,
} from "../types/quant";

const QUANT_PREFIX = "/api/v1/quant_ml";
const DASHBOARD_CACHE_TTL_MS = 60_000;
const LIVE_CACHE_TTL_MS = 0;

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
}

async function requestJson<T>(baseUrl: string, path: string, init: RequestInit): Promise<T> {
  const response = await fetch(`${baseUrl}${path}`, init);
  if (!response.ok) {
    let detail = "";
    try {
      const payload = await response.json();
      detail = payload?.detail ? String(payload.detail) : "";
    } catch {
      detail = "";
    }
    throw new Error(detail || `Request failed (${response.status})`);
  }
  return (await response.json()) as T;
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

export function invalidateQuantCaches(baseUrl: string, runId?: string, modelName?: ModelName): void {
  clearCachePrefix("dashboard-");
  clearCachePrefix("portfolio-current:");
  clearCachePrefix("predictions-latest:");
  clearCachePrefix("model-performance:");

  if (runId && modelName) {
    clearCachePrefix(`portfolio-current:${baseUrl}:${runId}:${modelName}`);
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
  const query = new URLSearchParams({ model_name: modelName });
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
