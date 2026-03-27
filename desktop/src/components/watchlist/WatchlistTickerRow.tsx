interface WatchlistTickerRowProps {
  symbol: string;
  name: string;
  changePercent: number | null;
  changeDollar: number | null;
  isSelected: boolean;
  onClick: () => void;
}

function formatPct(value: number | null): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "-";
  const sign = value >= 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
}

function formatChange(value: number | null): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "";
  const sign = value >= 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}`;
}

export function WatchlistTickerRow({
  symbol,
  name,
  changePercent,
  changeDollar,
  isSelected,
  onClick,
}: WatchlistTickerRowProps) {
  const isPositive = (changePercent ?? 0) >= 0;
  const colorClass = isPositive ? "text-emerald-400" : "text-red-400";

  return (
    <button
      type="button"
      onClick={onClick}
      className={`flex w-full items-center justify-between gap-2 rounded-sm px-3 py-2.5 text-left transition-colors ${
        isSelected
          ? "border-l-2 border-blue-500 bg-blue-500/10"
          : "border-l-2 border-transparent hover:bg-theme-secondary/60"
      }`}
    >
      <div className="min-w-0 flex-1">
        <div className="body-xs-medium text-theme-primary">{symbol}</div>
        <div className="body-xxs-regular text-theme-muted truncate">{name || symbol}</div>
      </div>
      <div className="text-right">
        <div className={`body-xs-medium ${colorClass}`}>{formatPct(changePercent)}</div>
        <div className={`body-xxs-regular ${colorClass}`}>{formatChange(changeDollar)}</div>
      </div>
    </button>
  );
}
