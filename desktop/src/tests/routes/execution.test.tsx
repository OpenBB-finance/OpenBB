/// <reference types="vitest/globals" />
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";
import { vi } from "vitest";
import { invoke } from "@tauri-apps/api/core";
import { Route as ExecutionRoute } from "../../routes/execution";

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

describe("Execution Route", () => {
  const ExecutionComponent = ExecutionRoute.options.component as React.ComponentType;

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

    global.fetch = vi.fn(async (input: string | URL) => {
      const url = String(input);
      if (url.endsWith("/api/v1/system")) return mockResponse({ results: {} });
      if (url.endsWith("/api/v1/quant_ml/universe/list")) {
        return mockResponse({ universes: [{ id: "default", has_file: true, count_hint: 2 }] });
      }
      if (url.endsWith("/api/v1/quant_ml/execution/orders/preview")) {
        return mockResponse({
          run_id: "run-1",
          model_name: "lgbm_ranker",
          status: "ok",
          orders: [{ order_id: "o1", symbol: "AAPL", side: "buy", quantity: 1, current_weight: 0, target_weight: 0.1, est_price: 1, est_notional: 1, status: "preview" }],
        });
      }
      if (url.endsWith("/api/v1/quant_ml/risk/check/pretrade")) {
        return mockResponse({
          run_id: "run-1",
          model_name: "lgbm_ranker",
          status: "ok",
          passed: true,
          kill_switch: false,
          violations: [],
        });
      }
      if (url.includes("/api/v1/quant_ml/execution/orders/current")) {
        return mockResponse({ run_id: "run-1", model_name: "lgbm_ranker", status: "ok", orders: [] });
      }
      if (url.includes("/api/v1/quant_ml/execution/fills/history")) {
        return mockResponse({ run_id: "run-1", model_name: "lgbm_ranker", status: "ok", fills: [] });
      }
      if (url.includes("/api/v1/quant_ml/execution/positions/current")) {
        return mockResponse({ run_id: "run-1", model_name: "lgbm_ranker", status: "ok", positions: [], cash: 0, gross_exposure: 0, net_exposure: 0 });
      }
      if (url.includes("/api/v1/quant_ml/execution/pnl")) {
        return mockResponse({ run_id: "run-1", model_name: "lgbm_ranker", status: "ok", realized_pnl: 0, unrealized_pnl: 0, total_pnl: 0, return_pct: 0 });
      }
      if (url.includes("/api/v1/quant_ml/risk/limits")) {
        return mockResponse({ run_id: "run-1", model_name: "lgbm_ranker", status: "ok", limits: {}, kill_switch: false });
      }
      if (url.includes("/api/v1/quant_ml/risk/events")) {
        return mockResponse({ run_id: "run-1", model_name: "lgbm_ranker", status: "ok", events: [] });
      }
      if (url.endsWith("/api/v1/quant_ml/execution/orders/submit")) {
        return mockResponse({
          run_id: "run-1",
          model_name: "lgbm_ranker",
          status: "ok",
          orders: [],
          fills_count: 0,
          cash_after: 0,
          nav_after: 0,
          kill_switch: false,
        });
      }
      return mockResponse({ detail: "not-found" }, false, 404);
    }) as unknown as typeof fetch;
  });

  test("runs preview and risk workflow without crashing", async () => {
    await act(async () => {
      render(<ExecutionComponent />);
    });

    await waitFor(() => {
      expect(screen.getByText(/Execution \/ Risk/i)).toBeInTheDocument();
    });

    await act(async () => {
      fireEvent.change(screen.getByPlaceholderText("run_id"), { target: { value: "run-1" } });
      fireEvent.click(screen.getByRole("button", { name: /Preview \+ Risk Check/i }));
    });

    await waitFor(() => {
      const calls = vi.mocked(global.fetch).mock.calls.map((call) => String(call[0]));
      expect(calls.some((url) => url.endsWith("/api/v1/quant_ml/execution/orders/preview"))).toBe(true);
      expect(calls.some((url) => url.endsWith("/api/v1/quant_ml/risk/check/pretrade"))).toBe(true);
      expect(calls.some((url) => url.includes("/api/v1/quant_ml/execution/orders/current"))).toBe(true);
    });
  });
});

