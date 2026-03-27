import type {
  MacroCycleLevel,
  MacroCycleLevelSnapshot,
  MacroRegimePoint,
  MacroRegimeStateResponse,
} from "../../types/macro";
import { ScoreGauge } from "./ScoreGauge";

const LEVEL_LABELS: Record<MacroCycleLevel, string> = {
  expansion: "Expansion",
  late_expansion: "Early/Late Expansion",
  transition: "Transition",
  slowdown: "Slowdown",
  contraction: "Contraction",
};

const LEVEL_STYLES: Record<MacroCycleLevel, { badge: string; hint: string }> = {
  expansion: {
    badge: "border-emerald-500/50 bg-emerald-500/20 text-emerald-200",
    hint: "Broad growth and risk appetite remain supportive. Cyclical exposure can stay active.",
  },
  late_expansion: {
    badge: "border-lime-500/50 bg-lime-500/20 text-lime-200",
    hint: "Conditions still support risk, but late-cycle rollover risk is building.",
  },
  transition: {
    badge: "border-amber-500/50 bg-amber-500/20 text-amber-200",
    hint: "Cross-currents are rising. Keep positioning balanced and avoid concentration.",
  },
  slowdown: {
    badge: "border-orange-500/50 bg-orange-500/20 text-orange-200",
    hint: "Growth is softening. Quality and lower-beta positioning deserve more weight.",
  },
  contraction: {
    badge: "border-rose-500/50 bg-rose-500/20 text-rose-200",
    hint: "Risk management, liquidity, and defense should dominate allocation decisions.",
  },
};

const ACTION_STYLES: Record<MacroCycleLevelSnapshot["action_hint"], string> = {
  aggressive: "border-emerald-500/40 bg-emerald-500/15 text-emerald-200",
  neutral: "border-zinc-500/40 bg-zinc-500/15 text-zinc-200",
  defensive: "border-red-500/40 bg-red-500/15 text-red-200",
};

function clamp(value: number, lower: number, upper: number): number {
  return Math.max(lower, Math.min(value, upper));
}

function toScore(value: unknown): number {
  const numeric = Number(value);
  if (Number.isNaN(numeric) || !Number.isFinite(numeric)) {
    return 0;
  }
  return clamp(numeric, 0, 100);
}

function computeComposite(point: MacroRegimePoint): number {
  const riskOn = toScore(point.risk_on_score);
  const growth = toScore(point.growth_score);
  const liquidity = toScore(point.liquidity_score);
  const creditStress = toScore(point.credit_stress_score);
  const inflation = toScore(point.inflation_score);
  return clamp(
    0.3 * riskOn +
      0.25 * growth +
      0.2 * liquidity +
      0.15 * (100 - creditStress) +
      0.1 * (100 - inflation),
    0,
    100,
  );
}

function levelFromScore(score: number): MacroCycleLevel {
  if (score >= 70) {
    return "expansion";
  }
  if (score >= 55) {
    return "late_expansion";
  }
  if (score >= 40) {
    return "transition";
  }
  if (score >= 25) {
    return "slowdown";
  }
  return "contraction";
}

function daysSinceIsoDate(isoDate: string | null): number | null {
  if (!isoDate) {
    return null;
  }
  const parsed = new Date(`${isoDate}T00:00:00Z`);
  if (Number.isNaN(parsed.getTime())) {
    return null;
  }
  const now = new Date();
  const todayUtc = Date.UTC(now.getUTCFullYear(), now.getUTCMonth(), now.getUTCDate());
  const dateUtc = Date.UTC(parsed.getUTCFullYear(), parsed.getUTCMonth(), parsed.getUTCDate());
  return Math.max(0, Math.floor((todayUtc - dateUtc) / (24 * 60 * 60 * 1000)));
}

function actionHintFromSnapshot(
  score: number,
  riskOffProxy: boolean,
): MacroCycleLevelSnapshot["action_hint"] {
  if (riskOffProxy) {
    return "defensive";
  }
  if (score >= 65) {
    return "aggressive";
  }
  if (score >= 45) {
    return "neutral";
  }
  return "defensive";
}

function buildCycleLevelSnapshot(
  latestRegime: MacroRegimePoint | null,
  regimeState: MacroRegimeStateResponse | null,
  regimeSeries: MacroRegimePoint[],
): MacroCycleLevelSnapshot | null {
  if (!latestRegime) {
    return null;
  }

  const score = computeComposite(latestRegime);
  let level = levelFromScore(score);
  const riskOffProxy = Boolean(regimeState?.risk_off_proxy);
  const growthDown = Boolean(regimeState?.growth_down);
  const inflationUp = Boolean(regimeState?.inflation_up);

  if (riskOffProxy && growthDown && (level === "expansion" || level === "late_expansion")) {
    level = "transition";
  }

  const baseIndex = regimeSeries.length > 4 ? regimeSeries.length - 5 : -1;
  const baselinePoint = baseIndex >= 0 ? regimeSeries[baseIndex] : null;
  const baseline = baselinePoint ? computeComposite(baselinePoint) : score;

  return {
    score,
    level,
    delta_4w: score - baseline,
    as_of: latestRegime.date || null,
    stale_days: daysSinceIsoDate(latestRegime.date || null),
    risk_off_proxy: riskOffProxy,
    growth_down: growthDown,
    inflation_up: inflationUp,
    action_hint: actionHintFromSnapshot(score, riskOffProxy),
  };
}

function statePill(active: boolean, label: string, onText: string, offText: string): JSX.Element {
  return (
    <span
      className={`rounded-full border px-2.5 py-1 body-xxs-medium ${
        active
          ? "border-amber-500/40 bg-amber-500/15 text-amber-200"
          : "border-theme-outline bg-theme-secondary text-theme-muted"
      }`}
    >
      {label}: {active ? onText : offText}
    </span>
  );
}

function scoreTile(label: string, value: number | null | undefined, invert = false): JSX.Element {
  const score = toScore(value ?? 0);
  const tone = invert ? 100 - score : score;
  const toneClass =
    tone >= 70
      ? "text-emerald-300"
      : tone >= 40
        ? "text-amber-300"
        : "text-red-300";
  return (
    <div className="rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2">
      <p className="body-xxs-regular text-theme-muted">{label}</p>
      <p className={`body-sm-medium ${toneClass}`}>{score.toFixed(1)}</p>
    </div>
  );
}

interface MacroRegimeSummaryProps {
  latestRegime: MacroRegimePoint | null;
  regimeState: MacroRegimeStateResponse | null;
  regimeSeries: MacroRegimePoint[];
}

export function MacroRegimeSummary({
  latestRegime,
  regimeState,
  regimeSeries,
}: MacroRegimeSummaryProps) {
  const snapshot = buildCycleLevelSnapshot(latestRegime, regimeState, regimeSeries);

  if (!snapshot || !latestRegime) {
    return (
      <div className="rounded-md border border-dashed border-theme-outline bg-theme-secondary px-4 py-5">
        <div className="body-sm-medium text-theme-primary">Regime Summary</div>
        <p className="mt-1 body-sm-regular text-theme-muted">
          No macro regime score is available yet. Refresh the macro dataset or wait for the next update cycle.
        </p>
      </div>
    );
  }

  const levelMeta = LEVEL_STYLES[snapshot.level];

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 gap-4 xl:grid-cols-[220px_minmax(0,1fr)]">
        <div className="rounded-md border border-theme-outline bg-theme-secondary px-4 py-4">
          <div className="body-xxs-regular uppercase tracking-[0.12em] text-theme-muted">
            Composite Score
          </div>
          <div
            data-testid="macro-cycle-level-score"
            className="mt-2 body-lg-medium text-theme-primary"
          >
            {snapshot.score.toFixed(1)}
          </div>
          <div
            className={`mt-1 body-xxs-medium ${
              snapshot.delta_4w >= 0 ? "text-emerald-300" : "text-red-300"
            }`}
          >
            4W delta {snapshot.delta_4w >= 0 ? "+" : ""}
            {snapshot.delta_4w.toFixed(1)}
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            <span className={`rounded-full border px-2.5 py-1 body-xxs-medium ${levelMeta.badge}`}>
              {LEVEL_LABELS[snapshot.level]}
            </span>
            <span className={`rounded-full border px-2.5 py-1 body-xxs-medium ${ACTION_STYLES[snapshot.action_hint]}`}>
              {snapshot.action_hint}
            </span>
          </div>
        </div>

        <div className="grid grid-cols-1 gap-3 lg:grid-cols-3">
          <div className="rounded-md border border-theme-outline bg-theme-secondary px-3 py-3">
            <div className="body-xxs-regular text-theme-muted">Cycle Level</div>
            <div className="mt-1 body-sm-medium text-theme-primary">{LEVEL_LABELS[snapshot.level]}</div>
            <p className="mt-2 body-xxs-regular text-theme-muted">{levelMeta.hint}</p>
          </div>
          <div className="rounded-md border border-theme-outline bg-theme-secondary px-3 py-3">
            <div className="body-xxs-regular text-theme-muted">As Of</div>
            <div className="mt-1 body-sm-medium text-theme-primary">{snapshot.as_of ?? "n/a"}</div>
            <p className="mt-2 body-xxs-regular text-theme-muted">
              {snapshot.stale_days === null ? "Freshness unavailable." : `Stale by ${snapshot.stale_days} day(s).`}
            </p>
          </div>
          <div className="rounded-md border border-theme-outline bg-theme-secondary px-3 py-3">
            <div className="body-xxs-regular text-theme-muted">Action Bias</div>
            <div className="mt-1 body-sm-medium capitalize text-theme-primary">{snapshot.action_hint}</div>
            <p className="mt-2 body-xxs-regular text-theme-muted">
              Use this as a top-down bias, then confirm with study-specific evidence before sizing risk.
            </p>
          </div>
        </div>
      </div>

      <div className="flex flex-wrap gap-2">
        {statePill(snapshot.inflation_up, "Inflation", "up", "stable")}
        {statePill(snapshot.growth_down, "Growth", "down", "stable")}
        {statePill(snapshot.risk_off_proxy, "Risk", "off", "on")}
      </div>

      <div className="grid grid-cols-2 gap-2 xl:grid-cols-5">
        {scoreTile("Risk", latestRegime.risk_on_score)}
        {scoreTile("Growth", latestRegime.growth_score)}
        {scoreTile("Inflation", latestRegime.inflation_score, true)}
        {scoreTile("Liquidity", latestRegime.liquidity_score)}
        {scoreTile("Credit Stress", latestRegime.credit_stress_score, true)}
      </div>

      <div className="grid grid-cols-1 gap-3 xl:grid-cols-2">
        <ScoreGauge
          label="Risk-On"
          value={latestRegime.risk_on_score}
          advice="Higher scores support cyclical and higher-beta exposure."
        />
        <ScoreGauge
          label="Growth"
          value={latestRegime.growth_score}
          advice="Growth acts as the core demand backdrop for the study basket."
        />
        <ScoreGauge
          label="Inflation"
          value={latestRegime.inflation_score}
          invert
          advice="Higher inflation pressure argues for tighter duration and stronger hedge discipline."
        />
        <ScoreGauge
          label="Liquidity"
          value={latestRegime.liquidity_score}
          advice="Liquidity determines how much shock absorption the market has."
        />
        <ScoreGauge
          label="Credit Stress"
          value={latestRegime.credit_stress_score}
          invert
          advice="Credit stress usually shows up before broad risk repricing becomes obvious."
        />
      </div>
    </div>
  );
}
