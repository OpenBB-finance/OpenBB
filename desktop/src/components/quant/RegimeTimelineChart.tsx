import type { HmmRegimePayload, MacroRegimeResponse } from "../../types/macro";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface RegimeTimelineChartProps {
  hmmData: HmmRegimePayload | null;
  regimeData: MacroRegimeResponse | null;
}

export function RegimeTimelineChart({ hmmData, regimeData }: RegimeTimelineChartProps) {
  const points = (regimeData?.data ?? []).map((item) => ({
    date: item.date,
    risk_on_score: item.risk_on_score,
    inflation_score: item.inflation_score,
    growth_score: item.growth_score,
    liquidity_score: item.liquidity_score,
    credit_stress_score: item.credit_stress_score,
  }));

  return (
    <div className="rounded-sm border border-theme-outline bg-theme-primary p-3">
      <p className="body-xs-medium text-theme-muted">Regime Timeline</p>
      <div className="mt-2 h-[260px] w-full">
        {points.length === 0 ? (
          <p className="body-xxs-regular text-theme-muted">No timeline data</p>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={points} margin={{ top: 8, right: 12, left: 0, bottom: 4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(148,163,184,0.2)" />
              <XAxis dataKey="date" tick={{ fill: "#94a3b8", fontSize: 11 }} />
              <YAxis domain={[0, 100]} tick={{ fill: "#64748b", fontSize: 10 }} />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="risk_on_score" stroke="#22c55e" dot={false} />
              <Line type="monotone" dataKey="inflation_score" stroke="#f59e0b" dot={false} />
              <Line type="monotone" dataKey="growth_score" stroke="#38bdf8" dot={false} />
              <Line type="monotone" dataKey="liquidity_score" stroke="#a855f7" dot={false} />
              <Line type="monotone" dataKey="credit_stress_score" stroke="#ef4444" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
      <p className="mt-2 body-xxs-regular text-theme-muted">HMM states: {hmmData?.states.length ?? 0}</p>
    </div>
  );
}
