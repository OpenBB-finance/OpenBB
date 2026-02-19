import { invoke } from "@tauri-apps/api/core";
import type { BackendResolution, BackendService } from "../types/quant";

const DEFAULT_OPENBB_API_URL = "http://127.0.0.1:6900";

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

async function checkHealth(baseUrl: string): Promise<boolean> {
  const normalized = normalizeBaseUrl(baseUrl);
  const endpoints = ["/api/v1/system", "/openapi.json", "/docs"];

  for (const endpoint of endpoints) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 5000);
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

export function formatBackendDetail(detail: string, connected: boolean): string {
  if (connected && /web[- ]dev[- ]fallback/i.test(detail)) {
    return "Web development fallback URL connected.";
  }
  if (connected && /Failed to query backend services/i.test(detail)) {
    return "Backend service query unavailable; fallback URL connected.";
  }
  return detail;
}

export async function resolveOpenBBBackend(): Promise<BackendResolution> {
  let candidateUrl = DEFAULT_OPENBB_API_URL;
  let source: BackendResolution["source"] = "fallback";
  let detail = "Using fallback URL.";
  let serviceQueryFailed = false;

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
    candidateUrl = DEFAULT_OPENBB_API_URL;
    source = "fallback";
    detail = "Failed to query backend services. Using fallback URL.";
  }

  const connected = await checkHealth(candidateUrl);
  if (serviceQueryFailed && connected) {
    source = "web-dev-fallback";
    detail = "Web-dev-fallback: backend service query unavailable, default API URL connected.";
  }

  return {
    baseUrl: candidateUrl,
    source,
    connected,
    detail,
  };
}
