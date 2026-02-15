import type { MacroDataPoint } from "../../types/macro";

function pathFromPoints(points: MacroDataPoint[], width: number, height: number): string {
  if (points.length < 2) {
    return "";
  }
  const values = points.map((point) => point.value);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = Math.max(max - min, 1e-12);
  return points
    .map((point, index) => {
      const x = (index / (points.length - 1)) * width;
      const y = ((max - point.value) / span) * height;
      return `${index === 0 ? "M" : "L"} ${x.toFixed(2)} ${y.toFixed(2)}`;
    })
    .join(" ");
}

interface RelationshipPanelProps {
  leftSymbol: string;
  rightSymbol: string;
  onLeftChange: (next: string) => void;
  onRightChange: (next: string) => void;
  onRun: () => void;
  ratioPoints: MacroDataPoint[];
  spreadPoints: MacroDataPoint[];
  corrPoints: MacroDataPoint[];
  betaPoints: MacroDataPoint[];
}

function MiniChart({ title, points, color }: { title: string; points: MacroDataPoint[]; color: string }) {
  const path = pathFromPoints(points, 420, 120);
  return (
    <div className="rounded-sm bg-theme-secondary p-2">
      <p className="body-xxs-regular text-theme-muted">{title}</p>
      {points.length < 2 ? (
        <div className="mt-1 h-24 rounded-sm bg-theme-primary px-2 py-2">
          <p className="body-xxs-regular text-theme-muted">No data</p>
        </div>
      ) : (
        <svg viewBox="0 0 420 120" className="mt-1 h-24 w-full rounded-sm bg-theme-primary">
          <path d={path} fill="none" stroke={color} strokeWidth="1.8" />
        </svg>
      )}
    </div>
  );
}

export function RelationshipPanel({
  leftSymbol,
  rightSymbol,
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
          <button type="button" className="button-secondary rounded-sm px-2 py-1.5 body-xs-medium" onClick={onRun}>
            Update
          </button>
        </div>
      </div>

      <div className="mt-2 grid grid-cols-1 gap-2 xl:grid-cols-2">
        <MiniChart title="Ratio" points={ratioPoints} color="#22c55e" />
        <MiniChart title="Spread" points={spreadPoints} color="#0ea5e9" />
        <MiniChart title="Rolling Corr(60)" points={corrPoints} color="#f59e0b" />
        <MiniChart title="Rolling Beta(60)" points={betaPoints} color="#a855f7" />
      </div>
    </div>
  );
}
