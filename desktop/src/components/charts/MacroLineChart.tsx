import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine,
} from "recharts";

interface DataPoint {
  date: string;
  value: number;
}

interface MacroLineChartProps {
  points: DataPoint[];
  title?: string;
  subtitle?: string;
  color?: string;
  height?: number;
  showGrid?: boolean;
  referenceLine?: number;
  referenceLabel?: string;
  formatValue?: (v: number) => string;
}

function formatDate(dateStr: string): string {
  if (!dateStr) return "";
  return dateStr.length >= 7 ? dateStr.slice(0, 7) : dateStr;
}

function defaultFormat(v: number): string {
  if (Math.abs(v) >= 1_000_000) return `${(v / 1_000_000).toFixed(1)}M`;
  if (Math.abs(v) >= 1_000) return `${(v / 1_000).toFixed(1)}K`;
  return v.toFixed(2);
}

export function MacroLineChart({
  points,
  title,
  subtitle,
  color = "#38bdf8",
  height = 280,
  showGrid = true,
  referenceLine,
  referenceLabel,
  formatValue = defaultFormat,
}: MacroLineChartProps) {
  const latest = points.length > 0 ? points[points.length - 1] : null;

  return (
    <div className="rounded-sm border border-theme-outline bg-theme-primary p-3">
      {(title || latest) && (
        <div className="flex items-center justify-between mb-2">
          <div>
            {title && <h3 className="body-sm-medium text-theme-primary">{title}</h3>}
            {subtitle && <p className="body-xxs-regular text-theme-muted">{subtitle}</p>}
          </div>
          {latest && (
            <p className="body-xs-regular text-theme-muted">
              Latest: <span className="text-theme-primary">{formatValue(latest.value)}</span>{" "}
              <span className="text-theme-muted">({latest.date})</span>
            </p>
          )}
        </div>
      )}
      {points.length < 2 ? (
        <div
          className="rounded-sm bg-theme-secondary flex items-center justify-center"
          style={{ height }}
        >
          <p className="body-xs-regular text-theme-muted">데이터가 부족합니다. Refresh Defaults를 실행하세요.</p>
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={height}>
          <LineChart data={points} margin={{ top: 8, right: 12, left: 0, bottom: 4 }}>
            {showGrid && (
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(100,100,120,0.15)" />
            )}
            <XAxis
              dataKey="date"
              tickFormatter={formatDate}
              tick={{ fontSize: 10, fill: "#8a8a90" }}
              axisLine={{ stroke: "rgba(100,100,120,0.2)" }}
              tickLine={false}
              minTickGap={60}
            />
            <YAxis
              tickFormatter={formatValue}
              tick={{ fontSize: 10, fill: "#8a8a90" }}
              axisLine={false}
              tickLine={false}
              width={55}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "rgba(33,33,36,0.95)",
                border: "1px solid rgba(70,70,79,0.5)",
                borderRadius: "4px",
                fontSize: "12px",
                color: "#fff",
              }}
              labelFormatter={(label) => `Date: ${label}`}
              formatter={(v: unknown) => [formatValue(Number(v ?? 0)), "Value"]}
            />
            {referenceLine !== undefined && (
              <ReferenceLine
                y={referenceLine}
                stroke="#ef4444"
                strokeDasharray="4 4"
                label={{
                  value: referenceLabel || String(referenceLine),
                  position: "right",
                  fill: "#ef4444",
                  fontSize: 10,
                }}
              />
            )}
            <Line
              type="monotone"
              dataKey="value"
              stroke={color}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, strokeWidth: 0 }}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
