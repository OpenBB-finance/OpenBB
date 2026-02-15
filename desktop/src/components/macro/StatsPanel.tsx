import type { MacroSeriesMeta, MacroSeriesStats } from "../../types/macro";

function valueText(value: number | null | undefined, digits = 4): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "-";
  }
  return value.toFixed(digits);
}

interface StatsPanelProps {
  meta: MacroSeriesMeta | null;
  stats: MacroSeriesStats | null;
}

export function StatsPanel({ meta, stats }: StatsPanelProps) {
  return (
    <div className="rounded-sm border border-theme-outline bg-theme-primary p-3">
      <h3 className="body-sm-medium text-theme-primary">Stats</h3>
      {!meta || !stats ? (
        <p className="mt-2 body-xs-regular text-theme-muted">No series selected.</p>
      ) : (
        <div className="mt-2 space-y-2">
          <div className="rounded-sm bg-theme-secondary p-2">
            <p className="body-xxs-regular text-theme-muted">Key</p>
            <p className="body-xs-medium text-theme-primary">{meta.key}</p>
          </div>
          <div className="rounded-sm bg-theme-secondary p-2">
            <p className="body-xxs-regular text-theme-muted">Title</p>
            <p className="body-xs-medium text-theme-primary">{meta.title || "-"}</p>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Last</p>
              <p className="body-xs-medium text-theme-primary">{valueText(stats.last)}</p>
            </div>
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Change 1M</p>
              <p className="body-xs-medium text-theme-primary">{valueText(stats.change_1m)}</p>
            </div>
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Change 3M</p>
              <p className="body-xs-medium text-theme-primary">{valueText(stats.change_3m)}</p>
            </div>
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Z</p>
              <p className="body-xs-medium text-theme-primary">{valueText(stats.z, 3)}</p>
            </div>
            <div className="col-span-2 rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Percentile 5Y</p>
              <p className="body-xs-medium text-theme-primary">{valueText(stats.percentile_5y, 3)}</p>
            </div>
          </div>
          <div className="rounded-sm bg-theme-secondary p-2">
            <p className="body-xxs-regular text-theme-muted">Meta</p>
            <p className="body-xs-regular text-theme-primary">
              freq: {meta.frequency || "-"} | units: {meta.units || "-"} | lag: {meta.lag_applied || "-"}
            </p>
          </div>
          {meta.warning ? (
            <div className="rounded-sm border border-amber-500/50 bg-amber-500/10 p-2">
              <p className="body-xs-regular text-amber-300">{meta.warning}</p>
            </div>
          ) : null}
        </div>
      )}
    </div>
  );
}
