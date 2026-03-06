import { useCallback, useMemo, useState } from "react";
import type { MacroFill, MacroFreq } from "../../types/macro";

interface ExpressionBarProps {
  expression: string;
  onExpressionChange: (next: string) => void;
  transform: string;
  onTransformChange: (next: string) => void;
  freq: MacroFreq;
  onFreqChange: (next: MacroFreq) => void;
  fill: MacroFill;
  onFillChange: (next: MacroFill) => void;
  startDate: string;
  endDate: string;
  onStartDateChange: (next: string) => void;
  onEndDateChange: (next: string) => void;
  onRun: () => void;
  onSave: () => void;
  isBusy: boolean;
}

const TRANSFORMS = [
  { value: "level", label: "level", desc: "원본 값" },
  { value: "diff", label: "diff", desc: "1기간 차분" },
  { value: "log", label: "log", desc: "자연로그" },
  { value: "mom", label: "mom", desc: "전월비 변화" },
  { value: "yoy", label: "yoy", desc: "전년동기비" },
  { value: "annualized_mom", label: "ann_mom", desc: "연환산 전월비" },
  { value: "qoq_saar", label: "qoq_saar", desc: "분기 연환산" },
  { value: "zscore", label: "zscore", desc: "Z-Score 표준화" },
  { value: "percentile_5y", label: "pctl_5y", desc: "5년 백분위" },
];

interface ExpressionExample {
  expr: string;
  label: string;
  desc: string;
}

const EXPRESSION_EXAMPLES: ExpressionExample[] = [
  { expr: "FRED:DGS10-FRED:DGS2", label: "장단기 금리차", desc: "수익률 곡선 역전 모니터링" },
  { expr: "rolling_corr(GLD,SPY,60)", label: "금-주식 상관계수", desc: "60일 롤링 상관관계" },
  { expr: "rolling_beta(QQQ,SPY,120)", label: "QQQ 베타", desc: "SPY 대비 120일 베타" },
  { expr: "FRED:CPIAUCSL", label: "CPI", desc: "소비자물가지수 (yoy로 전환 추천)" },
  { expr: "FRED:FEDFUNDS", label: "기준금리", desc: "연방기금금리" },
  { expr: "FRED:VIXCLS", label: "VIX", desc: "변동성 지수" },
];

export function ExpressionBar({
  expression,
  onExpressionChange,
  transform,
  onTransformChange,
  freq,
  onFreqChange,
  fill,
  onFillChange,
  startDate,
  endDate,
  onStartDateChange,
  onEndDateChange,
  onRun,
  onSave,
  isBusy,
}: ExpressionBarProps) {
  const [showExamples, setShowExamples] = useState(false);

  const filteredExamples = useMemo(() => {
    if (!expression.trim()) return EXPRESSION_EXAMPLES;
    const lower = expression.toLowerCase();
    return EXPRESSION_EXAMPLES.filter(
      (ex) =>
        ex.expr.toLowerCase().includes(lower) ||
        ex.label.toLowerCase().includes(lower),
    );
  }, [expression]);

  const handleSelectExample = useCallback(
    (expr: string) => {
      onExpressionChange(expr);
      setShowExamples(false);
    },
    [onExpressionChange],
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === "Enter") {
        e.preventDefault();
        setShowExamples(false);
        onRun();
      }
      if (e.key === "Escape") {
        setShowExamples(false);
      }
    },
    [onRun],
  );

  return (
    <div className="rounded-sm border border-theme-outline bg-theme-primary p-3">
      <div className="grid grid-cols-1 gap-2 xl:grid-cols-[minmax(0,1fr)_150px_110px_110px_140px_140px_auto_auto]">
        <div className="relative">
          <label className="body-xs-medium text-theme-muted">
            Expression
            <div className="relative">
              <input
                type="text"
                value={expression}
                onChange={(event) => {
                  onExpressionChange(event.target.value);
                  setShowExamples(true);
                }}
                onFocus={() => setShowExamples(true)}
                onBlur={() => setTimeout(() => setShowExamples(false), 200)}
                onKeyDown={handleKeyDown}
                placeholder="GLD/SPY, FRED:UNRATE, rolling_corr(GLD,SPY,60)"
                className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary p-2 body-xs-regular text-theme-primary pr-16"
              />
              <button
                type="button"
                className="absolute right-1 top-1/2 -translate-y-1/2 mt-0.5 rounded-sm bg-theme-tertiary px-2 py-0.5 body-xxs-medium text-theme-muted hover:text-theme-primary"
                onClick={() => setShowExamples(!showExamples)}
              >
                예시 ▾
              </button>
            </div>
          </label>
          {showExamples && filteredExamples.length > 0 && (
            <div className="absolute left-0 right-0 top-full z-20 mt-1 rounded-sm border border-theme-outline bg-theme-primary shadow-lg max-h-48 overflow-auto">
              {filteredExamples.map((ex) => (
                <button
                  key={ex.expr}
                  type="button"
                  className="w-full text-left px-3 py-2 hover:bg-theme-secondary border-b border-theme-outline/30 last:border-b-0"
                  onMouseDown={(e) => e.preventDefault()}
                  onClick={() => handleSelectExample(ex.expr)}
                >
                  <p className="body-xs-medium text-theme-primary">{ex.label}</p>
                  <p className="body-xxs-regular text-theme-muted">
                    <code className="text-sky-400">{ex.expr}</code> — {ex.desc}
                  </p>
                </button>
              ))}
            </div>
          )}
        </div>
        <label className="body-xs-medium text-theme-muted">
          Transform
          <select
            value={transform}
            onChange={(event) => onTransformChange(event.target.value)}
            className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary p-2 body-xs-regular text-theme-primary"
          >
            {TRANSFORMS.map((item) => (
              <option key={item.value} value={item.value}>
                {item.label}
              </option>
            ))}
          </select>
          <p className="body-xxs-regular text-theme-muted mt-0.5">
            {TRANSFORMS.find((t) => t.value === transform)?.desc}
          </p>
        </label>
        <label className="body-xs-medium text-theme-muted">
          Freq
          <select
            value={freq}
            onChange={(event) => onFreqChange(event.target.value as MacroFreq)}
            className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary p-2 body-xs-regular text-theme-primary"
          >
            <option value="native">native</option>
            <option value="D">D</option>
            <option value="W">W</option>
            <option value="M">M</option>
            <option value="Q">Q</option>
          </select>
        </label>
        <label className="body-xs-medium text-theme-muted">
          Fill
          <select
            value={fill}
            onChange={(event) => onFillChange(event.target.value as MacroFill)}
            className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary p-2 body-xs-regular text-theme-primary"
          >
            <option value="ffill">ffill</option>
            <option value="interpolate">interpolate</option>
            <option value="none">none</option>
          </select>
        </label>
        <label className="body-xs-medium text-theme-muted">
          Start
          <input
            type="date"
            value={startDate}
            onChange={(event) => onStartDateChange(event.target.value)}
            className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary p-2 body-xs-regular text-theme-primary"
          />
        </label>
        <label className="body-xs-medium text-theme-muted">
          End
          <input
            type="date"
            value={endDate}
            onChange={(event) => onEndDateChange(event.target.value)}
            className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary p-2 body-xs-regular text-theme-primary"
          />
        </label>
        <button
          type="button"
          className="button-neutral mt-5 rounded-sm px-3 py-2 body-xs-medium"
          onClick={onRun}
          disabled={isBusy}
        >
          {isBusy ? "Running..." : "Execute"}
        </button>
        <button
          type="button"
          className="button-secondary mt-5 rounded-sm px-3 py-2 body-xs-medium"
          onClick={onSave}
          disabled={isBusy}
        >
          Save
        </button>
      </div>
    </div>
  );
}
