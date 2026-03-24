import { useEffect, useState } from "react";
import { PanelCard } from "../quant/PanelCard";
import { FinanceControlsCard } from "./FinanceControlsCard";
import { FinanceFundamentalsPanel } from "./FinanceFundamentalsPanel";
import { FinanceSymbolPicker } from "./FinanceSymbolPicker";
import { TradingViewWidgetEmbed } from "./TradingViewWidgetEmbed";
import type { TradingViewThemeMode } from "../../types/finance";

interface FinancePageLayoutProps {
  activeSymbol: string;
  symbolInput: string;
  recentSymbols: string[];
  theme: TradingViewThemeMode;
  onSymbolInputChange: (value: string) => void;
  onSubmit: () => void;
  onSelectRecentSymbol: (symbol: string) => void;
}

export function FinancePageLayout({
  activeSymbol,
  symbolInput,
  recentSymbols,
  theme,
  onSymbolInputChange,
  onSubmit,
  onSelectRecentSymbol,
}: FinancePageLayoutProps) {
  const [chartHeight, setChartHeight] = useState(720);
  const [fundamentalHeight, setFundamentalHeight] = useState(920);

  useEffect(() => {
    const syncHeights = () => {
      if (typeof window === "undefined") return;
      setChartHeight(Math.max(560, Math.min(window.innerHeight - 220, 780)));
      setFundamentalHeight(Math.max(760, Math.min(window.innerHeight + 80, 1120)));
    };
    syncHeights();
    window.addEventListener("resize", syncHeights);
    return () => window.removeEventListener("resize", syncHeights);
  }, []);

  return (
    <div className="grid grid-cols-1 gap-4 xl:grid-cols-[320px_minmax(0,1fr)]">
      <div className="space-y-4 xl:sticky xl:top-4 xl:self-start">
        <FinanceControlsCard
          activeSymbol={activeSymbol}
          symbolInput={symbolInput}
          recentSymbols={recentSymbols}
          onSymbolInputChange={onSymbolInputChange}
          onSubmit={onSubmit}
          onSelectRecentSymbol={onSelectRecentSymbol}
        />
      </div>
      <div className="space-y-4">
        <PanelCard title="Advanced Chart" description="TradingView advanced chart with detailed timeframe and indicator controls.">
          <div className="mb-4">
            <FinanceSymbolPicker
              activeSymbol={activeSymbol}
              inputId="finance-chart-symbol-input"
              label="Chart Symbol Search"
              symbolInput={symbolInput}
              recentSymbols={recentSymbols}
              submitLabel="Update"
              compact
              onSymbolInputChange={onSymbolInputChange}
              onSubmit={onSubmit}
              onSelectSymbol={onSelectRecentSymbol}
            />
          </div>
          <TradingViewWidgetEmbed
            widgetType="advanced-chart"
            symbol={activeSymbol}
            theme={theme}
            title="Advanced Chart"
            minHeight={chartHeight}
            frameHeight={chartHeight}
          />
        </PanelCard>
        <FinanceFundamentalsPanel
          symbol={activeSymbol}
          theme={theme}
          overviewHeight={fundamentalHeight}
        />
        <div className="grid grid-cols-1 gap-4 xl:grid-cols-[320px_minmax(0,1fr)]">
          <PanelCard title="Symbol Info" description="TradingView summary snapshot and headline market data.">
            <TradingViewWidgetEmbed
              widgetType="symbol-info"
              symbol={activeSymbol}
              theme={theme}
              title="Symbol Info"
              lazy
              minHeight={420}
              frameHeight={420}
            />
          </PanelCard>
          <PanelCard title="Company Profile" description="TradingView company description, sector, and industry metadata.">
            <TradingViewWidgetEmbed
              widgetType="company-profile"
              symbol={activeSymbol}
              theme={theme}
              title="Company Profile"
              lazy
              minHeight={320}
              frameHeight={320}
            />
          </PanelCard>
        </div>
      </div>
    </div>
  );
}
