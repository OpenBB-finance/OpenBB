import { beforeEach, describe, expect, test, vi } from "vitest";
import {
  clearFinanceStatementCache,
  fetchFinanceForecast,
  fetchFinanceStatement,
} from "../../lib/financeApi";

vi.mock("../../lib/openbbBackend", () => ({
  resolveOpenBBBackend: vi.fn(async () => ({
    baseUrl: "http://127.0.0.1:6900",
    connected: true,
    detail: "ok",
    source: "fallback",
  })),
}));

describe("financeApi", () => {
  beforeEach(() => {
    clearFinanceStatementCache();
    vi.restoreAllMocks();
  });

  test("loads a statement with extracted ticker and caches the result", async () => {
    const fetchMock = vi.spyOn(global, "fetch").mockResolvedValue({
      ok: true,
      json: async () => ({
        provider: "yfinance",
        results: [{ period_ending: "2025-09-30", total_revenue: 416161000000 }],
        extra: { metadata: { timestamp: "2026-03-22T01:02:03Z" } },
      }),
    } as Response);

    const first = await fetchFinanceStatement("income", "NASDAQ:AAPL", "annual");
    const second = await fetchFinanceStatement("income", "NASDAQ:AAPL", "annual");

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock.mock.calls[0]?.[0]).toContain("/api/v1/equity/fundamental/income");
    expect(fetchMock.mock.calls[0]?.[0]).toContain("symbol=AAPL");
    expect(fetchMock.mock.calls[0]?.[0]).toContain("provider=yfinance");
    expect(first.rows[0]?.total_revenue).toBe(416161000000);
    expect(second.provider).toBe("yfinance");
  });

  test("loads forecast consensus and caches the result", async () => {
    const fetchMock = vi.spyOn(global, "fetch").mockResolvedValue({
      ok: true,
      json: async () => ({
        provider: "yfinance",
        results: [
          {
            symbol: "AAPL",
            target_consensus: 295.43,
            target_low: 205,
            target_high: 350,
            current_price: 247.99,
            number_of_analysts: 41,
          },
        ],
        extra: { metadata: { timestamp: "2026-03-22T01:02:03Z" } },
      }),
    } as Response);

    const first = await fetchFinanceForecast("NASDAQ:AAPL");
    const second = await fetchFinanceForecast("NASDAQ:AAPL");

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(fetchMock.mock.calls[0]?.[0]).toContain("/api/v1/equity/estimates/consensus");
    expect(fetchMock.mock.calls[0]?.[0]).toContain("symbol=AAPL");
    expect(first.consensus?.target_consensus).toBe(295.43);
    expect(second.provider).toBe("yfinance");
  });
});
