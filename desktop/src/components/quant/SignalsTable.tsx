import type { SignalItem } from "../../types/quant";
import { PanelCard } from "./PanelCard";

interface SignalsTableProps {
  asOfDate?: string;
  signals: SignalItem[];
}

function sideColor(side: SignalItem["side"]): string {
  if (side === "buy") {
    return "text-green-400";
  }
  if (side === "sell") {
    return "text-red-400";
  }
  return "text-theme-muted";
}

export function SignalsTable({ asOfDate, signals }: SignalsTableProps) {
  const staleDays = (() => {
    if (!asOfDate) {
      return null;
    }
    const value = new Date(asOfDate);
    if (Number.isNaN(value.getTime())) {
      return null;
    }
    const today = new Date();
    const diff = Math.floor((today.getTime() - value.getTime()) / (1000 * 60 * 60 * 24));
    return diff >= 0 ? diff : 0;
  })();

  return (
    <PanelCard
      title="Signals"
      description={asOfDate ? `As of ${asOfDate}` : "Generate signals to display results."}
    >
      {staleDays !== null && staleDays > 14 ? (
        <p className="mb-2 body-xs-regular text-amber-400">
          Signal date is {staleDays} days old. Refresh training if you need latest market data.
        </p>
      ) : null}
      {signals.length === 0 ? (
        <p className="body-sm-regular text-theme-muted">No signals available.</p>
      ) : (
        <div className="overflow-auto">
          <table className="min-w-full text-left">
            <thead>
              <tr className="border-b border-theme-outline">
                <th className="px-2 py-2 body-xs-medium text-theme-muted">Symbol</th>
                <th className="px-2 py-2 body-xs-medium text-theme-muted">Side</th>
                <th className="px-2 py-2 body-xs-medium text-theme-muted">Pred. Return</th>
                <th className="px-2 py-2 body-xs-medium text-theme-muted">Confidence</th>
                <th className="px-2 py-2 body-xs-medium text-theme-muted">Reason</th>
              </tr>
            </thead>
            <tbody>
              {signals.map((signal) => (
                <tr key={signal.symbol} className="border-b border-theme-outline/40">
                  <td className="px-2 py-2 body-xs-regular text-theme-primary">{signal.symbol}</td>
                  <td className={`px-2 py-2 body-xs-medium ${sideColor(signal.side)}`}>{signal.side}</td>
                  <td className="px-2 py-2 body-xs-regular text-theme-primary">
                    {(signal.predicted_return * 100).toFixed(3)}%
                  </td>
                  <td className="px-2 py-2 body-xs-regular text-theme-primary">
                    {(signal.confidence * 100).toFixed(1)}%
                  </td>
                  <td className="px-2 py-2 body-xs-regular text-theme-muted">
                    {signal.reason_codes.join(", ")}
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
