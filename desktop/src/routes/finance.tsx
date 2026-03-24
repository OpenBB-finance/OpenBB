import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { FinancePageLayout } from "../components/finance/FinancePageLayout";
import { getTradingViewThemeMode } from "../lib/tradingView";
import { useFinanceSymbolState } from "../hooks/useFinanceSymbolState";
import type { TradingViewThemeMode } from "../types/finance";

function FinancePage() {
  const {
    activeSymbol,
    symbolInput,
    recentSymbols,
    setSymbolInput,
    submitSymbol,
    selectRecentSymbol,
  } = useFinanceSymbolState();
  const [theme, setTheme] = useState<TradingViewThemeMode>(() => getTradingViewThemeMode());

  useEffect(() => {
    const root = document.documentElement;
    const observer = new MutationObserver(() => {
      setTheme(getTradingViewThemeMode());
    });
    observer.observe(root, {
      attributes: true,
      attributeFilter: ["class", "data-theme"],
    });
    return () => observer.disconnect();
  }, []);

  return (
    <div className="h-full min-h-0 overflow-auto py-4">
      <div className="mb-4 flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="body-lg-medium text-theme-primary">Finance</h1>
          <p className="body-sm-regular text-theme-muted">
            TradingView-backed chart and company fundamentals.
          </p>
        </div>
        <div className="rounded-full border border-theme-outline bg-theme-primary px-4 py-2">
          <p className="body-xxs-regular text-theme-muted">Active Symbol</p>
          <p className="body-sm-medium text-theme-primary">{activeSymbol}</p>
        </div>
      </div>

      <FinancePageLayout
        activeSymbol={activeSymbol}
        symbolInput={symbolInput}
        recentSymbols={recentSymbols}
        theme={theme}
        onSymbolInputChange={setSymbolInput}
        onSubmit={submitSymbol}
        onSelectRecentSymbol={selectRecentSymbol}
      />
    </div>
  );
}

export const Route = createFileRoute("/finance")({
  component: FinancePage,
  validateSearch: (search: Record<string, unknown>) => ({
    symbol: typeof search.symbol === "string" ? search.symbol : undefined,
  }),
});
