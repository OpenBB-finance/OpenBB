import type { MacroRegimePoint } from "../../types/macro";
import {
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

interface RegimeRadarChartProps {
  scores: MacroRegimePoint | null;
}

export function RegimeRadarChart({ scores }: RegimeRadarChartProps) {
  const data = scores
    ? [
        { axis: "Risk-On", value: scores.risk_on_score },
        { axis: "Inflation", value: scores.inflation_score },
        { axis: "Growth", value: scores.growth_score },
        { axis: "Liquidity", value: scores.liquidity_score },
        { axis: "Credit", value: scores.credit_stress_score },
      ]
    : [];

  return (
    <div className="rounded-sm border border-theme-outline bg-theme-primary p-3">
      <p className="body-xs-medium text-theme-muted">5-Axis Radar</p>
      <div className="mt-2 h-[220px] w-full">
        {data.length === 0 ? (
          <p className="body-xxs-regular text-theme-muted">No data</p>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <RadarChart data={data}>
              <PolarGrid stroke="rgba(148,163,184,0.35)" />
              <PolarAngleAxis dataKey="axis" tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <PolarRadiusAxis domain={[0, 100]} tick={{ fill: "#64748b", fontSize: 10 }} />
              <Tooltip />
              <Radar
                name="score"
                dataKey="value"
                stroke="#38bdf8"
                fill="#38bdf8"
                fillOpacity={0.35}
                animationDuration={500}
              />
            </RadarChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
