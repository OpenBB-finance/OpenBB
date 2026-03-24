import type {
  FinanceFundamentalsTab,
  FinanceSymbolSuggestion,
  TradingViewFinancialLink,
  TradingViewFinanceWidgetType,
  TradingViewThemeMode,
  TradingViewWidgetConfig,
} from "../types/finance";

export const DEFAULT_FINANCE_SYMBOL = "NASDAQ:AAPL";
export const FINANCE_LATEST_SYMBOL_KEY = "finance.latestSymbol";
export const FINANCE_RECENT_SYMBOLS_KEY = "finance.recentSymbols";
export const FINANCE_RECENT_SYMBOL_LIMIT = 5;
export const TRADING_VIEW_WIDGET_TIMEOUT_MS = 8_000;
export const POPULAR_FINANCE_SYMBOLS = [
  "NASDAQ:AAPL",
  "NASDAQ:MSFT",
  "NASDAQ:NVDA",
  "NASDAQ:AMZN",
  "NASDAQ:GOOGL",
  "NASDAQ:META",
  "NASDAQ:TSLA",
  "NASDAQ:AVGO",
  "NASDAQ:AMD",
  "NYSE:JPM",
];

const WIDGET_SCRIPT_PATHS: Record<TradingViewFinanceWidgetType, string> = {
  "advanced-chart": "embed-widget-advanced-chart.js",
  "symbol-info": "embed-widget-symbol-info.js",
  "company-profile": "embed-widget-symbol-profile.js",
  "fundamental-data": "embed-widget-financials.js",
};

export function normalizeTradingViewSymbol(value: string | null | undefined): string {
  const trimmed = (value ?? "").trim();
  if (!trimmed) return "";
  return trimmed.includes(":") ? trimmed : trimmed.toUpperCase();
}

export function extractTickerFromSymbol(symbol: string): string {
  const normalized = normalizeTradingViewSymbol(symbol) || DEFAULT_FINANCE_SYMBOL;
  const parts = normalized.split(":");
  return (parts.at(-1) ?? normalized).trim().toUpperCase();
}

export function getTradingViewThemeMode(): TradingViewThemeMode {
  if (typeof document === "undefined") {
    return "dark";
  }
  return document.documentElement.classList.contains("dark") ? "dark" : "light";
}

export function buildTradingViewWidgetConfig(
  widgetType: TradingViewFinanceWidgetType,
  symbol: string,
  theme: TradingViewThemeMode,
  frameHeight?: number,
): TradingViewWidgetConfig {
  const normalizedSymbol = normalizeTradingViewSymbol(symbol) || DEFAULT_FINANCE_SYMBOL;
  const basePayload = {
    symbol: normalizedSymbol,
    locale: "en",
    isTransparent: true,
  };

  if (widgetType === "advanced-chart") {
    return {
      widgetType,
      symbol: normalizedSymbol,
      theme,
      scriptSrc: `https://s3.tradingview.com/external-embedding/${WIDGET_SCRIPT_PATHS[widgetType]}`,
      payload: {
        ...basePayload,
        width: "100%",
        height: frameHeight ?? 720,
        interval: "D",
        timezone: "Etc/UTC",
        theme,
        style: "1",
        allow_symbol_change: true,
        withdateranges: true,
        hide_side_toolbar: false,
        save_image: false,
        details: true,
        hotlist: false,
        calendar: false,
        support_host: "https://www.tradingview.com",
      },
    };
  }

  if (widgetType === "symbol-info") {
    return {
      widgetType,
      symbol: normalizedSymbol,
      theme,
      scriptSrc: `https://s3.tradingview.com/external-embedding/${WIDGET_SCRIPT_PATHS[widgetType]}`,
      payload: {
        ...basePayload,
        width: "100%",
        height: frameHeight ?? 190,
        colorTheme: theme,
      },
    };
  }

  if (widgetType === "company-profile") {
    return {
      widgetType,
      symbol: normalizedSymbol,
      theme,
      scriptSrc: `https://s3.tradingview.com/external-embedding/${WIDGET_SCRIPT_PATHS[widgetType]}`,
      payload: {
        ...basePayload,
        width: "100%",
        height: frameHeight ?? 320,
        colorTheme: theme,
      },
    };
  }

  return {
    widgetType,
    symbol: normalizedSymbol,
    theme,
    scriptSrc: `https://s3.tradingview.com/external-embedding/${WIDGET_SCRIPT_PATHS[widgetType]}`,
    payload: {
      ...basePayload,
      width: "100%",
      height: frameHeight ?? 920,
      colorTheme: theme,
      displayMode: "regular",
      largeChartUrl: "",
    },
  };
}

export function toTradingViewSymbolPath(symbol: string): string {
  const normalized = normalizeTradingViewSymbol(symbol) || DEFAULT_FINANCE_SYMBOL;
  return normalized.replace(":", "-");
}

export function buildTradingViewFinancialLinks(symbol: string): TradingViewFinancialLink[] {
  const symbolPath = toTradingViewSymbolPath(symbol);
  const base = `https://www.tradingview.com/symbols/${symbolPath}`;
  return [
    { label: "Overview", href: `${base}/financials-overview/` },
    { label: "Income Statement", href: `${base}/financials-income-statement/` },
    { label: "Balance Sheet", href: `${base}/financials-balance-sheet/` },
    { label: "Cash Flow", href: `${base}/financials-cash-flow/` },
  ];
}

export function buildTradingViewFinancialLink(
  symbol: string,
  tab: FinanceFundamentalsTab,
): TradingViewFinancialLink {
  const fallback = buildTradingViewFinancialLinks(symbol)[0];
  if (tab === "overview" || tab === "forecast") {
    return fallback;
  }

  const linksByTab: Record<
    Exclude<FinanceFundamentalsTab, "overview" | "forecast">,
    TradingViewFinancialLink
  > = {
    "income-statement": {
      label: "Open Income Statement in TradingView",
      href: buildTradingViewFinancialLinks(symbol)[1].href,
    },
    "balance-sheet": {
      label: "Open Balance Sheet in TradingView",
      href: buildTradingViewFinancialLinks(symbol)[2].href,
    },
    "cash-flow": {
      label: "Open Cash Flow in TradingView",
      href: buildTradingViewFinancialLinks(symbol)[3].href,
    },
  };

  return linksByTab[tab];
}

export function buildFinanceSymbolSuggestions(
  symbolInput: string,
  recentSymbols: string[],
  activeSymbol: string,
): FinanceSymbolSuggestion[] {
  const normalizedInput = normalizeTradingViewSymbol(symbolInput);
  const query = normalizedInput.toLowerCase();
  const candidates: FinanceSymbolSuggestion[] = [];
  const seen = new Set<string>();

  const push = (symbol: string, source: FinanceSymbolSuggestion["source"]) => {
    const normalized = normalizeTradingViewSymbol(symbol);
    if (!normalized || seen.has(normalized)) return;
    if (query && !normalized.toLowerCase().includes(query)) return;
    seen.add(normalized);
    candidates.push({ symbol: normalized, source });
  };

  push(activeSymbol, "active");
  for (const symbol of recentSymbols) push(symbol, "recent");
  for (const symbol of POPULAR_FINANCE_SYMBOLS) push(symbol, "popular");
  if (normalizedInput) push(normalizedInput, "typed");

  return candidates.slice(0, 8);
}

export function readRecentFinanceSymbols(): string[] {
  if (typeof localStorage === "undefined") return [];
  try {
    const raw = localStorage.getItem(FINANCE_RECENT_SYMBOLS_KEY);
    if (!raw) return [];
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed)
      ? parsed
          .map((item) => normalizeTradingViewSymbol(String(item)))
          .filter((item) => item.length > 0)
      : [];
  } catch {
    return [];
  }
}

export function writeRecentFinanceSymbols(symbols: string[]): void {
  if (typeof localStorage === "undefined") return;
  localStorage.setItem(
    FINANCE_RECENT_SYMBOLS_KEY,
    JSON.stringify(symbols.slice(0, FINANCE_RECENT_SYMBOL_LIMIT)),
  );
}

export function updateRecentFinanceSymbols(symbol: string): string[] {
  const normalized = normalizeTradingViewSymbol(symbol);
  if (!normalized) return readRecentFinanceSymbols();
  const next = [
    normalized,
    ...readRecentFinanceSymbols().filter((item) => item !== normalized),
  ].slice(0, FINANCE_RECENT_SYMBOL_LIMIT);
  writeRecentFinanceSymbols(next);
  return next;
}
