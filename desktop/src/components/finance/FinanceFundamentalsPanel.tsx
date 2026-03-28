import { useEffect, useMemo, useState } from "react";
import {
  fetchFinanceForecast,
  fetchFinanceStatement,
  type FinanceForecastPayload,
  type FinanceStatementPayload,
} from "../../lib/financeApi";
import { buildTradingViewFinancialLink } from "../../lib/tradingView";
import type {
  FinanceFundamentalsTab,
  FinanceStatementKind,
  FinanceStatementPeriod,
  FinanceStatementRecord,
  TradingViewThemeMode,
} from "../../types/finance";
import { PanelCard } from "../quant/PanelCard";
import { SummaryCard } from "../quant/SummaryCard";
import { TradingViewWidgetEmbed } from "./TradingViewWidgetEmbed";

interface FinanceFundamentalsPanelProps {
  baseUrl: string;
  symbol: string;
  theme: TradingViewThemeMode;
  overviewHeight: number;
}

const TAB_OPTIONS: Array<{ id: FinanceFundamentalsTab; label: string }> = [
  { id: "overview", label: "Overview" },
  { id: "forecast", label: "Forecast" },
  { id: "income-statement", label: "I/S" },
  { id: "balance-sheet", label: "B/S" },
  { id: "cash-flow", label: "C/F" },
];

const STATEMENT_KIND_BY_TAB: Record<
  Exclude<FinanceFundamentalsTab, "overview" | "forecast">,
  FinanceStatementKind
> = {
  "income-statement": "income",
  "balance-sheet": "balance",
  "cash-flow": "cash",
};

const METRIC_PRIORITIES: Record<FinanceStatementKind, string[]> = {
  income: [
    "total_revenue",
    "gross_profit",
    "operating_income",
    "net_income",
    "ebitda",
    "basic_earnings_per_share",
    "diluted_earnings_per_share",
    "operating_expense",
    "research_and_development_expense",
    "selling_general_and_admin_expense",
    "tax_rate_for_calcs",
  ],
  balance: [
    "total_assets",
    "current_assets",
    "cash_and_cash_equivalents",
    "inventory",
    "net_ppe",
    "total_liabilities_net_minority_interest",
    "current_liabilities",
    "long_term_debt",
    "stockholders_equity",
    "working_capital",
    "net_debt",
  ],
  cash: [
    "operating_cash_flow",
    "investing_cash_flow",
    "financing_cash_flow",
    "end_cash_position",
    "capital_expenditure",
    "free_cash_flow",
    "issuance_of_debt",
    "repayment_of_debt",
    "repurchase_of_capital_stock",
    "cash_dividends_paid",
  ],
};

const VISUAL_METRICS: Record<FinanceStatementKind, string[]> = {
  income: ["total_revenue", "gross_profit", "net_income"],
  balance: ["total_assets", "total_liabilities_net_minority_interest", "stockholders_equity"],
  cash: ["operating_cash_flow", "free_cash_flow", "capital_expenditure"],
};

const METRIC_ALIASES: Partial<Record<string, string[]>> = {
  total_liabilities_net_minority_interest: [
    "total_liabilities_net_minority_interest",
    "total_liabilities",
  ],
  stockholders_equity: [
    "stockholders_equity",
    "total_shareholder_equity",
    "total_equity_gross_minority_interest",
  ],
  operating_cash_flow: ["operating_cash_flow", "operating_cashflow"],
  investing_cash_flow: ["investing_cash_flow", "cashflow_from_investment"],
  financing_cash_flow: ["financing_cash_flow", "cashflow_from_financing"],
  capital_expenditure: ["capital_expenditure", "capital_expenditures"],
};

function formatTimestamp(value: string | null): string {
  if (!value) return "Unknown";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) {
    return value;
  }
  return parsed.toLocaleString("en-US", {
    year: "numeric",
    month: "short",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function humanizeMetricLabel(metric: string): string {
  return metric
    .replace(/_/g, " ")
    .replace(/\b([a-z])/g, (match) => match.toUpperCase())
    .replace(/\bEbitda\b/g, "EBITDA")
    .replace(/\bEbit\b/g, "EBIT")
    .replace(/\bPpe\b/g, "PPE")
    .replace(/\bSg&a\b/g, "SG&A")
    .replace(/\bNi\b/g, "NI")
    .replace(/\bAvailto\b/g, "Available To");
}

function getNumericValue(value: FinanceStatementRecord[string] | number | null | undefined): number | null {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }
  return null;
}

function getResolvedMetricValue(
  row: FinanceStatementRecord,
  metric: string,
): FinanceStatementRecord[string] | number | null | undefined {
  const aliases = METRIC_ALIASES[metric] ?? [metric];
  for (const candidate of aliases) {
    const value = row[candidate];
    if (value !== null && value !== undefined && value !== "") {
      return value;
    }
  }

  if (metric === "free_cash_flow") {
    const operatingCashFlow = getNumericValue(getResolvedMetricValue(row, "operating_cash_flow"));
    const capitalExpenditure = getNumericValue(getResolvedMetricValue(row, "capital_expenditure"));
    if (operatingCashFlow !== null && capitalExpenditure !== null) {
      return operatingCashFlow - capitalExpenditure;
    }
  }

  return row[metric];
}

function formatFinancialValue(metric: string, value: FinanceStatementRecord[string] | number | null | undefined): string {
  if (value === null || value === undefined || value === "") {
    return "-";
  }

  if (typeof value === "boolean") {
    return value ? "Yes" : "No";
  }

  if (typeof value === "string") {
    return value;
  }

  const absolute = Math.abs(value);
  const lowerMetric = metric.toLowerCase();
  const isPercentLike =
    lowerMetric.includes("rate") ||
    lowerMetric.includes("margin") ||
    lowerMetric.includes("yield") ||
    lowerMetric.includes("pct") ||
    lowerMetric.includes("percent");

  if (isPercentLike && absolute <= 1) {
    return `${(value * 100).toFixed(1)}%`;
  }
  if (absolute >= 1_000_000_000_000) {
    return `${(value / 1_000_000_000_000).toFixed(2)}T`;
  }
  if (absolute >= 1_000_000_000) {
    return `${(value / 1_000_000_000).toFixed(2)}B`;
  }
  if (absolute >= 1_000_000) {
    return `${(value / 1_000_000).toFixed(2)}M`;
  }
  if (absolute >= 1_000) {
    return `${(value / 1_000).toFixed(2)}K`;
  }
  if (absolute >= 1 || Number.isInteger(value)) {
    return value.toLocaleString("en-US", { maximumFractionDigits: 2 });
  }
  return value.toFixed(4);
}

function formatCurrencyValue(value: number | null | undefined, currency: string | null | undefined): string {
  if (value === null || value === undefined || !Number.isFinite(value)) {
    return "-";
  }
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: currency || "USD",
    maximumFractionDigits: 2,
  }).format(value);
}

function formatPercent(value: number | null | undefined): string {
  if (value === null || value === undefined || !Number.isFinite(value)) {
    return "-";
  }
  return `${value.toFixed(1)}%`;
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

function buildMetricKeys(kind: FinanceStatementKind, rows: FinanceStatementRecord[]): string[] {
  const set = new Set<string>();
  for (const row of rows) {
    for (const key of Object.keys(row)) {
      if (key !== "period_ending" && row[key] !== null && row[key] !== undefined) {
        set.add(key);
      }
    }
  }

  const priorities = METRIC_PRIORITIES[kind];
  const rest = Array.from(set).filter((metric) => !priorities.includes(metric)).sort();
  return [...priorities.filter((metric) => set.has(metric)), ...rest];
}

function buildHighlights(kind: FinanceStatementKind, latestRow: FinanceStatementRecord | null) {
  if (!latestRow) {
    return [];
  }

  const summaryByKind: Record<FinanceStatementKind, Array<{ label: string; key: string }>> = {
    income: [
      { label: "Revenue", key: "total_revenue" },
      { label: "Gross Profit", key: "gross_profit" },
      { label: "Net Income", key: "net_income" },
    ],
    balance: [
      { label: "Total Assets", key: "total_assets" },
      { label: "Total Liabilities", key: "total_liabilities_net_minority_interest" },
      { label: "Stockholders Equity", key: "stockholders_equity" },
    ],
    cash: [
      { label: "Operating Cash Flow", key: "operating_cash_flow" },
      { label: "Investing Cash Flow", key: "investing_cash_flow" },
      { label: "Free Cash Flow", key: "free_cash_flow" },
    ],
  };

  return summaryByKind[kind].map((item) => ({
    label: item.label,
    value: formatFinancialValue(item.key, getResolvedMetricValue(latestRow, item.key)),
  }));
}

function renderMetricVisualCard(
  title: string,
  metric: string,
  rows: FinanceStatementRecord[],
) {
  const points = rows
    .map((row, index) => {
      const numericValue = getNumericValue(getResolvedMetricValue(row, metric));
      return {
        key: `${metric}-${row.period_ending ?? index}`,
        label: row.period_ending ?? `P${index + 1}`,
        value: numericValue,
      };
    })
    .filter((point) => point.value !== null) as Array<{
    key: string;
    label: string;
    value: number;
  }>;

  if (points.length === 0) {
    return null;
  }

  const scale = Math.max(...points.map((point) => Math.abs(point.value)), 1);

  return (
    <div key={metric} className="rounded-sm border border-theme-outline bg-theme-secondary/40 p-3">
      <div className="mb-3 flex items-center justify-between gap-2">
        <div>
          <p className="body-xxs-regular text-theme-muted">{title}</p>
          <p className="body-xs-medium text-theme-primary">{formatFinancialValue(metric, points[0]?.value ?? null)}</p>
        </div>
        <p className="body-xxs-regular text-theme-muted">{points.length} periods</p>
      </div>
      <div className="flex items-end gap-3">
        {points.map((point) => {
          const ratio = Math.abs(point.value) / scale;
          const height = `${24 + ratio * 72}px`;
          const negative = point.value < 0;
          return (
            <div key={point.key} className="flex min-w-0 flex-1 flex-col items-center gap-2">
              <div className="flex h-[104px] w-full items-end">
                <div
                  className={`w-full rounded-t-sm ${negative ? "bg-amber-500/70" : "bg-sky-500/70"}`}
                  style={{ height }}
                />
              </div>
              <p className="line-clamp-1 text-center body-xxs-medium text-theme-primary">{formatFinancialValue(metric, point.value)}</p>
              <p className="text-center body-xxs-regular text-theme-muted">{point.label}</p>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function renderStatementVisuals(kind: FinanceStatementKind, payload: FinanceStatementPayload) {
  const visualMetrics = VISUAL_METRICS[kind];
  const visuals = visualMetrics
    .map((metric) => renderMetricVisualCard(humanizeMetricLabel(metric), metric, payload.rows))
    .filter(Boolean);

  if (visuals.length === 0) {
    return null;
  }

  return <div className="grid grid-cols-1 gap-3 xl:grid-cols-3">{visuals}</div>;
}

function renderForecast(payload: FinanceForecastPayload) {
  const consensus = payload.consensus;
  if (!consensus) {
    return (
      <div className="rounded-sm border border-dashed border-theme-outline bg-theme-secondary/40 px-4 py-6">
        <p className="body-xs-medium text-theme-primary">No forecast data returned.</p>
        <p className="mt-1 body-xxs-regular text-theme-muted">
          Consensus target data is not available for this ticker from the active provider.
        </p>
      </div>
    );
  }

  const low = consensus.target_low ?? null;
  const high = consensus.target_high ?? null;
  const current = consensus.current_price ?? null;
  const consensusTarget = consensus.target_consensus ?? null;
  const medianTarget = consensus.target_median ?? null;
  const rangeMin = low ?? Math.min(current ?? 0, consensusTarget ?? 0, medianTarget ?? 0);
  const rangeMax = high ?? Math.max(current ?? 0, consensusTarget ?? 0, medianTarget ?? 0, 1);
  const rangeSpan = Math.max(rangeMax - rangeMin, 1);
  const currentPosition = current !== null ? clamp(((current - rangeMin) / rangeSpan) * 100, 0, 100) : null;
  const consensusPosition =
    consensusTarget !== null ? clamp(((consensusTarget - rangeMin) / rangeSpan) * 100, 0, 100) : null;
  const medianPosition =
    medianTarget !== null ? clamp(((medianTarget - rangeMin) / rangeSpan) * 100, 0, 100) : null;
  const upside =
    consensusTarget !== null && current !== null && current !== 0
      ? ((consensusTarget - current) / current) * 100
      : null;

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 gap-3 md:grid-cols-4">
        <SummaryCard
          label="Current Price"
          value={formatCurrencyValue(current, consensus.currency)}
        />
        <SummaryCard
          label="Consensus Target"
          value={formatCurrencyValue(consensusTarget, consensus.currency)}
        />
        <SummaryCard
          label="Implied Upside"
          value={formatPercent(upside)}
          status={upside !== null && upside < 0 ? "warning" : "ok"}
        />
        <SummaryCard
          label="Analysts"
          value={consensus.number_of_analysts ?? "-"}
        />
      </div>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-[minmax(0,1.4fr)_minmax(0,0.9fr)]">
        <div className="rounded-sm border border-theme-outline bg-theme-secondary/40 p-4">
          <div className="flex items-center justify-between gap-3">
            <div>
              <p className="body-xs-medium text-theme-primary">Analyst target range</p>
              <p className="mt-1 body-xxs-regular text-theme-muted">
                Consensus target plotted against the low/high analyst range and current price.
              </p>
            </div>
            <p className="body-xxs-regular text-theme-muted">{payload.provider ?? "yfinance"}</p>
          </div>

          <div className="mt-6 space-y-4">
            <div className="relative h-3 rounded-full bg-theme-primary">
              <div className="absolute inset-y-0 left-0 rounded-full bg-sky-500/20" style={{ width: "100%" }} />
              {currentPosition !== null ? (
                <div
                  className="absolute -top-2 h-7 w-[2px] bg-theme-primary"
                  style={{ left: `${currentPosition}%` }}
                  aria-label="current price marker"
                />
              ) : null}
              {consensusPosition !== null ? (
                <div
                  className="absolute -top-3 h-9 w-[2px] bg-sky-400"
                  style={{ left: `${consensusPosition}%` }}
                  aria-label="consensus target marker"
                />
              ) : null}
              {medianPosition !== null ? (
                <div
                  className="absolute -top-1 h-5 w-[2px] bg-emerald-400"
                  style={{ left: `${medianPosition}%` }}
                  aria-label="median target marker"
                />
              ) : null}
            </div>
            <div className="grid grid-cols-2 gap-3 md:grid-cols-4">
              <SummaryCard label="Low" value={formatCurrencyValue(low, consensus.currency)} />
              <SummaryCard label="Current" value={formatCurrencyValue(current, consensus.currency)} />
              <SummaryCard label="Consensus" value={formatCurrencyValue(consensusTarget, consensus.currency)} />
              <SummaryCard label="High" value={formatCurrencyValue(high, consensus.currency)} />
            </div>
          </div>
        </div>

        <div className="rounded-sm border border-theme-outline bg-theme-secondary/40 p-4">
          <p className="body-xs-medium text-theme-primary">Forecast snapshot</p>
          <div className="mt-4 grid grid-cols-1 gap-3">
            <SummaryCard
              label="Recommendation"
              value={(consensus.recommendation ?? "unknown").toUpperCase()}
            />
            <SummaryCard
              label="Recommendation Mean"
              value={
                consensus.recommendation_mean !== null && consensus.recommendation_mean !== undefined
                  ? consensus.recommendation_mean.toFixed(2)
                  : "-"
              }
            />
            <SummaryCard
              label="Median Target"
              value={formatCurrencyValue(medianTarget, consensus.currency)}
            />
            <SummaryCard
              label="Last refreshed"
              value={formatTimestamp(payload.timestamp)}
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function renderTradingViewFallback(
  symbol: string,
  theme: TradingViewThemeMode,
  overviewHeight: number,
  title: string,
  message: string,
  detail?: string | null,
) {
  return (
    <div className="space-y-4">
      <div className="rounded-sm border border-amber-500/40 bg-amber-500/10 px-4 py-4">
        <p className="body-xs-medium text-theme-primary">{title}</p>
        <p className="mt-1 body-xxs-regular text-theme-muted">{message}</p>
        {detail ? <p className="mt-2 body-xxs-regular text-theme-muted">{detail}</p> : null}
      </div>
      <TradingViewWidgetEmbed
        widgetType="fundamental-data"
        symbol={symbol}
        theme={theme}
        title="TradingView Financial Fallback"
        minHeight={overviewHeight}
        frameHeight={overviewHeight}
      />
    </div>
  );
}

function renderTable(
  kind: FinanceStatementKind,
  payload: FinanceStatementPayload,
  period: FinanceStatementPeriod,
) {
  const metrics = buildMetricKeys(kind, payload.rows);

  if (payload.rows.length === 0 || metrics.length === 0) {
    return (
      <div className="rounded-sm border border-dashed border-theme-outline bg-theme-secondary/40 px-4 py-6">
        <p className="body-xs-medium text-theme-primary">No statement rows returned.</p>
        <p className="mt-1 body-xxs-regular text-theme-muted">
          Try another ticker or switch between annual and quarterly periods.
        </p>
      </div>
    );
  }

  const highlights = buildHighlights(kind, payload.rows[0] ?? null);

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
        {highlights.map((item) => (
          <SummaryCard key={item.label} label={item.label} value={item.value} />
        ))}
      </div>

      {renderStatementVisuals(kind, payload)}

      <div className="flex flex-wrap items-center justify-between gap-3 rounded-sm border border-theme-outline bg-theme-secondary/40 px-3 py-2">
        <div>
          <p className="body-xxs-regular text-theme-muted">Period</p>
          <p className="body-xs-medium text-theme-primary">
            {period === "annual" ? "Annual statements" : "Quarterly statements"}
          </p>
        </div>
        <div>
          <p className="body-xxs-regular text-theme-muted">Provider</p>
          <p className="body-xs-medium text-theme-primary">{payload.provider ?? "OpenBB"}</p>
        </div>
        <div>
          <p className="body-xxs-regular text-theme-muted">Last refreshed</p>
          <p className="body-xs-medium text-theme-primary">{formatTimestamp(payload.timestamp)}</p>
        </div>
      </div>

      <div className="overflow-auto rounded-sm border border-theme-outline">
        <table className="min-w-full divide-y divide-theme-outline">
          <thead className="bg-theme-secondary">
            <tr>
              <th className="sticky left-0 z-10 min-w-[260px] bg-theme-secondary px-4 py-3 text-left body-xxs-medium text-theme-muted">
                Metric
              </th>
              {payload.rows.map((row, index) => (
                <th
                  key={`${row.period_ending ?? "period"}-${index}`}
                  className="min-w-[160px] px-4 py-3 text-right body-xxs-medium text-theme-muted"
                >
                  {row.period_ending ?? `Period ${index + 1}`}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-theme-outline bg-theme-primary">
            {metrics.map((metric) => (
              <tr key={metric}>
                <th className="sticky left-0 bg-theme-primary px-4 py-3 text-left body-xxs-medium text-theme-primary">
                  {humanizeMetricLabel(metric)}
                </th>
                {payload.rows.map((row, index) => (
                  <td
                    key={`${metric}-${row.period_ending ?? index}`}
                    className="px-4 py-3 text-right body-xxs-regular text-theme-primary"
                  >
                    {formatFinancialValue(metric, row[metric])}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}

export function FinanceFundamentalsPanel({
  baseUrl,
  symbol,
  theme,
  overviewHeight,
}: FinanceFundamentalsPanelProps) {
  const [activeTab, setActiveTab] = useState<FinanceFundamentalsTab>("overview");
  const [period, setPeriod] = useState<FinanceStatementPeriod>("annual");
  const [payloads, setPayloads] = useState<Record<FinanceStatementKind, FinanceStatementPayload | null>>({
    income: null,
    balance: null,
    cash: null,
  });
  const [forecastPayload, setForecastPayload] = useState<FinanceForecastPayload | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isForecastLoading, setIsForecastLoading] = useState(false);
  const [errorsByKind, setErrorsByKind] = useState<Partial<Record<FinanceStatementKind, string>>>({});
  const [forecastError, setForecastError] = useState<string | null>(null);
  const activeKind =
    activeTab === "overview" || activeTab === "forecast" ? null : STATEMENT_KIND_BY_TAB[activeTab];

  useEffect(() => {
    setPayloads({
      income: null,
      balance: null,
      cash: null,
    });
    setErrorsByKind({});
    setForecastPayload(null);
    setForecastError(null);
  }, [baseUrl, symbol]);

  useEffect(() => {
    if (!baseUrl || !symbol || !activeKind) {
      setIsLoading(false);
      return () => undefined;
    }

    const controller = new AbortController();
    let cancelled = false;

    const loadStatements = async () => {
      setIsLoading(true);
      setErrorsByKind((current) => ({
        ...current,
        [activeKind]: undefined,
      }));
      try {
        const payload = await fetchFinanceStatement(baseUrl, activeKind, symbol, period, controller.signal);
        if (cancelled) {
          return;
        }
        setPayloads((current) => ({
          ...current,
          [activeKind]: payload,
        }));
      } catch (error) {
        if (cancelled || controller.signal.aborted) {
          return;
        }
        setPayloads((current) => ({
          ...current,
          [activeKind]: null,
        }));
        setErrorsByKind((current) => ({
          ...current,
          [activeKind]:
            error instanceof Error
              ? error.message
              : `Failed to load ${activeKind.replace("-", " ")} statement.`,
        }));
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    };

    void loadStatements();

    return () => {
      cancelled = true;
      controller.abort();
    };
  }, [activeKind, baseUrl, period, symbol]);

  useEffect(() => {
    if (!baseUrl || !symbol || activeTab !== "forecast") {
      setIsForecastLoading(false);
      return () => undefined;
    }

    const controller = new AbortController();
    let cancelled = false;

    const loadForecast = async () => {
      setIsForecastLoading(true);
      setForecastError(null);
      try {
        const payload = await fetchFinanceForecast(baseUrl, symbol, controller.signal);
        if (cancelled) {
          return;
        }
        setForecastPayload(payload);
      } catch (error) {
        if (cancelled || controller.signal.aborted) {
          return;
        }
        setForecastError(error instanceof Error ? error.message : "Failed to load forecast.");
        setForecastPayload(null);
      } finally {
        if (!cancelled) {
          setIsForecastLoading(false);
        }
      }
    };

    void loadForecast();

    return () => {
      cancelled = true;
      controller.abort();
    };
  }, [activeTab, baseUrl, symbol]);

  const tradingViewLink = useMemo(
    () => buildTradingViewFinancialLink(symbol, activeTab),
    [activeTab, symbol],
  );
  const activePayload = activeKind ? payloads[activeKind] : null;
  const activeError = activeKind ? errorsByKind[activeKind] ?? null : null;
  const forecastFallback = renderTradingViewFallback(
    symbol,
    theme,
    overviewHeight,
    "OpenBB forecast is unavailable. Showing TradingView financial view instead.",
    "TradingView remains available even when analyst consensus data cannot be loaded from the active backend.",
    forecastError,
  );
  const statementFallback = renderTradingViewFallback(
    symbol,
    theme,
    overviewHeight,
    "OpenBB statements are unavailable. Showing TradingView financial view instead.",
    "TradingView financials are shown as a fallback while the selected backend is offline, unauthenticated, or missing statement coverage for this ticker.",
    activeError ?? (!baseUrl ? "OpenBB backend is not currently connected." : null),
  );

  return (
    <PanelCard
      title="Fundamental Data"
      description="TradingView powers the overview. Forecasts and each financial statement render inline with visual summaries so you can inspect targets, trends, and raw statement rows without leaving this page."
    >
      <div className="space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap gap-2">
            {TAB_OPTIONS.map((tab) => (
              <button
                key={tab.id}
                type="button"
                onClick={() => setActiveTab(tab.id)}
                className={`rounded-full border px-3 py-1.5 body-xxs-medium transition-colors ${
                  activeTab === tab.id
                    ? "border-sky-400/60 bg-sky-500/10 text-sky-300"
                    : "border-theme-outline bg-theme-secondary text-theme-muted hover:text-theme-primary"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
          <div className="flex flex-wrap items-center gap-2">
            {activeKind ? (
              <div className="flex rounded-full border border-theme-outline bg-theme-secondary p-1">
                {(["annual", "quarterly"] as FinanceStatementPeriod[]).map((option) => (
                  <button
                    key={option}
                    type="button"
                    onClick={() => setPeriod(option)}
                    className={`rounded-full px-3 py-1 body-xxs-medium transition-colors ${
                      period === option
                        ? "bg-theme-primary text-theme-primary"
                        : "text-theme-muted hover:text-theme-primary"
                    }`}
                  >
                    {option === "annual" ? "Annual" : "Quarterly"}
                  </button>
                ))}
              </div>
            ) : null}
            <a
              href={tradingViewLink.href}
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-full border border-theme-outline bg-theme-secondary px-3 py-1.5 body-xxs-medium text-theme-primary transition-colors hover:border-sky-400/60 hover:text-sky-300"
            >
              Open in TradingView
            </a>
          </div>
        </div>

        {activeTab === "overview" ? (
          <TradingViewWidgetEmbed
            widgetType="fundamental-data"
            symbol={symbol}
            theme={theme}
            title="Fundamental Data"
            minHeight={overviewHeight}
            frameHeight={overviewHeight}
          />
        ) : activeTab === "forecast" ? (
          forecastError && !forecastPayload ? (
            forecastFallback
          ) : isForecastLoading && !forecastPayload ? (
            <div className="rounded-sm border border-dashed border-theme-outline bg-theme-secondary/40 px-4 py-6">
              <p className="body-xs-medium text-theme-primary">Loading forecast...</p>
              <p className="mt-1 body-xxs-regular text-theme-muted">
                Pulling analyst consensus targets and recommendation data from OpenBB.
              </p>
            </div>
          ) : forecastPayload ? (
            forecastPayload.consensus ? renderForecast(forecastPayload) : forecastFallback
          ) : null
        ) : !baseUrl ? (
          statementFallback
        ) : activeError && !activePayload ? (
          statementFallback
        ) : isLoading && !activePayload ? (
          <div className="rounded-sm border border-dashed border-theme-outline bg-theme-secondary/40 px-4 py-6">
            <p className="body-xs-medium text-theme-primary">Loading financial statements...</p>
            <p className="mt-1 body-xxs-regular text-theme-muted">
              Pulling the latest {activeTab.replace("-", " ")} data from OpenBB.
            </p>
          </div>
        ) : activeKind && activePayload ? (
          activePayload.rows.length > 0 ? renderTable(activeKind, activePayload, period) : statementFallback
        ) : null}
      </div>
    </PanelCard>
  );
}
