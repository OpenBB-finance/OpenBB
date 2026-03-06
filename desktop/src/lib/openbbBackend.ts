import { invoke } from "@tauri-apps/api/core";
import type { BackendResolution, BackendService } from "../types/quant";

const DEFAULT_OPENBB_API_URL = "http://127.0.0.1:6900";
const FALLBACK_OPENBB_API_URLS = [
  DEFAULT_OPENBB_API_URL,
  "http://127.0.0.1:6901",
  "http://127.0.0.1:8000",
];
const HEALTH_CHECK_TIMEOUT_MS = 3000;
const MAX_RETRIES = 2;
const RETRY_DELAY_MS = 500;
const RESOLUTION_CACHE_TTL_MS = 15_000;

let cachedResolution: { result: BackendResolution; expiresAt: number } | null = null;

function normalizeBaseUrl(url: string): string {
  return url.replace(/\/+$/, "");
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
  // In dev mode skip /openapi.json probe because schema build is expensive.
  const includeOpenApiProbe = !import.meta.env.DEV;
  const endpoints = includeOpenApiProbe
    ? ["/api/v1/coverage/providers", "/docs", "/api/v1/system", "/openapi.json"]
    : ["/api/v1/coverage/providers", "/api/v1/system", "/docs"];

  for (const endpoint of endpoints) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), HEALTH_CHECK_TIMEOUT_MS);
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

async function checkHealthWithRetry(baseUrl: string, retries: number = MAX_RETRIES): Promise<boolean> {
  for (let attempt = 0; attempt < retries; attempt++) {
    const ok = await checkHealth(baseUrl);
    if (ok) return true;
    if (attempt < retries - 1) {
      await new Promise((resolve) => setTimeout(resolve, RETRY_DELAY_MS));
    }
  }
  return false;
}

function buildFallbackCandidateUrls(primaryUrl: string, storedUrl?: string | null): string[] {
  const urls = [
    primaryUrl,
    storedUrl ?? null,
    ...FALLBACK_OPENBB_API_URLS,
  ].filter((url): url is string => Boolean(url));

  return Array.from(new Set(urls.map(normalizeBaseUrl)));
}

async function resolveReachableUrl(candidateUrls: string[]): Promise<string | null> {
  for (let index = 0; index < candidateUrls.length; index += 1) {
    const candidate = candidateUrls[index];
    const ok = index === 0
      ? await checkHealthWithRetry(candidate)
      : await checkHealth(candidate);
    if (ok) {
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
  let storedUrl: string | null = null;

  try {
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

    storedUrl = getStoredBackendUrl();
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
    expiresAt: Date.now() + (connected ? RESOLUTION_CACHE_TTL_MS : 5_000),
  };

  return result;
}
