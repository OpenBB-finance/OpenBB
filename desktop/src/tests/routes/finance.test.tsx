/// <reference types="vitest/globals" />
import { fireEvent, render, screen } from "@testing-library/react";
import React from "react";
import { vi } from "vitest";
import { Route as FinanceRoute } from "../../routes/finance";

vi.mock("@tanstack/react-router", () => ({
  createFileRoute: vi.fn(() => (options: {
    component: React.ComponentType;
    validateSearch?: (search: Record<string, unknown>) => Record<string, unknown>;
  }) => ({
    options: {
      component: options.component,
      validateSearch: options.validateSearch,
    },
  })),
}));

vi.mock("../../components/finance/TradingViewWidgetEmbed", () => ({
  TradingViewWidgetEmbed: ({
    widgetType,
    symbol,
    theme,
  }: {
    widgetType: string;
    symbol: string;
    theme: string;
  }) => (
    <div data-testid={`tv-${widgetType}`} data-symbol={symbol} data-theme={theme}>
      {widgetType}
    </div>
  ),
}));

vi.mock("../../components/finance/FinanceFundamentalsPanel", () => ({
  FinanceFundamentalsPanel: ({ symbol }: { symbol: string }) => (
    <div data-testid="finance-fundamentals-panel" data-symbol={symbol}>
      <h2>Fundamental Data</h2>
      <button type="button">Overview</button>
      <button type="button">Forecast</button>
      <button type="button">I/S</button>
      <button type="button">B/S</button>
      <button type="button">C/F</button>
    </div>
  ),
}));

describe("Finance Route", () => {
  const FinanceComponent = FinanceRoute.options.component as React.ComponentType;

  beforeEach(() => {
    window.history.replaceState({}, "", "/finance");
    localStorage.clear();
    document.documentElement.classList.add("dark");
  });

  test("renders finance route smoke view", () => {
    render(<FinanceComponent />);

    expect(screen.getByText("Finance")).toBeInTheDocument();
    expect(
      screen.getByText(/TradingView-backed chart and company fundamentals\./i),
    ).toBeInTheDocument();
    expect(screen.getByLabelText(/Ticker \/ TV Symbol/i)).toHaveValue("NASDAQ:AAPL");
    expect(screen.getByLabelText(/Chart Symbol Search/i)).toHaveValue("NASDAQ:AAPL");
    expect(screen.getByRole("heading", { name: "Finance Controls" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Advanced Chart" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Symbol Info" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Company Profile" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Fundamental Data" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Forecast" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "I/S" })).toBeInTheDocument();
    expect(screen.getByTestId("tv-advanced-chart")).toHaveAttribute("data-symbol", "NASDAQ:AAPL");
    expect(screen.getByTestId("finance-fundamentals-panel")).toHaveAttribute("data-symbol", "NASDAQ:AAPL");
  });

  test("prefers URL search symbol over localStorage", () => {
    localStorage.setItem("finance.latestSymbol", "NASDAQ:NVDA");
    window.history.replaceState({}, "", "/finance?symbol=NASDAQ:MSFT");

    render(<FinanceComponent />);

    expect(screen.getByLabelText(/Ticker \/ TV Symbol/i)).toHaveValue("NASDAQ:MSFT");
  });

  test("falls back to localStorage symbol", () => {
    localStorage.setItem("finance.latestSymbol", "NASDAQ:NVDA");

    render(<FinanceComponent />);

    expect(screen.getByLabelText(/Ticker \/ TV Symbol/i)).toHaveValue("NASDAQ:NVDA");
  });

  test("submits a symbol, updates widgets, recent symbols, and URL", () => {
    render(<FinanceComponent />);

    fireEvent.change(screen.getByLabelText(/Ticker \/ TV Symbol/i), {
      target: { value: "nvda" },
    });
    fireEvent.click(screen.getByRole("button", { name: /Load/i }));

    expect(screen.getByLabelText(/Ticker \/ TV Symbol/i)).toHaveValue("NVDA");
    expect(localStorage.getItem("finance.latestSymbol")).toBe("NVDA");
    expect(window.location.search).toContain("symbol=NVDA");
    expect(screen.getByRole("button", { name: "NVDA" })).toBeInTheDocument();
    expect(screen.getByTestId("tv-advanced-chart")).toHaveAttribute("data-symbol", "NVDA");
  });

  test("shows suggestions on input focus and applies a selected symbol", () => {
    render(<FinanceComponent />);

    fireEvent.click(screen.getByLabelText(/Ticker \/ TV Symbol/i));
    fireEvent.change(screen.getByLabelText(/Ticker \/ TV Symbol/i), {
      target: { value: "msft" },
    });

    expect(screen.getByRole("button", { name: /NASDAQ:MSFT/i })).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: /NASDAQ:MSFT/i }));

    expect(screen.getByLabelText(/Ticker \/ TV Symbol/i)).toHaveValue("NASDAQ:MSFT");
    expect(screen.getByLabelText(/Chart Symbol Search/i)).toHaveValue("NASDAQ:MSFT");
    expect(screen.getByTestId("tv-advanced-chart")).toHaveAttribute("data-symbol", "NASDAQ:MSFT");
  });
});
