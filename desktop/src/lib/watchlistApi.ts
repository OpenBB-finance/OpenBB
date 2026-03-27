import { buildOpenBBRequestInit, buildOpenBBRequestUrl } from "./openbbBackend";
import { extractTickerFromSymbol } from "./tradingView";

function asNewsItems(payload: unknown): NewsItem[] {
  if (payload && typeof payload === "object") {
    const record = payload as { news_items?: unknown; results?: unknown };
    if (Array.isArray(record.news_items)) {
      return record.news_items as NewsItem[];
    }
    if (Array.isArray(record.results)) {
      return record.results as NewsItem[];
    }
  }
  return [];
}

// ---------------------------------------------------------------------------
// Watchlist
// ---------------------------------------------------------------------------

export interface WatchlistGroup {
  name: string;
  tickers: string[];
}

export interface WatchlistPayload {
  groups: WatchlistGroup[];
}

export async function fetchWatchlist(baseUrl: string): Promise<WatchlistPayload> {
  const res = await fetch(
    buildOpenBBRequestUrl(baseUrl, "/api/v1/quant_ml/finance/watchlist"),
    buildOpenBBRequestInit({ method: "GET" }),
  );
  if (!res.ok) throw new Error(`Watchlist fetch failed (${res.status})`);
  return (await res.json()) as WatchlistPayload;
}

export async function updateWatchlist(
  baseUrl: string,
  params: {
    action: string;
    group_name?: string;
    symbol?: string;
    ordered_symbols?: string;
  },
): Promise<WatchlistPayload> {
  const query = new URLSearchParams({ action: params.action });
  if (params.group_name) query.set("group_name", params.group_name);
  if (params.symbol) query.set("symbol", params.symbol);
  if (params.ordered_symbols) query.set("ordered_symbols", params.ordered_symbols);

  const res = await fetch(
    buildOpenBBRequestUrl(baseUrl, `/api/v1/quant_ml/finance/watchlist?${query.toString()}`),
    buildOpenBBRequestInit({ method: "POST" }),
  );
  if (!res.ok) throw new Error(`Watchlist update failed (${res.status})`);
  return (await res.json()) as WatchlistPayload;
}

// ---------------------------------------------------------------------------
// Stock News
// ---------------------------------------------------------------------------

export interface NewsItem {
  id: string;
  title: string;
  summary: string;
  published_at: string;
  source: string;
  url: string;
  thumbnail: string;
  is_breaking: boolean;
}

export interface StockNewsPayload {
  symbol: string;
  news_items: NewsItem[];
  total: number;
  error?: string;
}

export async function fetchStockNews(
  baseUrl: string,
  symbol: string,
  days = 7,
  limit = 30,
  signal?: AbortSignal,
): Promise<StockNewsPayload> {
  const ticker = extractTickerFromSymbol(symbol);
  const query = new URLSearchParams({
    symbol: ticker,
    days: String(days),
    limit: String(limit),
  });
  const res = await fetch(
    buildOpenBBRequestUrl(baseUrl, `/api/v1/quant_ml/finance/news?${query.toString()}`),
    buildOpenBBRequestInit({ method: "GET", signal }),
  );
  if (!res.ok) throw new Error(`Stock news fetch failed (${res.status})`);
  const payload = (await res.json()) as Record<string, unknown>;
  const newsItems = asNewsItems(payload);
  return {
    symbol: typeof payload.symbol === "string" ? payload.symbol : ticker,
    news_items: newsItems,
    total: typeof payload.total === "number" ? payload.total : newsItems.length,
    error: typeof payload.error === "string" ? payload.error : undefined,
  };
}

export interface MarketNewsPayload {
  news_items: NewsItem[];
  total: number;
  error?: string;
}

export async function fetchMarketNews(
  baseUrl: string,
  limit = 20,
  signal?: AbortSignal,
): Promise<MarketNewsPayload> {
  const query = new URLSearchParams({ limit: String(limit) });
  const res = await fetch(
    buildOpenBBRequestUrl(baseUrl, `/api/v1/quant_ml/finance/market_news?${query.toString()}`),
    buildOpenBBRequestInit({ method: "GET", signal }),
  );
  if (!res.ok) throw new Error(`Market news fetch failed (${res.status})`);
  const payload = (await res.json()) as Record<string, unknown>;
  const newsItems = asNewsItems(payload);
  return {
    news_items: newsItems,
    total: typeof payload.total === "number" ? payload.total : newsItems.length,
    error: typeof payload.error === "string" ? payload.error : undefined,
  };
}

// ---------------------------------------------------------------------------
// Batch Quotes (uses OpenBB Core equity price quote)
// ---------------------------------------------------------------------------

export interface QuoteRecord {
  symbol: string;
  last_price: number | null;
  change: number | null;
  change_percent: number | null;
  volume: number | null;
  name: string;
}

export async function fetchBatchQuotes(
  baseUrl: string,
  symbols: string[],
  signal?: AbortSignal,
): Promise<QuoteRecord[]> {
  if (symbols.length === 0) return [];
  const aliasesByTicker = new Map<string, string[]>();
  for (const symbol of symbols) {
    const ticker = extractTickerFromSymbol(symbol);
    if (!ticker) continue;
    const aliases = aliasesByTicker.get(ticker) ?? [];
    aliases.push(symbol);
    aliasesByTicker.set(ticker, aliases);
  }
  const tickers = Array.from(aliasesByTicker.keys());
  if (tickers.length === 0) return [];
  const query = new URLSearchParams({
    symbol: tickers.join(","),
    provider: "yfinance",
  });
  const res = await fetch(
    buildOpenBBRequestUrl(baseUrl, `/api/v1/equity/price/quote?${query.toString()}`),
    buildOpenBBRequestInit({ method: "GET", signal }),
  );
  if (!res.ok) return [];

  const envelope = (await res.json()) as { results?: Record<string, unknown>[] };
  const results = Array.isArray(envelope.results) ? envelope.results : [];
  return results.flatMap((r) => {
    const ticker = String(r.symbol ?? "").trim().toUpperCase();
    const aliases = aliasesByTicker.get(ticker) ?? [ticker];
    const quote = {
      last_price: typeof r.last_price === "number" ? r.last_price : null,
      change: typeof r.change === "number" ? r.change : null,
      change_percent: typeof r.change_percent === "number" ? r.change_percent : null,
      volume: typeof r.volume === "number" ? r.volume : null,
      name: String(r.name ?? r.short_name ?? ""),
    };
    return aliases.map((alias) => ({
      symbol: alias,
      ...quote,
    }));
  });
}
