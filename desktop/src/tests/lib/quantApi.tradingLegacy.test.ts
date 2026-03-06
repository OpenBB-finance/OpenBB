/// <reference types="vitest/globals" />
import { beforeEach, describe, expect, test, vi } from "vitest";
import {
  fetchTradingExecutionMode,
  fetchTradingSettings,
} from "../../lib/quantApi";

function mockJsonResponse(payload: unknown, ok = true, status = 200): Response {
  return {
    ok,
    status,
    json: async () => payload,
  } as Response;
}

describe("trading legacy route fallback", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    sessionStorage.clear();
  });

  test("returns default trading settings for legacy GET collision", async () => {
    global.fetch = vi.fn(async (input: string | URL) => {
      const url = String(input);
      if (url.endsWith("/api/v1/quant_ml/trading/settings")) {
        return mockJsonResponse(
          {
            detail:
              "Unexpected Error -> ValidationError -> 1 validation error for trading_settings_update request",
          },
          false,
          500,
        );
      }
      return mockJsonResponse({ detail: "not-found" }, false, 404);
    }) as unknown as typeof fetch;

    const first = await fetchTradingSettings("http://127.0.0.1:8000");
    const second = await fetchTradingSettings("http://127.0.0.1:8000");

    expect(first.tab_name).toBe("Trading");
    expect(first.execution.auto_order).toBe(false);
    expect(second.risk.stop_loss_pct).toBe(0.08);
    expect(vi.mocked(global.fetch).mock.calls).toHaveLength(1);
  });

  test("derives execution mode from trading status for legacy GET collision", async () => {
    global.fetch = vi.fn(async (input: string | URL) => {
      const url = String(input);
      if (url.endsWith("/api/v1/quant_ml/trading/execution/mode")) {
        return mockJsonResponse(
          {
            detail:
              "Unexpected Error -> ValidationError -> 1 validation error for trading_execution_mode_update request",
          },
          false,
          500,
        );
      }
      if (url.endsWith("/api/v1/quant_ml/trading/status")) {
        return mockJsonResponse({
          mode: "shadow_live",
          runtime_status: "running",
          active_strategy_count: 1,
          watchlist_size: 10,
          open_position_count: 2,
          today_signal_count: 5,
          today_order_count: 2,
          today_realized_pnl: 100,
          cumulative_pnl: 200,
          intraday_drawdown: -0.01,
          used_capital: 5000,
          available_cash: 10000,
        });
      }
      return mockJsonResponse({ detail: "not-found" }, false, 404);
    }) as unknown as typeof fetch;

    const first = await fetchTradingExecutionMode("http://127.0.0.1:8000");
    const second = await fetchTradingExecutionMode("http://127.0.0.1:8000");

    expect(first.mode).toBe("shadow_live");
    expect(first.broker_ready).toBe(false);
    expect(second.mode).toBe("shadow_live");
    expect(vi.mocked(global.fetch).mock.calls.filter((call) =>
      String(call[0]).endsWith("/api/v1/quant_ml/trading/execution/mode"))).toHaveLength(1);
  });
});
