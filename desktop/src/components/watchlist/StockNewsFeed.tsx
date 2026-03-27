import { useMemo } from "react";
import { NewsItemCard } from "./NewsItemCard";
import type { NewsItem, QuoteRecord } from "../../lib/watchlistApi";

interface StockNewsFeedProps {
  symbol: string;
  symbolTicker?: string;
  quote: QuoteRecord | null;
  news: NewsItem[];
  isLoading: boolean;
  error: string | null;
  isUsingMarketFallback?: boolean;
}

function formatDate(isoDate: string): string {
  try {
    return new Date(isoDate).toLocaleDateString("en-US", {
      weekday: "long",
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  } catch {
    return isoDate;
  }
}

function groupByDate(items: NewsItem[]): Array<{ date: string; items: NewsItem[] }> {
  const grouped = new Map<string, NewsItem[]>();
  for (const item of items) {
    const dateKey = formatDate(item.published_at);
    const existing = grouped.get(dateKey) ?? [];
    existing.push(item);
    grouped.set(dateKey, existing);
  }
  return Array.from(grouped.entries()).map(([date, groupedItems]) => ({
    date,
    items: groupedItems,
  }));
}

function formatPrice(value: number | null): string {
  if (value === null || value === undefined) return "-";
  return value.toLocaleString("en-US", { style: "currency", currency: "USD" });
}

function formatPct(value: number | null): string {
  if (value === null || value === undefined) return "";
  const sign = value >= 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
}

export function StockNewsFeed({
  symbol,
  symbolTicker,
  quote,
  news,
  isLoading,
  error,
  isUsingMarketFallback = false,
}: StockNewsFeedProps) {
  const groupedNews = useMemo(() => groupByDate(news), [news]);
  const isPositive = (quote?.change_percent ?? 0) >= 0;
  const newsLabel = symbolTicker || symbol;

  return (
    <div className="flex h-full flex-col rounded-sm border border-theme-outline bg-theme-primary">
      <div className="flex items-center justify-between border-b border-theme-outline px-4 py-3">
        <h2 className="body-sm-medium text-theme-muted tracking-wider uppercase">Watchlist News</h2>
        <a
          href={`/finance?symbol=${encodeURIComponent(symbol)}`}
          className="body-xxs-medium text-blue-400 hover:text-blue-300"
        >
          Open in Finance Lab
        </a>
      </div>

      <div className="flex items-center gap-3 border-b border-theme-outline px-4 py-3">
        <span className="body-lg-medium text-theme-primary">{symbol}</span>
        <span className="body-sm-medium text-theme-primary">{formatPrice(quote?.last_price ?? null)}</span>
        <span
          className={`rounded-sm px-2 py-0.5 body-xs-medium ${
            isPositive ? "bg-emerald-500/15 text-emerald-400" : "bg-red-500/15 text-red-400"
          }`}
        >
          {formatPct(quote?.change_percent ?? null)}
        </span>
      </div>

      <div className="flex-1 overflow-auto px-1 py-2">
        {error && news.length === 0 ? (
          <div className="px-3 py-6 text-center">
            <p className="body-xs-medium text-red-400">{error}</p>
          </div>
        ) : isLoading && news.length === 0 ? (
          <div className="px-3 py-6 text-center">
            <p className="body-xs-medium text-theme-muted">Loading news for {newsLabel}...</p>
          </div>
        ) : news.length === 0 ? (
          <div className="px-3 py-6 text-center">
            <p className="body-xs-medium text-theme-muted">No recent news found for {newsLabel}.</p>
          </div>
        ) : (
          <div className="space-y-1">
            {isUsingMarketFallback ? (
              <div className="mx-3 rounded-sm border border-amber-500/30 bg-amber-500/10 px-3 py-2">
                <p className="body-xxs-medium text-amber-300">
                  Showing market headlines while symbol-specific news catches up.
                </p>
              </div>
            ) : null}
            {error ? (
              <div className="mx-3 rounded-sm border border-red-500/30 bg-red-500/10 px-3 py-2">
                <p className="body-xxs-medium text-red-300">{error}</p>
              </div>
            ) : null}
            {groupedNews.map((group) => (
              <div key={group.date}>
                <div className="sticky top-0 z-10 bg-theme-primary px-3 py-2">
                  <p className="body-xxs-medium text-theme-muted">{group.date}</p>
                  <div className="mt-1 h-px bg-theme-outline" />
                </div>
                <div className="space-y-0.5">
                  {group.items.map((item) => (
                    <NewsItemCard key={item.id || `${item.url}-${item.published_at}`} item={item} />
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="border-t border-theme-outline px-4 py-3">
        <div className="flex items-center gap-2 rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2">
          <span className="text-theme-muted">AI</span>
          <input
            type="text"
            placeholder="Ask your agent anything..."
            className="flex-1 bg-transparent body-xs-regular text-theme-primary outline-none placeholder:text-theme-muted"
            onKeyDown={(event) => {
              if (event.key !== "Enter") {
                return;
              }
              const query = (event.target as HTMLInputElement).value.trim();
              if (query) {
                window.location.href = `/ai?symbol=${encodeURIComponent(symbol)}&query=${encodeURIComponent(query)}`;
              }
            }}
          />
        </div>
        <div className="mt-2 flex items-center gap-3">
          <span className="body-xxs-regular text-theme-muted">
            Agent: <span className="text-blue-400">/Deep Research</span>
          </span>
          <span className="body-xxs-regular text-theme-muted">Auto Sources On</span>
        </div>
      </div>
    </div>
  );
}
