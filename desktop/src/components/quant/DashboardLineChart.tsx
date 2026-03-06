import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from "recharts";

export interface TimeSeriesPoint {
  date: string;
  value: number;
}

interface DashboardLineChartProps {
  points: TimeSeriesPoint[];
  secondaryPoints?: TimeSeriesPoint[];
  color?: string;
  secondaryColor?: string;
  height?: number;
  formatValue?: (v: number) => string;
  primaryLabel?: string;
  secondaryLabel?: string;
}

function formatDate(dateStr: string): string {
  if (!dateStr) return "";
  return dateStr.length >= 10 ? dateStr.slice(0, 10) : dateStr.length >= 7 ? dateStr.slice(0, 7) : dateStr;
}

function defaultFormat(v: number): string {
  if (Math.abs(v) >= 1) return v.toFixed(2);
  if (Math.abs(v) >= 0.01) return v.toFixed(4);
  return v.toFixed(6);
}

export function DashboardLineChart({
  points,
  secondaryPoints,
  color = "#0ea5e9",
  secondaryColor = "#22c55e",
  height = 120,
  formatValue = defaultFormat,
  primaryLabel = "Value",
  secondaryLabel = "Secondary",
}: DashboardLineChartProps) {
  const data = points.map((p) => ({
    ...p,
    date: p.date,
    value: p.value,
    secondary: secondaryPoints
      ? secondaryPoints.find((s) => s.date === p.date)?.value ?? null
      : null,
  }));

  if (data.length < 2) {
    return (
      <div
        className="flex items-center justify-center rounded-sm bg-theme-secondary"
        style={{ height }}
      >
        <p className="body-xs-regular text-theme-muted">데이터 부족</p>
      </div>
    );
  }

  return (
    <ResponsiveContainer width="100%" height={height}>
      <LineChart data={data} margin={{ top: 8, right: 12, left: 0, bottom: 4 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(100,100,120,0.15)" />
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
          formatter={(v: unknown, name?: string) => {
            const val = Number(v ?? 0);
            if (Number.isNaN(val)) return ["-", name ?? primaryLabel];
            return [formatValue(val), name === "secondary" ? secondaryLabel : primaryLabel];
          }}
        />
        <Line
          type="monotone"
          dataKey="value"
          stroke={color}
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 4, strokeWidth: 0 }}
          name={primaryLabel}
        />
        {secondaryPoints && secondaryPoints.length > 0 && (
          <Line
            type="monotone"
            dataKey="secondary"
            stroke={secondaryColor}
            strokeWidth={1.7}
            dot={false}
            activeDot={{ r: 4, strokeWidth: 0 }}
            name={secondaryLabel}
          />
        )}
        {(secondaryPoints?.length ?? 0) > 0 && (
          <Legend
            wrapperStyle={{ fontSize: 10 }}
            formatter={(value) => (value === "secondary" ? secondaryLabel : primaryLabel)}
          />
        )}
      </LineChart>
    </ResponsiveContainer>
  );
}
