/// <reference types="vitest/globals" />
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";
import { vi } from "vitest";
import { invoke } from "@tauri-apps/api/core";
import { clearCachePrefix } from "../../lib/quantCache";
import { Route as TradingRoute } from "../../routes/trading";

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

describe("Trading Route", () => {
  const TradingComponent = TradingRoute.options.component as React.ComponentType;

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
      if (url.endsWith("/api/v1/coverage/providers") || url.endsWith("/api/v1/system")) {
        return mockResponse({ results: {} });
      }
      if (url.endsWith("/api/v1/quant_ml/universe/list")) {
        return mockResponse({
          universes: [{ id: "default", has_file: true, count_hint: 3 }],
        });
      }
      if (url.endsWith("/api/v1/quant_ml/trading/status")) {
        return mockResponse({
          mode: "paper",
          runtime_status: "running",
          last_scan_at: "2026-03-06T06:30:00Z",
          last_order_at: "2026-03-06T06:35:00Z",
          active_strategy_count: 4,
          watchlist_size: 120,
          open_position_count: 1,
          today_signal_count: 3,
          today_order_count: 2,
          today_realized_pnl: 125.5,
          cumulative_pnl: 540.25,
          intraday_drawdown: -0.012,
          used_capital: 12000,
          available_cash: 88000,
        });
      }
      if (url.endsWith("/api/v1/quant_ml/trading/settings/update") && init?.method === "POST") {
        const body = init.body ? JSON.parse(String(init.body)) : {};
        return mockResponse({
          version: "1",
          mode: "paper",
          runtime_status: "running",
          universe_id: "default",
          schedule: {},
          scan: body.scan ?? { lookback_days: 320 },
          execution: body.execution ?? {
            auto_order: false,
            manual_approval: true,
            signal_generation: true,
          },
          account: body.account ?? {
            max_concurrent_positions: 12,
            position_size_value: 0.05,
            max_daily_new_entries: 5,
          },
          risk: body.risk ?? {
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
          built_in_strategies: [
            {
              name: "ema_cross",
              version: "1.0.0",
              enabled: true,
              parameters: {},
            },
          ],
          custom_algorithm_records: [],
        });
      }
      if (url.includes("/api/v1/quant_ml/trading/scan/latest")) {
        return mockResponse({
          items: [
            {
              signal_id: "sig-1",
              timestamp: "2026-03-06T06:30:00Z",
              ticker: "AAPL",
              name: "Apple",
              current_price: 210.15,
              signal: "entry",
              signal_type: "buy",
              side: "buy",
              strategy_name: "ema_cross",
              algorithm_version: "1.0.0",
              signal_strength: 0.88,
              entry_score: 0.91,
              priority: 1,
              confidence: 0.87,
              rsi: 48.2,
              macd_hist: 0.12,
              ma_relation: 1,
              volume_change_pct: 0.22,
              atr: 4.2,
              recent_return: 0.03,
              recommended_action: "buy",
              position_held: true,
              risk_check_status: "pass",
              risk_reason_codes: [],
              reason: "EMA cross and momentum confirmation.",
            },
          ],
        });
      }
      if (url.includes("/api/v1/quant_ml/trading/scan/history")) {
        return mockResponse({
          items: [
            {
              signal_id: "sig-h1",
              timestamp: "2026-03-05T06:30:00Z",
              ticker: "MSFT",
              current_price: 402.5,
              signal_type: "hold",
              side: "buy",
              strategy_name: "rsi_reversal",
              signal_strength: 0.45,
              entry_score: 0.4,
              priority: 2,
              confidence: 0.55,
              rsi: 39.2,
              macd_hist: -0.03,
              ma_relation: 0,
              volume_change_pct: 0.1,
              atr: 3.1,
              recent_return: 0.01,
              recommended_action: "hold",
              position_held: false,
              risk_check_status: "pass",
              risk_reason_codes: [],
            },
          ],
        });
      }
      if (url.includes("/api/v1/quant_ml/trading/orders")) {
        if (url.endsWith("/approve") || url.endsWith("/cancel")) {
          return mockResponse({
            order_id: "ord-1",
            ticker: "AAPL",
            strategy_name: "ema_cross",
            status: "filled",
            side: "buy",
            quantity: 10,
            requested_price: 210.15,
            notional: 2101.5,
          });
        }
        return mockResponse({
          items: [
            {
              order_id: "ord-1",
              created_at: "2026-03-06T06:31:00Z",
              ticker: "AAPL",
              strategy_name: "ema_cross",
              status: "pending",
              side: "buy",
              signal_type: "buy",
              quantity: 10,
              requested_price: 210.15,
              notional: 2101.5,
            },
          ],
        });
      }
      if (url.includes("/api/v1/quant_ml/trading/fills")) {
        return mockResponse({ items: [{ fill_id: "fill-1" }] });
      }
      if (url.endsWith("/api/v1/quant_ml/trading/positions")) {
        return mockResponse({
          mode: "paper",
          items: [
            {
              ticker: "AAPL",
              entry_time: "2026-03-05T06:30:00Z",
              entry_price: 205,
              current_price: 210.15,
              quantity: 10,
              unrealized_pnl: 51.5,
              holding_period_days: 1,
            },
          ],
        });
      }
      if (url.includes("/api/v1/quant_ml/trading/positions/AAPL/close")) {
        return mockResponse({
          order_id: "ord-close-1",
          ticker: "AAPL",
          strategy_name: "ema_cross",
          status: "submitted",
          side: "sell",
          quantity: 10,
          requested_price: 210.15,
          notional: 2101.5,
        });
      }
      if (url.endsWith("/api/v1/quant_ml/trading/performance")) {
        return mockResponse({
          cumulative_return: 0.12,
          win_rate: 0.58,
          sharpe: 1.42,
          max_drawdown: -0.06,
          equity_curve: [
            { date: "2026-03-05", value: 100000 },
            { date: "2026-03-06", value: 100540 },
          ],
          drawdown_curve: [
            { date: "2026-03-05", value: 0 },
            { date: "2026-03-06", value: -0.01 },
          ],
          daily_pnl: [
            { date: "2026-03-05", value: 0 },
            { date: "2026-03-06", value: 540 },
          ],
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
          events: [
            {
              created_at: "2026-03-06T06:32:00Z",
              reason_code: "insufficient_liquidity",
              status: "warning",
              message: "Liquidity filter blocked one candidate.",
            },
          ],
        });
      }
      if (url.includes("/api/v1/quant_ml/trading/events")) {
        return mockResponse({
          items: [
            {
              timestamp: "2026-03-06T06:33:00Z",
              event_type: "signal_generated",
              ticker: "AAPL",
              strategy: "ema_cross",
              status: "info",
              message: "Signal normalized and queued.",
            },
          ],
        });
      }
      if (url.endsWith("/api/v1/quant_ml/trading/algorithms")) {
        return mockResponse({
          items: [
            {
              name: "sample_custom_algo",
              version: "0.1.0",
              status: "sandbox",
              active: false,
              sandbox_mode: true,
              signal_only: true,
              parameters: {},
              required_columns: ["close", "volume"],
              validation_result: {},
              recent_run_result: {},
              performance_summary: {},
            },
          ],
        });
      }
      if (url.endsWith("/api/v1/quant_ml/trading/algorithms/toggle")) {
        return mockResponse({
          items: [
            {
              name: "sample_custom_algo",
              version: "0.1.0",
              status: "active",
              active: true,
              sandbox_mode: true,
              signal_only: true,
              parameters: {},
              required_columns: ["close", "volume"],
              validation_result: {},
              recent_run_result: {},
              performance_summary: {},
            },
          ],
        });
      }
      if (url.endsWith("/api/v1/quant_ml/trading/algorithms/validate")) {
        return mockResponse({
          name: "sample_custom_algo",
          version: "0.1.0",
          status: "validated",
          checks: [],
          summary: {},
        });
      }
      if (url.endsWith("/api/v1/quant_ml/trading/execution/mode/update") && init?.method === "POST") {
        const body = init.body ? JSON.parse(String(init.body)) : {};
        return mockResponse({
          mode: body.mode,
          live_adapter_enabled: false,
          broker_ready: false,
          kill_switch: false,
        });
      }
      if (url.endsWith("/api/v1/quant_ml/trading/execution/mode")) {
        return mockResponse({ mode: "paper", live_adapter_enabled: false, broker_ready: false, kill_switch: false });
      }
      if (url.endsWith("/api/v1/quant_ml/trading/symbol/AAPL")) {
        return mockResponse({
          ticker: "AAPL",
          series: [
            { date: "2026-03-04", close: 204, ema_fast: 202, rsi: 41 },
            { date: "2026-03-05", close: 205, ema_fast: 203, rsi: 44 },
            { date: "2026-03-06", close: 210.15, ema_fast: 206, rsi: 48.2 },
          ],
          signals: [],
          orders: [],
          position: { ticker: "AAPL" },
          explanation: "Fast EMA crossed above the slow EMA with stable RSI and volume support.",
        });
      }
      if (url.endsWith("/api/v1/quant_ml/trading/cycle/run")) {
        const body = init?.body ? JSON.parse(String(init.body)) : {};
        return mockResponse({
          cycle_id: "cycle-1",
          status: body.auto_execute ? "executed" : "queued",
          signal_count: 1,
          order_count: 1,
          fill_count: 1,
        });
      }
      return mockResponse({ detail: "not-found" }, false, 404);
    }) as unknown as typeof fetch;
  });

  test("loads trading console data without crashing", async () => {
    await act(async () => {
      render(<TradingComponent />);
    });

    await waitFor(() => {
      expect(screen.getByText("Portfolio & Execution")).toBeInTheDocument();
      expect(screen.getByText(/Unified workflow for signals, pretrade risk, order preview, positions, fills, and broker runtime/i)).toBeInTheDocument();
      expect(screen.getByText(/Execution Context/i)).toBeInTheDocument();
      expect(screen.getByRole("tab", { name: "Signals" })).toBeInTheDocument();
      expect(screen.getByRole("tab", { name: "Brokers" })).toBeInTheDocument();
    });

    await waitFor(() => {
      const calls = vi.mocked(global.fetch).mock.calls.map((call) => String(call[0]));
      expect(calls.some((url) => url.endsWith("/api/v1/quant_ml/trading/status"))).toBe(true);
      expect(calls.some((url) => url.includes("/api/v1/quant_ml/trading/scan/latest"))).toBe(true);
      expect(calls.some((url) => url.includes("/api/v1/quant_ml/trading/scan/history"))).toBe(true);
      expect(calls.some((url) => url.includes("/api/v1/quant_ml/trading/orders"))).toBe(true);
      expect(calls.some((url) => url.endsWith("/api/v1/quant_ml/trading/symbol/AAPL"))).toBe(true);
    });
  });

  test("runs a scan cycle from the trading console", async () => {
    await act(async () => {
      render(<TradingComponent />);
    });

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Run Scan Cycle/i })).toBeInTheDocument();
    });

    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: /Run Scan Cycle/i }));
    });

    await waitFor(() => {
      const calls = vi.mocked(global.fetch).mock.calls.filter(
        (call) => String(call[0]).endsWith("/api/v1/quant_ml/trading/cycle/run"),
      );
      expect(calls.length).toBeGreaterThan(0);
    });
  });

  test("updates trading execution mode from the console", async () => {
    await act(async () => {
      render(<TradingComponent />);
    });

    await waitFor(() => {
      expect(screen.getByLabelText(/^Execution Mode$/i)).toBeInTheDocument();
    });

    await act(async () => {
      fireEvent.change(screen.getByLabelText(/^Execution Mode$/i), { target: { value: "shadow_live" } });
    });

    await waitFor(() => {
      const calls = vi.mocked(global.fetch).mock.calls.filter(
        (call) => String(call[0]).endsWith("/api/v1/quant_ml/trading/execution/mode/update") && call[1]?.method === "POST",
      );
      expect(calls.length).toBeGreaterThan(0);
    });
  });
});
