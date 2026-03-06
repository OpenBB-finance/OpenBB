import type { MacroDataPoint, MacroSeriesMultiResponse } from "../../types/macro";
import { MultiLineChart } from "../charts/MultiLineChart";

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

export function MultiSeriesComparePanel({
  compareKeys,
  onCompareKeysChange,
  onRefresh,
  isBusy,
  payload,
  errorMessage,
}: MultiSeriesComparePanelProps) {
  const normalized = normalizeSeries(payload);

  return (
    <div className="rounded-sm border border-theme-outline bg-theme-primary p-3">
      <div className="flex items-center justify-between gap-2 mb-2">
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
      <p className="body-xxs-regular text-theme-muted mb-2">
        쉼표로 구분된 키를 입력하세요. 각 시리즈는 첫 관측값 기준 100으로 정규화됩니다.
      </p>
      {errorMessage ? <p className="mb-2 body-xxs-regular text-amber-300">{errorMessage}</p> : null}
      <MultiLineChart
        series={normalized}
        height={220}
        formatValue={(v) => v.toFixed(1)}
      />
    </div>
  );
}
