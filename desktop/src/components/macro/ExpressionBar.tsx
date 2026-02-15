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
  "level",
  "diff",
  "log",
  "mom",
  "yoy",
  "annualized_mom",
  "qoq_saar",
  "zscore",
  "percentile_5y",
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
  return (
    <div className="rounded-sm border border-theme-outline bg-theme-primary p-3">
      <div className="grid grid-cols-1 gap-2 xl:grid-cols-[minmax(0,1fr)_150px_110px_110px_140px_140px_auto_auto]">
        <label className="body-xs-medium text-theme-muted">
          Expression
          <input
            type="text"
            value={expression}
            onChange={(event) => onExpressionChange(event.target.value)}
            placeholder="GLD/SPY, FRED:UNRATE, rolling_corr(GLD,SPY,60)"
            className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary p-2 body-xs-regular text-theme-primary"
          />
        </label>
        <label className="body-xs-medium text-theme-muted">
          Transform
          <select
            value={transform}
            onChange={(event) => onTransformChange(event.target.value)}
            className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary p-2 body-xs-regular text-theme-primary"
          >
            {TRANSFORMS.map((item) => (
              <option key={item} value={item}>
                {item}
              </option>
            ))}
          </select>
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
