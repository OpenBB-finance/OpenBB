import type { MacroDataPoint, MacroSeriesMultiResponse } from "../../types/macro";

interface MultiSeriesComparePanelProps {
  compareKeys: string;
  onCompareKeysChange: (value: string) => void;
  onRefresh: () => void;
  isBusy: boolean;
  payload: MacroSeriesMultiResponse | null;
  errorMessage?: string | null;
}

interface NormalizedSeries {
  key: string;
  points: MacroDataPoint[];
}

const COLORS = ["#38bdf8", "#22c55e", "#f59e0b", "#ef4444", "#a855f7", "#14b8a6"];

function normalizeSeries(payload: MacroSeriesMultiResponse | null): NormalizedSeries[] {
  if (!payload || !payload.series || typeof payload.series !== "object") {
    return [];
  }
  const out: NormalizedSeries[] = [];
  for (const [key, series] of Object.entries(payload.series)) {
    const data = Array.isArray(series?.data) ? series.data : [];
    if (data.length < 2) {
      continue;
    }
    const first = Number(data[0].value);
    const base = Number.isFinite(first) && Math.abs(first) > 1e-12 ? first : 1;
    const points = data.map((row) => ({
      date: row.date,
      value: (Number(row.value) / base) * 100,
    }));
    out.push({ key, points });
  }
  return out;
}

function buildPath(values: number[], width: number, height: number, min: number, max: number): string {
  if (values.length < 2) {
    return "";
  }
  const span = Math.max(max - min, 1e-12);
  return values
    .map((value, index) => {
      const x = (index / (values.length - 1)) * width;
      const y = ((max - value) / span) * height;
      return `${index === 0 ? "M" : "L"} ${x.toFixed(2)} ${y.toFixed(2)}`;
    })
    .join(" ");
}

export function MultiSeriesComparePanel({
  compareKeys,
  onCompareKeysChange,
  onRefresh,
  isBusy,
  payload,
  errorMessage,
}: MultiSeriesComparePanelProps) {
  const normalized = normalizeSeries(payload);
  const allValues = normalized.flatMap((item) => item.points.map((point) => point.value));
  const min = allValues.length > 0 ? Math.min(...allValues) : 0;
  const max = allValues.length > 0 ? Math.max(...allValues) : 1;

  return (
    <div className="rounded-sm border border-theme-outline bg-theme-primary p-3">
      <div className="flex items-center justify-between gap-2">
        <h3 className="body-sm-medium text-theme-primary">Multi-Series Compare (Index=100)</h3>
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={compareKeys}
            onChange={(event) => onCompareKeysChange(event.target.value)}
            className="w-[360px] rounded-sm border border-theme-outline bg-theme-secondary p-1.5 body-xs-regular text-theme-primary"
            placeholder="FRED:UNRATE,FRED:CPIAUCSL,FRED:FEDFUNDS"
          />
          <button type="button" className="button-secondary rounded-sm px-2 py-1.5 body-xs-medium" onClick={onRefresh} disabled={isBusy}>
            Refresh
          </button>
        </div>
      </div>
      <p className="mt-1 body-xxs-regular text-theme-muted">
        Comma-separated keys. Each series is normalized to 100 at the first visible observation.
      </p>
      {errorMessage ? <p className="mt-2 body-xxs-regular text-amber-300">{errorMessage}</p> : null}
      {normalized.length < 2 ? (
        <div className="mt-3 rounded-sm bg-theme-secondary p-3">
          <p className="body-xs-regular text-theme-muted">At least 2 non-empty series are required to compare.</p>
        </div>
      ) : (
        <svg viewBox="0 0 920 220" className="mt-3 h-[220px] w-full rounded-sm bg-theme-secondary">
          {normalized.map((item, index) => {
            const values = item.points.map((point) => point.value);
            const path = buildPath(values, 920, 220, min, max);
            return (
              <path
                key={item.key}
                d={path}
                fill="none"
                stroke={COLORS[index % COLORS.length]}
                strokeWidth="2"
              />
            );
          })}
        </svg>
      )}
      <div className="mt-2 flex flex-wrap gap-2">
        {normalized.map((item, index) => (
          <span key={item.key} className="rounded-sm bg-theme-secondary px-2 py-1 body-xxs-regular text-theme-muted">
            <span style={{ color: COLORS[index % COLORS.length] }}>{item.key}</span>
          </span>
        ))}
      </div>
    </div>
  );
}

