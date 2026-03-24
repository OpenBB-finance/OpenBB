import { useEffect, useMemo, useRef, useState } from "react";
import { buildFinanceSymbolSuggestions } from "../../lib/tradingView";

interface FinanceSymbolPickerProps {
  activeSymbol: string;
  inputId: string;
  label: string;
  symbolInput: string;
  recentSymbols: string[];
  placeholder?: string;
  submitLabel?: string;
  compact?: boolean;
  onSymbolInputChange: (value: string) => void;
  onSubmit: () => void;
  onSelectSymbol: (symbol: string) => void;
}

export function FinanceSymbolPicker({
  activeSymbol,
  inputId,
  label,
  symbolInput,
  recentSymbols,
  placeholder = "NASDAQ:AAPL",
  submitLabel = "Load",
  compact = false,
  onSymbolInputChange,
  onSubmit,
  onSelectSymbol,
}: FinanceSymbolPickerProps) {
  const rootRef = useRef<HTMLDivElement | null>(null);
  const [isOpen, setIsOpen] = useState(false);
  const suggestions = useMemo(
    () => buildFinanceSymbolSuggestions(symbolInput, recentSymbols, activeSymbol),
    [activeSymbol, recentSymbols, symbolInput],
  );

  useEffect(() => {
    const handlePointerDown = (event: MouseEvent) => {
      if (!rootRef.current?.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener("mousedown", handlePointerDown);
    return () => document.removeEventListener("mousedown", handlePointerDown);
  }, []);

  return (
    <div ref={rootRef}>
      <label htmlFor={inputId} className="body-xs-medium text-theme-muted">
        {label}
      </label>
      <div className={`relative ${compact ? "mt-2" : "mt-2"}`}>
        <div className="flex gap-2">
          <input
            id={inputId}
            value={symbolInput}
            onChange={(event) => {
              onSymbolInputChange(event.target.value);
              setIsOpen(true);
            }}
            onFocus={() => setIsOpen(true)}
            onClick={() => setIsOpen(true)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                event.preventDefault();
                setIsOpen(false);
                onSubmit();
              }
              if (event.key === "Escape") {
                setIsOpen(false);
              }
            }}
            placeholder={placeholder}
            autoComplete="off"
            className="w-full rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2 body-xs-regular text-theme-primary outline-none transition-colors focus:border-sky-400"
          />
          <button
            type="button"
            onClick={() => {
              setIsOpen(false);
              onSubmit();
            }}
            className="button-secondary shrink-0 rounded-sm px-3 py-2 body-xs-medium"
          >
            {submitLabel}
          </button>
        </div>
        {isOpen && suggestions.length > 0 ? (
          <div className="absolute z-20 mt-2 w-full rounded-sm border border-theme-outline bg-theme-primary/95 shadow-2xl backdrop-blur">
            <div className="max-h-72 overflow-y-auto py-2">
              {suggestions.map((suggestion) => (
                <button
                  key={`${suggestion.source}-${suggestion.symbol}`}
                  type="button"
                  onClick={() => {
                    onSelectSymbol(suggestion.symbol);
                    setIsOpen(false);
                  }}
                  className="flex w-full items-center justify-between px-3 py-2 text-left transition-colors hover:bg-theme-secondary"
                >
                  <span className="body-xs-medium text-theme-primary">{suggestion.symbol}</span>
                  <span className="body-xxs-regular uppercase tracking-[0.14em] text-theme-muted">
                    {suggestion.source}
                  </span>
                </button>
              ))}
            </div>
          </div>
        ) : null}
      </div>
    </div>
  );
}
