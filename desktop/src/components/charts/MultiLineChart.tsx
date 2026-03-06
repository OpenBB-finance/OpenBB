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

interface SeriesData {
  key: string;
  points: Array<{ date: string; value: number }>;
}

interface MultiLineChartProps {
  series: SeriesData[];
  title?: string;
  subtitle?: string;
  height?: number;
  colors?: string[];
  formatValue?: (v: number) => string;
}

const DEFAULT_COLORS = ["#38bdf8", "#22c55e", "#f59e0b", "#ef4444", "#a855f7", "#14b8a6"];

function formatDate(dateStr: string): string {
  return dateStr.length >= 7 ? dateStr.slice(0, 7) : dateStr;
}

function defaultFormat(v: number): string {
  return v.toFixed(1);
}

export function MultiLineChart({
  series,
  title,
  subtitle,
  height = 240,
  colors = DEFAULT_COLORS,
  formatValue = defaultFormat,
}: MultiLineChartProps) {
  if (series.length === 0) {
    return (
      <div className="rounded-sm border border-theme-outline bg-theme-primary p-3">
        {title && <h3 className="body-sm-medium text-theme-primary">{title}</h3>}
        <div className="mt-2 rounded-sm bg-theme-secondary p-3" style={{ height }}>
          <p className="body-xs-regular text-theme-muted">비교할 시리즈가 2개 이상 필요합니다.</p>
        </div>
      </div>
    );
  }

  const dateSet = new Set<string>();
  for (const s of series) {
    for (const p of s.points) {
      dateSet.add(p.date);
    }
  }
  const allDates = Array.from(dateSet).sort();

  const lookupMaps = series.map((s) => {
    const map = new Map<string, number>();
    for (const p of s.points) map.set(p.date, p.value);
    return map;
  });

  const merged = allDates.map((date) => {
    const row: Record<string, string | number> = { date };
    for (let i = 0; i < series.length; i++) {
      const val = lookupMaps[i].get(date);
      if (val !== undefined) row[series[i].key] = val;
    }
    return row;
  });

  return (
    <div className="rounded-sm border border-theme-outline bg-theme-primary p-3">
      <div className="flex items-center justify-between mb-2">
        <div>
          {title && <h3 className="body-sm-medium text-theme-primary">{title}</h3>}
          {subtitle && <p className="body-xxs-regular text-theme-muted">{subtitle}</p>}
        </div>
      </div>
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={merged} margin={{ top: 8, right: 12, left: 0, bottom: 4 }}>
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
              fontSize: "11px",
              color: "#fff",
            }}
            labelFormatter={(label) => `${label}`}
            formatter={(v: unknown, name: unknown) => [formatValue(Number(v ?? 0)), String(name ?? "")]}
          />
          <Legend
            wrapperStyle={{ fontSize: "11px", color: "#8a8a90" }}
            iconSize={10}
          />
          {series.map((s, i) => (
            <Line
              key={s.key}
              type="monotone"
              dataKey={s.key}
              stroke={colors[i % colors.length]}
              strokeWidth={1.8}
              dot={false}
              connectNulls
              activeDot={{ r: 3, strokeWidth: 0 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
