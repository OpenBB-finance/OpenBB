import { invoke } from "@tauri-apps/api/core";
import type { BackendResolution, BackendService } from "../types/quant";

const DEFAULT_OPENBB_API_URL = "http://127.0.0.1:6900";
const FALLBACK_OPENBB_API_URLS = [
  DEFAULT_OPENBB_API_URL,
  "http://127.0.0.1:6901",
];
const HEALTH_CHECK_TIMEOUT_MS = 3000;
const LOCAL_HEALTH_CHECK_TIMEOUT_MS = 900;
const QUANT_COMPATIBILITY_TIMEOUT_MS = 3000;
const DEV_PROBE_PATH = "/__openbb_probe";
const MAX_RETRIES = 2;
const RETRY_DELAY_MS = 500;
const LOCAL_RETRY_DELAY_MS = 150;
const CONNECTED_RESOLUTION_CACHE_TTL_MS = import.meta.env.DEV ? 120_000 : 60_000;
const DISCONNECTED_RESOLUTION_CACHE_TTL_MS = 5_000;

let cachedResolution: { result: BackendResolution; expiresAt: number } | null = null;

function normalizeBaseUrl(url: string): string {
  return url.replace(/\/+$/, "");
}

function parseUrl(url: string): URL | null {
  try {
    return new URL(normalizeBaseUrl(url));
  } catch {
    return null;
  }
}

function isLoopbackHost(host: string): boolean {
  return host === "127.0.0.1" || host === "::1" || host === "localhost" || host.endsWith(".localhost");
}

function isLoopbackUrl(url: string): boolean {
  const parsed = parseUrl(url);
  return parsed ? isLoopbackHost(parsed.hostname) : false;
}

function canQueryTauriBackendServices(): boolean {
  if (typeof window === "undefined") {
    return true;
  }
  return typeof (window as Window & { __TAURI_INTERNALS__?: unknown }).__TAURI_INTERNALS__ !== "undefined";
}

function shouldUseDevProbeProxy(baseUrl: string): boolean {
  if (!import.meta.env.DEV || typeof window === "undefined") {
    return false;
  }

  if (canQueryTauriBackendServices() || !isLoopbackUrl(baseUrl)) {
    return false;
  }

  return (
    window.location.protocol === "http:"
    && (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1")
    && window.location.port === "1470"
  );
}

async function probeViaDevProxy(baseUrl: string, path: string, timeoutMs: number): Promise<boolean> {
  const normalized = normalizeBaseUrl(baseUrl);
  const target = `${normalized}${path}`;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(
      `${DEV_PROBE_PATH}?target=${encodeURIComponent(target)}&timeoutMs=${timeoutMs}`,
      {
        method: "GET",
        signal: controller.signal,
      },
    );

    if (!response.ok) {
      return false;
    }

    const payload = await response.json() as { ok?: boolean };
    return payload.ok === true;
  } catch {
    return false;
  } finally {
    clearTimeout(timeoutId);
  }
}

function getHealthCheckTimeoutMs(baseUrl: string): number {
  return isLoopbackUrl(baseUrl) ? LOCAL_HEALTH_CHECK_TIMEOUT_MS : HEALTH_CHECK_TIMEOUT_MS;
}

function getHealthEndpoints(baseUrl: string): string[] {
  if (isLoopbackUrl(baseUrl)) {
    return ["/api/v1/coverage/providers"];
  }

  return import.meta.env.DEV
    ? ["/api/v1/coverage/providers", "/docs"]
    : ["/api/v1/coverage/providers", "/docs", "/openapi.json"];
}

function getRetrySettings(baseUrl: string): { retries: number; delayMs: number } {
  if (isLoopbackUrl(baseUrl)) {
    return {
      retries: import.meta.env.DEV ? 1 : 2,
      delayMs: LOCAL_RETRY_DELAY_MS,
    };
  }

  return {
    retries: MAX_RETRIES,
    delayMs: RETRY_DELAY_MS,
  };
}

function parseOpenbbUrlFromCommand(command: string): string | null {
  const hostMatch = command.match(/--host\s+([^\s]+)/);
  const portMatch = command.match(/--port\s+([0-9]+)/);
  if (hostMatch && portMatch) {
    return `http://${hostMatch[1]}:${portMatch[1]}`;
  }

  const inlineUrl = command.match(/https?:\/\/[^\s]+/);
  if (inlineUrl) {
    return normalizeBaseUrl(inlineUrl[0]);
  }

  return null;
}

function getStoredBackendUrl(): string | null {
  try {
    const stored = localStorage.getItem("openbb-backend-url");
    if (stored) {
      const parsed = JSON.parse(stored) as { url: string; storedAt: number };
      if (Date.now() - parsed.storedAt < 3600_000) {
        return parsed.url;
      }
      localStorage.removeItem("openbb-backend-url");
    }
  } catch { /* ignore parse errors */ }
  return null;
}

function storeBackendUrl(url: string): void {
  try {
    localStorage.setItem(
      "openbb-backend-url",
      JSON.stringify({ url, storedAt: Date.now() }),
    );
  } catch { /* ignore storage errors */ }
}

async function checkHealth(baseUrl: string): Promise<boolean> {
  const normalized = normalizeBaseUrl(baseUrl);
  const endpoints = getHealthEndpoints(normalized);
  const timeoutMs = getHealthCheckTimeoutMs(normalized);

  for (const endpoint of endpoints) {
    if (shouldUseDevProbeProxy(normalized)) {
      if (await probeViaDevProxy(normalized, endpoint, timeoutMs)) {
        return true;
      }
      continue;
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
    try {
      const response = await fetch(`${normalized}${endpoint}`, {
        method: "GET",
        signal: controller.signal,
      });
      if (response.ok) {
        return true;
      }
    } catch {
      // Try next health endpoint.
    } finally {
      clearTimeout(timeoutId);
    }
  }

  return false;
}

async function checkEndpointOk(baseUrl: string, path: string, timeoutMs: number): Promise<boolean> {
  const normalized = normalizeBaseUrl(baseUrl);

  if (shouldUseDevProbeProxy(normalized)) {
    return probeViaDevProxy(normalized, path, timeoutMs);
  }

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(`${normalized}${path}`, {
      method: "GET",
      signal: controller.signal,
    });
    return response.ok;
  } catch {
    return false;
  } finally {
    clearTimeout(timeoutId);
  }
}

async function getLoopbackCompatibilityScore(baseUrl: string): Promise<number> {
  const [hasUniverseList, hasTradingOrders] = await Promise.all([
    checkEndpointOk(baseUrl, "/api/v1/quant_ml/universe/list", QUANT_COMPATIBILITY_TIMEOUT_MS),
    checkEndpointOk(baseUrl, "/api/v1/quant_ml/trading/orders?limit=1", QUANT_COMPATIBILITY_TIMEOUT_MS),
  ]);

  return Number(hasUniverseList) + Number(hasTradingOrders);
}

async function checkHealthWithRetry(baseUrl: string, retries: number = MAX_RETRIES): Promise<boolean> {
  const { delayMs } = getRetrySettings(baseUrl);
  for (let attempt = 0; attempt < retries; attempt++) {
    const ok = await checkHealth(baseUrl);
    if (ok) return true;
    if (attempt < retries - 1) {
      await new Promise((resolve) => setTimeout(resolve, delayMs));
    }
  }
  return false;
}

function buildFallbackCandidateUrls(primaryUrl: string, storedUrl?: string | null): string[] {
  const urls = [
    storedUrl ?? null,
    primaryUrl,
    ...FALLBACK_OPENBB_API_URLS,
  ].filter((url): url is string => Boolean(url));

  return Array.from(new Set(urls.map(normalizeBaseUrl)));
}

async function resolveReachableUrl(candidateUrls: string[]): Promise<string | null> {
  if (candidateUrls.length === 0) {
    return null;
  }

  if (candidateUrls.every(isLoopbackUrl)) {
    const reachable = await Promise.all(
      candidateUrls.map(async (candidate, index) => {
        const { retries } = getRetrySettings(candidate);
        const ok = await checkHealthWithRetry(candidate, retries);
        return {
          candidate,
          index,
          ok,
          compatibilityScore: ok ? await getLoopbackCompatibilityScore(candidate) : -1,
        };
      }),
    );

    const compatible = reachable
      .filter((entry) => entry.ok)
      .sort((left, right) => {
        if (right.compatibilityScore !== left.compatibilityScore) {
          return right.compatibilityScore - left.compatibilityScore;
        }
        return left.index - right.index;
      });

    return compatible[0]?.candidate ?? null;
  }

  const [primaryUrl, ...fallbackUrls] = candidateUrls;
  const { retries } = getRetrySettings(primaryUrl);
  if (await checkHealthWithRetry(primaryUrl, retries)) {
    return primaryUrl;
  }

  for (const candidate of fallbackUrls) {
    if (await checkHealth(candidate)) {
      return candidate;
    }
  }

  return null;
}

export function formatBackendDetail(detail: string, connected: boolean): string {
  if (connected && /web[- ]dev[- ]fallback/i.test(detail)) {
    return "Web development fallback URL connected.";
  }
  if (connected && /Failed to query backend services/i.test(detail)) {
    return "Backend service query unavailable; fallback URL connected.";
  }
  return detail;
}

export function invalidateBackendCache(): void {
  cachedResolution = null;
}

export async function resolveOpenBBBackend(): Promise<BackendResolution> {
  if (cachedResolution && cachedResolution.expiresAt > Date.now()) {
    return cachedResolution.result;
  }

  let candidateUrl = DEFAULT_OPENBB_API_URL;
  let source: BackendResolution["source"] = "fallback";
  let detail = "Using fallback URL.";
  let serviceQueryFailed = false;
  const storedUrl = getStoredBackendUrl();

  if (storedUrl) {
    const storedHealthy = await checkHealth(storedUrl);
    if (storedHealthy && !isLoopbackUrl(storedUrl)) {
      const result: BackendResolution = {
        baseUrl: storedUrl,
        source: "stored-url",
        connected: true,
        detail: "Using previously stored backend URL.",
      };

      cachedResolution = {
        result,
        expiresAt: Date.now() + CONNECTED_RESOLUTION_CACHE_TTL_MS,
      };

      return result;
    }
  }

  try {
    if (!canQueryTauriBackendServices()) {
      throw new Error("tauri backend services unavailable");
    }

    const backends = await invoke<BackendService[]>("list_backend_services");
    const backendRows = Array.isArray(backends) ? backends : [];

    const runningOpenbb = backendRows.find((backend) => {
      const url = typeof backend?.url === "string" ? backend.url.trim() : "";
      return backend?.name === "OpenBB API" && backend?.status === "running" && url.length > 0;
    });

    if (runningOpenbb?.url) {
      candidateUrl = normalizeBaseUrl(runningOpenbb.url);
      source = "running-service-url";
      detail = "Resolved from running OpenBB API service URL.";
    } else {
      const openbbBackend = backendRows.find((backend) => backend?.name === "OpenBB API");
      if (openbbBackend?.command) {
        const parsed = parseOpenbbUrlFromCommand(openbbBackend.command);
        if (parsed) {
          candidateUrl = normalizeBaseUrl(parsed);
          source = "command-parse";
          detail = "Resolved host/port from OpenBB API command.";
        }
      }
    }
  } catch {
    serviceQueryFailed = true;

    if (storedUrl) {
      candidateUrl = storedUrl;
      source = "stored-url";
      detail = "Using previously stored backend URL.";
    } else {
      candidateUrl = DEFAULT_OPENBB_API_URL;
      source = "fallback";
      detail = "Failed to query backend services. Using fallback URL.";
    }
  }

  const reachableUrl = await resolveReachableUrl(
    buildFallbackCandidateUrls(candidateUrl, storedUrl),
  );
  const connected = reachableUrl !== null;

  if (reachableUrl) {
    if (reachableUrl !== candidateUrl) {
      candidateUrl = reachableUrl;
      if (serviceQueryFailed) {
        source = "web-dev-fallback";
        detail = `Web-dev-fallback: backend service query unavailable, connected to local API at ${candidateUrl}.`;
      } else {
        source = "fallback-recovery";
        detail = "Primary URL unreachable; connected via fallback.";
      }
    } else {
      candidateUrl = reachableUrl;
    }
  }

  if (serviceQueryFailed && connected && source !== "stored-url") {
    source = "web-dev-fallback";
    detail = `Web-dev-fallback: backend service query unavailable, connected to local API at ${candidateUrl}.`;
  }

  if (connected) {
    storeBackendUrl(candidateUrl);
  }

  const result: BackendResolution = {
    baseUrl: candidateUrl,
    source,
    connected,
    detail,
  };

  cachedResolution = {
    result,
    expiresAt: Date.now() + (connected ? CONNECTED_RESOLUTION_CACHE_TTL_MS : DISCONNECTED_RESOLUTION_CACHE_TTL_MS),
  };

  return result;
}
