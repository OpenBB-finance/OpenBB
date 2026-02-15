import type { BenchmarkCurvePoint, EquityCurvePoint } from "../../types/quant";
import { PanelCard } from "./PanelCard";

interface EquityCurveChartProps {
  points: EquityCurvePoint[];
  benchmarkPoints: BenchmarkCurvePoint[];
  benchmarkSymbol: string;
  baseIndex: number;
}

interface ChartRow {
  date: string;
  strategy: number;
  benchmark: number;
}

const WIDTH = 760;
const HEIGHT = 300;
const MARGIN = { top: 12, right: 16, bottom: 40, left: 52 };

function formatDateLabel(date: string): string {
  const d = new Date(date);
  if (Number.isNaN(d.getTime())) {
    return date;
  }
  const year = String(d.getFullYear()).slice(-2);
  const month = String(d.getMonth() + 1).padStart(2, "0");
  return `${year}-${month}`;
}

function buildRows(
  points: EquityCurvePoint[],
  benchmarkPoints: BenchmarkCurvePoint[],
  baseIndex: number,
): ChartRow[] {
  if (points.length === 0) {
    return [];
  }

  const strategyStart = points[0]?.equity || 1;
  const benchmarkMap = new Map(benchmarkPoints.map((item) => [item.date, item.benchmark]));
  const benchmarkStart = benchmarkPoints[0]?.benchmark || baseIndex;

  const strategyDiv = strategyStart === 0 ? 1 : strategyStart;
  const benchmarkDiv = benchmarkStart === 0 ? 1 : benchmarkStart;

  return points.map((point) => {
    const benchmarkRaw = benchmarkMap.get(point.date) ?? benchmarkStart;
    return {
      date: point.date,
      strategy: (point.equity / strategyDiv) * baseIndex,
      benchmark: (benchmarkRaw / benchmarkDiv) * baseIndex,
    };
  });
}

function yTicks(min: number, max: number, count = 5): number[] {
  const span = Math.max(max - min, 1e-9);
  return Array.from({ length: count }, (_, idx) => min + (span * idx) / Math.max(count - 1, 1));
}

function xTickIndexes(length: number, count = 6): number[] {
  if (length <= 1) {
    return [0];
  }

  const step = Math.max(1, Math.floor((length - 1) / Math.max(count - 1, 1)));
  const indexes: number[] = [];

  for (let i = 0; i < length; i += step) {
    indexes.push(i);
  }
  if (indexes[indexes.length - 1] !== length - 1) {
    indexes.push(length - 1);
  }

  return indexes;
}

function makePath(
  rows: ChartRow[],
  valueKey: "strategy" | "benchmark",
  yMin: number,
  yMax: number,
): string {
  if (rows.length === 0) {
    return "";
  }

  const plotWidth = WIDTH - MARGIN.left - MARGIN.right;
  const plotHeight = HEIGHT - MARGIN.top - MARGIN.bottom;

  return rows
    .map((row, index) => {
      const x = MARGIN.left + (index / Math.max(rows.length - 1, 1)) * plotWidth;
      const value = row[valueKey];
      const y = MARGIN.top + ((yMax - value) / Math.max(yMax - yMin, 1e-9)) * plotHeight;
      return `${index === 0 ? "M" : "L"} ${x.toFixed(2)} ${y.toFixed(2)}`;
    })
    .join(" ");
}

export function EquityCurveChart({
  points,
  benchmarkPoints,
  benchmarkSymbol,
  baseIndex,
}: EquityCurveChartProps) {
  const normalizedBase = Number.isFinite(baseIndex) && baseIndex > 0 ? baseIndex : 100;
  const rows = buildRows(points, benchmarkPoints, normalizedBase);
  const latest = rows.at(-1);

  const values = rows.flatMap((row) => [row.strategy, row.benchmark]);
  const rawMin = values.length ? Math.min(...values) : normalizedBase;
  const rawMax = values.length ? Math.max(...values) : normalizedBase;
  const minValue = Math.min(normalizedBase, rawMin);
  const maxValue = Math.max(normalizedBase, rawMax);
  const padding = Math.max((maxValue - minValue) * 0.08, 2);
  const yMin = minValue - padding;
  const yMax = maxValue + padding;

  const plotWidth = WIDTH - MARGIN.left - MARGIN.right;
  const plotHeight = HEIGHT - MARGIN.top - MARGIN.bottom;
  const xTicks = xTickIndexes(rows.length);
  const yAxisTicks = yTicks(yMin, yMax, 5);

  const strategyPath = makePath(rows, "strategy", yMin, yMax);
  const benchmarkPath = makePath(rows, "benchmark", yMin, yMax);
  const baseLineY = MARGIN.top + ((yMax - normalizedBase) / Math.max(yMax - yMin, 1e-9)) * plotHeight;

  return (
    <PanelCard
      title="Equity Curve"
      description={
        latest
          ? `Base ${normalizedBase.toFixed(0)} | Strategy ${latest.strategy.toFixed(2)} | ${benchmarkSymbol} ${latest.benchmark.toFixed(2)}`
          : "Run backtest to display chart."
      }
    >
      {rows.length === 0 ? (
        <p className="body-sm-regular text-theme-muted">No equity data available.</p>
      ) : (
        <div className="rounded-sm bg-theme-secondary p-2">
          <div className="mb-2 flex items-center gap-4">
            <div className="flex items-center gap-1">
              <span className="inline-block h-2 w-2 rounded-full bg-sky-500" />
              <span className="body-xs-regular text-theme-primary">Strategy</span>
            </div>
            <div className="flex items-center gap-1">
              <span className="inline-block h-2 w-2 rounded-full bg-amber-400" />
              <span className="body-xs-regular text-theme-primary">{benchmarkSymbol} Benchmark</span>
            </div>
          </div>

          <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} className="h-64 w-full">
            {yAxisTicks.map((tick) => {
              const y = MARGIN.top + ((yMax - tick) / Math.max(yMax - yMin, 1e-9)) * plotHeight;
              return (
                <g key={`y-${tick}`}>
                  <line
                    x1={MARGIN.left}
                    y1={y}
                    x2={WIDTH - MARGIN.right}
                    y2={y}
                    stroke="rgba(255,255,255,0.08)"
                    strokeWidth="1"
                  />
                  <text
                    x={MARGIN.left - 8}
                    y={y + 4}
                    textAnchor="end"
                    className="fill-current text-[10px] text-theme-muted"
                  >
                    {tick.toFixed(0)}
                  </text>
                </g>
              );
            })}

            <line
              x1={MARGIN.left}
              y1={baseLineY}
              x2={WIDTH - MARGIN.right}
              y2={baseLineY}
              stroke="rgba(160,160,160,0.75)"
              strokeDasharray="4 4"
              strokeWidth="1"
            />

            {xTicks.map((index) => {
              const x = MARGIN.left + (index / Math.max(rows.length - 1, 1)) * plotWidth;
              return (
                <g key={`x-${index}`}>
                  <line
                    x1={x}
                    y1={HEIGHT - MARGIN.bottom}
                    x2={x}
                    y2={HEIGHT - MARGIN.bottom + 4}
                    stroke="rgba(255,255,255,0.22)"
                    strokeWidth="1"
                  />
                  <text
                    x={x}
                    y={HEIGHT - MARGIN.bottom + 16}
                    textAnchor="middle"
                    className="fill-current text-[10px] text-theme-muted"
                  >
                    {formatDateLabel(rows[index].date)}
                  </text>
                </g>
              );
            })}

            <line
              x1={MARGIN.left}
              y1={MARGIN.top}
              x2={MARGIN.left}
              y2={HEIGHT - MARGIN.bottom}
              stroke="rgba(255,255,255,0.35)"
              strokeWidth="1"
            />
            <line
              x1={MARGIN.left}
              y1={HEIGHT - MARGIN.bottom}
              x2={WIDTH - MARGIN.right}
              y2={HEIGHT - MARGIN.bottom}
              stroke="rgba(255,255,255,0.35)"
              strokeWidth="1"
            />

            <path d={benchmarkPath} fill="none" stroke="#f59e0b" strokeWidth="2" />
            <path d={strategyPath} fill="none" stroke="#0ea5e9" strokeWidth="2.5" />
          </svg>
        </div>
      )}
    </PanelCard>
  );
}
