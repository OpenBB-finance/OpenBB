/// <reference types="vitest/globals" />
import { afterEach, beforeEach, expect, test, vi } from "vitest";
import { fetchBatchQuotes, fetchStockNews } from "../../lib/watchlistApi";

describe("watchlistApi", () => {
  const fetchMock = vi.fn();

  beforeEach(() => {
    fetchMock.mockReset();
    vi.stubGlobal("fetch", fetchMock);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  test("normalizes exchange-qualified symbols for stock news requests", async () => {
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => ({
        results: [
          {
            id: "news-1",
            title: "Headline",
            summary: "Summary",
            published_at: "2026-03-27T00:00:00Z",
            source: "Wire",
            url: "https://example.com/story",
            thumbnail: "",
            is_breaking: false,
          },
        ],
        error: "warning",
      }),
    });

    const payload = await fetchStockNews("http://127.0.0.1:6900", "NASDAQ:AAPL");

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(String(fetchMock.mock.calls[0]?.[0])).toContain("symbol=AAPL");
    expect(payload.symbol).toBe("AAPL");
    expect(payload.news_items).toHaveLength(1);
    expect(payload.total).toBe(1);
    expect(payload.error).toBe("warning");
  });

  test("maps quote responses back to the original watchlist symbols", async () => {
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => ({
        results: [
          {
            symbol: "AAPL",
            last_price: 192.34,
            change: 1.23,
            change_percent: 0.64,
            volume: 123456,
            name: "Apple Inc.",
          },
        ],
      }),
    });

    const payload = await fetchBatchQuotes("http://127.0.0.1:6900", ["NASDAQ:AAPL", "AAPL"]);

    expect(fetchMock).toHaveBeenCalledTimes(1);
    expect(String(fetchMock.mock.calls[0]?.[0])).toContain("symbol=AAPL");
    expect(payload).toEqual([
      {
        symbol: "NASDAQ:AAPL",
        last_price: 192.34,
        change: 1.23,
        change_percent: 0.64,
        volume: 123456,
        name: "Apple Inc.",
      },
      {
        symbol: "AAPL",
        last_price: 192.34,
        change: 1.23,
        change_percent: 0.64,
        volume: 123456,
        name: "Apple Inc.",
      },
    ]);
  });
});
