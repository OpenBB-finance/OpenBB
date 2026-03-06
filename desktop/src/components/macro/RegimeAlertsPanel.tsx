import type { MacroAlertItem, MacroRegimePoint, MacroRegimeStateResponse } from "../../types/macro";
import { RegimeScoreCards } from "./ScoreGauge";

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
  const riskOnScore = latestRegime?.risk_on_score ?? 50;
  const suggestedProfile = riskOnScore < 40 ? "defensive" : "aggressive";
  const suggestedProfileLabel = suggestedProfile === "defensive" ? "Defensive" : "Aggressive";

  return (
    <div className="space-y-3">
      <div className="rounded-sm border border-theme-outline bg-theme-primary p-3">
        <h3 className="body-sm-medium text-theme-primary mb-2">Regime State</h3>
        <div className="grid grid-cols-3 gap-2">
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
      </div>

      <RegimeScoreCards
        riskOn={latestRegime?.risk_on_score}
        inflation={latestRegime?.inflation_score}
        growth={latestRegime?.growth_score}
        liquidity={latestRegime?.liquidity_score}
        creditStress={latestRegime?.credit_stress_score}
        date={latestRegime?.date}
      />

      <div className="rounded-sm border border-theme-outline bg-theme-primary p-3">
        <p className="body-xs-medium text-theme-primary mb-2">Quant Lab 연동</p>
        <div className="grid grid-cols-2 gap-2">
          <a
            href={`/quant?macro_hint=${suggestedProfile}`}
            className="rounded-sm border border-sky-500/30 bg-sky-500/10 p-2 text-center hover:bg-sky-500/20 transition-colors"
          >
            <p className="body-xxs-medium text-sky-300">Quant Lab에서 적용</p>
            <p className="body-xxs-regular text-sky-200/60 mt-0.5">
              {`→ ${suggestedProfileLabel} profile hint`}
            </p>
          </a>
          <a
            href="/dashboard"
            className="rounded-sm border border-theme-outline bg-theme-secondary p-2 text-center hover:bg-theme-tertiary transition-colors"
          >
            <p className="body-xxs-medium text-theme-primary">Dashboard 보기</p>
            <p className="body-xxs-regular text-theme-muted mt-0.5">전략 성과 모니터링</p>
          </a>
        </div>
        <p className="body-xxs-regular text-theme-muted mt-2">
          Hint applies when Quant Lab is in default universe mode. Universe set mode can override profile selection.
        </p>
      </div>

      <div className="rounded-sm border border-theme-outline bg-theme-primary p-3">
        <div className="flex items-center justify-between mb-2">
          <p className="body-xs-medium text-theme-primary">Active Alerts</p>
          <span className="body-xxs-regular text-theme-muted">
            {currentAlerts.length} active / {historyAlerts.length} history
          </span>
        </div>
        {currentAlerts.length === 0 ? (
          <p className="body-xs-regular text-theme-muted">활성 알림이 없습니다.</p>
        ) : (
          <ul className="space-y-1.5">
            {currentAlerts.map((item, index) => (
              <li key={`${item.rule_id}-${index}`} className="rounded-sm border border-theme-outline bg-theme-secondary p-2">
                <div className="flex items-start justify-between gap-2">
                  <p className="body-xs-regular text-theme-primary flex-1">{item.message}</p>
                  <span className={`rounded-sm border px-2 py-[2px] body-xxs-medium shrink-0 ${severityClass(item.severity)}`}>
                    {item.severity.toUpperCase()}
                  </span>
                </div>
                <p className="body-xxs-regular text-theme-muted mt-1">
                  {item.triggered_at} | value: {item.value.toFixed(3)} | threshold: {item.threshold.toFixed(3)}
                </p>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
