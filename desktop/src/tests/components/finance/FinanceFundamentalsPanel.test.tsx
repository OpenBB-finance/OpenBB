import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, test, vi } from "vitest";
import { FinanceFundamentalsPanel } from "../../../components/finance/FinanceFundamentalsPanel";
import { clearFinanceStatementCache } from "../../../lib/financeApi";

vi.mock("../../../components/finance/TradingViewWidgetEmbed", () => ({
  TradingViewWidgetEmbed: ({ widgetType, symbol }: { widgetType: string; symbol: string }) => (
    <div data-testid={`tv-${widgetType}`} data-symbol={symbol}>
      {widgetType}
    </div>
  ),
}));

vi.mock("../../../lib/openbbBackend", () => ({
  resolveOpenBBBackend: vi.fn(async () => ({
    baseUrl: "http://127.0.0.1:6900",
    connected: true,
    detail: "ok",
    source: "fallback",
  })),
}));

function buildEnvelope(results: Array<Record<string, unknown>>) {
  return {
    provider: "yfinance",
    results,
    extra: {
      metadata: {
        timestamp: "2026-03-22T01:02:03Z",
      },
    },
  };
}

describe("FinanceFundamentalsPanel", () => {
  beforeEach(() => {
    vi.restoreAllMocks();
    clearFinanceStatementCache();
  });

  test("shows TradingView overview by default", async () => {
    const fetchMock = vi.spyOn(global, "fetch").mockResolvedValue({
      ok: true,
      json: async () => buildEnvelope([{ period_ending: "2025-09-30", total_revenue: 416161000000 }]),
    } as Response);

    render(
      <FinanceFundamentalsPanel
        symbol="NASDAQ:AAPL"
        theme="dark"
        overviewHeight={920}
      />,
    );

    expect(screen.getByTestId("tv-fundamental-data")).toHaveAttribute("data-symbol", "NASDAQ:AAPL");
    expect(screen.getByRole("button", { name: "I/S" })).toBeInTheDocument();

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledTimes(4);
    });
  });

  test("renders inline income statement rows", async () => {
    vi.spyOn(global, "fetch").mockImplementation(async (input) => {
      const url = String(input);
      if (url.includes("/consensus")) {
        return {
          ok: true,
          json: async () =>
            buildEnvelope([
              {
                symbol: "AAPL",
                target_consensus: 295.43,
                target_low: 205,
                target_high: 350,
                current_price: 247.99,
                number_of_analysts: 41,
              },
            ]),
        } as Response;
      }
      if (url.includes("/income")) {
        return {
          ok: true,
          json: async () =>
            buildEnvelope([
              {
                period_ending: "2025-09-30",
                total_revenue: 416161000000,
                gross_profit: 195201000000,
                net_income: 112010000000,
              },
              {
                period_ending: "2024-09-30",
                total_revenue: 391035000000,
                gross_profit: 180683000000,
                net_income: 93736000000,
              },
            ]),
        } as Response;
      }

      return {
        ok: true,
        json: async () => buildEnvelope([{ period_ending: "2025-09-30", operating_cash_flow: 135470000000 }]),
      } as Response;
    });

    render(
      <FinanceFundamentalsPanel
        symbol="NASDAQ:AAPL"
        theme="dark"
        overviewHeight={920}
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: "I/S" }));

    await waitFor(() => {
      expect(screen.getByText("Revenue")).toBeInTheDocument();
    });

    expect(screen.getAllByText("416.16B").length).toBeGreaterThan(0);
    expect(screen.getAllByText("2025-09-30").length).toBeGreaterThan(0);
    expect(screen.getByRole("link", { name: /Open in TradingView/i })).toBeInTheDocument();
  });

  test("switches to quarterly statement mode", async () => {
    const fetchMock = vi.spyOn(global, "fetch").mockImplementation(async (input) => {
      const url = String(input);
      if (url.includes("/consensus")) {
        return {
          ok: true,
          json: async () =>
            buildEnvelope([
              {
                symbol: "AAPL",
                target_consensus: 295.43,
                target_low: 205,
                target_high: 350,
                current_price: 247.99,
                number_of_analysts: 41,
              },
            ]),
        } as Response;
      }
      return {
        ok: true,
        json: async () =>
          buildEnvelope([
            {
              period_ending: url.includes("period=quarter") ? "2025-12-31" : "2025-09-30",
              total_assets: 364980000000,
              stockholders_equity: 73753000000,
            },
          ]),
      } as Response;
    });

    render(
      <FinanceFundamentalsPanel
        symbol="NASDAQ:AAPL"
        theme="dark"
        overviewHeight={920}
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: "B/S" }));

    await waitFor(() => {
      expect(screen.getAllByText("Total Assets").length).toBeGreaterThan(0);
    });

    fireEvent.click(screen.getByRole("button", { name: "Quarterly" }));

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("period=quarter"),
        expect.any(Object),
      );
    });
  });

  test("renders forecast snapshot inline", async () => {
    vi.spyOn(global, "fetch").mockImplementation(async (input) => {
      const url = String(input);
      if (url.includes("/consensus")) {
        return {
          ok: true,
          json: async () => ({
            provider: "yfinance",
            results: [
              {
                symbol: "AAPL",
                target_consensus: 295.43,
                target_low: 205,
                target_high: 350,
                target_median: 300,
                current_price: 247.99,
                number_of_analysts: 41,
                recommendation: "buy",
                recommendation_mean: 1.9,
                currency: "USD",
              },
            ],
            extra: { metadata: { timestamp: "2026-03-22T01:02:03Z" } },
          }),
        } as Response;
      }
      return {
        ok: true,
        json: async () => buildEnvelope([{ period_ending: "2025-09-30", total_revenue: 416161000000 }]),
      } as Response;
    });

    render(
      <FinanceFundamentalsPanel
        symbol="NASDAQ:AAPL"
        theme="dark"
        overviewHeight={920}
      />,
    );

    fireEvent.click(screen.getByRole("button", { name: "Forecast" }));

    await waitFor(() => {
      expect(screen.getByText("Consensus Target")).toBeInTheDocument();
    });

    expect(screen.getAllByText("$295.43").length).toBeGreaterThan(0);
    expect(screen.getByText("Implied Upside")).toBeInTheDocument();
    expect(screen.getByText("BUY")).toBeInTheDocument();
  });
});
