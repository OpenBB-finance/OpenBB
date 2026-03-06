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

function adviceText(
  label: string,
  value: number,
  max: number,
  invert: boolean,
): string {
  const ratio = value / max;
  if (invert) {
    if (ratio >= 0.7) return `${label} 높음 — 리스크 축소 고려.`;
    if (ratio >= 0.4) return `${label} 중립 구간. 현 포지션 유지.`;
    return `${label} 낮음 — 공격적 자산 비중 유지 적합.`;
  }
  if (ratio >= 0.7) return `${label} 강세 — 공격적 포지션 유지.`;
  if (ratio >= 0.4) return `${label} 중립. 분산 투자 유지.`;
  return `${label} 약세 — 방어적 전환 고려.`;
}

export function ScoreGauge({
  label,
  value,
  maxValue = 1,
  invert = false,
  advice,
}: ScoreGaugeProps) {
  const numericValue = typeof value === "number" && !Number.isNaN(value) ? value : 0;
  const clamped = Math.max(0, Math.min(numericValue, maxValue));
  const pct = (clamped / maxValue) * 100;
  const color = gaugeColor(clamped, maxValue, invert);
  const displayAdvice = advice || adviceText(label, clamped, maxValue, invert);

  return (
    <div className="rounded-sm bg-theme-secondary p-2.5">
      <div className="flex items-center justify-between mb-1.5">
        <p className="body-xxs-medium text-theme-muted">{label}</p>
        <p className="body-xs-medium text-theme-primary">{numericValue.toFixed(2)}</p>
      </div>
      <div className="h-2 w-full rounded-full bg-theme-tertiary overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${color}`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <p className="body-xxs-regular text-theme-muted mt-1.5 leading-tight">{displayAdvice}</p>
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
      <div className="flex items-center justify-between mb-2">
        <h3 className="body-sm-medium text-theme-primary">Macro Regime Scores</h3>
        {date && <p className="body-xxs-regular text-theme-muted">as of {date}</p>}
      </div>
      <div className="grid grid-cols-1 gap-2">
        <ScoreGauge
          label="Risk-On"
          value={riskOn}
          advice={
            (riskOn ?? 0) >= 0.6
              ? "위험선호 구간. 공격적 자산(주식/HY) 비중 유지 적합."
              : (riskOn ?? 0) >= 0.3
                ? "중립. 포트폴리오 현 수준 유지."
                : "위험회피 구간. 방어적 자산(채권/금) 확대 고려."
          }
        />
        <ScoreGauge
          label="Inflation"
          value={inflation}
          invert
          advice={
            (inflation ?? 0) >= 0.7
              ? "인플레이션 압력 높음. TIPS, 원자재 비중 확대."
              : (inflation ?? 0) >= 0.4
                ? "인플레이션 중립. 현 배분 유지."
                : "디플레이션 리스크. 장기채 비중 확대 고려."
          }
        />
        <ScoreGauge
          label="Growth"
          value={growth}
          advice={
            (growth ?? 0) >= 0.6
              ? "성장 견조. 성장주/기술주 비중 유지."
              : (growth ?? 0) >= 0.3
                ? "성장 둔화 징후. 섹터 분산 강화."
                : "성장 위축. 경기방어주/유틸리티 ETF 전환."
          }
        />
        <ScoreGauge
          label="Liquidity"
          value={liquidity}
          advice={
            (liquidity ?? 0) >= 0.6
              ? "유동성 풍부. 리스크 자산 접근 용이."
              : (liquidity ?? 0) >= 0.3
                ? "유동성 보통. 대형주 중심 유지."
                : "유동성 위축. 소형주 축소, 현금 비중 확대."
          }
        />
        <ScoreGauge
          label="Credit Stress"
          value={creditStress}
          invert
          advice={
            (creditStress ?? 0) >= 0.6
              ? "신용 스트레스 높음. HY채권 축소, 국채 확대."
              : (creditStress ?? 0) >= 0.3
                ? "신용 환경 보통. IG 채권 유지."
                : "신용 스트레스 낮음. 스프레드 정상 범위."
          }
        />
      </div>
    </div>
  );
}
