import { createFileRoute } from "@tanstack/react-router";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { PortfolioSidebar } from "../components/watchlist/PortfolioSidebar";
import { StockNewsFeed } from "../components/watchlist/StockNewsFeed";
import { MarketLivePanel } from "../components/watchlist/MarketLivePanel";
import { resolveOpenBBBackend } from "../lib/openbbBackend";
import { extractTickerFromSymbol, getTradingViewThemeMode, normalizeTradingViewSymbol } from "../lib/tradingView";
import {
  fetchWatchlist,
  fetchStockNews,
  fetchMarketNews,
  fetchBatchQuotes,
  updateWatchlist,
  type WatchlistGroup,
  type QuoteRecord,
  type NewsItem,
} from "../lib/watchlistApi";
import type { TradingViewThemeMode } from "../types/finance";

function WatchlistPage() {
  // --- Core state ---
  const [baseUrl, setBaseUrl] = useState("");
  const [theme, setTheme] = useState<TradingViewThemeMode>(() => getTradingViewThemeMode());

  // --- Watchlist ---
  const [groups, setGroups] = useState<WatchlistGroup[]>([]);
  const [quotes, setQuotes] = useState<Map<string, QuoteRecord>>(new Map());
  const [activeSymbol, setActiveSymbol] = useState("IBM");

  // --- News ---
  const [stockNews, setStockNews] = useState<NewsItem[]>([]);
  const [stockNewsLoading, setStockNewsLoading] = useState(false);
  const [stockNewsError, setStockNewsError] = useState<string | null>(null);
  const [marketNews, setMarketNews] = useState<NewsItem[]>([]);
  const [marketNewsLoading, setMarketNewsLoading] = useState(false);
  const [marketNewsError, setMarketNewsError] = useState<string | null>(null);

  const quoteTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const marketTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const stockNewsTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // --- Theme observer ---
  useEffect(() => {
    const root = document.documentElement;
    const observer = new MutationObserver(() => setTheme(getTradingViewThemeMode()));
    observer.observe(root, { attributes: true, attributeFilter: ["class", "data-theme"] });
    return () => observer.disconnect();
  }, []);

  // --- Backend connection ---
  useEffect(() => {
    const load = async () => {
      try {
        const backend = await resolveOpenBBBackend();
        if (backend.connected) setBaseUrl(backend.baseUrl);
      } catch {
        setBaseUrl("");
      }
    };
    void load();
  }, []);

  // --- Load watchlist ---
  useEffect(() => {
    if (!baseUrl) return;
    const load = async () => {
      try {
        const data = await fetchWatchlist(baseUrl);
        setGroups(data.groups);
        // Auto-select first ticker if none
        if (data.groups.length > 0 && data.groups[0].tickers.length > 0) {
          setActiveSymbol((prev) => {
            const allTickers = data.groups.flatMap((g) => g.tickers);
            return allTickers.includes(prev) ? prev : allTickers[0];
          });
        }
      } catch {
        // Use defaults
        setGroups([
          { name: "Default Watchlist", tickers: ["NFLX", "AAPL", "GOOGL", "TSLA", "NVDA", "IBM", "INTC", "XOM", "AMZN", "AMD", "META"] },
        ]);
      }
    };
    void load();
  }, [baseUrl]);

  // --- Batch quotes (30s refresh, visibility-aware) ---
  const loadQuotes = useCallback(async () => {
    if (!baseUrl) return;
    const allTickers = groups.flatMap((g) => g.tickers);
    if (allTickers.length === 0) return;
    try {
      const results = await fetchBatchQuotes(baseUrl, allTickers);
      const next = new Map<string, QuoteRecord>();
      for (const r of results) next.set(r.symbol, r);
      setQuotes(next);
    } catch {
      // quiet fail
    }
  }, [baseUrl, groups]);

  useEffect(() => {
    void loadQuotes();
    if (quoteTimerRef.current) clearInterval(quoteTimerRef.current);
    quoteTimerRef.current = setInterval(() => {
      if (document.visibilityState === "visible") void loadQuotes();
    }, 30_000);
    return () => {
      if (quoteTimerRef.current) clearInterval(quoteTimerRef.current);
    };
  }, [loadQuotes]);

  // --- Stock news ---
  const loadStockNews = useCallback(
    async (signal?: AbortSignal) => {
      if (!baseUrl || !activeSymbol) return;
      setStockNewsLoading(true);
      setStockNewsError(null);
      try {
        const data = await fetchStockNews(baseUrl, activeSymbol, 7, 30, signal);
        setStockNews(data.news_items);
        if (data.error) {
          setStockNewsError(data.error);
        }
      } catch (err) {
        if (!signal?.aborted) {
          setStockNews([]);
          setStockNewsError(err instanceof Error ? err.message : "Failed to load news");
        }
      } finally {
        if (!signal?.aborted) {
          setStockNewsLoading(false);
        }
      }
    },
    [activeSymbol, baseUrl],
  );

  useEffect(() => {
    if (!baseUrl || !activeSymbol) return;
    const controller = new AbortController();
    void loadStockNews(controller.signal);
    if (stockNewsTimerRef.current) clearInterval(stockNewsTimerRef.current);
    stockNewsTimerRef.current = setInterval(() => {
      if (document.visibilityState === "visible") {
        const nextController = new AbortController();
        void loadStockNews(nextController.signal);
      }
    }, 180_000);
    return () => {
      controller.abort();
      if (stockNewsTimerRef.current) clearInterval(stockNewsTimerRef.current);
    };
  }, [activeSymbol, baseUrl, loadStockNews]);

  // --- Market news (5min refresh) ---
  const loadMarketNews = useCallback(async () => {
    if (!baseUrl) return;
    setMarketNewsLoading(true);
    setMarketNewsError(null);
    try {
      const data = await fetchMarketNews(baseUrl, 30);
      setMarketNews(data.news_items);
      if (data.error) setMarketNewsError(data.error);
    } catch {
      setMarketNews([]);
      setMarketNewsError("Failed to load market headlines.");
    } finally {
      setMarketNewsLoading(false);
    }
  }, [baseUrl]);

  useEffect(() => {
    void loadMarketNews();
    if (marketTimerRef.current) clearInterval(marketTimerRef.current);
    marketTimerRef.current = setInterval(() => {
      if (document.visibilityState === "visible") void loadMarketNews();
    }, 300_000);
    return () => {
      if (marketTimerRef.current) clearInterval(marketTimerRef.current);
    };
  }, [loadMarketNews]);

  // --- Watchlist mutations ---
  const handleAddTicker = useCallback(
    async (groupName: string, symbol: string) => {
      if (!baseUrl) return;
      try {
        const updated = await updateWatchlist(baseUrl, { action: "add_ticker", group_name: groupName, symbol });
        setGroups(updated.groups);
      } catch {
        // quiet fail
      }
    },
    [baseUrl],
  );

  const handleRemoveTicker = useCallback(
    async (groupName: string, symbol: string) => {
      if (!baseUrl) return;
      try {
        const updated = await updateWatchlist(baseUrl, { action: "remove_ticker", group_name: groupName, symbol });
        setGroups(updated.groups);
      } catch {
        // quiet fail
      }
    },
    [baseUrl],
  );

  const handleAddGroup = useCallback(
    async (name: string) => {
      if (!baseUrl) return;
      try {
        const updated = await updateWatchlist(baseUrl, { action: "add_group", group_name: name });
        setGroups(updated.groups);
      } catch {
        // quiet fail
      }
    },
    [baseUrl],
  );

  const activeQuote = quotes.get(activeSymbol) ?? null;
  const activeChartSymbol = useMemo(() => normalizeTradingViewSymbol(activeSymbol) || "AAPL", [activeSymbol]);
  const stockNewsFallback = useMemo(
    () => stockNews.length === 0 && marketNews.length > 0,
    [marketNews.length, stockNews.length],
  );
  const displayedNews = stockNewsFallback ? marketNews : stockNews;
  const activeTicker = useMemo(() => extractTickerFromSymbol(activeSymbol), [activeSymbol]);

  return (
    <div className="h-full min-h-0 overflow-hidden py-2">
      <div className="grid h-full grid-cols-[260px_minmax(0,1fr)_360px] gap-3">
        {/* Left: Portfolio Watchlist */}
        <PortfolioSidebar
          groups={groups}
          quotes={quotes}
          activeSymbol={activeSymbol}
          onSelectSymbol={setActiveSymbol}
          onAddTicker={handleAddTicker}
          onRemoveTicker={handleRemoveTicker}
          onAddGroup={handleAddGroup}
        />

        {/* Center: Stock News Feed */}
        <StockNewsFeed
          symbol={activeSymbol}
          symbolTicker={activeTicker}
          quote={activeQuote}
          news={displayedNews}
          isLoading={stockNewsLoading}
          error={stockNewsError}
          isUsingMarketFallback={stockNewsFallback}
        />

        {/* Right: Market Live */}
        <MarketLivePanel
          symbol={activeChartSymbol}
          quote={activeQuote}
          marketNews={marketNews}
          marketNewsLoading={marketNewsLoading}
          marketNewsError={marketNewsError}
          theme={theme}
        />
      </div>
    </div>
  );
}

export const Route = createFileRoute("/watchlist")({
  component: WatchlistPage,
});
