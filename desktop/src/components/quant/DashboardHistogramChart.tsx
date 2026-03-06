import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from "recharts";

function computeHistogram(values: number[], bins = 20): Array<{ bin: string; count: number }> {
  if (values.length === 0) return [];
  const min = Math.min(...values);
  const max = Math.max(...values);
  const span = Math.max(max - min, 1e-9);
  const bucketCount = Math.max(4, bins);
  const buckets = new Array(bucketCount).fill(0).map((_, i) => ({
    bin: ((min + (span * i) / bucketCount) + (min + (span * (i + 1)) / bucketCount)) / 2,
    count: 0,
  }));
  for (const value of values) {
    const idx = Math.min(bucketCount - 1, Math.floor(((value - min) / span) * bucketCount));
    buckets[idx].count += 1;
  }
  return buckets.map((b) => ({ bin: b.bin.toFixed(3), count: b.count }));
}

interface DashboardHistogramChartProps {
  values: number[];
  bins?: number;
  height?: number;
  color?: string;
}

export function DashboardHistogramChart({
  values,
  bins = 20,
  height = 120,
  color = "#0ea5e9",
}: DashboardHistogramChartProps) {
  const data = computeHistogram(values, bins);

  if (data.length === 0 || data.every((d) => d.count === 0)) {
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
      <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 4 }}>
        <XAxis
          dataKey="bin"
          tick={{ fontSize: 9, fill: "#8a8a90" }}
          axisLine={{ stroke: "rgba(100,100,120,0.2)" }}
          tickLine={false}
        />
        <YAxis
          tick={{ fontSize: 9, fill: "#8a8a90" }}
          axisLine={false}
          tickLine={false}
          width={30}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: "rgba(33,33,36,0.95)",
            border: "1px solid rgba(70,70,79,0.5)",
            borderRadius: "4px",
            fontSize: "12px",
            color: "#fff",
          }}
          formatter={(v: unknown) => [String(v ?? 0), "Count"]}
          labelFormatter={(label) => `Bin: ${label}`}
        />
        <Bar dataKey="count" fill={color} radius={[2, 2, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
