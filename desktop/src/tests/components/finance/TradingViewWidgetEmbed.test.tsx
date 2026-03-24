import { act, render, screen } from "@testing-library/react";
import { vi } from "vitest";
import { TradingViewWidgetEmbed } from "../../../components/finance/TradingViewWidgetEmbed";

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

  test("shows fallback message after timeout", () => {
    render(
      <TradingViewWidgetEmbed
        widgetType="fundamental-data"
        symbol="NASDAQ:AAPL"
        theme="dark"
        title="Fundamental Data"
      />,
    );

    act(() => {
      vi.advanceTimersByTime(8_000);
    });

    expect(
      screen.getByText(/TradingView widget failed to load\. Try another symbol or reload\./i),
    ).toBeInTheDocument();
  });
});
