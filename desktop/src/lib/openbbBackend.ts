import { invoke } from "@tauri-apps/api/core";
import type { BackendResolution, BackendService } from "../types/quant";

const DEFAULT_OPENBB_API_URL = "http://127.0.0.1:6900";
export const OPENBB_API_BEARER_TOKEN_STORAGE_KEY = "openbb-api-bearer-token";
export const OPENBB_API_BASIC_USERNAME_STORAGE_KEY = "openbb-api-basic-username";
export const OPENBB_API_BASIC_PASSWORD_STORAGE_KEY = "openbb-api-basic-password";
const FALLBACK_OPENBB_API_URLS = [
  DEFAULT_OPENBB_API_URL,
  "http://127.0.0.1:6901",
];
const HEALTH_CHECK_TIMEOUT_MS = 3000;
const LOCAL_HEALTH_CHECK_TIMEOUT_MS = 900;
const QUANT_COMPATIBILITY_TIMEOUT_MS = 3000;
const DEV_PROBE_PATH = "/__openbb_probe";
const DEV_PROXY_PATH = "/__openbb_proxy";
const MAX_RETRIES = 2;
const RETRY_DELAY_MS = 500;
const LOCAL_RETRY_DELAY_MS = 300;
const CONNECTED_RESOLUTION_CACHE_TTL_MS = import.meta.env.DEV ? 120_000 : 60_000;
const DISCONNECTED_RESOLUTION_CACHE_TTL_MS = 1_500;

let cachedResolution: { result: BackendResolution; expiresAt: number } | null = null;
let pendingResolutionPromise: Promise<BackendResolution> | null = null;

function getStorageItem(key: string): string | null {
  if (typeof window === "undefined") {
    return null;
  }

  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}

function formatBearerAuthorization(token: string | null | undefined): string | null {
  const normalized = String(token ?? "").trim();
  if (!normalized) {
    return null;
  }
  return /^bearer\s+/i.test(normalized) ? normalized : `Bearer ${normalized}`;
}

function encodeBase64Utf8(value: string): string {
  if (typeof globalThis.btoa === "function") {
    const bytes = new TextEncoder().encode(value);
    let binary = "";
    for (const byte of bytes) {
      binary += String.fromCharCode(byte);
    }
    return globalThis.btoa(binary);
  }

  if (typeof Buffer !== "undefined") {
    return Buffer.from(value, "utf-8").toString("base64");
  }

  throw new Error("Base64 encoding is unavailable in this environment.");
}

function formatBasicAuthorization(
  username: string | null | undefined,
  password: string | null | undefined,
): string | null {
  const normalizedUsername = String(username ?? "").trim();
  const normalizedPassword = String(password ?? "").trim();
  if (!normalizedUsername || !normalizedPassword) {
    return null;
  }
  return `Basic ${encodeBase64Utf8(`${normalizedUsername}:${normalizedPassword}`)}`;
}

function getStoredBearerToken(): string | null {
  return getStorageItem(OPENBB_API_BEARER_TOKEN_STORAGE_KEY);
}

function getStoredBasicUsername(): string | null {
  return getStorageItem(OPENBB_API_BASIC_USERNAME_STORAGE_KEY);
}

function getStoredBasicPassword(): string | null {
  return getStorageItem(OPENBB_API_BASIC_PASSWORD_STORAGE_KEY);
}

export function getOpenBBBearerAuthorization(): string | null {
  const stored = formatBearerAuthorization(getStoredBearerToken());
  if (stored) {
    return stored;
  }

  return formatBearerAuthorization(import.meta.env.VITE_OPENBB_API_BEARER_TOKEN);
}

export function getOpenBBBasicAuthorization(): string | null {
  const stored = formatBasicAuthorization(
    getStoredBasicUsername(),
    getStoredBasicPassword(),
  );
  if (stored) {
    return stored;
  }

  return formatBasicAuthorization(
    import.meta.env.VITE_OPENBB_API_USERNAME,
    import.meta.env.VITE_OPENBB_API_PASSWORD,
  );
}

export function getOpenBBAuthorization(): string | null {
  const basic = getOpenBBBasicAuthorization();
  if (basic) {
    return basic;
  }

  return getOpenBBBearerAuthorization();
}

export function setOpenBBBasicCredentials(
  username: string | null,
  password: string | null,
): void {
  if (typeof window === "undefined") {
    return;
  }

  try {
    const normalizedUsername = String(username ?? "").trim();
    const normalizedPassword = String(password ?? "").trim();
    if (!normalizedUsername || !normalizedPassword) {
      localStorage.removeItem(OPENBB_API_BASIC_USERNAME_STORAGE_KEY);
      localStorage.removeItem(OPENBB_API_BASIC_PASSWORD_STORAGE_KEY);
    } else {
      localStorage.setItem(OPENBB_API_BASIC_USERNAME_STORAGE_KEY, normalizedUsername);
      localStorage.setItem(OPENBB_API_BASIC_PASSWORD_STORAGE_KEY, normalizedPassword);
    }
  } catch {
    // Ignore storage failures.
  }

  invalidateBackendCache();
}

export function setOpenBBBearerToken(token: string | null): void {
  if (typeof window === "undefined") {
    return;
  }

  try {
    const normalized = String(token ?? "").trim();
    if (!normalized) {
      localStorage.removeItem(OPENBB_API_BEARER_TOKEN_STORAGE_KEY);
    } else {
      localStorage.setItem(OPENBB_API_BEARER_TOKEN_STORAGE_KEY, normalized);
    }
  } catch {
    // Ignore storage failures.
  }

  invalidateBackendCache();
}

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

export function buildOpenBBRequestUrl(baseUrl: string, path: string): string {
  const normalizedBaseUrl = normalizeBaseUrl(baseUrl);
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const target = `${normalizedBaseUrl}${normalizedPath}`;

  if (!shouldUseDevProbeProxy(normalizedBaseUrl)) {
    return target;
  }

  return `${DEV_PROXY_PATH}?target=${encodeURIComponent(target)}`;
}

export function buildOpenBBRequestInit(init: RequestInit = {}): RequestInit {
  const headers = new Headers(init.headers ?? {});
  const authorization = getOpenBBAuthorization();
  if (authorization && !headers.has("Authorization")) {
    headers.set("Authorization", authorization);
  }
  return {
    ...init,
    headers,
  };
}

async function probeViaDevProxy(baseUrl: string, path: string, timeoutMs: number): Promise<boolean> {
  const normalized = normalizeBaseUrl(baseUrl);
  const target = `${normalized}${path}`;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(
      `${DEV_PROBE_PATH}?target=${encodeURIComponent(target)}&timeoutMs=${timeoutMs}`,
      buildOpenBBRequestInit({
        method: "GET",
        signal: controller.signal,
      }),
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
      retries: import.meta.env.DEV ? 3 : 2,
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
      const response = await fetch(`${normalized}${endpoint}`, buildOpenBBRequestInit({
        method: "GET",
        signal: controller.signal,
      }));
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
    const response = await fetch(`${normalized}${path}`, buildOpenBBRequestInit({
      method: "GET",
      signal: controller.signal,
    }));
    return response.ok;
  } catch {
    return false;
  } finally {
    clearTimeout(timeoutId);
  }
}

async function getLoopbackCompatibilityScore(baseUrl: string): Promise<number> {
  const checks = await Promise.all([
    checkEndpointOk(baseUrl, "/api/v1/quant_ml/universe/list", QUANT_COMPATIBILITY_TIMEOUT_MS),
    checkEndpointOk(baseUrl, "/api/v1/quant_ml/trading/orders?limit=1", QUANT_COMPATIBILITY_TIMEOUT_MS),
    checkEndpointOk(baseUrl, "/api/v1/quant_ml/workspace/brief", QUANT_COMPATIBILITY_TIMEOUT_MS),
    checkEndpointOk(baseUrl, "/api/v1/quant_ml/macro/studies", QUANT_COMPATIBILITY_TIMEOUT_MS),
    checkEndpointOk(baseUrl, "/api/v1/quant_ml/ops/issues", QUANT_COMPATIBILITY_TIMEOUT_MS),
    checkEndpointOk(baseUrl, "/api/v1/quant_ml/runs/compare?limit=2", QUANT_COMPATIBILITY_TIMEOUT_MS),
    checkEndpointOk(baseUrl, "/api/v1/quant_ml/symbol/context?symbol=SPY", QUANT_COMPATIBILITY_TIMEOUT_MS),
    checkEndpointOk(
      baseUrl,
      "/api/v1/equity/fundamental/income?symbol=SPY&provider=yfinance&period=annual&limit=1",
      QUANT_COMPATIBILITY_TIMEOUT_MS,
    ),
  ]);

  return checks.reduce((score, ok) => score + Number(ok), 0);
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
        const compatibilityScore = await getLoopbackCompatibilityScore(candidate);
        return {
          candidate,
          index,
          ok,
          compatibilityScore,
        };
      }),
    );

    const compatible = reachable
      .filter((entry) => entry.ok || entry.compatibilityScore > 0)
      .sort((left, right) => {
        if (right.compatibilityScore !== left.compatibilityScore) {
          return right.compatibilityScore - left.compatibilityScore;
        }
        if (Number(right.ok) !== Number(left.ok)) {
          return Number(right.ok) - Number(left.ok);
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
  pendingResolutionPromise = null;
}

export async function resolveOpenBBBackend(): Promise<BackendResolution> {
  if (cachedResolution && cachedResolution.expiresAt > Date.now()) {
    return cachedResolution.result;
  }

  if (pendingResolutionPromise) {
    return pendingResolutionPromise;
  }

  pendingResolutionPromise = (async () => {
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
  })();

  try {
    return await pendingResolutionPromise;
  } finally {
    pendingResolutionPromise = null;
  }
}
