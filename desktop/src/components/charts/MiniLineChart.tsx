import {
  ResponsiveContainer,
  LineChart,
  Line,
  Tooltip,
  YAxis,
  XAxis,
  CartesianGrid,
} from "recharts";

interface DataPoint {
  date: string;
  value: number;
}

interface MiniLineChartProps {
  title: string;
  points: DataPoint[];
  color?: string;
  height?: number;
  xAxisLabel?: string;
  yAxisLabel?: string;
}

function formatVal(v: number): string {
  return v.toFixed(4);
}

function formatDate(dateStr: string): string {
  if (!dateStr) return "";
  return dateStr.length >= 7 ? dateStr.slice(2, 7) : dateStr;
}

export function MiniLineChart({
  title,
  points,
  color = "#38bdf8",
  height = 132,
  xAxisLabel = "Date",
  yAxisLabel = "Value",
}: MiniLineChartProps) {
  const latest = points.length > 0 ? points[points.length - 1] : null;

  return (
    <div className="rounded-sm bg-theme-secondary p-2">
      <div className="flex items-center justify-between mb-1">
        <p className="body-xxs-regular text-theme-muted">{title}</p>
        {latest && (
          <p className="body-xxs-regular text-theme-primary">{formatVal(latest.value)}</p>
        )}
      </div>
      {points.length < 2 ? (
        <div
          className="rounded-sm bg-theme-primary flex items-center justify-center"
          style={{ height }}
        >
          <p className="body-xxs-regular text-theme-muted">No data</p>
        </div>
      ) : (
        <ResponsiveContainer width="100%" height={height}>
          <LineChart data={points} margin={{ top: 6, right: 8, left: 18, bottom: 12 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="rgba(100,100,120,0.14)" />
            <XAxis
              dataKey="date"
              tickFormatter={formatDate}
              tick={{ fontSize: 9, fill: "#8a8a90" }}
              axisLine={{ stroke: "rgba(100,100,120,0.24)" }}
              tickLine={false}
              minTickGap={32}
              label={{
                value: xAxisLabel,
                position: "insideBottomRight",
                offset: -2,
                fill: "#8a8a90",
                fontSize: 9,
              }}
            />
            <YAxis
              domain={["auto", "auto"]}
              tick={{ fontSize: 9, fill: "#8a8a90" }}
              axisLine={false}
              tickLine={false}
              width={42}
              tickFormatter={(v) => formatVal(Number(v ?? 0))}
              label={{
                value: yAxisLabel,
                angle: -90,
                position: "insideLeft",
                fill: "#8a8a90",
                fontSize: 9,
                offset: 6,
              }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "rgba(33,33,36,0.95)",
                border: "1px solid rgba(70,70,79,0.5)",
                borderRadius: "4px",
                fontSize: "10px",
                color: "#fff",
                padding: "4px 8px",
              }}
              labelFormatter={(label) => `${label}`}
              formatter={(v: unknown) => [formatVal(Number(v ?? 0)), ""]}
            />
            <Line
              type="monotone"
              dataKey="value"
              stroke={color}
              strokeWidth={1.8}
              dot={false}
              activeDot={{ r: 3, strokeWidth: 0 }}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}
