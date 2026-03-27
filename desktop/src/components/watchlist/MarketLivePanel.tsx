import { useMemo } from "react";
import { TradingViewWidgetEmbed } from "../finance/TradingViewWidgetEmbed";
import { NewsItemCard } from "./NewsItemCard";
import type { NewsItem, QuoteRecord } from "../../lib/watchlistApi";
import type { TradingViewThemeMode } from "../../types/finance";

interface MarketLivePanelProps {
  symbol: string;
  quote: QuoteRecord | null;
  marketNews: NewsItem[];
  marketNewsLoading: boolean;
  marketNewsError?: string | null;
  theme: TradingViewThemeMode;
}

function formatNum(value: number | null, digits = 2): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "-";
  return value.toFixed(digits);
}

function formatVol(value: number | null): string {
  if (value === null || value === undefined) return "-";
  if (value >= 1_000_000) return `${(value / 1_000_000).toFixed(2)}M`;
  if (value >= 1_000) return `${(value / 1_000).toFixed(1)}K`;
  return String(value);
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
  return Array.from(grouped.entries()).map(([date, groupedItems]) => ({ date, items: groupedItems }));
}

export function MarketLivePanel({
  symbol,
  quote,
  marketNews,
  marketNewsLoading,
  marketNewsError = null,
  theme,
}: MarketLivePanelProps) {
  const groupedNews = useMemo(() => groupByDate(marketNews), [marketNews]);
  const isPositive = (quote?.change_percent ?? 0) >= 0;

  return (
    <div className="flex h-full flex-col rounded-sm border border-theme-outline bg-theme-primary">
      <div className="border-b border-theme-outline px-3 py-3">
        <h2 className="body-sm-medium text-theme-muted tracking-wider uppercase">Market Live</h2>
      </div>

      <div className="border-b border-theme-outline px-3 py-2">
        <div className="flex items-center gap-2">
          <span className="body-xs-medium text-blue-400">Ticker</span>
          <span className="body-xs-medium text-theme-primary">{quote?.name || symbol}</span>
        </div>
        <div className="mt-1 flex items-center gap-3">
          <span className="body-sm-medium text-theme-primary">{formatNum(quote?.last_price ?? null)}</span>
          <span className={`body-xxs-medium ${isPositive ? "text-emerald-400" : "text-red-400"}`}>
            {quote?.change_percent != null ? `${isPositive ? "+" : ""}${quote.change_percent.toFixed(2)}%` : ""}
          </span>
        </div>
        <div className="mt-1 body-xxs-regular text-theme-muted">Vol {formatVol(quote?.volume ?? null)}</div>
      </div>

      <div className="border-b border-theme-outline">
        <TradingViewWidgetEmbed
          widgetType="advanced-chart"
          symbol={symbol}
          theme={theme}
          title="Market Chart"
          minHeight={300}
          frameHeight={300}
        />
      </div>

      <div className="flex-1 overflow-auto px-1 py-2">
        {marketNewsError && marketNews.length === 0 ? (
          <div className="px-3 py-4 text-center">
            <p className="body-xxs-regular text-red-400">{marketNewsError}</p>
          </div>
        ) : marketNewsLoading && marketNews.length === 0 ? (
          <div className="px-3 py-4 text-center">
            <p className="body-xxs-regular text-theme-muted">Loading market news...</p>
          </div>
        ) : marketNews.length === 0 ? (
          <div className="px-3 py-4 text-center">
            <p className="body-xxs-regular text-theme-muted">No market news available.</p>
          </div>
        ) : (
          <div className="space-y-1">
            {groupedNews.map((group) => (
              <div key={group.date}>
                <div className="sticky top-0 z-10 bg-theme-primary px-3 py-1.5">
                  <p className="body-xxs-medium text-theme-muted">{group.date}</p>
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
    </div>
  );
}
