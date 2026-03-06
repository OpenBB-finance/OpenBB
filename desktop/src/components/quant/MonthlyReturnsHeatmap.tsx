import type { MonthlyReturnPoint } from "../../types/quant";
import { PanelCard } from "./PanelCard";

interface MonthlyReturnsHeatmapProps {
  points: MonthlyReturnPoint[];
}

const MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

function toPercent(value: number | null): string {
  if (value == null || Number.isNaN(value)) {
    return "-";
  }
  return `${(value * 100).toFixed(1)}%`;
}

function cellClass(value: number | null): string {
  if (value == null || Number.isNaN(value)) {
    return "bg-theme-secondary text-theme-muted";
  }
  if (value >= 0.08) {
    return "bg-emerald-600/35 text-emerald-100";
  }
  if (value > 0.0) {
    return "bg-emerald-500/20 text-emerald-200";
  }
  if (value <= -0.08) {
    return "bg-red-600/35 text-red-100";
  }
  if (value < 0.0) {
    return "bg-red-500/20 text-red-200";
  }
  return "bg-theme-secondary text-theme-primary";
}

export function MonthlyReturnsHeatmap({ points }: MonthlyReturnsHeatmapProps) {
  if (!points || points.length === 0) {
    return (
      <PanelCard title="Monthly Returns" description="Calendar heatmap by year/month">
        <p className="body-sm-regular text-theme-muted">Run backtest to view monthly returns heatmap.</p>
      </PanelCard>
    );
  }

  const values = new Map<string, number>();
  for (const item of points) {
    const month = Number(item.month);
    const year = Number(item.year);
    if (!Number.isFinite(month) || !Number.isFinite(year)) {
      continue;
    }
    const key = `${year}-${String(month).padStart(2, "0")}`;
    values.set(key, Number(item.return));
  }

  const years = Array.from(new Set(points.map((item) => Number(item.year))))
    .filter((year) => Number.isFinite(year))
    .sort((a, b) => b - a);

  return (
    <PanelCard title="Monthly Returns" description="Calendar heatmap by year/month">
      <div className="overflow-x-auto rounded-sm border border-theme-outline/50">
        <table className="min-w-full text-left">
          <thead>
            <tr className="border-b border-theme-outline/50">
              <th className="px-2 py-1 body-xs-medium text-theme-muted">Year</th>
              {MONTHS.map((month) => (
                <th key={month} className="px-2 py-1 body-xs-medium text-theme-muted text-right">
                  {month}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {years.map((year) => (
              <tr key={year} className="border-b border-theme-outline/30">
                <td className="px-2 py-1 body-xs-medium text-theme-primary">{year}</td>
                {MONTHS.map((_, idx) => {
                  const month = idx + 1;
                  const value = values.get(`${year}-${String(month).padStart(2, "0")}`) ?? null;
                  return (
                    <td key={`${year}-${month}`} className="px-1 py-1">
                      <div className={`rounded-sm px-2 py-1 text-right body-xxs-medium ${cellClass(value)}`}>
                        {toPercent(value)}
                      </div>
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </PanelCard>
  );
}
