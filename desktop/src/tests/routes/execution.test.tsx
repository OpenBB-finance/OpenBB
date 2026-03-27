/// <reference types="vitest/globals" />
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";
import { vi } from "vitest";
import { invoke } from "@tauri-apps/api/core";
import { clearCachePrefix } from "../../lib/quantCache";
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
    clearCachePrefix("");
    window.history.replaceState({}, "", "/execution");
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
      if (url.endsWith("/api/v1/coverage/providers") || url.endsWith("/api/v1/system")) {
        return mockResponse({ results: {} });
      }
      if (url.endsWith("/api/v1/quant_ml/universe/list")) {
        return mockResponse({ universes: [{ id: "default", has_file: true, count_hint: 2 }] });
      }
      if (url.endsWith("/api/v1/quant_ml/trading/status")) {
        return mockResponse({
          mode: "paper",
          runtime_status: "running",
          last_scan_at: "2026-03-06T06:30:00Z",
          last_order_at: "2026-03-06T06:35:00Z",
          active_strategy_count: 2,
          watchlist_size: 50,
          open_position_count: 0,
          today_signal_count: 0,
          today_order_count: 0,
          today_realized_pnl: 0,
          cumulative_pnl: 0,
          intraday_drawdown: -0.002,
          used_capital: 0,
          available_cash: 100000,
        });
      }
      if (url.endsWith("/api/v1/quant_ml/trading/settings")) {
        return mockResponse({
          version: "1",
          tab_name: "Trading",
          mode: "paper",
          runtime_status: "running",
          universe_id: "default",
          schedule: { mode: "eod" },
          scan: { lookback_days: 320 },
          execution: {
            auto_order: false,
            manual_approval: true,
            signal_generation: true,
          },
          account: {
            max_concurrent_positions: 12,
            position_size_value: 0.05,
            max_daily_new_entries: 5,
          },
          risk: {
            stop_loss_pct: 0.08,
            take_profit_pct: 0.15,
            trailing_stop_enabled: false,
          },
          strategies: {},
          custom_algorithms: {},
          ui: {},
          built_in_strategies: [],
          custom_algorithm_records: [],
        });
      }
      if (url.includes("/api/v1/quant_ml/trading/scan/latest")) {
        return mockResponse({ items: [] });
      }
      if (url.includes("/api/v1/quant_ml/trading/scan/history")) {
        return mockResponse({ items: [] });
      }
      if (url.includes("/api/v1/quant_ml/trading/orders")) {
        return mockResponse({ items: [] });
      }
      if (url.includes("/api/v1/quant_ml/trading/fills")) {
        return mockResponse({ items: [] });
      }
      if (url.endsWith("/api/v1/quant_ml/trading/positions")) {
        return mockResponse({ mode: "paper", items: [] });
      }
      if (url.endsWith("/api/v1/quant_ml/trading/performance")) {
        return mockResponse({
          cumulative_return: 0,
          win_rate: 0,
          sharpe: 0,
          max_drawdown: 0,
          equity_curve: [],
          drawdown_curve: [],
          daily_pnl: [],
        });
      }
      if (url.endsWith("/api/v1/quant_ml/trading/risk")) {
        return mockResponse({
          limits: {
            max_position_weight: 0.1,
            daily_loss_limit: 1500,
            max_concurrent_positions: 12,
            stop_loss_pct: 0.08,
          },
          events: [],
        });
      }
      if (url.includes("/api/v1/quant_ml/trading/events")) {
        return mockResponse({ items: [] });
      }
      if (url.endsWith("/api/v1/quant_ml/trading/algorithms")) {
        return mockResponse({ items: [] });
      }
      if (url.endsWith("/api/v1/quant_ml/trading/execution/mode")) {
        return mockResponse({
          mode: "paper",
          live_adapter_enabled: false,
          broker_ready: false,
          kill_switch: false,
          updated_at: "2026-03-06T06:35:00Z",
        });
      }
      if (url.includes("/api/v1/quant_ml/execution/mode?")) {
        return mockResponse({
          run_id: "run-1",
          model_name: "lgbm_ranker",
          mode: "paper",
          live_adapter_enabled: false,
          broker_ready: false,
          kill_switch: false,
          updated_at: "2026-03-06T06:35:00Z",
        });
      }
      if (url.endsWith("/api/v1/quant_ml/execution/mode/update") && init?.method === "POST") {
        const body = init?.body ? JSON.parse(String(init.body)) : {};
        return mockResponse({
          run_id: "run-1",
          model_name: "lgbm_ranker",
          mode: body.mode,
          live_adapter_enabled: false,
          broker_ready: false,
          kill_switch: false,
          updated_at: "2026-03-06T06:35:00Z",
        });
      }
      if (url.includes("/api/v1/quant_ml/execution/orders/current?")) {
        return mockResponse({
          run_id: "run-1",
          model_name: "lgbm_ranker",
          status: "ok",
          orders: [],
        });
      }
      if (url.includes("/api/v1/quant_ml/execution/fills/history?")) {
        return mockResponse({
          run_id: "run-1",
          model_name: "lgbm_ranker",
          status: "ok",
          fills: [],
        });
      }
      if (url.includes("/api/v1/quant_ml/execution/positions/current?")) {
        return mockResponse({
          run_id: "run-1",
          model_name: "lgbm_ranker",
          status: "ok",
          positions: [],
          cash: 100000,
          gross_exposure: 0,
          net_exposure: 0,
        });
      }
      if (url.includes("/api/v1/quant_ml/execution/pnl?")) {
        return mockResponse({
          run_id: "run-1",
          model_name: "lgbm_ranker",
          status: "ok",
          total_pnl: 0,
          realized_pnl: 0,
          unrealized_pnl: 0,
          return_pct: 0,
        });
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
      if (url.includes("/api/v1/quant_ml/runs/run-1/constraints")) {
        return mockResponse({ turnover_limit: 0.4, max_weight: 0.1 });
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

  test("shows empty-state guard until a run handoff is loaded", async () => {
    await act(async () => {
      render(<ExecutionComponent />);
    });

    await waitFor(() => {
      expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Execution");
      expect(screen.getByText(/Execution requires a run handoff/i)).toBeInTheDocument();
      expect(screen.getByRole("link", { name: /Open Strategy Lab/i })).toBeInTheDocument();
    });
  });

  test("runs preview and risk workflow without crashing", async () => {
    window.history.replaceState({}, "", "/execution?runId=run-1&modelName=lgbm_ranker");
    await act(async () => {
      render(<ExecutionComponent />);
    });

    await waitFor(() => {
      expect(screen.getByRole("heading", { level: 1 })).toHaveTextContent("Execution");
      expect(screen.getByRole("tab", { name: "Orders" })).toHaveAttribute("aria-selected", "true");
    });

    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: /Preview \+ Risk Check/i }));
    });

    await waitFor(() => {
      const calls = vi.mocked(global.fetch).mock.calls.map((call) => String(call[0]));
      expect(calls.some((url) => url.endsWith("/api/v1/quant_ml/execution/orders/preview"))).toBe(true);
      expect(calls.some((url) => url.endsWith("/api/v1/quant_ml/risk/check/pretrade"))).toBe(true);
      expect(calls.some((url) => url.includes("/api/v1/quant_ml/runs/run-1/constraints"))).toBe(true);
      expect(screen.queryByText(/Latest Submission/i)).not.toBeInTheDocument();
    });
  });

  test("updates execution mode without crashing", async () => {
    window.history.replaceState({}, "", "/execution?runId=run-1&modelName=lgbm_ranker");
    await act(async () => {
      render(<ExecutionComponent />);
    });

    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: /Preview \+ Risk Check/i }));
    });

    await waitFor(() => {
      expect(screen.getByLabelText(/^Execution Mode$/i)).toBeInTheDocument();
    });

    await act(async () => {
      fireEvent.change(screen.getByLabelText(/^Execution Mode$/i), { target: { value: "shadow_live" } });
    });

    await waitFor(() => {
      const calls = vi.mocked(global.fetch).mock.calls.filter(
        (call) => String(call[0]).endsWith("/api/v1/quant_ml/execution/mode/update") && call[1]?.method === "POST",
      );
      expect(calls.length).toBeGreaterThan(0);
    });

    expect(screen.getByText(/Live adapter is not broker-ready in this environment./i)).toBeInTheDocument();
  });
});
