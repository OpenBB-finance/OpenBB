/// <reference types="vitest/globals" />
import { beforeEach, describe, expect, test, vi } from "vitest";
import {
  OPENBB_API_BASIC_PASSWORD_STORAGE_KEY,
  OPENBB_API_BASIC_USERNAME_STORAGE_KEY,
  buildOpenBBRequestInit,
  invalidateBackendCache,
  OPENBB_API_BEARER_TOKEN_STORAGE_KEY,
  setOpenBBBasicCredentials,
  resolveOpenBBBackend,
  setOpenBBBearerToken,
} from "../../lib/openbbBackend";
import { invoke } from "@tauri-apps/api/core";

vi.mock("@tauri-apps/api/core", () => ({
  invoke: vi.fn(),
}));

function mockJsonResponse(payload: unknown, ok = true, status = 200): Response {
  return {
    ok,
    status,
    json: async () => payload,
  } as Response;
}

describe("openbbBackend", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    invalidateBackendCache();
    localStorage.clear();
  });

  test("adds bearer authorization from local storage to request init", () => {
    setOpenBBBearerToken("secret-token");

    const init = buildOpenBBRequestInit({
      method: "GET",
      headers: { Accept: "application/json" },
    });
    const headers = new Headers(init.headers);

    expect(headers.get("Authorization")).toBe("Bearer secret-token");
    expect(headers.get("Accept")).toBe("application/json");
    expect(localStorage.getItem(OPENBB_API_BEARER_TOKEN_STORAGE_KEY)).toBe("secret-token");
  });

  test("prefers basic authorization when username and password are stored", () => {
    setOpenBBBasicCredentials("openbb", "secret-password");
    setOpenBBBearerToken("secret-token");

    const init = buildOpenBBRequestInit({
      method: "GET",
      headers: { Accept: "application/json" },
    });
    const headers = new Headers(init.headers);

    expect(headers.get("Authorization")).toBe("Basic b3BlbmJiOnNlY3JldC1wYXNzd29yZA==");
    expect(localStorage.getItem(OPENBB_API_BASIC_USERNAME_STORAGE_KEY)).toBe("openbb");
    expect(localStorage.getItem(OPENBB_API_BASIC_PASSWORD_STORAGE_KEY)).toBe("secret-password");
  });

  test("falls back to an alternate local API port in browser mode", async () => {
    vi.mocked(invoke).mockRejectedValue(new Error("tauri invoke unavailable"));

    global.fetch = vi.fn(async (input: string | URL) => {
      const url = String(input);
      if (url.startsWith("http://127.0.0.1:6900")) {
        throw new TypeError("fetch failed");
      }
      if (url === "http://127.0.0.1:6901/api/v1/coverage/providers") {
        return mockJsonResponse({ providers: [] });
      }
      return mockJsonResponse({ detail: "unavailable" }, false, 503);
    }) as unknown as typeof fetch;

    const result = await resolveOpenBBBackend();

    expect(result.connected).toBe(true);
    expect(result.baseUrl).toBe("http://127.0.0.1:6901");
    expect(result.source).toBe("web-dev-fallback");
    expect(invoke).not.toHaveBeenCalled();
    expect(localStorage.getItem("openbb-backend-url")).toContain("6901");
  });

  test("prefers a stored non-loopback backend URL before probing default ports", async () => {
    vi.mocked(invoke).mockRejectedValue(new Error("tauri invoke unavailable"));
    localStorage.setItem(
      "openbb-backend-url",
      JSON.stringify({ url: "https://example.com/openbb", storedAt: Date.now() }),
    );

    global.fetch = vi.fn(async (input: string | URL) => {
      const url = String(input);
      if (url === "https://example.com/openbb/api/v1/coverage/providers") {
        return mockJsonResponse({ providers: [] });
      }
      return mockJsonResponse({ detail: "unexpected" }, false, 503);
    }) as unknown as typeof fetch;

    const result = await resolveOpenBBBackend();
    const requestedUrls = vi.mocked(global.fetch).mock.calls.map((call) => String(call[0]));

    expect(result.connected).toBe(true);
    expect(result.baseUrl).toBe("https://example.com/openbb");
    expect(result.source).toBe("stored-url");
    expect(invoke).not.toHaveBeenCalled();
    expect(requestedUrls.some((url) => url.startsWith("http://127.0.0.1:6900"))).toBe(false);
  });

  test("treats the default local OpenBB API as connected when coverage providers responds", async () => {
    vi.mocked(invoke).mockRejectedValue(new Error("tauri invoke unavailable"));

    global.fetch = vi.fn(async (input: string | URL) => {
      const url = String(input);
      if (url === "http://127.0.0.1:6900/api/v1/coverage/providers") {
        return mockJsonResponse({ providers: ["intrinio"] });
      }
      return mockJsonResponse({ detail: "unexpected" }, false, 404);
    }) as unknown as typeof fetch;

    const result = await resolveOpenBBBackend();

    expect(result.connected).toBe(true);
    expect(result.baseUrl).toBe("http://127.0.0.1:6900");
    expect(result.source).toBe("web-dev-fallback");
  });

  test("prefers the compatible local quant backend when the default port is stale", async () => {
    vi.mocked(invoke).mockRejectedValue(new Error("tauri invoke unavailable"));

    global.fetch = vi.fn(async (input: string | URL) => {
      const url = String(input);

      if (url === "http://127.0.0.1:6900/api/v1/coverage/providers") {
        return mockJsonResponse({ providers: ["fred"] });
      }
      if (url === "http://127.0.0.1:6900/api/v1/quant_ml/universe/list") {
        return mockJsonResponse({ universes: [{ id: "legacy" }] });
      }
      if (url === "http://127.0.0.1:6900/api/v1/quant_ml/trading/orders?limit=1") {
        return mockJsonResponse({ items: [] });
      }
      if (url === "http://127.0.0.1:6900/api/v1/quant_ml/workspace/brief") {
        return mockJsonResponse({ detail: "workspace unavailable" }, false, 404);
      }
      if (url === "http://127.0.0.1:6900/api/v1/quant_ml/macro/studies") {
        return mockJsonResponse({ detail: "macro unavailable" }, false, 404);
      }
      if (url === "http://127.0.0.1:6900/api/v1/quant_ml/ops/issues") {
        return mockJsonResponse({ detail: "ops unavailable" }, false, 404);
      }
      if (url === "http://127.0.0.1:6900/api/v1/quant_ml/runs/compare?limit=2") {
        return mockJsonResponse({ detail: "compare unavailable" }, false, 404);
      }
      if (url === "http://127.0.0.1:6900/api/v1/quant_ml/symbol/context?symbol=SPY") {
        return mockJsonResponse({ detail: "symbol unavailable" }, false, 404);
      }
      if (url === "http://127.0.0.1:6901/api/v1/coverage/providers") {
        return mockJsonResponse({ providers: ["fred"] });
      }
      if (url === "http://127.0.0.1:6901/api/v1/quant_ml/universe/list") {
        return mockJsonResponse({ universes: [{ id: "default" }] });
      }
      if (url === "http://127.0.0.1:6901/api/v1/quant_ml/trading/orders?limit=1") {
        return mockJsonResponse({ items: [] });
      }
      if (url === "http://127.0.0.1:6901/api/v1/quant_ml/workspace/brief") {
        return mockJsonResponse({ actions: [] });
      }
      if (url === "http://127.0.0.1:6901/api/v1/quant_ml/macro/studies") {
        return mockJsonResponse({ items: [] });
      }
      if (url === "http://127.0.0.1:6901/api/v1/quant_ml/ops/issues") {
        return mockJsonResponse({ items: [] });
      }
      if (url === "http://127.0.0.1:6901/api/v1/quant_ml/runs/compare?limit=2") {
        return mockJsonResponse({ items: [] });
      }
      if (url === "http://127.0.0.1:6901/api/v1/quant_ml/symbol/context?symbol=SPY") {
        return mockJsonResponse({ symbol: "SPY" });
      }

      return mockJsonResponse({ detail: "unexpected" }, false, 404);
    }) as unknown as typeof fetch;

    const result = await resolveOpenBBBackend();

    expect(result.connected).toBe(true);
    expect(result.baseUrl).toBe("http://127.0.0.1:6901");
    expect(result.source).toBe("web-dev-fallback");
  });

  test("prefers the loopback backend whose finance endpoints still work", async () => {
    vi.mocked(invoke).mockRejectedValue(new Error("tauri invoke unavailable"));

    global.fetch = vi.fn(async (input: string | URL) => {
      const url = String(input);

      if (url === "http://127.0.0.1:6900/api/v1/coverage/providers") {
        return mockJsonResponse({ providers: ["fred"] });
      }
      if (url === "http://127.0.0.1:6901/api/v1/coverage/providers") {
        return mockJsonResponse({ providers: ["fred"] });
      }

      const sharedQuantResponses = new Map<string, unknown>([
        ["/api/v1/quant_ml/universe/list", { universes: [{ id: "default" }] }],
        ["/api/v1/quant_ml/trading/orders?limit=1", { items: [] }],
        ["/api/v1/quant_ml/workspace/brief", { actions: [] }],
        ["/api/v1/quant_ml/macro/studies", { items: [] }],
        ["/api/v1/quant_ml/ops/issues", { items: [] }],
        ["/api/v1/quant_ml/runs/compare?limit=2", { items: [] }],
        ["/api/v1/quant_ml/symbol/context?symbol=SPY", { symbol: "SPY" }],
      ]);

      for (const [suffix, payload] of sharedQuantResponses.entries()) {
        if (url === `http://127.0.0.1:6900${suffix}` || url === `http://127.0.0.1:6901${suffix}`) {
          return mockJsonResponse(payload);
        }
      }

      if (
        url
        === "http://127.0.0.1:6900/api/v1/equity/fundamental/income?symbol=SPY&provider=yfinance&period=annual&limit=1"
      ) {
        return mockJsonResponse({ detail: "finance route failed" }, false, 500);
      }
      if (
        url
        === "http://127.0.0.1:6901/api/v1/equity/fundamental/income?symbol=SPY&provider=yfinance&period=annual&limit=1"
      ) {
        return mockJsonResponse({ results: [] });
      }

      return mockJsonResponse({ detail: "unexpected" }, false, 404);
    }) as unknown as typeof fetch;

    const result = await resolveOpenBBBackend();

    expect(result.connected).toBe(true);
    expect(result.baseUrl).toBe("http://127.0.0.1:6901");
    expect(result.source).toBe("web-dev-fallback");
  });

  test("deduplicates concurrent backend resolution and shares the same result", async () => {
    vi.mocked(invoke).mockRejectedValue(new Error("tauri invoke unavailable"));

    let healthChecks = 0;

    global.fetch = vi.fn(async (input: string | URL) => {
      const url = String(input);

      if (url === "http://127.0.0.1:6900/api/v1/coverage/providers") {
        healthChecks += 1;
        await new Promise((resolve) => setTimeout(resolve, 25));
        return mockJsonResponse({ providers: ["fred"] });
      }
      if (url === "http://127.0.0.1:6901/api/v1/coverage/providers") {
        healthChecks += 1;
        return mockJsonResponse({ providers: ["fred"] });
      }

      const sharedQuantResponses = new Map<string, unknown>([
        ["/api/v1/quant_ml/universe/list", { universes: [{ id: "default" }] }],
        ["/api/v1/quant_ml/trading/orders?limit=1", { items: [] }],
        ["/api/v1/quant_ml/workspace/brief", { actions: [] }],
        ["/api/v1/quant_ml/macro/studies", { items: [] }],
        ["/api/v1/quant_ml/ops/issues", { items: [] }],
        ["/api/v1/quant_ml/runs/compare?limit=2", { items: [] }],
        ["/api/v1/quant_ml/symbol/context?symbol=SPY", { symbol: "SPY" }],
      ]);

      for (const [suffix, payload] of sharedQuantResponses.entries()) {
        if (url === `http://127.0.0.1:6900${suffix}` || url === `http://127.0.0.1:6901${suffix}`) {
          return mockJsonResponse(payload);
        }
      }

      if (
        url
        === "http://127.0.0.1:6900/api/v1/equity/fundamental/income?symbol=SPY&provider=yfinance&period=annual&limit=1"
      ) {
        return mockJsonResponse({ detail: "finance route failed" }, false, 500);
      }
      if (
        url
        === "http://127.0.0.1:6901/api/v1/equity/fundamental/income?symbol=SPY&provider=yfinance&period=annual&limit=1"
      ) {
        return mockJsonResponse({ results: [] });
      }

      return mockJsonResponse({ detail: "unexpected" }, false, 404);
    }) as unknown as typeof fetch;

    const [first, second] = await Promise.all([resolveOpenBBBackend(), resolveOpenBBBackend()]);

    expect(first.baseUrl).toBe("http://127.0.0.1:6901");
    expect(second.baseUrl).toBe("http://127.0.0.1:6901");
    expect(healthChecks).toBe(2);
  });
});
