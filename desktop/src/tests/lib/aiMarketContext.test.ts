/// <reference types="vitest/globals" />

import { describe, expect, test, vi } from "vitest";
import {
  AI_MARKET_BACKEND_REQUIRED_MESSAGE,
  analyzeAiMarketPrompt,
  buildAiMarketContext,
} from "../../lib/aiMarketContext";

const resolveOpenBBBackendMock = vi.fn();
const fetchFinanceForecastMock = vi.fn();
const fetchFinanceStatementMock = vi.fn();
const fetchBatchQuotesMock = vi.fn();

vi.mock("../../lib/openbbBackend", () => ({
  resolveOpenBBBackend: () => resolveOpenBBBackendMock(),
}));

vi.mock("../../lib/financeApi", () => ({
  fetchFinanceForecast: (...args: unknown[]) => fetchFinanceForecastMock(...args),
  fetchFinanceStatement: (...args: unknown[]) => fetchFinanceStatementMock(...args),
}));

vi.mock("../../lib/watchlistApi", () => ({
  fetchBatchQuotes: (...args: unknown[]) => fetchBatchQuotesMock(...args),
}));

describe("aiMarketContext", () => {
  beforeEach(() => {
    resolveOpenBBBackendMock.mockReset();
    fetchFinanceForecastMock.mockReset();
    fetchFinanceStatementMock.mockReset();
    fetchBatchQuotesMock.mockReset();
  });

  test("detects a Korean finance question with a ticker symbol", () => {
    expect(
      analyzeAiMarketPrompt("IBM의 재무제표를 분석한 후 예상 주가의 범위를 알려주세요"),
    ).toEqual({
      isFinanceQuestion: true,
      symbol: "IBM",
      searchQuery: "IBM",
    });
  });

  test("extracts a company-name search query when no ticker is present", () => {
    expect(
      analyzeAiMarketPrompt("Analyze International Business Machines financial statements and estimate a price range."),
    ).toEqual({
      isFinanceQuestion: true,
      symbol: null,
      searchQuery: "International Business Machines",
    });
  });

  test("builds supplemental context from OpenBB data", async () => {
    resolveOpenBBBackendMock.mockResolvedValue({
      baseUrl: "http://127.0.0.1:6900",
      connected: true,
      detail: "ok",
      source: "fallback",
    });
    fetchBatchQuotesMock.mockResolvedValue([
      {
        symbol: "IBM",
        last_price: 194.5,
        change: 1.25,
        change_percent: 0.65,
        volume: 1000,
        name: "IBM",
      },
    ]);
    fetchFinanceForecastMock.mockResolvedValue({
      consensus: {
        symbol: "IBM",
        target_low: 175,
        target_consensus: 205,
        target_median: 202,
        target_high: 225,
        recommendation: "buy",
        recommendation_mean: 2.1,
        number_of_analysts: 18,
        current_price: 194.5,
        currency: "USD",
      },
      provider: "openbb",
      timestamp: "2026-03-28T00:00:00Z",
    });
    fetchFinanceStatementMock
      .mockResolvedValueOnce({
        rows: [
          { period_ending: "2025-12-31", total_revenue: 61_000_000_000, net_income: 8_500_000_000, diluted_earnings_per_share: 9.25 },
          { period_ending: "2024-12-31", total_revenue: 59_000_000_000, net_income: 7_900_000_000, diluted_earnings_per_share: 8.6 },
        ],
      })
      .mockResolvedValueOnce({
        rows: [
          { period_ending: "2025-12-31", cash_and_cash_equivalents: 14_000_000_000, long_term_debt: 52_000_000_000, stockholders_equity: 26_000_000_000 },
          { period_ending: "2024-12-31", cash_and_cash_equivalents: 13_200_000_000, long_term_debt: 54_000_000_000, stockholders_equity: 25_500_000_000 },
        ],
      })
      .mockResolvedValueOnce({
        rows: [
          { period_ending: "2025-12-31", operating_cash_flow: 14_500_000_000, free_cash_flow: 12_100_000_000, capital_expenditure: -2_300_000_000 },
          { period_ending: "2024-12-31", operating_cash_flow: 13_900_000_000, free_cash_flow: 11_700_000_000, capital_expenditure: -2_100_000_000 },
        ],
      });

    const result = await buildAiMarketContext(
      "IBM의 재무제표를 분석한 후 예상 주가의 범위를 알려주세요",
    );

    expect(result?.symbol).toBe("IBM");
    expect(result?.actionLabel).toBe("Using OpenBB market data for IBM.");
    expect(result?.supplementalContext).toContain("Target range: low $175.00");
    expect(result?.supplementalContext).toContain("Revenue up");
    expect(result?.supplementalContext).toContain("OpenBB market data for IBM:");
    expect(result?.supplementalContext).toContain("Providers: openbb");
    expect(result?.supplementalContext).toContain("As of: 2026-03-28T00:00:00Z");
    expect(result?.snapshot.currentPrice).toBe("$194.50");
    expect(result?.snapshot.targetRange).toContain("$175.00 - $225.00");
    expect(result?.snapshot.providerSummary).toBe("openbb");
    expect(result?.snapshot.asOf).toBe("2026-03-28T00:00:00Z");
    expect(result?.snapshot.sections[0]?.title).toBe("Income statement");
  });

  test("fails fast when the backend is disconnected", async () => {
    resolveOpenBBBackendMock.mockResolvedValue({
      baseUrl: "http://127.0.0.1:6900",
      connected: false,
      detail: "offline",
      source: "fallback",
    });

    await expect(
      buildAiMarketContext("Analyze IBM financial statements and estimate a price range."),
    ).rejects.toThrow(AI_MARKET_BACKEND_REQUIRED_MESSAGE);
  });

  test("resolves a ticker from company name search before loading market data", async () => {
    resolveOpenBBBackendMock.mockResolvedValue({
      baseUrl: "http://127.0.0.1:6900",
      connected: true,
      detail: "ok",
      source: "fallback",
    });
    fetchFinanceForecastMock.mockResolvedValue({
      consensus: null,
      provider: "openbb",
      timestamp: "2026-03-28T00:00:00Z",
    });
    fetchFinanceStatementMock.mockResolvedValue({ rows: [] });
    fetchBatchQuotesMock.mockResolvedValue([]);

    const fetchMock = vi.fn(async () => ({
      ok: true,
      json: async () => ({
        results: [
          {
            symbol: "IBM",
            name: "International Business Machines",
          },
        ],
      }),
    }));
    const previousFetch = global.fetch;
    vi.stubGlobal("fetch", fetchMock);

    try {
      await expect(
        buildAiMarketContext("Analyze International Business Machines financial statements."),
      ).rejects.toThrow(/did not return usable market data/i);
      expect(fetchMock).not.toHaveBeenCalled();
      expect(fetchFinanceForecastMock).toHaveBeenCalledWith("http://127.0.0.1:6900", "IBM");
    } finally {
      vi.stubGlobal("fetch", previousFetch);
    }
  });
});
