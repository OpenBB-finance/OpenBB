import type { MacroAlertItem, MacroRegimePoint, MacroRegimeStateResponse } from "../../types/macro";

function valueText(value: number | null | undefined, digits = 1): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "-";
  }
  return value.toFixed(digits);
}

function severityClass(severity: MacroAlertItem["severity"]): string {
  if (severity === "critical") {
    return "border-red-500/50 bg-red-500/15 text-red-300";
  }
  if (severity === "warning") {
    return "border-amber-500/50 bg-amber-500/15 text-amber-300";
  }
  return "border-sky-500/50 bg-sky-500/15 text-sky-300";
}

interface RegimeAlertsPanelProps {
  latestRegime: MacroRegimePoint | null;
  regimeState: MacroRegimeStateResponse | null;
  currentAlerts: MacroAlertItem[];
  historyAlerts: MacroAlertItem[];
}

function lightClass(active: boolean): string {
  return active ? "border-emerald-500/50 bg-emerald-500/15 text-emerald-300" : "border-zinc-500/50 bg-zinc-500/15 text-zinc-300";
}

export function RegimeAlertsPanel({ latestRegime, regimeState, currentAlerts, historyAlerts }: RegimeAlertsPanelProps) {
  return (
    <div className="rounded-sm border border-theme-outline bg-theme-primary p-3">
      <h3 className="body-sm-medium text-theme-primary">Regime + Alerts</h3>
      <div className="mt-2 grid grid-cols-3 gap-2">
        <div className={`rounded-sm border p-2 ${lightClass(Boolean(regimeState?.inflation_up))}`}>
          <p className="body-xxs-regular">Inflation Up</p>
          <p className="body-xs-medium">{regimeState?.inflation_up ? "ON" : "OFF"}</p>
        </div>
        <div className={`rounded-sm border p-2 ${lightClass(Boolean(regimeState?.growth_down))}`}>
          <p className="body-xxs-regular">Growth Down</p>
          <p className="body-xs-medium">{regimeState?.growth_down ? "ON" : "OFF"}</p>
        </div>
        <div className={`rounded-sm border p-2 ${lightClass(Boolean(regimeState?.risk_off_proxy))}`}>
          <p className="body-xxs-regular">Risk Off</p>
          <p className="body-xs-medium">{regimeState?.risk_off_proxy ? "ON" : "OFF"}</p>
        </div>
      </div>
      <div className="mt-2 grid grid-cols-2 gap-2">
        <div className="rounded-sm bg-theme-secondary p-2">
          <p className="body-xxs-regular text-theme-muted">Risk-On</p>
          <p className="body-xs-medium text-theme-primary">{valueText(latestRegime?.risk_on_score)}</p>
        </div>
        <div className="rounded-sm bg-theme-secondary p-2">
          <p className="body-xxs-regular text-theme-muted">Inflation</p>
          <p className="body-xs-medium text-theme-primary">{valueText(latestRegime?.inflation_score)}</p>
        </div>
        <div className="rounded-sm bg-theme-secondary p-2">
          <p className="body-xxs-regular text-theme-muted">Growth</p>
          <p className="body-xs-medium text-theme-primary">{valueText(latestRegime?.growth_score)}</p>
        </div>
        <div className="rounded-sm bg-theme-secondary p-2">
          <p className="body-xxs-regular text-theme-muted">Liquidity</p>
          <p className="body-xs-medium text-theme-primary">{valueText(latestRegime?.liquidity_score)}</p>
        </div>
        <div className="col-span-2 rounded-sm bg-theme-secondary p-2">
          <p className="body-xxs-regular text-theme-muted">Credit Stress</p>
          <p className="body-xs-medium text-theme-primary">{valueText(latestRegime?.credit_stress_score)}</p>
          <p className="body-xxs-regular text-theme-muted mt-1">as of {latestRegime?.date || "-"}</p>
        </div>
      </div>

      <div className="mt-3">
        <p className="body-xs-medium text-theme-primary">Current Alerts</p>
        {currentAlerts.length === 0 ? (
          <p className="mt-1 body-xs-regular text-theme-muted">No active alerts.</p>
        ) : (
          <ul className="mt-1 space-y-1">
            {currentAlerts.map((item, index) => (
              <li key={`${item.rule_id}-${index}`} className="rounded-sm border border-theme-outline bg-theme-secondary p-2">
                <div className="flex items-start justify-between gap-2">
                  <p className="body-xs-regular text-theme-primary">{item.message}</p>
                  <span className={`rounded-sm border px-2 py-[2px] body-xxs-medium ${severityClass(item.severity)}`}>
                    {item.severity.toUpperCase()}
                  </span>
                </div>
                <p className="body-xxs-regular text-theme-muted mt-1">{item.triggered_at}</p>
              </li>
            ))}
          </ul>
        )}
      </div>

      <p className="mt-2 body-xxs-regular text-theme-muted">History events: {historyAlerts.length}</p>
    </div>
  );
}
