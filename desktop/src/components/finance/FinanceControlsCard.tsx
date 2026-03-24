import { PanelCard } from "../quant/PanelCard";
import { SummaryCard } from "../quant/SummaryCard";
import { FinanceSymbolPicker } from "./FinanceSymbolPicker";

interface FinanceControlsCardProps {
  activeSymbol: string;
  symbolInput: string;
  recentSymbols: string[];
  onSymbolInputChange: (value: string) => void;
  onSubmit: () => void;
  onSelectRecentSymbol: (symbol: string) => void;
}

export function FinanceControlsCard({
  activeSymbol,
  symbolInput,
  recentSymbols,
  onSymbolInputChange,
  onSubmit,
  onSelectRecentSymbol,
}: FinanceControlsCardProps) {
  return (
    <PanelCard title="Finance Controls" description="Load TradingView chart and company fundamentals for a single symbol.">
      <div className="space-y-4">
        <SummaryCard label="Active Symbol" value={activeSymbol} />
        <div>
          <FinanceSymbolPicker
            activeSymbol={activeSymbol}
            inputId="finance-symbol-input"
            label="Ticker / TV Symbol"
            symbolInput={symbolInput}
            recentSymbols={recentSymbols}
            onSymbolInputChange={onSymbolInputChange}
            onSubmit={onSubmit}
            onSelectSymbol={onSelectRecentSymbol}
          />
          <p className="mt-2 body-xxs-regular text-theme-muted">
            Raw symbols work, but fully-qualified TradingView symbols like NASDAQ:AAPL are more reliable.
          </p>
        </div>
        <div>
          <p className="body-xxs-medium text-theme-muted">Recent Symbols</p>
          <div className="mt-2 flex flex-wrap gap-2">
            {recentSymbols.map((symbol) => (
              <button
                key={symbol}
                type="button"
                onClick={() => onSelectRecentSymbol(symbol)}
                className={`rounded-full border px-3 py-1 body-xxs-medium transition-colors ${
                  symbol === activeSymbol
                    ? "border-sky-400/60 bg-sky-500/10 text-sky-300"
                    : "border-theme-outline bg-theme-secondary text-theme-muted hover:text-theme-primary"
                }`}
              >
                {symbol}
              </button>
            ))}
          </div>
        </div>
      </div>
    </PanelCard>
  );
}
