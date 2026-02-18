/// <reference types="vitest/globals" />
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";
import { vi } from "vitest";
import { invoke } from "@tauri-apps/api/core";
import { Route as MacroRoute } from "../../routes/macro";
import { clearCachePrefix } from "../../lib/quantCache";

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
    clearCachePrefix("");

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
        if (url.includes("ids=")) {
          return mockResponse({
            status: "ok",
            message: null,
            series: {
              "FRED:UNRATE": {
                meta: { key: "FRED:UNRATE", source: "FRED", transform: "level" },
                data: [
                  { date: "2025-01-31", value: 4.0 },
                  { date: "2025-02-28", value: 4.1 },
                ],
                stats: { last: 4.1 },
                status: "ok",
              },
              "FRED:CPIAUCSL": {
                meta: { key: "FRED:CPIAUCSL", source: "FRED", transform: "level" },
                data: [
                  { date: "2025-01-31", value: 300.0 },
                  { date: "2025-02-28", value: 301.0 },
                ],
                stats: { last: 301.0 },
                status: "ok",
              },
            },
          });
        }
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
      if (url.includes("/api/v1/quant_ml/market/ratio")) {
        return mockResponse({
          meta: { key: "GLD/SPY", source: "expression", transform: "level" },
          data: [
            { date: "2025-01-31", value: 1.2 },
            { date: "2025-02-28", value: 1.25 },
          ],
          stats: { last: 1.25, change_1m: 0.05, change_3m: 0.1, z: 0.2, percentile_5y: 0.6 },
          status: "ok",
          message: null,
        });
      }
      if (url.includes("/api/v1/quant_ml/market/rolling_corr")) {
        return mockResponse({
          meta: { key: "rolling_corr(GLD,SPY,60)", source: "expression", transform: "level" },
          data: [
            { date: "2025-01-31", value: 0.8 },
            { date: "2025-02-28", value: 0.82 },
          ],
          stats: { last: 0.82, change_1m: 0.02, change_3m: 0.03, z: 0.1, percentile_5y: 0.5 },
          status: "ok",
          message: null,
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
      if (url.includes("/api/v1/quant_ml/macro/health")) {
        return mockResponse({
          status: "ok",
          fred_api_key_configured: true,
          macro_db_path: "/tmp/macro.db",
          obs_stats: { total_series_in_catalog: 1, total_series_with_obs: 1 },
          feature_stats: { total_feature_rows: 10, feature_names_present: [] },
          warnings: [],
        });
      }
      if (url.includes("/api/v1/quant_ml/macro/update")) {
        return mockResponse({
          status: "ok",
          updated_series: ["UNRATE"],
        });
      }
      if (url.includes("/api/v1/quant_ml/macro/presets/copper_gold")) {
        return mockResponse({
          status: "ok",
          message: null,
          preset_id: "copper_gold",
          inputs: {},
          series: [],
          events: [],
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
      fireEvent.change(screen.getByLabelText(/Expression/i), { target: { value: "GLD/SPY" } });
      fireEvent.click(screen.getByRole("button", { name: /Execute/i }));
    });

    await waitFor(() => {
      const calls = vi.mocked(global.fetch).mock.calls.map((call) => String(call[0]));
      expect(calls.some((url) => url.includes("/api/v1/quant_ml/macro/expression"))).toBe(true);
    });
  });

  test("requests multi-series comparison payload", async () => {
    await act(async () => {
      render(<MacroComponent />);
    });

    await waitFor(() => {
      const calls = vi.mocked(global.fetch).mock.calls.map((call) => String(call[0]));
      expect(calls.some((url) => url.includes("/api/v1/quant_ml/macro/series?ids="))).toBe(true);
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
        if (url.includes("ids=")) {
          return mockResponse({
            status: "insufficient_data",
            message: "No comparison data",
            series: {},
          });
        }
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
      if (url.includes("/api/v1/quant_ml/market/ratio")) {
        return mockResponse({
          meta: { key: "GLD/SPY", source: "expression", transform: "level" },
          status: "insufficient_data",
          message: "No market observations found",
          data: [],
          stats: {},
        });
      }
      if (url.includes("/api/v1/quant_ml/market/rolling_corr")) {
        return mockResponse({
          meta: { key: "rolling_corr(GLD,SPY,60)", source: "expression", transform: "level" },
          status: "insufficient_data",
          message: "No market observations found",
          data: [],
          stats: {},
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
      if (url.includes("/api/v1/quant_ml/macro/health")) {
        return mockResponse({
          status: "ok",
          fred_api_key_configured: false,
          macro_db_path: "/tmp/macro.db",
          obs_stats: { total_series_in_catalog: 0, total_series_with_obs: 0 },
          feature_stats: { total_feature_rows: 0, feature_names_present: [] },
          warnings: ["FRED_API_KEY missing"],
        });
      }
      if (url.includes("/api/v1/quant_ml/macro/presets/copper_gold")) {
        return mockResponse({
          status: "insufficient_data",
          message: "No preset data",
          preset_id: "copper_gold",
          inputs: {},
          series: [],
          events: [],
        });
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
