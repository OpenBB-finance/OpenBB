import { createFileRoute } from "@tanstack/react-router";
import { useCallback, useEffect, useMemo, useState } from "react";
import { FinancePageLayout } from "../components/finance/FinancePageLayout";
import { formatBackendDetail, resolveOpenBBBackend } from "../lib/openbbBackend";
import { fetchSymbolContext } from "../lib/quantApi";
import { getTradingViewThemeMode } from "../lib/tradingView";
import { useFinanceSymbolState } from "../hooks/useFinanceSymbolState";
import type { TradingViewThemeMode } from "../types/finance";
import type { BackendResolution, SymbolContextPayload, SymbolLabSearch } from "../types/quant";

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
  const [backendResolution, setBackendResolution] = useState<BackendResolution | null>(null);
  const [isResolvingBackend, setIsResolvingBackend] = useState(true);
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

  const refreshBackend = useCallback(async () => {
    setIsResolvingBackend(true);
    try {
      const backend = await resolveOpenBBBackend();
      setBackendResolution(backend);
      setBaseUrl(backend.baseUrl ?? "");
    } catch {
      setBackendResolution(null);
      setBaseUrl("");
    } finally {
      setIsResolvingBackend(false);
    }
  }, []);

  useEffect(() => {
    void refreshBackend();
  }, [refreshBackend]);

  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === "visible") {
        void refreshBackend();
      }
    };
    const handleFocus = () => {
      void refreshBackend();
    };
    const handleStorage = (event: StorageEvent) => {
      if (event.key?.startsWith("openbb-api-")) {
        void refreshBackend();
      }
    };
    const timer = window.setInterval(() => {
      if (!backendResolution?.connected && document.visibilityState === "visible") {
        void refreshBackend();
      }
    }, 10_000);

    window.addEventListener("focus", handleFocus);
    window.addEventListener("storage", handleStorage);
    document.addEventListener("visibilitychange", handleVisibilityChange);
    return () => {
      window.clearInterval(timer);
      window.removeEventListener("focus", handleFocus);
      window.removeEventListener("storage", handleStorage);
      document.removeEventListener("visibilitychange", handleVisibilityChange);
    };
  }, [backendResolution?.connected, refreshBackend]);

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

      <div className="mb-4 rounded-sm border border-theme-outline bg-theme-primary px-4 py-3">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="body-xxs-regular text-theme-muted">OpenBB Backend</p>
            <p className="body-sm-medium text-theme-primary">
              {isResolvingBackend
                ? "Resolving..."
                : backendResolution
                  ? backendResolution.connected
                    ? "Connected"
                    : "Offline or auth required"
                  : "Unavailable"}
            </p>
            <p className="mt-1 body-xxs-regular text-theme-muted">
              {backendResolution
                ? formatBackendDetail(backendResolution.detail, backendResolution.connected)
                : "Finance fundamentals will load once an OpenBB backend is available."}
            </p>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            {backendResolution?.baseUrl ? (
              <div className="rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2">
                <p className="body-xxs-regular text-theme-muted">URL</p>
                <p className="body-xs-medium text-theme-primary">{backendResolution.baseUrl}</p>
              </div>
            ) : null}
            <button
              type="button"
              className="button-secondary rounded-sm px-3 py-2 body-xs-medium"
              onClick={() => void refreshBackend()}
              disabled={isResolvingBackend}
            >
              {isResolvingBackend ? "Refreshing..." : "Retry Backend"}
            </button>
          </div>
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
