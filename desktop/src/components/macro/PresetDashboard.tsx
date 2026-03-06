import { useCallback } from "react";
import type {
  MacroCycleLevel,
  MacroCycleLevelSnapshot,
  MacroRegimePoint,
  MacroRegimeStateResponse,
} from "../../types/macro";

export interface MacroPresetConfig {
  id: string;
  label: string;
  description: string;
  category:
    | "cycle"
    | "inflation"
    | "financial"
    | "risk"
    | "housing"
    | "commodity"
    | "liquidity"
    | "rates"
    | "labor"
    | "credit"
    | "demand";
  compareKeys: string;
  leftSymbol: string;
  rightSymbol: string;
  ratioTicker: string;
  expression: string;
  interpretation: string;
}

interface PresetMeta {
  keyIndicators: string[];
  portfolioAction: string;
  actionTag: "aggressive" | "defensive" | "neutral" | "monitor";
  watchLevel: string;
  relatedETFs: string[];
}

const PRESETS: MacroPresetConfig[] = [
  {
    id: "business_cycle",
    label: "Business Cycle",
    description: "Track labor, production, and sentiment for cycle timing.",
    category: "cycle",
    compareKeys: "FRED:UNRATE,FRED:PAYEMS,FRED:INDPRO,FRED:UMCSENT",
    leftSymbol: "FRED:UNRATE",
    rightSymbol: "FRED:PAYEMS",
    ratioTicker: "XLY/XLP",
    expression: "FRED:UNRATE",
    interpretation:
      "Higher unemployment with weaker payroll growth increases recession risk. Favor defensives when labor momentum rolls over.",
  },
  {
    id: "inflation",
    label: "Inflation",
    description: "Monitor inflation pressure and expectations across CPI and breakevens.",
    category: "inflation",
    compareKeys: "FRED:CPIAUCSL,FRED:CPILFESL,FRED:T5YIE,FRED:T10YIE",
    leftSymbol: "FRED:CPIAUCSL",
    rightSymbol: "FRED:T5YIE",
    ratioTicker: "TIP/IEF",
    expression: "FRED:CPIAUCSL",
    interpretation:
      "Persistent CPI acceleration and rising breakevens support inflation hedges and shorter duration exposure.",
  },
  {
    id: "financial_conditions",
    label: "Financial Conditions",
    description: "Follow policy rates, curve shape, and credit spreads.",
    category: "financial",
    compareKeys: "FRED:FEDFUNDS,FRED:DGS10,FRED:DGS2,FRED:BAMLH0A0HYM2",
    leftSymbol: "FRED:DGS10",
    rightSymbol: "FRED:DGS2",
    ratioTicker: "HYG/LQD",
    expression: "FRED:DGS10-FRED:DGS2",
    interpretation:
      "A deeper inversion plus wider high-yield spreads usually means tighter financial conditions and weaker risk appetite.",
  },
  {
    id: "global_risk",
    label: "Global Risk",
    description: "Track volatility, dollar strength, oil, and gold for risk-off pressure.",
    category: "risk",
    compareKeys:
      "FRED:VIXCLS,FRED:DTWEXBGS,FRED:DCOILWTICO,FRED:GOLDAMGBD228NLBM",
    leftSymbol: "FRED:VIXCLS",
    rightSymbol: "FRED:GOLDAMGBD228NLBM",
    ratioTicker: "GLD/SPY",
    expression: "FRED:VIXCLS",
    interpretation:
      "Rising VIX with stronger gold and USD often reflects global risk-off positioning and tighter funding conditions.",
  },
  {
    id: "housing",
    label: "Housing",
    description: "Watch mortgage rates, starts, and house prices for real-economy stress.",
    category: "housing",
    compareKeys: "FRED:MORTGAGE30US,FRED:HOUST,FRED:CSUSHPINSA",
    leftSymbol: "FRED:MORTGAGE30US",
    rightSymbol: "FRED:HOUST",
    ratioTicker: "VNQ/SPY",
    expression: "FRED:MORTGAGE30US",
    interpretation:
      "Higher mortgage rates and falling starts usually weaken housing beta and building-related cyclicals.",
  },
  {
    id: "copper_gold",
    label: "Copper/Gold",
    description: "Use copper-to-gold as a growth and risk sentiment lead indicator.",
    category: "commodity",
    compareKeys: "HG,GC,FRED:DGS10,FRED:BAMLH0A0HYM2",
    leftSymbol: "HG",
    rightSymbol: "GC",
    ratioTicker: "COPX/GLD",
    expression: "((HG/16)/(GC*0.911458))*1000",
    interpretation:
      "Falling copper-to-gold ratio often leads to slower growth and lower cyclical risk-taking.",
  },
  {
    id: "liquidity_pulse",
    label: "Liquidity Pulse",
    description: "Measure liquidity breadth with money growth and financial stress index.",
    category: "liquidity",
    compareKeys: "FRED:M2SL,FRED:NFCI,SPY/IEF",
    leftSymbol: "FRED:M2SL",
    rightSymbol: "FRED:NFCI",
    ratioTicker: "SPY/IEF",
    expression: "FRED:M2SL",
    interpretation:
      "Improving liquidity with easing NFCI tends to support beta and carry; tightening suggests de-risking.",
  },
  {
    id: "dollar_rates",
    label: "Dollar/Rates",
    description: "Track dollar and rate regime shifts for cross-asset pressure.",
    category: "rates",
    compareKeys: "FRED:DTWEXBGS,FRED:DGS10,FRED:TB3MS,FRED:DGS2",
    leftSymbol: "FRED:DTWEXBGS",
    rightSymbol: "FRED:DGS10",
    ratioTicker: "UUP/TLT",
    expression: "FRED:DTWEXBGS",
    interpretation:
      "A stronger dollar with higher real rates can tighten global financial conditions and pressure risk assets.",
  },
  {
    id: "labor_momentum",
    label: "Labor Momentum",
    description: "Focus on labor trend shifts before they appear in GDP revisions.",
    category: "labor",
    compareKeys: "FRED:UNRATE,FRED:ICSA,FRED:PAYEMS,FRED:CES0500000003",
    leftSymbol: "FRED:PAYEMS",
    rightSymbol: "FRED:UNRATE",
    ratioTicker: "XLY/XLP",
    expression: "FRED:PAYEMS",
    interpretation:
      "Payroll deceleration with rising claims is a late-cycle warning and often precedes defensive rotations.",
  },
  {
    id: "credit_cycle",
    label: "Credit Cycle",
    description: "Monitor spread stress and curve shape for funding regime changes.",
    category: "credit",
    compareKeys: "FRED:BAA10Y,FRED:BAMLH0A0HYM2,FRED:DGS10,FRED:DGS2",
    leftSymbol: "FRED:BAA10Y",
    rightSymbol: "FRED:DGS10",
    ratioTicker: "HYG/LQD",
    expression: "FRED:BAA10Y",
    interpretation:
      "Widening credit spreads with curve stress signals weaker financing conditions and risk premium repricing.",
  },
  {
    id: "consumer_demand",
    label: "Consumer Demand",
    description: "Track spending and confidence to gauge household demand durability.",
    category: "demand",
    compareKeys: "FRED:RSAFS,FRED:UMCSENT,FRED:PI,FRED:UNRATE",
    leftSymbol: "FRED:RSAFS",
    rightSymbol: "FRED:UMCSENT",
    ratioTicker: "XLY/XLP",
    expression: "FRED:RSAFS",
    interpretation:
      "Soft retail and confidence trends point to consumer slowdown and lower cyclical earnings momentum.",
  },
  {
    id: "energy_shock",
    label: "Energy Shock",
    description: "Watch oil shock transmission into inflation and risk positioning.",
    category: "commodity",
    compareKeys: "FRED:DCOILWTICO,FRED:CPIAUCSL,FRED:T5YIE,FRED:INDPRO",
    leftSymbol: "FRED:DCOILWTICO",
    rightSymbol: "FRED:CPIAUCSL",
    ratioTicker: "XLE/SPY",
    expression: "FRED:DCOILWTICO",
    interpretation:
      "Oil spikes can tighten real income and lift inflation pressure, often reducing broad equity breadth.",
  },
];

const PRESET_META: Record<string, PresetMeta> = {
  business_cycle: {
    keyIndicators: ["UNRATE", "PAYEMS", "INDPRO"],
    portfolioAction: "Rotate toward defensives when labor momentum weakens.",
    actionTag: "monitor",
    watchLevel: "UNRATE trend > +0.3pp over 3 months",
    relatedETFs: ["XLY", "XLP", "TLT", "SHY"],
  },
  inflation: {
    keyIndicators: ["CPI", "CORE CPI", "T5YIE"],
    portfolioAction: "Favor inflation hedges and shorter duration in pressure spikes.",
    actionTag: "neutral",
    watchLevel: "T5YIE > 2.5 and CPI acceleration",
    relatedETFs: ["TIP", "GLD", "DJP", "IEF"],
  },
  financial_conditions: {
    keyIndicators: ["FEDFUNDS", "10Y-2Y", "HY OAS"],
    portfolioAction: "Reduce credit beta when inversion and spreads worsen together.",
    actionTag: "defensive",
    watchLevel: "10Y-2Y < 0 and HY OAS > 400bp",
    relatedETFs: ["HYG", "LQD", "BIL", "SHV"],
  },
  global_risk: {
    keyIndicators: ["VIX", "DXY", "WTI"],
    portfolioAction: "Trim equity risk when volatility and dollar stress rise together.",
    actionTag: "defensive",
    watchLevel: "VIX > 25 with rising DXY",
    relatedETFs: ["GLD", "UUP", "USO", "VIXY"],
  },
  housing: {
    keyIndicators: ["MORTGAGE30Y", "HOUST", "CSUSHPINSA"],
    portfolioAction: "Lower real-estate beta on prolonged housing demand slowdown.",
    actionTag: "monitor",
    watchLevel: "Mortgage30Y > 7 with falling starts",
    relatedETFs: ["VNQ", "IYR", "XHB", "ITB"],
  },
  copper_gold: {
    keyIndicators: ["HG", "GC", "Cu/Au Ratio"],
    portfolioAction: "De-risk cyclicals when copper/gold trend breaks down.",
    actionTag: "aggressive",
    watchLevel: "Cu/Au ratio drops > 20 over regime window",
    relatedETFs: ["COPX", "GLD", "DBC", "XME"],
  },
  liquidity_pulse: {
    keyIndicators: ["M2SL", "NFCI", "SPY/IEF"],
    portfolioAction: "Increase risk only when liquidity and conditions both improve.",
    actionTag: "monitor",
    watchLevel: "M2 trend up and NFCI easing",
    relatedETFs: ["SPY", "IEF", "QQQ", "BIL"],
  },
  dollar_rates: {
    keyIndicators: ["DXY", "DGS10", "TB3MS"],
    portfolioAction: "Stay selective on risk when USD and front-end rates both rise.",
    actionTag: "neutral",
    watchLevel: "DXY breakout with rising real yields",
    relatedETFs: ["UUP", "TLT", "IEF", "SHY"],
  },
  labor_momentum: {
    keyIndicators: ["PAYEMS", "UNRATE", "ICSA"],
    portfolioAction: "Reduce cyclical risk when claims rise with payroll deceleration.",
    actionTag: "monitor",
    watchLevel: "PAYEMS trend down and ICSA trend up",
    relatedETFs: ["XLY", "XLP", "IWM", "SPY"],
  },
  credit_cycle: {
    keyIndicators: ["BAA10Y", "HY OAS", "10Y-2Y"],
    portfolioAction: "Cut lower-quality credit when spread stress broadens.",
    actionTag: "defensive",
    watchLevel: "BAA10Y and HY OAS widen together",
    relatedETFs: ["HYG", "LQD", "JNK", "TLT"],
  },
  consumer_demand: {
    keyIndicators: ["RSAFS", "UMCSENT", "PI"],
    portfolioAction: "Lower discretionary tilt on demand downshifts.",
    actionTag: "neutral",
    watchLevel: "Retail sales and sentiment both trending lower",
    relatedETFs: ["XLY", "XLP", "VCR", "VDC"],
  },
  energy_shock: {
    keyIndicators: ["WTI", "CPI", "T5YIE"],
    portfolioAction: "Hedge inflation shock risk when oil trend accelerates.",
    actionTag: "monitor",
    watchLevel: "WTI surge with breakeven inflation rise",
    relatedETFs: ["XLE", "SPY", "USO", "TIP"],
  },
};

const CATEGORY_STYLES: Record<
  MacroPresetConfig["category"],
  { border: string; bg: string; text: string; chip: string }
> = {
  cycle: {
    border: "border-blue-500/40",
    bg: "bg-blue-500/10",
    text: "text-blue-200",
    chip: "bg-blue-500/20",
  },
  inflation: {
    border: "border-orange-500/40",
    bg: "bg-orange-500/10",
    text: "text-orange-200",
    chip: "bg-orange-500/20",
  },
  financial: {
    border: "border-purple-500/40",
    bg: "bg-purple-500/10",
    text: "text-purple-200",
    chip: "bg-purple-500/20",
  },
  risk: {
    border: "border-rose-500/40",
    bg: "bg-rose-500/10",
    text: "text-rose-200",
    chip: "bg-rose-500/20",
  },
  housing: {
    border: "border-teal-500/40",
    bg: "bg-teal-500/10",
    text: "text-teal-200",
    chip: "bg-teal-500/20",
  },
  commodity: {
    border: "border-amber-500/40",
    bg: "bg-amber-500/10",
    text: "text-amber-200",
    chip: "bg-amber-500/20",
  },
  liquidity: {
    border: "border-cyan-500/40",
    bg: "bg-cyan-500/10",
    text: "text-cyan-200",
    chip: "bg-cyan-500/20",
  },
  rates: {
    border: "border-indigo-500/40",
    bg: "bg-indigo-500/10",
    text: "text-indigo-200",
    chip: "bg-indigo-500/20",
  },
  labor: {
    border: "border-emerald-500/40",
    bg: "bg-emerald-500/10",
    text: "text-emerald-200",
    chip: "bg-emerald-500/20",
  },
  credit: {
    border: "border-red-500/40",
    bg: "bg-red-500/10",
    text: "text-red-200",
    chip: "bg-red-500/20",
  },
  demand: {
    border: "border-sky-500/40",
    bg: "bg-sky-500/10",
    text: "text-sky-200",
    chip: "bg-sky-500/20",
  },
};

const ACTION_TAG_STYLES: Record<PresetMeta["actionTag"], string> = {
  aggressive: "border-emerald-500/40 bg-emerald-500/20 text-emerald-200",
  defensive: "border-red-500/40 bg-red-500/20 text-red-200",
  neutral: "border-zinc-500/40 bg-zinc-500/20 text-zinc-200",
  monitor: "border-sky-500/40 bg-sky-500/20 text-sky-200",
};

const ACTION_TAG_LABELS: Record<PresetMeta["actionTag"], string> = {
  aggressive: "Aggressive",
  defensive: "Defensive",
  neutral: "Neutral",
  monitor: "Monitor",
};

const LEVEL_LABELS: Record<MacroCycleLevel, string> = {
  expansion: "Expansion",
  late_expansion: "Early/Late Expansion",
  transition: "Transition",
  slowdown: "Slowdown",
  contraction: "Contraction",
};

const LEVEL_STYLES: Record<
  MacroCycleLevel,
  { badge: string; hint: string }
> = {
  expansion: {
    badge: "border-emerald-500/50 bg-emerald-500/20 text-emerald-200",
    hint: "Risk appetite can stay elevated with selective cyclicals.",
  },
  late_expansion: {
    badge: "border-lime-500/50 bg-lime-500/20 text-lime-200",
    hint: "Stay pro-risk but monitor late-cycle rollover risk.",
  },
  transition: {
    badge: "border-amber-500/50 bg-amber-500/20 text-amber-200",
    hint: "Keep balanced exposure and reduce concentration risk.",
  },
  slowdown: {
    badge: "border-orange-500/50 bg-orange-500/20 text-orange-200",
    hint: "Favor quality and lower beta while preserving optionality.",
  },
  contraction: {
    badge: "border-rose-500/50 bg-rose-500/20 text-rose-200",
    hint: "Prioritize defense, liquidity, and drawdown control.",
  },
};

interface PresetDashboardProps {
  activePresetId: string | null;
  onApplyPreset: (preset: MacroPresetConfig) => void;
  latestRegime: MacroRegimePoint | null;
  regimeState: MacroRegimeStateResponse | null;
  regimeSeries: MacroRegimePoint[];
}

function clamp(value: number, lower: number, upper: number): number {
  return Math.max(lower, Math.min(value, upper));
}

function toScore(value: unknown): number {
  const out = Number(value);
  if (Number.isNaN(out) || !Number.isFinite(out)) {
    return 0;
  }
  return clamp(out, 0, 100);
}

function computeComposite(point: MacroRegimePoint): number {
  const riskOn = toScore(point.risk_on_score);
  const growth = toScore(point.growth_score);
  const liquidity = toScore(point.liquidity_score);
  const creditStress = toScore(point.credit_stress_score);
  const inflation = toScore(point.inflation_score);
  const score =
    0.3 * riskOn +
    0.25 * growth +
    0.2 * liquidity +
    0.15 * (100 - creditStress) +
    0.1 * (100 - inflation);
  return clamp(score, 0, 100);
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
  const todayUtc = Date.UTC(
    now.getUTCFullYear(),
    now.getUTCMonth(),
    now.getUTCDate(),
  );
  const dateUtc = Date.UTC(
    parsed.getUTCFullYear(),
    parsed.getUTCMonth(),
    parsed.getUTCDate(),
  );
  const diff = Math.floor((todayUtc - dateUtc) / (24 * 60 * 60 * 1000));
  return Math.max(0, diff);
}

function actionHintFromSnapshot(
  score: number,
  riskOffProxy: boolean,
): "aggressive" | "neutral" | "defensive" {
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
  const basePoint = baseIndex >= 0 ? regimeSeries[baseIndex] : null;
  const baseline = basePoint ? computeComposite(basePoint) : score;
  const delta4w = score - baseline;
  const asOf = latestRegime.date || null;
  const staleDays = daysSinceIsoDate(asOf);

  return {
    score,
    level,
    delta_4w: delta4w,
    as_of: asOf,
    stale_days: staleDays,
    risk_off_proxy: riskOffProxy,
    growth_down: growthDown,
    inflation_up: inflationUp,
    action_hint: actionHintFromSnapshot(score, riskOffProxy),
  };
}

function axisTile(label: string, value: number | null | undefined): JSX.Element {
  const score = toScore(value ?? 0);
  return (
    <div className="rounded-sm border border-theme-outline bg-theme-secondary px-2 py-1.5">
      <p className="body-xxs-regular text-theme-muted">{label}</p>
      <p className="body-xs-medium text-theme-primary">{score.toFixed(1)}</p>
    </div>
  );
}

export function PresetDashboard({
  activePresetId,
  onApplyPreset,
  latestRegime,
  regimeState,
  regimeSeries,
}: PresetDashboardProps) {
  const activePreset = activePresetId
    ? PRESETS.find((preset) => preset.id === activePresetId) ?? null
    : null;
  const activeMeta = activePresetId ? PRESET_META[activePresetId] ?? null : null;
  const cycleSnapshot = buildCycleLevelSnapshot(
    latestRegime,
    regimeState,
    regimeSeries,
  );

  const handlePresetClick = useCallback(
    (preset: MacroPresetConfig) => {
      onApplyPreset(preset);
    },
    [onApplyPreset],
  );

  const renderPresetChip = (preset: MacroPresetConfig): JSX.Element => {
    const isActive = activePresetId === preset.id;
    const meta = PRESET_META[preset.id];
    const style = CATEGORY_STYLES[preset.category];
    return (
      <button
        key={preset.id}
        type="button"
        data-testid={`macro-preset-tab-${preset.id}`}
        onClick={() => handlePresetClick(preset)}
        className={`rounded-sm border px-2 py-2 text-left transition-colors ${
          isActive
            ? `${style.border} ${style.bg} ${style.text} ring-1 ring-current`
            : "border-theme-outline bg-theme-secondary text-theme-primary hover:border-theme-accent hover:bg-theme-tertiary"
        }`}
      >
        <div className="flex items-center justify-between gap-2">
          <p className="body-xxs-medium truncate">{preset.label}</p>
          {meta ? (
            <span
              className={`rounded-sm border px-1.5 py-[1px] text-[9px] font-medium ${ACTION_TAG_STYLES[meta.actionTag]}`}
            >
              {ACTION_TAG_LABELS[meta.actionTag]}
            </span>
          ) : null}
        </div>
        <p className="mt-1 text-[11px] leading-tight opacity-80 line-clamp-2">
          {preset.description}
        </p>
      </button>
    );
  };

  const cycleLevelText = cycleSnapshot
    ? `${LEVEL_LABELS[cycleSnapshot.level]}${
        (cycleSnapshot.stale_days ?? 0) > 14 ? " (Stale)" : ""
      }`
    : "No data";
  const cycleBadgeClass = cycleSnapshot
    ? LEVEL_STYLES[cycleSnapshot.level].badge
    : "border-zinc-500/40 bg-zinc-500/10 text-zinc-300";

  return (
    <div className="rounded-sm border border-theme-outline bg-theme-primary p-3">
      <div
        data-testid="cycle-level-card"
        className="rounded-sm border border-theme-outline bg-theme-secondary p-3"
      >
        <div className="flex flex-wrap items-center justify-between gap-2">
          <div>
            <h3 className="body-sm-medium text-theme-primary">
              Current Cycle Level
            </h3>
            <p className="body-xxs-regular text-theme-muted">
              Composite macro cycle score from risk, growth, inflation,
              liquidity, and credit stress.
            </p>
          </div>
          <span
            data-testid="cycle-level-state"
            className={`rounded-sm border px-2.5 py-1 body-xxs-medium ${cycleBadgeClass}`}
          >
            {cycleLevelText}
          </span>
        </div>

        {cycleSnapshot ? (
          <>
            <div className="mt-2 grid grid-cols-1 gap-2 md:grid-cols-[180px_minmax(0,1fr)]">
              <div className="rounded-sm border border-theme-outline bg-theme-primary p-2">
                <p className="body-xxs-regular text-theme-muted">Composite Score</p>
                <p
                  data-testid="cycle-level-score"
                  className="body-lg-medium text-theme-primary"
                >
                  {cycleSnapshot.score.toFixed(1)}
                </p>
                <p
                  className={`body-xxs-regular ${
                    cycleSnapshot.delta_4w >= 0
                      ? "text-emerald-300"
                      : "text-rose-300"
                  }`}
                >
                  Delta 4W: {cycleSnapshot.delta_4w >= 0 ? "+" : ""}
                  {cycleSnapshot.delta_4w.toFixed(1)}
                </p>
              </div>
              <div className="rounded-sm border border-theme-outline bg-theme-primary p-2">
                <p className="body-xxs-regular text-theme-muted">
                  {LEVEL_STYLES[cycleSnapshot.level].hint}
                </p>
                <div className="mt-1.5 flex flex-wrap gap-1.5">
                  <span className="rounded-sm bg-theme-secondary px-2 py-0.5 text-[10px] text-theme-primary">
                    Action: {cycleSnapshot.action_hint}
                  </span>
                  <span className="rounded-sm bg-theme-secondary px-2 py-0.5 text-[10px] text-theme-primary">
                    As of: {cycleSnapshot.as_of ?? "-"}
                  </span>
                  <span className="rounded-sm bg-theme-secondary px-2 py-0.5 text-[10px] text-theme-primary">
                    Stale days: {cycleSnapshot.stale_days ?? "-"}
                  </span>
                </div>
              </div>
            </div>

            <div className="mt-2 grid grid-cols-2 gap-1.5 xl:grid-cols-5">
              {axisTile("Risk", latestRegime?.risk_on_score)}
              {axisTile("Growth", latestRegime?.growth_score)}
              {axisTile("Inflation", latestRegime?.inflation_score)}
              {axisTile("Liquidity", latestRegime?.liquidity_score)}
              {axisTile("Credit", latestRegime?.credit_stress_score)}
            </div>
          </>
        ) : (
          <p className="mt-2 body-xxs-regular text-theme-muted">
            No regime data is available yet. Run macro refresh or wait for
            market data sync.
          </p>
        )}
      </div>

      <div className="mt-3">
        <div className="flex items-center justify-between">
          <h4 className="body-sm-medium text-theme-primary">Macro Presets</h4>
          <p className="body-xxs-regular text-theme-muted">
            12 tabs, 2-row layout on desktop
          </p>
        </div>

        <div
          data-testid="macro-preset-tabs-mobile"
          className="mt-2 md:hidden overflow-x-auto pb-1"
        >
          <div className="flex min-w-max gap-1.5">{PRESETS.map(renderPresetChip)}</div>
        </div>

        <div
          data-testid="macro-preset-tabs-desktop"
          className="mt-2 hidden md:grid md:grid-cols-6 gap-1.5"
        >
          {PRESETS.map(renderPresetChip)}
        </div>
      </div>

      {activePreset && activeMeta ? (
        <div
          className={`mt-3 rounded-sm border p-3 ${CATEGORY_STYLES[activePreset.category].border} ${CATEGORY_STYLES[activePreset.category].bg}`}
        >
          <div className="flex flex-wrap items-center justify-between gap-2">
            <p className={`body-sm-medium ${CATEGORY_STYLES[activePreset.category].text}`}>
              {activePreset.label}
            </p>
            <span
              className={`rounded-sm border px-2 py-[2px] text-[10px] font-medium ${ACTION_TAG_STYLES[activeMeta.actionTag]}`}
            >
              {ACTION_TAG_LABELS[activeMeta.actionTag]}
            </span>
          </div>

          <p className="mt-1 body-xxs-regular text-theme-primary/90">
            {activePreset.interpretation}
          </p>

          <div className="mt-2 grid grid-cols-1 gap-2 xl:grid-cols-3">
            <div className="rounded-sm border border-theme-outline bg-theme-primary p-2">
              <p className="text-[10px] text-theme-muted">Core Indicators</p>
              <div className="mt-1 flex flex-wrap gap-1">
                {activeMeta.keyIndicators.slice(0, 3).map((indicator) => (
                  <span
                    key={indicator}
                    className={`rounded-sm px-1.5 py-[1px] text-[10px] ${CATEGORY_STYLES[activePreset.category].chip} ${CATEGORY_STYLES[activePreset.category].text}`}
                  >
                    {indicator}
                  </span>
                ))}
              </div>
            </div>
            <div className="rounded-sm border border-theme-outline bg-theme-primary p-2">
              <p className="text-[10px] text-theme-muted">Watch Level</p>
              <p className="mt-1 text-[11px] text-theme-primary">
                {activeMeta.watchLevel}
              </p>
            </div>
            <div className="rounded-sm border border-theme-outline bg-theme-primary p-2">
              <p className="text-[10px] text-theme-muted">Related ETFs</p>
              <div className="mt-1 flex flex-wrap gap-1">
                {activeMeta.relatedETFs.map((etf) => (
                  <span
                    key={etf}
                    className="rounded-sm bg-theme-secondary px-1.5 py-[1px] text-[10px] text-theme-primary"
                  >
                    {etf}
                  </span>
                ))}
              </div>
            </div>
          </div>

          <div className="mt-2 grid grid-cols-1 gap-2 xl:grid-cols-4">
            <div className="rounded-sm border border-theme-outline bg-theme-primary p-2 xl:col-span-2">
              <p className="text-[10px] text-theme-muted">Expression</p>
              <p className="mt-1 text-[11px] font-mono text-theme-primary">
                {activePreset.expression}
              </p>
            </div>
            <div className="rounded-sm border border-theme-outline bg-theme-primary p-2">
              <p className="text-[10px] text-theme-muted">Ratio</p>
              <p className="mt-1 text-[11px] font-mono text-theme-primary">
                {activePreset.ratioTicker}
              </p>
            </div>
            <div className="rounded-sm border border-theme-outline bg-theme-primary p-2">
              <p className="text-[10px] text-theme-muted">Spread Pair</p>
              <p className="mt-1 text-[11px] font-mono text-theme-primary">
                {activePreset.leftSymbol} vs {activePreset.rightSymbol}
              </p>
            </div>
          </div>

          <p className="mt-2 body-xxs-regular text-theme-muted">
            Default action: {activeMeta.portfolioAction}
          </p>
        </div>
      ) : (
        <div className="mt-3 rounded-sm border border-theme-outline bg-theme-secondary p-3">
          <p className="body-xxs-regular text-theme-muted">
            Select a preset tab to auto-fill expression, compare universe, and
            cross-asset relationship inputs.
          </p>
        </div>
      )}
    </div>
  );
}

export { PRESETS };
