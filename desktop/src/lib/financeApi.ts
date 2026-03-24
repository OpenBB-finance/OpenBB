import { resolveOpenBBBackend } from "./openbbBackend";
import { extractTickerFromSymbol } from "./tradingView";
import type {
  FinanceForecastConsensusRecord,
  FinanceForecastEnvelope,
  FinanceStatementEnvelope,
  FinanceStatementKind,
  FinanceStatementPeriod,
  FinanceStatementRecord,
} from "../types/finance";

const FINANCE_API_CACHE_TTL_MS = 60_000;

const statementCache = new Map<string, { expiresAt: number; payload: FinanceStatementPayload }>();
const forecastCache = new Map<string, { expiresAt: number; payload: FinanceForecastPayload }>();

export interface FinanceStatementPayload {
  rows: FinanceStatementRecord[];
  provider: string | null;
  timestamp: string | null;
}

export interface FinanceForecastPayload {
  consensus: FinanceForecastConsensusRecord | null;
  provider: string | null;
  timestamp: string | null;
}

function toApiPeriod(period: FinanceStatementPeriod): "annual" | "quarter" {
  return period === "quarterly" ? "quarter" : "annual";
}

function getStatementPath(kind: FinanceStatementKind): string {
  if (kind === "income") return "/api/v1/equity/fundamental/income";
  if (kind === "balance") return "/api/v1/equity/fundamental/balance";
  return "/api/v1/equity/fundamental/cash";
}

function buildCacheKey(kind: FinanceStatementKind, symbol: string, period: FinanceStatementPeriod): string {
  return `${kind}:${extractTickerFromSymbol(symbol)}:${period}`;
}

function readCached(key: string): FinanceStatementPayload | null {
  const cached = statementCache.get(key);
  if (!cached) return null;
  if (cached.expiresAt < Date.now()) {
    statementCache.delete(key);
    return null;
  }
  return cached.payload;
}

function writeCached(key: string, payload: FinanceStatementPayload): FinanceStatementPayload {
  statementCache.set(key, {
    expiresAt: Date.now() + FINANCE_API_CACHE_TTL_MS,
    payload,
  });
  return payload;
}

function readForecastCached(key: string): FinanceForecastPayload | null {
  const cached = forecastCache.get(key);
  if (!cached) return null;
  if (cached.expiresAt < Date.now()) {
    forecastCache.delete(key);
    return null;
  }
  return cached.payload;
}

function writeForecastCached(key: string, payload: FinanceForecastPayload): FinanceForecastPayload {
  forecastCache.set(key, {
    expiresAt: Date.now() + FINANCE_API_CACHE_TTL_MS,
    payload,
  });
  return payload;
}

async function requestFinanceEnvelope(
  kind: FinanceStatementKind,
  symbol: string,
  period: FinanceStatementPeriod,
  signal?: AbortSignal,
): Promise<FinanceStatementEnvelope> {
  const backend = await resolveOpenBBBackend();
  if (!backend.connected) {
    throw new Error("OpenBB backend is not connected.");
  }

  const ticker = extractTickerFromSymbol(symbol);
  const query = new URLSearchParams({
    symbol: ticker,
    provider: "yfinance",
    period: toApiPeriod(period),
    limit: "4",
  });

  const response = await fetch(`${backend.baseUrl}${getStatementPath(kind)}?${query.toString()}`, {
    method: "GET",
    signal,
  });

  if (!response.ok) {
    let detail = "";
    try {
      const payload = (await response.json()) as { detail?: unknown };
      detail = typeof payload.detail === "string" ? payload.detail : "";
    } catch {
      detail = "";
    }
    throw new Error(detail || `Failed to load ${kind} statement (${response.status}).`);
  }

  return (await response.json()) as FinanceStatementEnvelope;
}

export function clearFinanceStatementCache(): void {
  statementCache.clear();
  forecastCache.clear();
}

export async function fetchFinanceStatement(
  kind: FinanceStatementKind,
  symbol: string,
  period: FinanceStatementPeriod,
  signal?: AbortSignal,
): Promise<FinanceStatementPayload> {
  const cacheKey = buildCacheKey(kind, symbol, period);
  const cached = readCached(cacheKey);
  if (cached) {
    return cached;
  }

  const envelope = await requestFinanceEnvelope(kind, symbol, period, signal);
  return writeCached(cacheKey, {
    rows: Array.isArray(envelope.results) ? envelope.results : [],
    provider: envelope.provider ?? null,
    timestamp: envelope.extra?.metadata?.timestamp ?? null,
  });
}

export async function fetchFinanceForecast(
  symbol: string,
  signal?: AbortSignal,
): Promise<FinanceForecastPayload> {
  const ticker = extractTickerFromSymbol(symbol);
  const cacheKey = `forecast:${ticker}`;
  const cached = readForecastCached(cacheKey);
  if (cached) {
    return cached;
  }

  const backend = await resolveOpenBBBackend();
  if (!backend.connected) {
    throw new Error("OpenBB backend is not connected.");
  }

  const query = new URLSearchParams({
    symbol: ticker,
    provider: "yfinance",
  });

  const response = await fetch(
    `${backend.baseUrl}/api/v1/equity/estimates/consensus?${query.toString()}`,
    {
      method: "GET",
      signal,
    },
  );

  if (!response.ok) {
    let detail = "";
    try {
      const payload = (await response.json()) as { detail?: unknown };
      detail = typeof payload.detail === "string" ? payload.detail : "";
    } catch {
      detail = "";
    }
    throw new Error(detail || `Failed to load forecast consensus (${response.status}).`);
  }

  const envelope = (await response.json()) as FinanceForecastEnvelope;
  return writeForecastCached(cacheKey, {
    consensus: Array.isArray(envelope.results) ? (envelope.results[0] ?? null) : null,
    provider: envelope.provider ?? null,
    timestamp: envelope.extra?.metadata?.timestamp ?? null,
  });
}
