import type { MacroDataPoint } from "../../types/macro";
import { MiniLineChart } from "../charts/MiniLineChart";

interface RelationshipPanelProps {
  leftSymbol: string;
  rightSymbol: string;
  ratioTicker: string;
  corrWindow: number;
  onRatioTickerChange: (next: string) => void;
  onCorrWindowChange: (next: number) => void;
  onLeftChange: (next: string) => void;
  onRightChange: (next: string) => void;
  onRun: () => void;
  ratioPoints: MacroDataPoint[];
  spreadPoints: MacroDataPoint[];
  corrPoints: MacroDataPoint[];
  betaPoints: MacroDataPoint[];
}

export function RelationshipPanel({
  leftSymbol,
  rightSymbol,
  ratioTicker,
  corrWindow,
  onRatioTickerChange,
  onCorrWindowChange,
  onLeftChange,
  onRightChange,
  onRun,
  ratioPoints,
  spreadPoints,
  corrPoints,
  betaPoints,
}: RelationshipPanelProps) {
  return (
    <div className="rounded-sm border border-theme-outline bg-theme-primary p-3">
      <div className="flex items-center justify-between">
        <h3 className="body-sm-medium text-theme-primary">Cross-Asset Relationship</h3>
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={ratioTicker}
            onChange={(event) => onRatioTickerChange(event.target.value)}
            className="w-28 rounded-sm border border-theme-outline bg-theme-secondary p-1.5 body-xs-regular text-theme-primary"
            placeholder="GLD/SPY"
          />
          <input
            type="text"
            value={leftSymbol}
            onChange={(event) => onLeftChange(event.target.value)}
            className="w-24 rounded-sm border border-theme-outline bg-theme-secondary p-1.5 body-xs-regular text-theme-primary"
            placeholder="GLD"
          />
          <span className="body-xs-regular text-theme-muted">vs</span>
          <input
            type="text"
            value={rightSymbol}
            onChange={(event) => onRightChange(event.target.value)}
            className="w-24 rounded-sm border border-theme-outline bg-theme-secondary p-1.5 body-xs-regular text-theme-primary"
            placeholder="SPY"
          />
          <select
            value={corrWindow}
            onChange={(event) => onCorrWindowChange(Number(event.target.value))}
            className="w-20 rounded-sm border border-theme-outline bg-theme-secondary p-1.5 body-xs-regular text-theme-primary"
          >
            <option value={20}>20</option>
            <option value={60}>60</option>
            <option value={120}>120</option>
          </select>
          <button type="button" className="button-secondary rounded-sm px-2 py-1.5 body-xs-medium" onClick={onRun}>
            Update
          </button>
        </div>
      </div>

      <div className="mt-2 grid grid-cols-1 gap-2 xl:grid-cols-2">
        <MiniLineChart title="Ratio" points={ratioPoints} color="#22c55e" xAxisLabel="Date" yAxisLabel="Ratio" />
        <MiniLineChart title="Spread" points={spreadPoints} color="#0ea5e9" xAxisLabel="Date" yAxisLabel="Spread" />
        <MiniLineChart title={`Rolling Corr(${corrWindow})`} points={corrPoints} color="#f59e0b" xAxisLabel="Date" yAxisLabel="Corr" />
        <MiniLineChart title={`Rolling Beta(${corrWindow})`} points={betaPoints} color="#a855f7" xAxisLabel="Date" yAxisLabel="Beta" />
      </div>
    </div>
  );
}
