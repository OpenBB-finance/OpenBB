import type { MacroRegimePoint } from "../../types/macro";

interface RegimeStatusCardProps {
  label: string | null;
  scores: MacroRegimePoint | null;
}

function tone(label: string | null): string {
  if (!label) return "text-theme-muted";
  if (label.includes("Risk-On")) return "text-emerald-300";
  if (label.includes("Risk-Off") || label.includes("Crisis")) return "text-red-300";
  if (label.includes("Stagflation")) return "text-amber-300";
  return "text-sky-300";
}

export function RegimeStatusCard({ label, scores }: RegimeStatusCardProps) {
  return (
    <div className="rounded-sm border border-theme-outline bg-theme-primary p-3">
      <p className="body-xs-medium text-theme-muted">Current Regime</p>
      <p className={`mt-1 body-sm-medium ${tone(label)}`}>{label ?? "-"}</p>
      {scores ? (
        <div className="mt-2 grid grid-cols-2 gap-1">
          <p className="body-xxs-regular text-theme-muted">Risk-On {scores.risk_on_score.toFixed(1)}</p>
          <p className="body-xxs-regular text-theme-muted">Inflation {scores.inflation_score.toFixed(1)}</p>
          <p className="body-xxs-regular text-theme-muted">Growth {scores.growth_score.toFixed(1)}</p>
          <p className="body-xxs-regular text-theme-muted">Liquidity {scores.liquidity_score.toFixed(1)}</p>
          <p className="body-xxs-regular text-theme-muted">Credit {scores.credit_stress_score.toFixed(1)}</p>
        </div>
      ) : (
        <p className="mt-2 body-xxs-regular text-theme-muted">No live score</p>
      )}
    </div>
  );
}
