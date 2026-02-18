import { clearCachePrefix, getCachedOrFetch } from "./quantCache";
import type { FeatureActivation, FeatureActivationResult } from "../types/feature-activation";
import type {
  MacroAlertsResponse,
  MacroCatalogResponse,
  MacroDerivedResponse,
  MacroExpressionRequest,
  MacroExpressionResponse,
  MacroHealthResponse,
  MacroPresetResponse,
  MacroRegimeResponse,
  MacroRegimeStateResponse,
  MacroSeriesResponse,
  MacroSeriesMultiResponse,
  MacroUpdateResponse,
} from "../types/macro";

const MACRO_PREFIX_CANONICAL = "/api/v1/quant_ml/macro";
const MACRO_PREFIX_ALIAS = "/api/v1/macro";
const CACHE_TTL_MS = 60_000;

function buildFeatureActivation(featureName: string, available: boolean, detail?: string): FeatureActivation {
  return {
    featureName,
    available,
    detail: detail ?? null,
    lastCheckedAt: new Date().toISOString(),
  };
}

async function requestMacro<T>(baseUrl: string, path: string, init: RequestInit): Promise<T> {
  const candidates = [`${MACRO_PREFIX_CANONICAL}${path}`, `${MACRO_PREFIX_ALIAS}${path}`];
  let lastError = "Unknown macro API error";

  for (let index = 0; index < candidates.length; index += 1) {
    const candidate = candidates[index];
    const response = await fetch(`${baseUrl}${candidate}`, init);
    if (response.ok) {
      return (await response.json()) as T;
    }

    let detail = "";
    try {
      const payload = await response.json();
      detail = payload?.detail ? String(payload.detail) : payload?.message ? String(payload.message) : "";
    } catch {
      detail = "";
    }
    lastError = detail || `Request failed (${response.status})`;

    const isNotFound = response.status === 404;
    const hasFallback = index < candidates.length - 1;
    if (isNotFound && hasFallback) {
      continue;
    }
    break;
  }

  throw new Error(lastError);
}

function cachedMacro<T>(key: string, fetcher: () => Promise<T>): Promise<T> {
  return getCachedOrFetch<T>(`macro:${key}`, CACHE_TTL_MS, fetcher);
}

export function invalidateMacroCache(): void {
  clearCachePrefix("macro:");
}

export function fetchMacroCatalog(baseUrl: string, domain?: string): Promise<MacroCatalogResponse> {
  const query = new URLSearchParams();
  if (domain) {
    query.set("domain", domain);
  }
  const path = query.toString() ? `/catalog?${query.toString()}` : "/catalog";
  return cachedMacro(`catalog:${baseUrl}:${domain ?? "*"}`, () => requestMacro(baseUrl, path, { method: "GET" }));
}

export function searchMacroCatalog(
  baseUrl: string,
  q: string,
  domain?: string,
  limit = 25,
): Promise<MacroCatalogResponse> {
  return requestMacro(baseUrl, "/catalog/search", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ q, domain, limit }),
  });
}

export function registerMacroSeries(
  baseUrl: string,
  payload: { series_id: string; domain?: string; publish_lag?: number; default_transform?: string },
): Promise<MacroCatalogResponse> {
  return requestMacro(baseUrl, "/catalog/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function fetchMacroSeries(
  baseUrl: string,
  params: {
    key: string;
    start?: string;
    end?: string;
    transform?: string;
    freq?: string;
    fill?: string;
  },
): Promise<MacroSeriesResponse> {
  const query = new URLSearchParams({ key: params.key });
  if (params.start) query.set("start", params.start);
  if (params.end) query.set("end", params.end);
  if (params.transform) query.set("transform", params.transform);
  if (params.freq) query.set("freq", params.freq);
  if (params.fill) query.set("fill", params.fill);
  const path = `/series?${query.toString()}`;
  return cachedMacro(`series:${baseUrl}:${query.toString()}`, () => requestMacro(baseUrl, path, { method: "GET" }));
}

export function fetchMacroSeriesMulti(
  baseUrl: string,
  params: {
    ids: string[];
    start?: string;
    end?: string;
    transform?: string;
    freq?: string;
    fill?: string;
  },
): Promise<MacroSeriesMultiResponse> {
  const query = new URLSearchParams({ ids: params.ids.join(",") });
  if (params.start) query.set("start", params.start);
  if (params.end) query.set("end", params.end);
  if (params.transform) query.set("transform", params.transform);
  if (params.freq) query.set("freq", params.freq);
  if (params.fill) query.set("fill", params.fill);
  const path = `/series?${query.toString()}`;
  return cachedMacro(`series-multi:${baseUrl}:${query.toString()}`, () => requestMacro(baseUrl, path, { method: "GET" }));
}

export function evaluateMacroExpression(baseUrl: string, payload: MacroExpressionRequest): Promise<MacroExpressionResponse> {
  return requestMacro(baseUrl, "/expression", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function fetchMacroRegime(
  baseUrl: string,
  params: { start?: string; end?: string; freq?: string; fill?: string },
): Promise<MacroRegimeResponse> {
  const query = new URLSearchParams();
  if (params.start) query.set("start", params.start);
  if (params.end) query.set("end", params.end);
  if (params.freq) query.set("freq", params.freq);
  if (params.fill) query.set("fill", params.fill);
  const path = query.toString() ? `/regime?${query.toString()}` : "/regime";
  return cachedMacro(`regime:${baseUrl}:${query.toString()}`, () => requestMacro(baseUrl, path, { method: "GET" }));
}

export function fetchMacroRegimeState(baseUrl: string, date?: string): Promise<MacroRegimeStateResponse> {
  const query = new URLSearchParams();
  if (date) query.set("date", date);
  const path = query.toString() ? `/regime?${query.toString()}` : "/regime";
  return cachedMacro(`regime-state:${baseUrl}:${query.toString()}`, () => requestMacro(baseUrl, path, { method: "GET" }));
}

export function fetchMacroAlerts(
  baseUrl: string,
  params: { start?: string; end?: string; limit?: number } = {},
): Promise<MacroAlertsResponse> {
  const query = new URLSearchParams();
  if (params.start) query.set("start", params.start);
  if (params.end) query.set("end", params.end);
  if (params.limit) query.set("limit", String(params.limit));
  const path = query.toString() ? `/alerts?${query.toString()}` : "/alerts";
  return cachedMacro(`alerts:${baseUrl}:${query.toString()}`, () => requestMacro(baseUrl, path, { method: "GET" }));
}

export function saveMacroDerived(
  baseUrl: string,
  payload: { derived_id: string; expression: string; default_transform?: string },
): Promise<MacroDerivedResponse> {
  return requestMacro(baseUrl, "/derived/save", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function fetchMacroDerived(baseUrl: string): Promise<MacroDerivedResponse> {
  return cachedMacro(`derived:${baseUrl}`, () => requestMacro(baseUrl, "/derived", { method: "GET" }));
}

export function triggerMacroUpdate(
  baseUrl: string,
  payload: {
    series_ids?: string[];
    start?: string;
    end?: string;
    all_default?: boolean;
    compute_features?: boolean;
    features_lookback_days?: number;
  },
): Promise<MacroUpdateResponse> {
  invalidateMacroCache();
  return requestMacro(baseUrl, "/update", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function fetchMacroHealth(baseUrl: string): Promise<MacroHealthResponse> {
  return cachedMacro(`health:${baseUrl}`, () => requestMacro(baseUrl, "/health", { method: "GET" }));
}

export async function fetchMacroHealthWithActivation(
  baseUrl: string,
): Promise<FeatureActivationResult<MacroHealthResponse>> {
  try {
    const data = await fetchMacroHealth(baseUrl);
    return {
      activation: buildFeatureActivation("macro", true),
      data,
    };
  } catch (error) {
    return {
      activation: buildFeatureActivation(
        "macro",
        false,
        error instanceof Error ? error.message : "macro extension unavailable",
      ),
    };
  }
}

export async function probeMacroActivation(baseUrl: string): Promise<FeatureActivation> {
  const result = await fetchMacroHealthWithActivation(baseUrl);
  return result.activation;
}

export function fetchCopperGoldPreset(
  baseUrl: string,
  params: {
    start?: string;
    end?: string;
    freq?: string;
    fill?: string;
    scale?: number;
    adjust_units?: boolean;
    yield_key?: string;
    corr_window?: number;
    slope_window?: number;
    divergence_min_weeks?: number;
    include_corr?: boolean;
  } = {},
): Promise<MacroPresetResponse> {
  const query = new URLSearchParams();
  if (params.start) query.set("start", params.start);
  if (params.end) query.set("end", params.end);
  if (params.freq) query.set("freq", params.freq);
  if (params.fill) query.set("fill", params.fill);
  if (params.scale !== undefined) query.set("scale", String(params.scale));
  if (params.adjust_units !== undefined) query.set("adjust_units", String(params.adjust_units));
  if (params.yield_key) query.set("yield_key", params.yield_key);
  if (params.corr_window !== undefined) query.set("corr_window", String(params.corr_window));
  if (params.slope_window !== undefined) query.set("slope_window", String(params.slope_window));
  if (params.divergence_min_weeks !== undefined) query.set("divergence_min_weeks", String(params.divergence_min_weeks));
  if (params.include_corr !== undefined) query.set("include_corr", String(params.include_corr));
  const suffix = query.toString() ? `?${query.toString()}` : "";
  return cachedMacro(`preset-copper-gold:${baseUrl}:${suffix}`, () =>
    requestMacro(baseUrl, `/presets/copper_gold${suffix}`, { method: "GET" }),
  );
}

export function fetchMarketRatio(
  baseUrl: string,
  params: { lhs: string; rhs: string; start?: string; end?: string; freq?: string; fill?: string },
): Promise<MacroSeriesResponse> {
  const query = new URLSearchParams({ lhs: params.lhs, rhs: params.rhs });
  if (params.start) query.set("start", params.start);
  if (params.end) query.set("end", params.end);
  if (params.freq) query.set("freq", params.freq);
  if (params.fill) query.set("fill", params.fill);
  return cachedMacro(
    `market-ratio:${baseUrl}:${query.toString()}`,
    () => requestJsonWithQuantPrefix(baseUrl, `/market/ratio?${query.toString()}`),
  );
}

export function fetchMarketRollingCorr(
  baseUrl: string,
  params: { x: string; y: string; window: number; start?: string; end?: string; freq?: string; fill?: string },
): Promise<MacroSeriesResponse> {
  const query = new URLSearchParams({
    x: params.x,
    y: params.y,
    window: String(params.window),
  });
  if (params.start) query.set("start", params.start);
  if (params.end) query.set("end", params.end);
  if (params.freq) query.set("freq", params.freq);
  if (params.fill) query.set("fill", params.fill);
  return cachedMacro(
    `market-corr:${baseUrl}:${query.toString()}`,
    () => requestJsonWithQuantPrefix(baseUrl, `/market/rolling_corr?${query.toString()}`),
  );
}

async function requestJsonWithQuantPrefix<T>(baseUrl: string, path: string): Promise<T> {
  const response = await fetch(`${baseUrl}/api/v1/quant_ml${path}`, { method: "GET" });
  if (!response.ok) {
    let detail = "";
    try {
      const payload = await response.json();
      detail = payload?.detail ? String(payload.detail) : payload?.message ? String(payload.message) : "";
    } catch {
      detail = "";
    }
    throw new Error(detail || `Request failed (${response.status})`);
  }
  return (await response.json()) as T;
}
