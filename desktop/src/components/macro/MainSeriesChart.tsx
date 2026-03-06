import type { MacroDataPoint } from "../../types/macro";
import { MacroLineChart } from "../charts/MacroLineChart";

interface MainSeriesChartProps {
  points: MacroDataPoint[];
  title?: string;
  subtitle?: string;
}

export function MainSeriesChart({ points, title, subtitle }: MainSeriesChartProps) {
  return (
    <MacroLineChart
      points={points}
      title={title || "Main Series"}
      subtitle={subtitle}
      color="#38bdf8"
      height={280}
    />
  );
}
