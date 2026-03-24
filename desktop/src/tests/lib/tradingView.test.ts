import {
  buildTradingViewWidgetConfig,
  normalizeTradingViewSymbol,
} from "../../lib/tradingView";

describe("tradingView helpers", () => {
  test("normalizes TradingView symbols", () => {
    expect(normalizeTradingViewSymbol("NASDAQ:AAPL")).toBe("NASDAQ:AAPL");
    expect(normalizeTradingViewSymbol(" aapl ")).toBe("AAPL");
    expect(normalizeTradingViewSymbol(" msft ")).toBe("MSFT");
  });

  test("builds widget config with propagated symbol and theme", () => {
    expect(buildTradingViewWidgetConfig("advanced-chart", "NASDAQ:AAPL", "dark")).toMatchObject({
      widgetType: "advanced-chart",
      symbol: "NASDAQ:AAPL",
      theme: "dark",
    });
    expect(buildTradingViewWidgetConfig("advanced-chart", "NASDAQ:AAPL", "dark").payload).toMatchObject({
      allow_symbol_change: true,
    });
    expect(buildTradingViewWidgetConfig("fundamental-data", "NASDAQ:AAPL", "light")).toMatchObject({
      widgetType: "fundamental-data",
      symbol: "NASDAQ:AAPL",
      theme: "light",
    });
  });
});
