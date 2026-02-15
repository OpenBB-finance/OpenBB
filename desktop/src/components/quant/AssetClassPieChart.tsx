interface PieSliceInput {
  category: string;
  weight: number;
}

interface PieSlice extends PieSliceInput {
  key: string;
}

interface AssetClassPieChartProps {
  slices: PieSliceInput[];
  size?: number;
}

const CATEGORY_COLORS: Record<string, string> = {
  us_sector_etf: "#0ea5e9",
  us_equity_etf: "#22c55e",
  us_tech_etf: "#38bdf8",
  us_tech_index: "#0284c7",
  korea_index: "#f59e0b",
  korea_etf: "#fbbf24",
  bond_etf: "#64748b",
  commodity_etf: "#f97316",
  global_equity_etf: "#14b8a6",
  developed_market_etf: "#2dd4bf",
  emerging_market_etf: "#a855f7",
  factor_etf: "#ec4899",
  reit_etf: "#8b5cf6",
  currency_etf: "#06b6d4",
  cash_proxy: "#94a3b8",
  other: "#6b7280",
};

const FALLBACK_COLORS = [
  "#0ea5e9",
  "#f97316",
  "#22c55e",
  "#ec4899",
  "#14b8a6",
  "#a855f7",
  "#f59e0b",
  "#64748b",
];

function categoryColor(category: string, index: number): string {
  return CATEGORY_COLORS[category] ?? FALLBACK_COLORS[index % FALLBACK_COLORS.length];
}

function normalizeSlices(input: PieSliceInput[]): PieSlice[] {
  const nonNegative = input
    .map((slice) => ({ ...slice, weight: Number.isFinite(slice.weight) ? Math.max(slice.weight, 0) : 0 }))
    .filter((slice) => slice.weight > 0);
  if (nonNegative.length === 0) {
    return [];
  }

  const total = nonNegative.reduce((sum, slice) => sum + slice.weight, 0);
  if (total <= 0) {
    return [];
  }

  const normalized = nonNegative.map((slice) => ({ ...slice, weight: slice.weight / total }));
  let other = 0;
  const kept: PieSlice[] = [];
  for (const slice of normalized) {
    if (slice.weight < 0.01) {
      other += slice.weight;
      continue;
    }
    kept.push({ ...slice, key: `${slice.category}-${slice.weight}` });
  }
  if (other > 0) {
    kept.push({ category: "other", weight: other, key: `other-${other}` });
  }

  const finalTotal = kept.reduce((sum, slice) => sum + slice.weight, 0);
  if (finalTotal <= 0) {
    return [];
  }
  return kept.map((slice) => ({ ...slice, weight: slice.weight / finalTotal }));
}

function describeArc(
  centerX: number,
  centerY: number,
  radius: number,
  startAngle: number,
  endAngle: number,
): string {
  const toPoint = (angle: number) => ({
    x: centerX + radius * Math.cos(angle),
    y: centerY + radius * Math.sin(angle),
  });

  const start = toPoint(startAngle);
  const end = toPoint(endAngle);
  const largeArcFlag = endAngle - startAngle > Math.PI ? 1 : 0;

  return [
    `M ${centerX} ${centerY}`,
    `L ${start.x} ${start.y}`,
    `A ${radius} ${radius} 0 ${largeArcFlag} 1 ${end.x} ${end.y}`,
    "Z",
  ].join(" ");
}

export function AssetClassPieChart({ slices, size = 220 }: AssetClassPieChartProps) {
  const normalized = normalizeSlices(slices);
  if (normalized.length === 0) {
    return (
      <div className="flex h-56 items-center justify-center rounded-sm bg-theme-secondary">
        <p className="body-xs-regular text-theme-muted">No allocation data.</p>
      </div>
    );
  }

  const radius = size / 2 - 2;
  const center = size / 2;
  const oneSlice = normalized.length === 1 && normalized[0].weight >= 0.99999;

  if (oneSlice) {
    return (
      <svg viewBox={`0 0 ${size} ${size}`} className="h-56 w-full">
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill={categoryColor(normalized[0].category, 0)}
          stroke="rgba(255,255,255,0.08)"
          strokeWidth="1"
        />
      </svg>
    );
  }

  let cursor = -Math.PI / 2;
  return (
    <svg viewBox={`0 0 ${size} ${size}`} className="h-56 w-full">
      {normalized.map((slice, index) => {
        const epsilon = 1e-6;
        const span = Math.max(slice.weight * Math.PI * 2, epsilon);
        const start = cursor;
        const end = cursor + span;
        cursor = end;
        return (
          <path
            key={slice.key}
            d={describeArc(center, center, radius, start, end)}
            fill={categoryColor(slice.category, index)}
            stroke="rgba(15,23,42,0.24)"
            strokeWidth="1"
          />
        );
      })}
    </svg>
  );
}
