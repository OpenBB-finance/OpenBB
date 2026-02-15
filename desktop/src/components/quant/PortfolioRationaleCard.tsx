import type { PortfolioCurrentPayload } from "../../types/quant";
import { AssetClassPieChart } from "./AssetClassPieChart";
import { PanelCard } from "./PanelCard";

interface PortfolioRationaleCardProps {
  portfolio: PortfolioCurrentPayload | null;
  isLoading: boolean;
  errorMessage: string | null;
  onRetry: () => void;
}

function toPercent(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

function topHoldingsText(portfolio: PortfolioCurrentPayload): string {
  if (portfolio.symbol_weights.length === 0) {
    return "No holdings available.";
  }
  return portfolio.symbol_weights
    .slice(0, 5)
    .map((item) => `${item.symbol} ${toPercent(item.weight)}`)
    .join(", ");
}

export function PortfolioRationaleCard({
  portfolio,
  isLoading,
  errorMessage,
  onRetry,
}: PortfolioRationaleCardProps) {
  return (
    <PanelCard
      title="Portfolio Rationale"
      description={
        portfolio?.as_of_date
          ? `Latest rebalance: ${portfolio.as_of_date}`
          : "Run backtest to view allocation rationale."
      }
    >
      {isLoading ? (
        <p className="body-sm-regular text-theme-muted">Loading allocation rationale...</p>
      ) : errorMessage ? (
        <div className="space-y-2">
          <p className="body-sm-regular text-red-400">{errorMessage}</p>
          <button
            type="button"
            className="button-secondary rounded-sm px-3 py-1 body-xs-medium"
            onClick={onRetry}
          >
            Retry
          </button>
        </div>
      ) : !portfolio || portfolio.asset_class_weights.length === 0 ? (
        <p className="body-sm-regular text-theme-muted">Run backtest to view allocation rationale.</p>
      ) : (
        <div className="space-y-3">
          <div className="rounded-sm bg-theme-secondary p-3">
            <p className="body-xs-medium text-theme-muted">Why this portfolio?</p>
            <ul className="mt-2 space-y-1">
              {portfolio.rationale.summary_lines.map((line, index) => (
                <li key={`${line}-${index}`} className="body-xs-regular text-theme-primary">
                  {line}
                </li>
              ))}
            </ul>
          </div>

          <div className="rounded-sm bg-theme-secondary p-2">
            <AssetClassPieChart slices={portfolio.asset_class_weights} />
          </div>

          <div className="rounded-sm bg-theme-secondary p-2">
            <p className="body-xs-medium text-theme-muted">Current Holdings (Latest Rebalance)</p>
            <p className="mt-1 body-xs-regular text-theme-primary">{topHoldingsText(portfolio)}</p>
            <p className="mt-1 body-xs-regular text-theme-muted">
              Total weight: {toPercent(portfolio.total_weight || 0)}
            </p>
            {portfolio.symbol_weights.length > 0 ? (
              <div className="mt-2 max-h-48 overflow-auto rounded-sm border border-theme-outline/50">
                <table className="min-w-full text-left">
                  <thead>
                    <tr className="border-b border-theme-outline/50">
                      <th className="px-2 py-1 body-xs-medium text-theme-muted">Symbol</th>
                      <th className="px-2 py-1 body-xs-medium text-theme-muted">Category</th>
                      <th className="px-2 py-1 body-xs-medium text-theme-muted text-right">Weight</th>
                    </tr>
                  </thead>
                  <tbody>
                    {portfolio.symbol_weights.map((item) => (
                      <tr key={`${item.symbol}-${item.category}`} className="border-b border-theme-outline/30">
                        <td className="px-2 py-1 body-xs-regular text-theme-primary">{item.symbol}</td>
                        <td className="px-2 py-1 body-xs-regular text-theme-muted">{item.category}</td>
                        <td className="px-2 py-1 body-xs-regular text-theme-primary text-right">
                          {toPercent(item.weight)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="mt-2 body-xs-regular text-theme-muted">No symbol-level weights available.</p>
            )}
          </div>

          <div className="rounded-sm bg-theme-secondary p-2">
            <p className="mb-2 body-xs-medium text-theme-muted">Asset Class Weights</p>
            <ul className="space-y-1">
              {portfolio.asset_class_weights.map((item) => (
                <li key={item.category} className="flex items-center justify-between">
                  <span className="body-xs-regular text-theme-primary">{item.category}</span>
                  <span className="body-xs-regular text-theme-muted">{toPercent(item.weight)}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </PanelCard>
  );
}
