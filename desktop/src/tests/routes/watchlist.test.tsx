/// <reference types="vitest/globals" />
import { render, screen, waitFor } from "@testing-library/react";
import React from "react";
import { vi } from "vitest";
import { Route as WatchlistRoute } from "../../routes/watchlist";

const resolveBackendMock = vi.fn();
const fetchWatchlistMock = vi.fn();
const fetchStockNewsMock = vi.fn();
const fetchMarketNewsMock = vi.fn();
const fetchBatchQuotesMock = vi.fn();
const updateWatchlistMock = vi.fn();

vi.mock("@tanstack/react-router", () => ({
  createFileRoute: vi.fn(
    () => (options: {
      component: React.ComponentType;
    }) => ({
      options: {
        component: options.component,
      },
    }),
  ),
}));

vi.mock("../../lib/openbbBackend", () => ({
  resolveOpenBBBackend: () => resolveBackendMock(),
}));

vi.mock("../../lib/watchlistApi", () => ({
  fetchWatchlist: (...args: unknown[]) => fetchWatchlistMock(...args),
  fetchStockNews: (...args: unknown[]) => fetchStockNewsMock(...args),
  fetchMarketNews: (...args: unknown[]) => fetchMarketNewsMock(...args),
  fetchBatchQuotes: (...args: unknown[]) => fetchBatchQuotesMock(...args),
  updateWatchlist: (...args: unknown[]) => updateWatchlistMock(...args),
}));

vi.mock("../../components/finance/TradingViewWidgetEmbed", () => ({
  TradingViewWidgetEmbed: ({ symbol, title }: { symbol: string; title: string }) => (
    <div data-testid="watchlist-tradingview-widget" data-symbol={symbol}>
      {title}
    </div>
  ),
}));

describe("Watchlist Route", () => {
  const WatchlistComponent = WatchlistRoute.options.component as React.ComponentType;

  beforeEach(() => {
    resolveBackendMock.mockReset();
    fetchWatchlistMock.mockReset();
    fetchStockNewsMock.mockReset();
    fetchMarketNewsMock.mockReset();
    fetchBatchQuotesMock.mockReset();
    updateWatchlistMock.mockReset();

    resolveBackendMock.mockResolvedValue({
      connected: true,
      baseUrl: "http://127.0.0.1:6900",
      source: "stored-url",
      detail: "ok",
    });

    fetchWatchlistMock.mockResolvedValue({
      groups: [{ name: "Default Watchlist", tickers: ["NASDAQ:AAPL"] }],
    });
    fetchBatchQuotesMock.mockResolvedValue([
      {
        symbol: "NASDAQ:AAPL",
        last_price: 192.34,
        change: 1.23,
        change_percent: 0.64,
        volume: 123456,
        name: "Apple Inc.",
      },
    ]);
    fetchMarketNewsMock.mockResolvedValue({
      news_items: [
        {
          id: "market-1",
          title: "Fed outlook steadies risk appetite",
          summary: "Market headline",
          published_at: "2026-03-27T00:00:00Z",
          source: "Wire",
          url: "https://example.com/market-1",
          thumbnail: "",
          is_breaking: false,
        },
      ],
      total: 1,
    });
  });

  test("falls back to market headlines when symbol-specific news is empty", async () => {
    fetchStockNewsMock.mockResolvedValue({
      symbol: "AAPL",
      news_items: [],
      total: 0,
    });

    render(<WatchlistComponent />);

    await waitFor(() => {
      expect(screen.getByText(/Showing market headlines while symbol-specific news catches up\./i)).toBeInTheDocument();
    });

    expect(screen.getAllByText("Fed outlook steadies risk appetite")).toHaveLength(2);
    expect(screen.getByRole("link", { name: /Open in Finance Lab/i })).toBeInTheDocument();
    expect(screen.getByTestId("watchlist-tradingview-widget")).toHaveAttribute("data-symbol", "NASDAQ:AAPL");
  });

  test("renders symbol-specific watchlist news when the backend returns it", async () => {
    fetchStockNewsMock.mockResolvedValue({
      symbol: "AAPL",
      news_items: [
        {
          id: "stock-1",
          title: "Apple suppliers raise guidance",
          summary: "Symbol-specific headline",
          published_at: "2026-03-27T00:00:00Z",
          source: "Reuters",
          url: "https://example.com/stock-1",
          thumbnail: "",
          is_breaking: false,
        },
      ],
      total: 1,
    });

    render(<WatchlistComponent />);

    await waitFor(() => {
      expect(screen.getByText("Apple suppliers raise guidance")).toBeInTheDocument();
    });

    expect(
      screen.queryByText(/Showing market headlines while symbol-specific news catches up\./i),
    ).not.toBeInTheDocument();
  });
});
