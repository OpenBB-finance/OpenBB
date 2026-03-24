/// <reference types="vitest/globals" />
import { beforeEach, describe, expect, test, vi } from "vitest";
import { invalidateBackendCache, resolveOpenBBBackend } from "../../lib/openbbBackend";
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
        return mockJsonResponse({ detail: "quant unavailable" }, false, 404);
      }
      if (url === "http://127.0.0.1:6901/api/v1/coverage/providers") {
        return mockJsonResponse({ providers: ["fred"] });
      }
      if (url === "http://127.0.0.1:6901/api/v1/quant_ml/universe/list") {
        return mockJsonResponse({ universes: [{ id: "default" }] });
      }

      return mockJsonResponse({ detail: "unexpected" }, false, 404);
    }) as unknown as typeof fetch;

    const result = await resolveOpenBBBackend();

    expect(result.connected).toBe(true);
    expect(result.baseUrl).toBe("http://127.0.0.1:6901");
    expect(result.source).toBe("web-dev-fallback");
  });
});
