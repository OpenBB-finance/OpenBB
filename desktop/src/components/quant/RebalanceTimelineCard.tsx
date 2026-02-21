import type { RebalanceHistoryItem } from "../../types/quant";
import { PanelCard } from "./PanelCard";

interface RebalanceTimelineCardProps {
  history: RebalanceHistoryItem[];
  isLoading: boolean;
  errorMessage: string | null;
  onRetry: () => void;
}

function formatPercent(value: number): string {
  return `${(value * 100).toFixed(2)}%`;
}

function listText(items: string[], empty = "None"): string {
  if (!items || items.length === 0) {
    return empty;
  }
  return items.join(", ");
}

function deltasText(
  rows: Array<{ symbol: string; delta: number }>,
  fallback = "None",
): string {
  if (!rows || rows.length === 0) {
    return fallback;
  }
  return rows
    .map((row) => `${row.symbol} ${formatPercent(row.delta)}`)
    .join(", ");
}

export function RebalanceTimelineCard({
  history,
  isLoading,
  errorMessage,
  onRetry,
}: RebalanceTimelineCardProps) {
  return (
    <PanelCard
      title="Portfolio Timeline"
      description="Monthly rebalance transitions (add/sell/weight deltas/turnover)."
    >
      {isLoading ? (
        <p className="body-sm-regular text-theme-muted">Loading rebalance history...</p>
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
      ) : history.length === 0 ? (
        <p className="body-sm-regular text-theme-muted">No rebalance history yet.</p>
      ) : (
        <div className="max-h-80 overflow-auto rounded-sm border border-theme-outline/50">
          <table className="min-w-full text-left">
            <thead>
              <tr className="border-b border-theme-outline/50">
                <th className="px-2 py-1 body-xs-medium text-theme-muted">Date</th>
                <th className="px-2 py-1 body-xs-medium text-theme-muted">Added</th>
                <th className="px-2 py-1 body-xs-medium text-theme-muted">Sold</th>
                <th className="px-2 py-1 body-xs-medium text-theme-muted">Top Weight Increases</th>
                <th className="px-2 py-1 body-xs-medium text-theme-muted">Top Weight Decreases</th>
                <th className="px-2 py-1 body-xs-medium text-theme-muted text-right">Turnover</th>
                <th className="px-2 py-1 body-xs-medium text-theme-muted">Binding Constraints</th>
              </tr>
            </thead>
            <tbody>
              {history.map((row) => (
                <tr key={row.date} className="border-b border-theme-outline/30 align-top">
                  <td className="px-2 py-1 body-xs-regular text-theme-primary">{row.date}</td>
                  <td className="px-2 py-1 body-xs-regular text-theme-primary">{listText(row.added, "No adds")}</td>
                  <td className="px-2 py-1 body-xs-regular text-theme-primary">{listText(row.sold, "No sells")}</td>
                  <td className="px-2 py-1 body-xs-regular text-theme-primary">
                    {deltasText(row.top_weight_increases)}
                  </td>
                  <td className="px-2 py-1 body-xs-regular text-theme-primary">
                    {deltasText(row.top_weight_decreases)}
                  </td>
                  <td className="px-2 py-1 body-xs-regular text-theme-primary text-right">
                    {formatPercent(row.turnover)}
                  </td>
                  <td className="px-2 py-1 body-xs-regular text-theme-primary">
                    {listText(row.binding_constraints, "None")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </PanelCard>
  );
}
