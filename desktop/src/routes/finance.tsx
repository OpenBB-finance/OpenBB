import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useMemo, useState } from "react";
import { FinancePageLayout } from "../components/finance/FinancePageLayout";
import { resolveOpenBBBackend } from "../lib/openbbBackend";
import { fetchSymbolContext } from "../lib/quantApi";
import { getTradingViewThemeMode } from "../lib/tradingView";
import { useFinanceSymbolState } from "../hooks/useFinanceSymbolState";
import type { TradingViewThemeMode } from "../types/finance";
import type { SymbolContextPayload, SymbolLabSearch } from "../types/quant";

function readSymbolLabSearch(): SymbolLabSearch {
  if (typeof window === "undefined") {
    return {};
  }
  const params = new URLSearchParams(window.location.search);
  return {
    symbol: typeof params.get("symbol") === "string" ? params.get("symbol") ?? undefined : undefined,
    source: params.get("source") ?? undefined,
    studyId: params.get("studyId") ?? undefined,
    runId: params.get("runId") ?? undefined,
    signalId: params.get("signalId") ?? undefined,
    reportPath: params.get("reportPath") ?? undefined,
  };
}

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
  const [baseUrl, setBaseUrl] = useState("");
  const [contextRail, setContextRail] = useState<SymbolContextPayload | null>(null);
  const [contextError, setContextError] = useState<string | null>(null);
  const symbolLabSearch = useMemo(() => readSymbolLabSearch(), [activeSymbol]);

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

  useEffect(() => {
    const loadBackend = async () => {
      try {
        const backend = await resolveOpenBBBackend();
        if (backend.connected) {
          setBaseUrl(backend.baseUrl);
        }
      } catch {
        setBaseUrl("");
      }
    };
    void loadBackend();
  }, []);

  useEffect(() => {
    if (!baseUrl || !activeSymbol) {
      setContextRail(null);
      return;
    }
    const loadContext = async () => {
      try {
        setContextError(null);
        const payload = await fetchSymbolContext(baseUrl, {
          symbol: activeSymbol,
          source: symbolLabSearch.source,
          studyId: symbolLabSearch.studyId,
          runId: symbolLabSearch.runId,
          signalId: symbolLabSearch.signalId,
          reportPath: symbolLabSearch.reportPath,
        });
        setContextRail(payload);
      } catch (error) {
        setContextError(error instanceof Error ? error.message : "Failed to load Finance Lab context.");
      }
    };
    void loadContext();
  }, [
    activeSymbol,
    baseUrl,
    symbolLabSearch.reportPath,
    symbolLabSearch.runId,
    symbolLabSearch.signalId,
    symbolLabSearch.source,
    symbolLabSearch.studyId,
  ]);

  return (
    <div className="h-full min-h-0 overflow-auto py-4">
      <div className="mb-4 flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="body-lg-medium text-theme-primary">Finance Lab</h1>
          <p className="body-sm-regular text-theme-muted">
            Symbol drilldown for macro-linked assets, strategy signals, and execution candidates.
          </p>
        </div>
        <div className="rounded-full border border-theme-outline bg-theme-primary px-4 py-2">
          <p className="body-xxs-regular text-theme-muted">Active Symbol</p>
          <p className="body-sm-medium text-theme-primary">{activeSymbol}</p>
        </div>
      </div>

      <FinancePageLayout
        activeSymbol={activeSymbol}
        baseUrl={baseUrl}
        symbolInput={symbolInput}
        recentSymbols={recentSymbols}
        theme={theme}
        onSymbolInputChange={setSymbolInput}
        onSubmit={submitSymbol}
        onSelectRecentSymbol={selectRecentSymbol}
        contextRail={contextRail}
        contextError={contextError}
        symbolSearch={symbolLabSearch}
      />
    </div>
  );
}

export const Route = createFileRoute("/finance")({
  component: FinancePage,
  validateSearch: (search: Record<string, unknown>) => ({
    symbol: typeof search.symbol === "string" ? search.symbol : undefined,
    source: typeof search.source === "string" ? search.source : undefined,
    studyId: typeof search.studyId === "string" ? search.studyId : undefined,
    runId: typeof search.runId === "string" ? search.runId : undefined,
    signalId: typeof search.signalId === "string" ? search.signalId : undefined,
    reportPath: typeof search.reportPath === "string" ? search.reportPath : undefined,
  }),
});
