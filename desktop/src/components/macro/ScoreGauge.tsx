interface ScoreGaugeProps {
  label: string;
  value: number | null | undefined;
  maxValue?: number;
  thresholds?: { warn: number; danger: number };
  invert?: boolean;
  advice?: string;
}

function gaugeColor(value: number, max: number, invert: boolean): string {
  const ratio = value / max;
  const effective = invert ? 1 - ratio : ratio;
  if (effective >= 0.7) return "bg-emerald-500";
  if (effective >= 0.4) return "bg-amber-400";
  return "bg-red-500";
}

function adviceText(label: string, value: number, max: number, invert: boolean): string {
  const ratio = value / max;
  if (invert) {
    if (ratio >= 0.7) return `${label} is elevated. Reduce the most rate- and credit-sensitive risk.`;
    if (ratio >= 0.4) return `${label} is mixed. Keep hedges balanced and avoid concentration.`;
    return `${label} is contained. Broad risk can stay constructive if other factors confirm.`;
  }
  if (ratio >= 0.7) return `${label} is supportive. Cyclicals and higher-beta exposure can stay active.`;
  if (ratio >= 0.4) return `${label} is balanced. Keep diversification and wait for confirmation.`;
  return `${label} is soft. Favor quality, resilience, and tighter risk budgets.`;
}

export function ScoreGauge({
  label,
  value,
  maxValue = 100,
  invert = false,
  advice,
}: ScoreGaugeProps) {
  const numericValue = typeof value === "number" && !Number.isNaN(value) ? value : 0;
  const clamped = Math.max(0, Math.min(numericValue, maxValue));
  const pct = (clamped / maxValue) * 100;
  const color = gaugeColor(clamped, maxValue, invert);
  const displayAdvice = advice || adviceText(label, clamped, maxValue, invert);
  const digits = maxValue <= 1 ? 2 : 1;

  return (
    <div className="rounded-sm bg-theme-secondary p-2.5">
      <div className="mb-1.5 flex items-center justify-between">
        <p className="body-xxs-medium text-theme-muted">{label}</p>
        <p className="body-xs-medium text-theme-primary">{numericValue.toFixed(digits)}</p>
      </div>
      <div className="h-2 w-full overflow-hidden rounded-full bg-theme-tertiary">
        <div
          className={`h-full rounded-full transition-all duration-500 ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <p className="mt-1.5 body-xxs-regular leading-tight text-theme-muted">{displayAdvice}</p>
    </div>
  );
}

interface RegimeScoreCardsProps {
  riskOn: number | null | undefined;
  inflation: number | null | undefined;
  growth: number | null | undefined;
  liquidity: number | null | undefined;
  creditStress: number | null | undefined;
  date: string | null | undefined;
}

export function RegimeScoreCards({
  riskOn,
  inflation,
  growth,
  liquidity,
  creditStress,
  date,
}: RegimeScoreCardsProps) {
  return (
    <div className="rounded-sm border border-theme-outline bg-theme-primary p-3">
      <div className="mb-2 flex items-center justify-between">
        <h3 className="body-sm-medium text-theme-primary">Macro Regime Scores</h3>
        {date ? <p className="body-xxs-regular text-theme-muted">as of {date}</p> : null}
      </div>
      <div className="grid grid-cols-1 gap-2">
        <ScoreGauge
          label="Risk-On"
          value={riskOn}
          advice={
            (riskOn ?? 0) >= 60
              ? "Risk appetite is firm. Higher-beta assets can stay active."
              : (riskOn ?? 0) >= 30
                ? "Risk appetite is mixed. Stay balanced across defensives and cyclicals."
                : "Risk appetite is weak. Tilt toward defensives, duration, or cash buffers."
          }
        />
        <ScoreGauge
          label="Inflation"
          value={inflation}
          invert
          advice={
            (inflation ?? 0) >= 70
              ? "Inflation pressure is high. Keep inflation hedges and duration control in focus."
              : (inflation ?? 0) >= 40
                ? "Inflation is mixed. Keep hedges balanced across real assets and rates."
                : "Inflation is contained. Longer duration can be reconsidered if growth also slows."
          }
        />
        <ScoreGauge
          label="Growth"
          value={growth}
          advice={
            (growth ?? 0) >= 60
              ? "Growth is holding up. Cyclicals and growth assets have room to work."
              : (growth ?? 0) >= 30
                ? "Growth is slowing. Reduce concentration and monitor recession-sensitive assets."
                : "Growth is weak. Favor defensives and cash-flow resilience."
          }
        />
        <ScoreGauge
          label="Liquidity"
          value={liquidity}
          advice={
            (liquidity ?? 0) >= 60
              ? "Liquidity is supportive. Risk assets have room to absorb volatility."
              : (liquidity ?? 0) >= 30
                ? "Liquidity is neutral. Position sizing matters more than outright beta."
                : "Liquidity is weak. Cut crowded trades and keep dry powder."
          }
        />
        <ScoreGauge
          label="Credit Stress"
          value={creditStress}
          invert
          advice={
            (creditStress ?? 0) >= 60
              ? "Credit stress is elevated. Trim spread risk and review liquidity buffers."
              : (creditStress ?? 0) >= 30
                ? "Credit conditions are mixed. Prefer higher quality and shorter spread duration."
                : "Credit stress is contained. Spreads remain supportive for selective risk."
          }
        />
      </div>
    </div>
  );
}
