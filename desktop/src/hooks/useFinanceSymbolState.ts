import { useCallback, useEffect, useState } from "react";
import {
  DEFAULT_FINANCE_SYMBOL,
  FINANCE_LATEST_SYMBOL_KEY,
  normalizeTradingViewSymbol,
  readRecentFinanceSymbols,
  updateRecentFinanceSymbols,
} from "../lib/tradingView";

function readInitialSymbol(): string {
  if (typeof window === "undefined") {
    return DEFAULT_FINANCE_SYMBOL;
  }

  const params = new URLSearchParams(window.location.search);
  const fromUrl = normalizeTradingViewSymbol(params.get("symbol"));
  if (fromUrl) {
    return fromUrl;
  }

  const fromStorage = normalizeTradingViewSymbol(localStorage.getItem(FINANCE_LATEST_SYMBOL_KEY));
  return fromStorage || DEFAULT_FINANCE_SYMBOL;
}

function syncSymbolToUrl(symbol: string) {
  if (typeof window === "undefined") return;
  const params = new URLSearchParams(window.location.search);
  params.set("symbol", symbol);
  const nextSearch = params.toString();
  const nextUrl = `${window.location.pathname}${nextSearch ? `?${nextSearch}` : ""}`;
  window.history.replaceState(window.history.state, "", nextUrl);
}

export function useFinanceSymbolState() {
  const [activeSymbol, setActiveSymbol] = useState(readInitialSymbol);
  const [symbolInput, setSymbolInput] = useState(readInitialSymbol);
  const [recentSymbols, setRecentSymbols] = useState<string[]>(() => {
    const initialSymbol = readInitialSymbol();
    const stored = readRecentFinanceSymbols();
    return [initialSymbol, ...stored.filter((item) => item !== initialSymbol)].slice(0, 5);
  });

  useEffect(() => {
    const normalized = normalizeTradingViewSymbol(activeSymbol) || DEFAULT_FINANCE_SYMBOL;
    localStorage.setItem(FINANCE_LATEST_SYMBOL_KEY, normalized);
    syncSymbolToUrl(normalized);
    setRecentSymbols(updateRecentFinanceSymbols(normalized));
  }, [activeSymbol]);

  const applySymbol = useCallback((nextValue: string) => {
    const normalized = normalizeTradingViewSymbol(nextValue) || DEFAULT_FINANCE_SYMBOL;
    setActiveSymbol(normalized);
    setSymbolInput(normalized);
  }, []);

  const submitSymbol = useCallback(() => {
    applySymbol(symbolInput);
  }, [applySymbol, symbolInput]);

  return {
    activeSymbol,
    symbolInput,
    recentSymbols,
    setSymbolInput,
    submitSymbol,
    selectRecentSymbol: applySymbol,
  };
}
