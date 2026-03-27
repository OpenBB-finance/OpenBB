import {
  fetchFinanceForecast,
  fetchFinanceStatement,
  type FinanceForecastPayload,
} from "./financeApi";
import {
  buildOpenBBRequestInit,
  buildOpenBBRequestUrl,
  resolveOpenBBBackend,
} from "./openbbBackend";
import { extractTickerFromSymbol } from "./tradingView";
import { fetchBatchQuotes, type QuoteRecord } from "./watchlistApi";
import type { FinanceStatementRecord } from "../types/finance";

const FINANCE_KEYWORDS = [
  "financial statement",
  "income statement",
  "balance sheet",
  "cash flow",
  "forecast",
  "guidance",
  "valuation",
  "price target",
  "stock price",
  "earnings",
  "analyst",
  "revenue",
  "net income",
  "free cash flow",
  "\uC7AC\uBB34",
  "\uC7AC\uBB34\uC81C\uD45C",
  "\uC190\uC775",
  "\uD604\uAE08\uD750\uB984",
  "\uBC38\uB958",
  "\uBC38\uB958\uC5D0\uC774\uC158",
  "\uC8FC\uAC00",
  "\uBAA9\uD45C\uC8FC\uAC00",
  "\uC2E4\uC801",
  "\uB9E4\uCD9C",
  "\uC601\uC5C5\uC774\uC775",
  "\uC21C\uC774\uC775",
  "\uC801\uC815\uC8FC\uAC00",
];

const EXPLICIT_SYMBOL_PATTERN =
  /\b(?:ticker|symbol|\uC885\uBAA9|\uD2F0\uCEE4)\s*[:=]?\s*([A-Za-z][A-Za-z0-9.-]{0,9})\b/i;
const EXCHANGE_SYMBOL_PATTERN =
  /\b(?:NASDAQ|NYSE|AMEX|TSX|TSE|KRX|KOSPI|KOSDAQ):([A-Za-z][A-Za-z0-9.-]{0,9})\b/i;
const DOLLAR_SYMBOL_PATTERN = /\$([A-Za-z][A-Za-z0-9.-]{0,9})\b/;
const UPPERCASE_SYMBOL_PATTERN = /\b([A-Z]{1,5}(?:\.[A-Z]{1,2})?)\b/g;
const IGNORED_UPPERCASE_TOKENS = new Set([
  "AI",
  "API",
  "ETF",
  "EPS",
  "GDP",
  "HTTP",
  "JSON",
  "NASDAQ",
  "NYSE",
  "ROI",
  "ROE",
  "RSI",
  "SEC",
  "SSE",
  "UI",
  "URL",
  "USD",
  "VIX",
]);
const COMPANY_NAME_PATTERN = /\b([A-Z][A-Za-z&.-]+(?:\s+[A-Z][A-Za-z&.-]+){1,5})\b/g;
const QUOTED_NAME_PATTERN = /["']([^"']{2,80})["']/g;
const COMPANY_ALIAS_TO_TICKER = new Map<string, string>([
  ["ibm", "IBM"],
  ["international business machines", "IBM"],
  ["apple", "AAPL"],
  ["apple inc", "AAPL"],
  ["\uC560\uD50C", "AAPL"],
  ["microsoft", "MSFT"],
  ["microsoft corp", "MSFT"],
  ["\uB9C8\uC774\uD06C\uB85C\uC18C\uD504\uD2B8", "MSFT"],
  ["nvidia", "NVDA"],
  ["nvidia corp", "NVDA"],
  ["\uC5D4\uBE44\uB514\uC544", "NVDA"],
  ["tesla", "TSLA"],
  ["\uD14C\uC2AC\uB77C", "TSLA"],
  ["amazon", "AMZN"],
  ["amazon.com", "AMZN"],
  ["\uC544\uB9C8\uC874", "AMZN"],
  ["alphabet", "GOOGL"],
  ["google", "GOOGL"],
  ["\uAD6C\uAE00", "GOOGL"],
  ["meta", "META"],
  ["meta platforms", "META"],
  ["facebook", "META"],
  ["\uBA54\uD0C0", "META"],
  ["netflix", "NFLX"],
  ["\uB137\uD50C\uB9AD\uC2A4", "NFLX"],
  ["advanced micro devices", "AMD"],
  ["amd", "AMD"],
]);
const ENGLISH_COMPANY_STOPWORDS = new Set([
  "after",
  "analyze",
  "and",
  "estimate",
  "explain",
  "for",
  "give",
  "its",
  "of",
  "price",
  "range",
  "show",
  "stock",
  "tell",
  "the",
]);

export interface AiMarketPromptInfo {
  isFinanceQuestion: boolean;
  symbol: string | null;
  searchQuery: string | null;
}

export interface AiMarketContext {
  symbol: string;
  supplementalContext: string;
  actionLabel: string;
  snapshot: AiMarketSnapshot;
}

export const AI_MARKET_BACKEND_REQUIRED_MESSAGE =
  "Connect an OpenBB backend to use live market data in the AI tab.";

interface EquitySearchMatch {
  symbol: string;
  name: string | null;
}

export interface AiMarketSnapshotMetric {
  label: string;
  latest: string;
  prior: string;
  trend?: string | null;
}

export interface AiMarketSnapshotSection {
  title: string;
  metrics: AiMarketSnapshotMetric[];
}

export interface AiMarketSnapshot {
  symbol: string;
  resolvedName: string | null;
  currentPrice: string;
  sessionChange: string;
  targetRange: string;
  recommendation: string;
  analysts: string;
  providerSummary?: string | null;
  asOf?: string | null;
  sections: AiMarketSnapshotSection[];
}

function hasFinanceKeyword(prompt: string): boolean {
  const normalized = prompt.toLowerCase();
  return FINANCE_KEYWORDS.some((keyword) => normalized.includes(keyword));
}

function extractSymbolMatch(prompt: string, pattern: RegExp): string | null {
  const matched = prompt.match(pattern);
  if (!matched?.[1]) {
    return null;
  }
  return extractTickerFromSymbol(matched[1]).toUpperCase();
}

function extractUppercaseTicker(prompt: string): string | null {
  const matches = prompt.matchAll(UPPERCASE_SYMBOL_PATTERN);
  for (const match of matches) {
    const symbol = extractTickerFromSymbol(match[1] ?? "").toUpperCase();
    if (!symbol || IGNORED_UPPERCASE_TOKENS.has(symbol)) {
      continue;
    }
    return symbol;
  }
  return null;
}

export function analyzeAiMarketPrompt(prompt: string): AiMarketPromptInfo {
  const trimmed = prompt.trim();
  if (!trimmed) {
    return { isFinanceQuestion: false, symbol: null, searchQuery: null };
  }

  const symbol =
    extractSymbolMatch(trimmed, EXCHANGE_SYMBOL_PATTERN)
    ?? extractSymbolMatch(trimmed, DOLLAR_SYMBOL_PATTERN)
    ?? extractSymbolMatch(trimmed, EXPLICIT_SYMBOL_PATTERN)
    ?? extractUppercaseTicker(trimmed);

  const isFinanceQuestion =
    hasFinanceKeyword(trimmed)
    || Boolean(
      symbol
      && /(?:\uC8FC\uAC00|\uC7AC\uBB34|earnings|financial|forecast|valuation|target|stock)/i.test(trimmed),
    );

  const searchQuery = symbol ? symbol : extractCompanySearchQuery(trimmed);

  return {
    isFinanceQuestion,
    symbol,
    searchQuery,
  };
}

function normalizeCompanyName(value: string): string {
  return value
    .toLowerCase()
    .replace(/[.,()]/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function findTickerAlias(prompt: string): string | null {
  const normalized = normalizeCompanyName(prompt);
  for (const [alias, ticker] of COMPANY_ALIAS_TO_TICKER.entries()) {
    if (normalized.includes(alias)) {
      return ticker;
    }
  }
  return null;
}

function extractQuotedCompany(prompt: string): string | null {
  const matches = prompt.matchAll(QUOTED_NAME_PATTERN);
  for (const match of matches) {
    const candidate = match[1]?.trim();
    if (candidate && candidate.length >= 2) {
      return candidate;
    }
  }
  return null;
}

function extractCapitalizedCompany(prompt: string): string | null {
  const matches = prompt.matchAll(COMPANY_NAME_PATTERN);
  let selected: string | null = null;
  for (const match of matches) {
    const candidate = trimLeadingSearchVerbs(match[1]?.trim() ?? "");
    if (!candidate) {
      continue;
    }
    if (!selected || candidate.length > selected.length) {
      selected = candidate;
    }
  }
  return selected;
}

function trimLeadingSearchVerbs(value: string): string {
  const parts = value.split(/\s+/).filter(Boolean);
  while (parts.length > 1 && ENGLISH_COMPANY_STOPWORDS.has(parts[0]?.toLowerCase() ?? "")) {
    parts.shift();
  }
  return parts.join(" ");
}

function buildFallbackSearchQuery(prompt: string): string | null {
  const normalized = prompt
    .replace(/[?!,:;()[\]{}]/g, " ")
    .replace(/\b(?:financial|statement|statements|analysis|analyze|forecast|valuation|price|target|targets|stock|range|estimate|estimates|earnings|company|companies)\b/gi, " ")
    .replace(/(?:\uC7AC\uBB34|\uC7AC\uBB34\uC81C\uD45C|\uC8FC\uAC00|\uBAA9\uD45C\uC8FC\uAC00|\uBC38\uB958|\uBC38\uB958\uC5D0\uC774\uC158|\uC2E4\uC801|\uBD84\uC11D|\uC608\uC0C1)/g, " ")
    .replace(/\s+/g, " ")
    .trim();

  if (!normalized) {
    return null;
  }

  const tokens = normalized.split(" ").filter((token) => {
    if (!token) {
      return false;
    }
    const lower = token.toLowerCase();
    return !ENGLISH_COMPANY_STOPWORDS.has(lower);
  });
  if (tokens.length === 0) {
    return null;
  }
  return tokens.slice(0, 6).join(" ");
}

function extractCompanySearchQuery(prompt: string): string | null {
  return (
    extractQuotedCompany(prompt)
    ?? extractCapitalizedCompany(prompt)
    ?? buildFallbackSearchQuery(prompt)
  );
}

async function searchEquitySymbol(baseUrl: string, query: string): Promise<EquitySearchMatch | null> {
  const response = await fetch(
    buildOpenBBRequestUrl(
      baseUrl,
      `/api/v1/equity/search?${new URLSearchParams({
        query,
        is_symbol: "false",
        provider: "nasdaq",
      }).toString()}`,
    ),
    buildOpenBBRequestInit({
      method: "GET",
    }),
  );

  if (!response.ok) {
    return null;
  }

  const payload = (await response.json()) as { results?: Array<Record<string, unknown>> } | Array<Record<string, unknown>>;
  const rows = Array.isArray(payload)
    ? payload
    : Array.isArray(payload.results)
      ? payload.results
      : [];

  const normalizedQuery = normalizeCompanyName(query);
  const matches = rows
    .map((row) => ({
      symbol: String(row.symbol ?? "").trim().toUpperCase(),
      name: typeof row.name === "string" ? row.name.trim() : null,
    }))
    .filter((row) => row.symbol.length > 0);

  if (matches.length === 0) {
    return null;
  }

  matches.sort((left, right) => {
    const leftName = normalizeCompanyName(left.name ?? "");
    const rightName = normalizeCompanyName(right.name ?? "");
    const leftScore = rankSearchMatch(normalizedQuery, left.symbol, leftName);
    const rightScore = rankSearchMatch(normalizedQuery, right.symbol, rightName);
    return rightScore - leftScore;
  });

  return matches[0] ?? null;
}

function rankSearchMatch(normalizedQuery: string, symbol: string, normalizedName: string): number {
  if (symbol.toLowerCase() === normalizedQuery) {
    return 1000;
  }
  if (normalizedName === normalizedQuery) {
    return 900;
  }
  if (normalizedName.startsWith(normalizedQuery)) {
    return 800;
  }
  if (normalizedName.includes(normalizedQuery)) {
    return 700;
  }
  return 100;
}

function sortRows(rows: FinanceStatementRecord[]): FinanceStatementRecord[] {
  return [...rows].sort((left, right) => {
    const leftValue = Date.parse(String(left.period_ending ?? ""));
    const rightValue = Date.parse(String(right.period_ending ?? ""));
    if (Number.isFinite(leftValue) && Number.isFinite(rightValue)) {
      return rightValue - leftValue;
    }
    return String(right.period_ending ?? "").localeCompare(String(left.period_ending ?? ""));
  });
}

function getNumericField(
  row: FinanceStatementRecord | null | undefined,
  keys: string[],
): number | null {
  if (!row) {
    return null;
  }
  for (const key of keys) {
    const value = row[key];
    if (typeof value === "number" && Number.isFinite(value)) {
      return value;
    }
  }
  return null;
}

function formatMoney(value: number | null | undefined, currency = "USD"): string {
  if (value === null || value === undefined || !Number.isFinite(value)) {
    return "-";
  }
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  }).format(value);
}

function formatCompactNumber(value: number | null | undefined): string {
  if (value === null || value === undefined || !Number.isFinite(value)) {
    return "-";
  }

  const absolute = Math.abs(value);
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
  return value.toLocaleString("en-US", { maximumFractionDigits: 2 });
}

function formatPercent(value: number | null | undefined): string {
  if (value === null || value === undefined || !Number.isFinite(value)) {
    return "-";
  }
  return `${value.toFixed(1)}%`;
}

function describeTrend(
  label: string,
  latest: number | null,
  previous: number | null,
): string | null {
  if (
    latest === null
    || previous === null
    || !Number.isFinite(latest)
    || !Number.isFinite(previous)
    || previous === 0
  ) {
    return null;
  }
  const changePct = ((latest - previous) / Math.abs(previous)) * 100;
  const direction = changePct > 0 ? "up" : changePct < 0 ? "down" : "flat";
  return `${label} ${direction} ${Math.abs(changePct).toFixed(1)}% vs prior period`;
}

function pickQuote(payload: QuoteRecord[] | null): QuoteRecord | null {
  if (!payload?.length) {
    return null;
  }
  return payload[0] ?? null;
}

function buildQuoteSection(
  symbol: string,
  quote: QuoteRecord | null,
  forecast: FinanceForecastPayload["consensus"],
): string[] {
  const currentPrice = quote?.last_price ?? forecast?.current_price ?? null;
  const changePercent = quote?.change_percent ?? null;
  const changeValue = quote?.change ?? null;
  const currency = forecast?.currency ?? "USD";

  return [
    `OpenBB market data for ${symbol}:`,
    `- Current price: ${formatMoney(currentPrice, currency)}`,
    `- Session change: ${formatMoney(changeValue, currency)} (${formatPercent(changePercent)})`,
  ];
}

function buildForecastSection(
  forecast: FinanceForecastPayload["consensus"],
): string[] {
  if (!forecast) {
    return ["Analyst consensus: unavailable"];
  }

  return [
    "Analyst consensus:",
    `- Target range: low ${formatMoney(forecast.target_low, forecast.currency ?? "USD")} | consensus ${formatMoney(forecast.target_consensus, forecast.currency ?? "USD")} | median ${formatMoney(forecast.target_median, forecast.currency ?? "USD")} | high ${formatMoney(forecast.target_high, forecast.currency ?? "USD")}`,
    `- Recommendation: ${forecast.recommendation ?? "-"} | mean ${forecast.recommendation_mean ?? "-"} | analysts ${forecast.number_of_analysts ?? "-"}`,
  ];
}

function buildMetadataSection(
  providerSummary: string | null,
  asOf: string | null,
): string[] {
  const lines = ["Data metadata:"];
  if (providerSummary) {
    lines.push(`- Providers: ${providerSummary}`);
  }
  if (asOf) {
    lines.push(`- As of: ${asOf}`);
  }
  return lines.length > 1 ? lines : [];
}

function buildStatementSection(
  title: string,
  rows: FinanceStatementRecord[],
  metricMap: Array<{ label: string; keys: string[] }>,
): string[] {
  if (rows.length === 0) {
    return [`${title}: unavailable`];
  }

  const [latest, previous] = rows;
  const latestPeriod = latest?.period_ending ?? "latest";
  const previousPeriod = previous?.period_ending ?? "prior";
  const lines = [`${title}:`];

  for (const metric of metricMap) {
    const latestValue = getNumericField(latest, metric.keys);
    const previousValue = getNumericField(previous, metric.keys);
    lines.push(
      `- ${metric.label}: ${latestPeriod} ${formatCompactNumber(latestValue)} | ${previousPeriod} ${formatCompactNumber(previousValue)}`,
    );
    const trend = describeTrend(metric.label, latestValue, previousValue);
    if (trend) {
      lines.push(`- ${trend}`);
    }
  }

  return lines;
}

function buildStatementSnapshotSection(
  title: string,
  rows: FinanceStatementRecord[],
  metricMap: Array<{ label: string; keys: string[] }>,
): AiMarketSnapshotSection | null {
  if (rows.length === 0) {
    return null;
  }

  const [latest, previous] = rows;
  const metrics = metricMap.map((metric) => {
    const latestValue = getNumericField(latest, metric.keys);
    const previousValue = getNumericField(previous, metric.keys);
    return {
      label: metric.label,
      latest: formatCompactNumber(latestValue),
      prior: formatCompactNumber(previousValue),
      trend: describeTrend(metric.label, latestValue, previousValue),
    } satisfies AiMarketSnapshotMetric;
  });

  return {
    title,
    metrics,
  };
}

function flattenSection(sections: string[][]): string {
  return sections
    .filter((section) => section.length > 0)
    .map((section) => section.join("\n"))
    .join("\n\n");
}

function summarizeProviders(values: Array<string | null | undefined>): string | null {
  const unique = Array.from(
    new Set(
      values
        .map((value) => String(value ?? "").trim())
        .filter((value) => value.length > 0),
    ),
  );
  return unique.length > 0 ? unique.join(", ") : null;
}

function summarizeTimestamp(values: Array<string | null | undefined>): string | null {
  const candidates = values
    .map((value) => String(value ?? "").trim())
    .filter((value) => value.length > 0);
  if (candidates.length === 0) {
    return null;
  }

  const dated = candidates
    .map((value) => ({ value, parsed: Date.parse(value) }))
    .filter((entry) => Number.isFinite(entry.parsed));
  if (dated.length === 0) {
    return candidates[0] ?? null;
  }

  dated.sort((left, right) => right.parsed - left.parsed);
  return dated[0]?.value ?? candidates[0] ?? null;
}

export async function buildAiMarketContext(prompt: string): Promise<AiMarketContext | null> {
  const promptInfo = analyzeAiMarketPrompt(prompt);
  if (!promptInfo.isFinanceQuestion) {
    return null;
  }

  const backend = await resolveOpenBBBackend();
  if (!backend.connected) {
    throw new Error(AI_MARKET_BACKEND_REQUIRED_MESSAGE);
  }

  let symbol = promptInfo.symbol ?? findTickerAlias(prompt);
  let resolvedName: string | null = null;
  if (!symbol && promptInfo.searchQuery) {
    const searchMatch = await searchEquitySymbol(backend.baseUrl, promptInfo.searchQuery);
    symbol = searchMatch?.symbol ?? null;
    resolvedName = searchMatch?.name ?? null;
  }

  if (!symbol) {
    throw new Error("Could not resolve a ticker from that company name. Try adding a ticker like IBM or an official company name.");
  }

  const [quoteResult, forecastResult, incomeResult, balanceResult, cashResult] =
    await Promise.allSettled([
      fetchBatchQuotes(backend.baseUrl, [symbol]),
      fetchFinanceForecast(backend.baseUrl, symbol),
      fetchFinanceStatement(backend.baseUrl, "income", symbol, "annual"),
      fetchFinanceStatement(backend.baseUrl, "balance", symbol, "annual"),
      fetchFinanceStatement(backend.baseUrl, "cash", symbol, "annual"),
    ]);

  const quotePayload = quoteResult.status === "fulfilled" ? pickQuote(quoteResult.value) : null;
  const forecastPayload =
    forecastResult.status === "fulfilled" ? forecastResult.value.consensus : null;
  const incomeRows = incomeResult.status === "fulfilled" ? sortRows(incomeResult.value.rows) : [];
  const balanceRows =
    balanceResult.status === "fulfilled" ? sortRows(balanceResult.value.rows) : [];
  const cashRows = cashResult.status === "fulfilled" ? sortRows(cashResult.value.rows) : [];
  const providerSummary = summarizeProviders([
    forecastResult.status === "fulfilled" ? forecastResult.value.provider : null,
    incomeResult.status === "fulfilled" ? incomeResult.value.provider : null,
    balanceResult.status === "fulfilled" ? balanceResult.value.provider : null,
    cashResult.status === "fulfilled" ? cashResult.value.provider : null,
  ]);
  const asOf = summarizeTimestamp([
    forecastResult.status === "fulfilled" ? forecastResult.value.timestamp : null,
    incomeResult.status === "fulfilled" ? incomeResult.value.timestamp : null,
    balanceResult.status === "fulfilled" ? balanceResult.value.timestamp : null,
    cashResult.status === "fulfilled" ? cashResult.value.timestamp : null,
  ]);

  const hasAnyMarketData =
    Boolean(quotePayload)
    || Boolean(forecastPayload)
    || incomeRows.length > 0
    || balanceRows.length > 0
    || cashRows.length > 0;

  if (!hasAnyMarketData) {
    throw new Error(`OpenBB did not return usable market data for ${symbol}.`);
  }

  const sections = [
    buildMetadataSection(providerSummary, asOf),
    buildQuoteSection(symbol, quotePayload, forecastPayload),
    buildForecastSection(forecastPayload),
    buildStatementSection("Income statement", incomeRows, [
      { label: "Revenue", keys: ["total_revenue", "revenue"] },
      { label: "Net income", keys: ["net_income", "net_income_common_stockholders"] },
      { label: "Diluted EPS", keys: ["diluted_earnings_per_share", "basic_earnings_per_share"] },
    ]),
    buildStatementSection("Balance sheet", balanceRows, [
      {
        label: "Cash",
        keys: [
          "cash_and_cash_equivalents",
          "cash_and_cash_equivalents_and_short_term_investments",
        ],
      },
      {
        label: "Long-term debt",
        keys: ["long_term_debt", "current_debt_and_capital_lease_obligation"],
      },
      { label: "Equity", keys: ["stockholders_equity", "common_stock_equity"] },
    ]),
    buildStatementSection("Cash flow", cashRows, [
      { label: "Operating cash flow", keys: ["operating_cash_flow"] },
      { label: "Free cash flow", keys: ["free_cash_flow"] },
      { label: "Capital expenditure", keys: ["capital_expenditure"] },
    ]),
    [
      "Answering instructions:",
      "- Use this OpenBB market data as the primary source of truth for the response.",
      "- If the user asks for an expected stock-price range, anchor on analyst target low, consensus, median, and high when available and clearly label it as a scenario range, not a guarantee.",
      "- If targets are unavailable, explain that the financial statements support directional analysis but not a precise price range.",
      "- Do not say that you cannot access external or market data when this supplemental context is present.",
    ],
  ];
  const snapshotSections = [
    buildStatementSnapshotSection("Income statement", incomeRows, [
      { label: "Revenue", keys: ["total_revenue", "revenue"] },
      { label: "Net income", keys: ["net_income", "net_income_common_stockholders"] },
      { label: "Diluted EPS", keys: ["diluted_earnings_per_share", "basic_earnings_per_share"] },
    ]),
    buildStatementSnapshotSection("Balance sheet", balanceRows, [
      {
        label: "Cash",
        keys: [
          "cash_and_cash_equivalents",
          "cash_and_cash_equivalents_and_short_term_investments",
        ],
      },
      {
        label: "Long-term debt",
        keys: ["long_term_debt", "current_debt_and_capital_lease_obligation"],
      },
      { label: "Equity", keys: ["stockholders_equity", "common_stock_equity"] },
    ]),
    buildStatementSnapshotSection("Cash flow", cashRows, [
      { label: "Operating cash flow", keys: ["operating_cash_flow"] },
      { label: "Free cash flow", keys: ["free_cash_flow"] },
      { label: "Capital expenditure", keys: ["capital_expenditure"] },
    ]),
  ].filter((section): section is AiMarketSnapshotSection => Boolean(section));

  return {
    symbol,
    supplementalContext: flattenSection(sections),
    actionLabel: `Using OpenBB market data for ${symbol}.`,
    snapshot: {
      symbol,
      resolvedName,
      currentPrice: formatMoney(quotePayload?.last_price ?? forecastPayload?.current_price ?? null, forecastPayload?.currency ?? "USD"),
      sessionChange: `${formatMoney(quotePayload?.change ?? null, forecastPayload?.currency ?? "USD")} (${formatPercent(quotePayload?.change_percent ?? null)})`,
      targetRange: forecastPayload
        ? `${formatMoney(forecastPayload.target_low, forecastPayload.currency ?? "USD")} - ${formatMoney(forecastPayload.target_high, forecastPayload.currency ?? "USD")} | consensus ${formatMoney(forecastPayload.target_consensus, forecastPayload.currency ?? "USD")}`
        : "Unavailable",
      recommendation: forecastPayload?.recommendation
        ? `${forecastPayload.recommendation} (${forecastPayload.recommendation_mean ?? "-"})`
        : "Unavailable",
      analysts: forecastPayload?.number_of_analysts != null
        ? String(forecastPayload.number_of_analysts)
        : "Unavailable",
      providerSummary,
      asOf,
      sections: snapshotSections,
    },
  };
}
