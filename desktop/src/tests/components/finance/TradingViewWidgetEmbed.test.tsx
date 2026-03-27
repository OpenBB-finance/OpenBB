import { act, fireEvent, render, screen } from "@testing-library/react";
import { vi } from "vitest";
import { TradingViewWidgetEmbed } from "../../../components/finance/TradingViewWidgetEmbed";
import { TRADING_VIEW_WIDGET_TIMEOUT_MS } from "../../../lib/tradingView";

describe("TradingViewWidgetEmbed", () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  test("mounts advanced chart widget script immediately", () => {
    const { container } = render(
      <TradingViewWidgetEmbed
        widgetType="advanced-chart"
        symbol="NASDAQ:AAPL"
        theme="dark"
        title="Advanced Chart"
      />,
    );

    const frame = container.querySelector('iframe[title="Advanced Chart"]');
    expect(frame).not.toBeNull();
    expect(frame?.getAttribute("srcdoc")).toContain("embed-widget-advanced-chart");
    expect(frame?.getAttribute("srcdoc")).toContain('"symbol":"NASDAQ:AAPL"');
    expect(frame?.getAttribute("srcdoc")).toContain('"theme":"dark"');
  });

  test("recreates widget when symbol changes", () => {
    const { container, rerender } = render(
      <TradingViewWidgetEmbed
        widgetType="advanced-chart"
        symbol="NASDAQ:AAPL"
        theme="dark"
        title="Advanced Chart"
      />,
    );

    rerender(
      <TradingViewWidgetEmbed
        widgetType="advanced-chart"
        symbol="NASDAQ:NVDA"
        theme="dark"
        title="Advanced Chart"
      />,
    );

    const frames = container.querySelectorAll('iframe[title="Advanced Chart"]');
    expect(frames).toHaveLength(1);
    expect(frames[0]?.getAttribute("srcdoc")).toContain('"symbol":"NASDAQ:NVDA"');
  });

  test("waits for intersection before mounting lazy widgets", () => {
    const { container } = render(
      <TradingViewWidgetEmbed
        widgetType="symbol-info"
        symbol="NASDAQ:AAPL"
        theme="light"
        title="Symbol Info"
        lazy
      />,
    );

    const frame = container.querySelector('iframe[title="Symbol Info"]');
    expect(frame).not.toBeNull();
    expect(frame?.getAttribute("srcdoc")).toBeNull();

    const observer = (
      IntersectionObserver as unknown as {
        mock: { instances: Array<{ callback: IntersectionObserverCallback }> };
      }
    ).mock.instances[0];

    act(() => {
      observer.callback(
        [{ isIntersecting: true } as IntersectionObserverEntry],
        observer as unknown as IntersectionObserver,
      );
    });

    expect(container.querySelector('iframe[title="Symbol Info"]')?.getAttribute("srcdoc")).toContain(
      "embed-widget-symbol-info",
    );
  });

  test("shows fallback message after retry budget is exhausted", () => {
    render(
      <TradingViewWidgetEmbed
        widgetType="fundamental-data"
        symbol="NASDAQ:AAPL"
        theme="dark"
        title="Fundamental Data"
      />,
    );

    act(() => {
      vi.advanceTimersByTime(TRADING_VIEW_WIDGET_TIMEOUT_MS);
    });

    expect(
      screen.queryByText(/TradingView widget failed to load\. Try another symbol or reload\./i),
    ).not.toBeInTheDocument();

    act(() => {
      vi.advanceTimersByTime(TRADING_VIEW_WIDGET_TIMEOUT_MS);
    });

    expect(
      screen.getByText(/TradingView widget failed to load\. Try another symbol or reload\./i),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Retry widget/i })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Open in TradingView/i })).toBeInTheDocument();
  });

  test("allows a timed-out widget to be retried", () => {
    const { container } = render(
      <TradingViewWidgetEmbed
        widgetType="fundamental-data"
        symbol="NASDAQ:AAPL"
        theme="dark"
        title="Fundamental Data"
      />,
    );

    act(() => {
      vi.advanceTimersByTime(TRADING_VIEW_WIDGET_TIMEOUT_MS);
    });

    act(() => {
      vi.advanceTimersByTime(TRADING_VIEW_WIDGET_TIMEOUT_MS);
    });

    fireEvent.click(screen.getByRole("button", { name: /Retry widget/i }));

    expect(
      screen.queryByText(/TradingView widget failed to load\. Try another symbol or reload\./i),
    ).not.toBeInTheDocument();
    expect(container.querySelector('iframe[title="Fundamental Data"]')?.getAttribute("srcdoc")).toContain(
      "embed-widget-financials",
    );
  });
});
