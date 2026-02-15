import type { BacktestMetrics } from "../../types/quant";
import { PanelCard } from "./PanelCard";

interface MetricsCardsProps {
  metrics: BacktestMetrics | null;
}

function metricValue(value: number | undefined, asPercent = true): string {
  if (value === undefined || value === null || Number.isNaN(value)) {
    return "-";
  }
  return asPercent ? `${(value * 100).toFixed(2)}%` : value.toFixed(3);
}

export function MetricsCards({ metrics }: MetricsCardsProps) {
  return (
    <PanelCard title="Performance KPI" description="CAGR, Sharpe, Max Drawdown, Volatility, Turnover">
      {!metrics ? (
        <p className="body-sm-regular text-theme-muted">Run backtest to display performance metrics.</p>
      ) : (
        <div className="grid grid-cols-2 gap-2 md:grid-cols-5">
          <div className="rounded-sm bg-theme-secondary p-2">
            <p className="body-xs-regular text-theme-muted">CAGR</p>
            <p className="body-sm-medium text-theme-primary">{metricValue(metrics.cagr)}</p>
          </div>
          <div className="rounded-sm bg-theme-secondary p-2">
            <p className="body-xs-regular text-theme-muted">Sharpe</p>
            <p className="body-sm-medium text-theme-primary">{metricValue(metrics.sharpe, false)}</p>
          </div>
          <div className="rounded-sm bg-theme-secondary p-2">
            <p className="body-xs-regular text-theme-muted">MDD</p>
            <p className="body-sm-medium text-theme-primary">{metricValue(metrics.max_drawdown)}</p>
          </div>
          <div className="rounded-sm bg-theme-secondary p-2">
            <p className="body-xs-regular text-theme-muted">Volatility</p>
            <p className="body-sm-medium text-theme-primary">{metricValue(metrics.volatility)}</p>
          </div>
          <div className="rounded-sm bg-theme-secondary p-2">
            <p className="body-xs-regular text-theme-muted">Turnover</p>
            <p className="body-sm-medium text-theme-primary">{metricValue(metrics.turnover, false)}</p>
          </div>
        </div>
      )}
    </PanelCard>
  );
}
