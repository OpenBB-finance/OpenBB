/// <reference types="vitest/globals" />
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";
import { vi } from "vitest";
import { invoke } from "@tauri-apps/api/core";
import { Route as MacroRoute } from "../../routes/macro";

vi.mock("@tanstack/react-router", () => ({
  createFileRoute: vi.fn(() => (options: { component: React.ComponentType }) => ({
    options: {
      component: options.component,
    },
  })),
}));

vi.mock("@tauri-apps/api/core", () => ({
  invoke: vi.fn(),
}));

function mockResponse(payload: unknown, ok = true, status = 200): Response {
  return {
    ok,
    status,
    json: async () => payload,
  } as Response;
}

describe("Macro Route", () => {
  const MacroComponent = MacroRoute.options.component as React.ComponentType;

  beforeEach(() => {
    vi.clearAllMocks();

    vi.mocked(invoke).mockResolvedValue([
      {
        id: "openbb-api",
        name: "OpenBB API",
        command: "openbb-api --host 127.0.0.1 --port 6900",
        status: "running",
        url: "http://127.0.0.1:6900",
      },
    ]);

    global.fetch = vi.fn(async (input: string | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith("/api/v1/system")) {
        return mockResponse({ results: {} });
      }
      if (url.includes("/api/v1/quant_ml/macro/catalog")) {
        return mockResponse({
          status: "ok",
          items: [
            {
              id: "FRED:UNRATE",
              source: "FRED",
              series_id: "UNRATE",
              title: "Unemployment Rate",
              frequency: "M",
              units: "Percent",
              domain: "Labor",
              default_transform: "yoy",
              publish_lag: 30,
              active: true,
            },
          ],
        });
      }
      if (url.includes("/api/v1/quant_ml/macro/series")) {
        return mockResponse({
          meta: {
            key: "FRED:UNRATE",
            title: "Unemployment Rate",
            units: "Percent",
            frequency: "monthly",
            source: "FRED",
            transform: "level",
            lag_applied: "P1M",
          },
          data: [
            { date: "2025-01-31", value: 4.0 },
            { date: "2025-02-28", value: 4.1 },
          ],
          stats: {
            last: 4.1,
            change_1m: 0.1,
            change_3m: 0.2,
            z: 0.4,
            percentile_5y: 0.66,
          },
          status: "ok",
          message: null,
        });
      }
      if (url.includes("/api/v1/quant_ml/macro/expression")) {
        const body = init?.body ? JSON.parse(String(init.body)) : {};
        return mockResponse({
          meta: {
            key: String(body.expr || "expr"),
            source: "expression",
            transform: "level",
          },
          data: [
            { date: "2025-01-31", value: 1.0 },
            { date: "2025-02-28", value: 1.1 },
          ],
          stats: {
            last: 1.1,
            change_1m: 0.1,
            change_3m: 0.2,
            z: 0.3,
            percentile_5y: 0.7,
          },
          status: "ok",
          message: null,
          dependencies: ["GLD", "SPY"],
        });
      }
      if (url.includes("/api/v1/quant_ml/macro/regime")) {
        return mockResponse({
          status: "ok",
          data: [
            {
              date: "2025-02-28",
              risk_on_score: 55,
              inflation_score: 48,
              growth_score: 52,
              liquidity_score: 50,
              credit_stress_score: 42,
            },
          ],
          latest: {
            date: "2025-02-28",
            risk_on_score: 55,
            inflation_score: 48,
            growth_score: 52,
            liquidity_score: 50,
            credit_stress_score: 42,
          },
        });
      }
      if (url.includes("/api/v1/quant_ml/macro/alerts")) {
        return mockResponse({
          status: "ok",
          current: [],
          history: [],
        });
      }
      if (url.includes("/api/v1/quant_ml/macro/derived")) {
        return mockResponse({
          status: "ok",
          items: [],
        });
      }
      if (url.includes("/api/v1/quant_ml/macro/update")) {
        return mockResponse({
          status: "ok",
          updated_series: ["UNRATE"],
        });
      }
      if (url.endsWith("/openapi.json") || url.endsWith("/docs")) {
        return mockResponse({ detail: "fallback" }, false, 404);
      }
      return mockResponse({ detail: "not-found" }, false, 404);
    }) as unknown as typeof fetch;
  });

  test("renders macro page and loads default data", async () => {
    await act(async () => {
      render(<MacroComponent />);
    });

    await waitFor(() => {
      expect(screen.getByText("Macro")).toBeInTheDocument();
      expect(screen.getByText("Catalog")).toBeInTheDocument();
      expect(screen.getByText("Cross-Asset Relationship")).toBeInTheDocument();
    });
  });

  test("runs expression execute action", async () => {
    await act(async () => {
      render(<MacroComponent />);
    });

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Execute/i })).toBeInTheDocument();
    });

    await act(async () => {
      fireEvent.change(screen.getByPlaceholderText(/GLD\/SPY/i), { target: { value: "GLD/SPY" } });
      fireEvent.click(screen.getByRole("button", { name: /Execute/i }));
    });

    await waitFor(() => {
      const calls = vi.mocked(global.fetch).mock.calls.map((call) => String(call[0]));
      expect(calls.some((url) => url.includes("/api/v1/quant_ml/macro/expression"))).toBe(true);
    });
  });

  test("does not crash when expression response omits data on insufficient_data", async () => {
    global.fetch = vi.fn(async (input: string | URL, init?: RequestInit) => {
      const url = String(input);
      if (url.endsWith("/api/v1/system")) {
        return mockResponse({ results: {} });
      }
      if (url.includes("/api/v1/quant_ml/macro/catalog")) {
        return mockResponse({
          status: "ok",
          items: [
            {
              id: "FRED:UNRATE",
              source: "FRED",
              series_id: "UNRATE",
              title: "Unemployment Rate",
              frequency: "M",
              units: "Percent",
              domain: "Labor",
              default_transform: "yoy",
              publish_lag: 30,
              active: true,
            },
          ],
        });
      }
      if (url.includes("/api/v1/quant_ml/macro/series")) {
        return mockResponse({
          meta: {
            key: "FRED:UNRATE",
            source: "FRED",
            transform: "level",
          },
          status: "ok",
          data: [{ date: "2025-01-31", value: 4.0 }],
          stats: { last: 4.0 },
        });
      }
      if (url.includes("/api/v1/quant_ml/macro/expression")) {
        const body = init?.body ? JSON.parse(String(init.body)) : {};
        return mockResponse({
          meta: {
            key: String(body.expr || "expr"),
            source: "expression",
            transform: "level",
          },
          status: "insufficient_data",
          message: "No market observations found for symbol: GLD",
          dependencies: [],
        });
      }
      if (url.includes("/api/v1/quant_ml/macro/regime")) {
        return mockResponse({ status: "insufficient_data", data: [] });
      }
      if (url.includes("/api/v1/quant_ml/macro/alerts")) {
        return mockResponse({ status: "insufficient_data", current: [], history: [] });
      }
      if (url.includes("/api/v1/quant_ml/macro/derived")) {
        return mockResponse({ status: "ok", items: [] });
      }
      if (url.endsWith("/openapi.json") || url.endsWith("/docs")) {
        return mockResponse({ detail: "fallback" }, false, 404);
      }
      return mockResponse({ detail: "not-found" }, false, 404);
    }) as unknown as typeof fetch;

    await act(async () => {
      render(<MacroComponent />);
    });

    await waitFor(() => {
      expect(screen.getByText("Macro")).toBeInTheDocument();
      expect(screen.getAllByText("No data").length).toBeGreaterThan(0);
    });
  });
});
