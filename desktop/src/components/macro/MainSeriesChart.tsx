import type { MacroDataPoint } from "../../types/macro";

function linePath(values: number[], width: number, height: number): string {
  if (values.length < 2) {
    return "";
  }
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = Math.max(max - min, 1e-12);
  return values
    .map((value, index) => {
      const x = (index / (values.length - 1)) * width;
      const y = ((max - value) / span) * height;
      return `${index === 0 ? "M" : "L"} ${x.toFixed(2)} ${y.toFixed(2)}`;
    })
    .join(" ");
}

interface MainSeriesChartProps {
  points: MacroDataPoint[];
  title?: string;
  subtitle?: string;
}

export function MainSeriesChart({ points, title, subtitle }: MainSeriesChartProps) {
  const values = points.map((point) => point.value);
  const path = linePath(values, 920, 260);
  const latest = points.length ? points[points.length - 1] : null;

  return (
    <div className="rounded-sm border border-theme-outline bg-theme-primary p-3">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="body-sm-medium text-theme-primary">{title || "Main Series"}</h3>
          {subtitle ? <p className="body-xxs-regular text-theme-muted">{subtitle}</p> : null}
        </div>
        {latest ? (
          <p className="body-xs-regular text-theme-muted">
            Latest: <span className="text-theme-primary">{latest.value.toFixed(4)}</span> ({latest.date})
          </p>
        ) : null}
      </div>
      {points.length < 2 ? (
        <div className="mt-3 h-[260px] rounded-sm bg-theme-secondary p-3">
          <p className="body-xs-regular text-theme-muted">No data to plot.</p>
        </div>
      ) : (
        <svg viewBox="0 0 920 260" className="mt-3 h-[260px] w-full rounded-sm bg-theme-secondary">
          <path d={path} fill="none" stroke="#38bdf8" strokeWidth="2" />
        </svg>
      )}
    </div>
  );
}
