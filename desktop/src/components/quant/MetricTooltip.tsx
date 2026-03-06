import { useState, useRef, useEffect } from "react";

export const METRIC_DEFINITIONS: Record<string, string> = {
  ic: "Information Coefficient: 예측과 실제 수익률의 상관계수. 0.05 이상이면 양호.",
  sharpe: "위험 대비 수익률. 1.0 이상이면 양호.",
  ndcg: "NDCG: 순위 품질 지표. 0.6 이상이면 양호.",
  max_drawdown: "최대 낙폭. -10% 이하면 양호.",
  staleness: "데이터 지연 일수. 0~1일이면 양호.",
  turnover: "거래 회전율. 과도하면 비용 증가.",
  hit_rate: "예측 적중률. 상위/하위 데시일 수익률 차이.",
  signal_dispersion: "시그널 분산. 예측값의 분포 정도.",
  crowding: "포지션 밀집도. 과도하면 리스크.",
  correlation: "종목 간 상관계수.",
  mismatch: "예측-실제 불일치 정도.",
  confidence: "모델 신뢰도.",
  trend_regime: "시장 트렌드: bull(상승), bear(하락), sideways(횡보).",
  vol_regime: "변동성 구간: low, mid, high.",
  liquidity_regime: "유동성 수준.",
  vix_level: "VIX 지수 수준.",
  breadth: "시장 폭 (상승 종목 비율).",
  spx_distance_200ma: "S&P500 대비 200일 이평선 거리.",
  beta_spy: "SPY 대비 베타.",
  beta_qqq: "QQQ 대비 베타.",
  vol_ex_ante: "사전 예상 변동성.",
  cvar_95: "95% CVaR (조건부 VaR). 꼬리 위험.",
  training_window: "학습 기간.",
  validation_window: "검증 기간.",
};

export type MetricStatus = "ok" | "warning" | "critical";

interface MetricTooltipProps {
  label: string;
  value: string | number;
  tooltip?: string;
  status?: MetricStatus;
  definitionKey?: string;
}

function InfoIcon() {
  return (
    <svg className="h-3.5 w-3.5" fill="currentColor" viewBox="0 0 20 20" aria-hidden="true">
      <path
        fillRule="evenodd"
        d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
        clipRule="evenodd"
      />
    </svg>
  );
}

export function MetricTooltip({
  label,
  value,
  tooltip,
  status,
  definitionKey,
}: MetricTooltipProps) {
  const [showTooltip, setShowTooltip] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  const resolvedTooltip =
    tooltip ?? (definitionKey && METRIC_DEFINITIONS[definitionKey]) ?? METRIC_DEFINITIONS[label] ?? "";

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        setShowTooltip(false);
      }
    }
    if (showTooltip) {
      document.addEventListener("mousedown", handleClickOutside);
      return () => document.removeEventListener("mousedown", handleClickOutside);
    }
  }, [showTooltip]);

  const statusBorder =
    status === "warning"
      ? "border-amber-500/50"
      : status === "critical"
        ? "border-red-500/50"
        : "border-theme-outline";

  return (
    <div
      ref={ref}
      className={`relative rounded-sm bg-theme-secondary p-2 ${statusBorder}`}
      aria-describedby={resolvedTooltip ? `tooltip-${label}` : undefined}
    >
      <div className="flex items-center justify-between gap-1">
        <p className="body-xxs-regular text-theme-muted">{label}</p>
        {resolvedTooltip && (
          <button
            type="button"
            className="rounded p-0.5 text-theme-muted hover:bg-theme-outline/50 hover:text-theme-primary"
            onClick={() => setShowTooltip(!showTooltip)}
            aria-label={`${label} 설명`}
          >
            <InfoIcon />
          </button>
        )}
      </div>
      <p className="body-xs-medium text-theme-primary">{value}</p>
      {showTooltip && resolvedTooltip && (
        <div
          id={`tooltip-${label}`}
          role="tooltip"
          className="absolute left-0 top-full z-10 mt-1 max-w-xs rounded-sm border border-theme-outline bg-theme-primary p-2 shadow-lg"
        >
          <p className="body-xxs-regular text-theme-muted">{resolvedTooltip}</p>
        </div>
      )}
    </div>
  );
}
