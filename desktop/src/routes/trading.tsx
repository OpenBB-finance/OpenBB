import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useMemo, useState } from "react";
import { DashboardLineChart } from "../components/quant/DashboardLineChart";
import { PanelCard } from "../components/quant/PanelCard";
import { SummaryCard } from "../components/quant/SummaryCard";
import { resolveOpenBBBackend } from "../lib/openbbBackend";
import {
  approveTradingOrder,
  cancelTradingOrder,
  closeTradingPosition,
  fetchTradingAlgorithms,
  fetchTradingEvents,
  fetchTradingExecutionMode,
  fetchTradingFills,
  fetchTradingOrders,
  fetchTradingPerformance,
  fetchTradingPositions,
  fetchTradingRisk,
  fetchTradingScanHistory,
  fetchTradingScanLatest,
  fetchTradingSettings,
  fetchTradingStatus,
  fetchTradingSymbolDetail,
  probeQuantMlActivation,
  runTradingCycle,
  toggleTradingAlgorithm,
  updateTradingExecutionMode,
  updateTradingSettings,
  validateTradingAlgorithm,
} from "../lib/quantApi";
import type {
  TradingAlgorithmRecordPayload,
  TradingExecutionModePayload,
  TradingOrderItemPayload,
  TradingPerformancePayload,
  TradingRiskPayload,
  TradingScanPayload,
  TradingSettingsPayload,
  TradingStatusPayload,
  TradingSymbolDetailPayload,
} from "../types/quant";

function toErrorMessage(error: unknown): string {
  return error instanceof Error ? error.message : "Request failed";
}

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === "object" ? (value as Record<string, unknown>) : {};
}

function numberFrom(value: unknown, fallback = 0): number {
  return typeof value === "number" && Number.isFinite(value) ? value : fallback;
}

function boolFrom(value: unknown, fallback = false): boolean {
  return typeof value === "boolean" ? value : fallback;
}

function formatMoney(value: number | null | undefined): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "-";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

function formatPct(value: number | null | undefined, digits = 2): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "-";
  return `${(value * 100).toFixed(digits)}%`;
}

function formatNum(value: number | null | undefined, digits = 2): string {
  if (value === null || value === undefined || Number.isNaN(value)) return "-";
  return value.toFixed(digits);
}

function formatDateTime(value: string | null | undefined): string {
  if (!value) return "-";
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return parsed.toLocaleString();
}

function badgeClass(value: string | null | undefined): string {
  const key = (value ?? "").toLowerCase();
  if (["pass", "filled", "running", "active"].includes(key)) return "bg-emerald-500/15 text-emerald-300";
  if (["pending", "warning", "paused", "submitted", "sandbox"].includes(key)) return "bg-amber-500/15 text-amber-300";
  if (["rejected", "critical", "cancelled", "stopped"].includes(key)) return "bg-red-500/15 text-red-300";
  return "bg-theme-secondary text-theme-muted";
}

interface SettingsFormState {
  lookbackDays: number;
  autoOrder: boolean;
  manualApproval: boolean;
  signalGeneration: boolean;
  maxConcurrentPositions: number;
  positionSizeValue: number;
  maxDailyNewEntries: number;
  stopLossPct: number;
  takeProfitPct: number;
  trailingStopEnabled: boolean;
}

function TradingPage() {
  const [baseUrl, setBaseUrl] = useState("");
  const [activationMessage, setActivationMessage] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [lastRefreshed, setLastRefreshed] = useState<string | null>(null);
  const [status, setStatus] = useState<TradingStatusPayload | null>(null);
  const [settings, setSettings] = useState<TradingSettingsPayload | null>(null);
  const [scan, setScan] = useState<TradingScanPayload | null>(null);
  const [scanHistory, setScanHistory] = useState<TradingScanPayload | null>(null);
  const [orders, setOrders] = useState<TradingOrderItemPayload[]>([]);
  const [fillsCount, setFillsCount] = useState(0);
  const [positions, setPositions] = useState<Array<Record<string, unknown>>>([]);
  const [performance, setPerformance] = useState<TradingPerformancePayload | null>(null);
  const [risk, setRisk] = useState<TradingRiskPayload | null>(null);
  const [events, setEvents] = useState<Array<Record<string, unknown>>>([]);
  const [algorithms, setAlgorithms] = useState<TradingAlgorithmRecordPayload[]>([]);
  const [symbolDetail, setSymbolDetail] = useState<TradingSymbolDetailPayload | null>(null);
  const [selectedTicker, setSelectedTicker] = useState("");
  const [executionMode, setExecutionMode] = useState("paper");
  const [executionModePayload, setExecutionModePayload] = useState<TradingExecutionModePayload | null>(null);
  const [form, setForm] = useState<SettingsFormState>({
    lookbackDays: 320,
    autoOrder: false,
    manualApproval: false,
    signalGeneration: true,
    maxConcurrentPositions: 12,
    positionSizeValue: 0.05,
    maxDailyNewEntries: 5,
    stopLossPct: 0.08,
    takeProfitPct: 0.15,
    trailingStopEnabled: false,
  });

  async function loadSymbolDetail(nextBaseUrl: string, ticker: string) {
    if (!ticker.trim()) return;
    try {
      setSymbolDetail(await fetchTradingSymbolDetail(nextBaseUrl, ticker));
    } catch (error) {
      setErrorMessage(toErrorMessage(error));
    }
  }

  async function refreshAll(nextBaseUrl: string) {
    if (!nextBaseUrl) return;
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const [
        nextStatus,
        nextSettings,
        nextScan,
        nextScanHistory,
        nextOrders,
        nextFills,
        nextPositions,
        nextPerformance,
        nextRisk,
        nextEvents,
        nextAlgorithms,
        nextExecutionMode,
      ] = await Promise.all([
        fetchTradingStatus(nextBaseUrl),
        fetchTradingSettings(nextBaseUrl),
        fetchTradingScanLatest(nextBaseUrl),
        fetchTradingScanHistory(nextBaseUrl),
        fetchTradingOrders(nextBaseUrl),
        fetchTradingFills(nextBaseUrl),
        fetchTradingPositions(nextBaseUrl),
        fetchTradingPerformance(nextBaseUrl),
        fetchTradingRisk(nextBaseUrl),
        fetchTradingEvents(nextBaseUrl),
        fetchTradingAlgorithms(nextBaseUrl),
        fetchTradingExecutionMode(nextBaseUrl),
      ]);
      setStatus(nextStatus);
      setSettings(nextSettings);
      setScan(nextScan);
      setScanHistory(nextScanHistory);
      setOrders(nextOrders.items);
      setFillsCount(nextFills.items.length);
      setPositions(nextPositions.items);
      setPerformance(nextPerformance);
      setRisk(nextRisk);
      setEvents(nextEvents.items);
      setAlgorithms(nextAlgorithms.items);
      setExecutionMode(nextExecutionMode.mode);
      setExecutionModePayload(nextExecutionMode);
      setLastRefreshed(new Date().toLocaleTimeString());
      const execution = asRecord(nextSettings.execution);
      const account = asRecord(nextSettings.account);
      const riskCfg = asRecord(nextSettings.risk);
      setForm({
        lookbackDays: numberFrom(asRecord(nextSettings.scan).lookback_days, 320),
        autoOrder: boolFrom(execution.auto_order, false),
        manualApproval: boolFrom(execution.manual_approval, false),
        signalGeneration: boolFrom(execution.signal_generation, true),
        maxConcurrentPositions: numberFrom(account.max_concurrent_positions, 12),
        positionSizeValue: numberFrom(account.position_size_value, 0.05),
        maxDailyNewEntries: numberFrom(account.max_daily_new_entries, 5),
        stopLossPct: numberFrom(riskCfg.stop_loss_pct, 0.08),
        takeProfitPct: numberFrom(riskCfg.take_profit_pct, 0.15),
        trailingStopEnabled: boolFrom(riskCfg.trailing_stop_enabled, false),
      });
      const fallbackTicker = selectedTicker || nextScan.items[0]?.ticker || String(nextPositions.items[0]?.ticker ?? "");
      if (fallbackTicker) {
        setSelectedTicker(fallbackTicker);
        await loadSymbolDetail(nextBaseUrl, fallbackTicker);
      }
    } catch (error) {
      setErrorMessage(toErrorMessage(error));
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void (async () => {
      try {
        const backend = await resolveOpenBBBackend();
        setBaseUrl(backend.baseUrl);
        const activation = await probeQuantMlActivation(backend.baseUrl);
        if (!activation.available) {
          setActivationMessage(activation.detail || "quant_ml extension unavailable.");
        }
      } catch (error) {
        setErrorMessage(toErrorMessage(error));
      }
    })();
  }, []);

  useEffect(() => {
    if (!baseUrl) return;
    void refreshAll(baseUrl);
    const timer = window.setInterval(() => {
      void refreshAll(baseUrl);
    }, 5000);
    return () => window.clearInterval(timer);
  }, [baseUrl]);

  useEffect(() => {
    if (!baseUrl || !selectedTicker) return;
    void loadSymbolDetail(baseUrl, selectedTicker);
  }, [baseUrl, selectedTicker]);

  const pricePoints = useMemo(
    () => (symbolDetail?.series ?? []).map((row) => {
      const record = asRecord(row);
      return { date: String(record.date ?? ""), value: numberFrom(record.close, 0) };
    }),
    [symbolDetail],
  );
  const emaPoints = useMemo(
    () => (symbolDetail?.series ?? []).map((row) => {
      const record = asRecord(row);
      return { date: String(record.date ?? ""), value: numberFrom(record.ema_fast, 0) };
    }),
    [symbolDetail],
  );
  const rsiPoints = useMemo(
    () => (symbolDetail?.series ?? []).map((row) => {
      const record = asRecord(row);
      return { date: String(record.date ?? ""), value: numberFrom(record.rsi, 0) };
    }),
    [symbolDetail],
  );

  const pendingOrders = orders.filter((row) => row.status === "pending");
  const riskEvents = risk?.events ?? [];
  const recentScanEvents = scanHistory?.items ?? [];
  const selectedSignal = scan?.items.find((row) => row.ticker === selectedTicker) ?? null;
  const selectedPosition =
    positions.find((row) => String(row.ticker ?? "").toUpperCase() === selectedTicker.toUpperCase()) ?? null;

  async function handleRunCycle() {
    if (!baseUrl) return;
    try {
      const result = await runTradingCycle(baseUrl, { auto_execute: form.autoOrder });
      setActionMessage(`Cycle ${result.status}: ${result.cycle_id}`);
      await refreshAll(baseUrl);
    } catch (error) {
      setErrorMessage(toErrorMessage(error));
    }
  }

  async function handleSaveSettings() {
    if (!baseUrl || !settings) return;
    try {
      await updateTradingSettings(baseUrl, {
        execution: { ...asRecord(settings.execution), auto_order: form.autoOrder, manual_approval: form.manualApproval, signal_generation: form.signalGeneration },
        scan: { ...asRecord(settings.scan), lookback_days: form.lookbackDays },
        account: { ...asRecord(settings.account), max_concurrent_positions: form.maxConcurrentPositions, position_size_value: form.positionSizeValue, max_daily_new_entries: form.maxDailyNewEntries },
        risk: { ...asRecord(settings.risk), stop_loss_pct: form.stopLossPct, take_profit_pct: form.takeProfitPct, trailing_stop_enabled: form.trailingStopEnabled },
      });
      setActionMessage("Trading settings saved.");
      await refreshAll(baseUrl);
    } catch (error) {
      setErrorMessage(toErrorMessage(error));
    }
  }

  async function handleToggleAlgorithm(row: TradingAlgorithmRecordPayload) {
    if (!baseUrl) return;
    try {
      const payload = await toggleTradingAlgorithm(baseUrl, {
        name: row.name,
        version: row.version,
        active: !row.active,
        status: row.active ? "paused" : "active",
        sandbox_mode: row.sandbox_mode,
        signal_only: row.signal_only,
      });
      setAlgorithms(payload.items);
    } catch (error) {
      setErrorMessage(toErrorMessage(error));
    }
  }

  async function handleValidateAlgorithm(row: TradingAlgorithmRecordPayload) {
    if (!baseUrl) return;
    try {
      const payload = await validateTradingAlgorithm(baseUrl, { name: row.name, version: row.version });
      setActionMessage(`${row.name} validation: ${payload.status}`);
      await refreshAll(baseUrl);
    } catch (error) {
      setErrorMessage(toErrorMessage(error));
    }
  }

  async function handleApproveOrder(orderId: string) {
    if (!baseUrl) return;
    try {
      await approveTradingOrder(baseUrl, orderId);
      await refreshAll(baseUrl);
    } catch (error) {
      setErrorMessage(toErrorMessage(error));
    }
  }

  async function handleCancelOrder(orderId: string) {
    if (!baseUrl) return;
    try {
      await cancelTradingOrder(baseUrl, orderId);
      await refreshAll(baseUrl);
    } catch (error) {
      setErrorMessage(toErrorMessage(error));
    }
  }

  async function handleClosePosition(ticker: string) {
    if (!baseUrl) return;
    try {
      await closeTradingPosition(baseUrl, ticker);
      await refreshAll(baseUrl);
    } catch (error) {
      setErrorMessage(toErrorMessage(error));
    }
  }

  async function handleUpdateExecutionMode(mode: string) {
    if (!baseUrl) return;
    try {
      const payload = await updateTradingExecutionMode(baseUrl, mode as "paper" | "shadow_live" | "live_adapter");
      setExecutionMode(payload.mode);
      setExecutionModePayload(payload);
      setActionMessage(`Trading execution mode updated to ${payload.mode}.`);
    } catch (error) {
      setErrorMessage(toErrorMessage(error));
    }
  }

  return (
    <div className="h-full min-h-0 overflow-auto py-4">
      <div className="mb-4 flex items-center justify-between gap-4">
        <div>
          <h1 className="body-lg-medium text-theme-primary">Trading</h1>
          <p className="body-sm-regular text-theme-muted">
            Paper-trading operations console for built-in strategies and custom algorithm runtime.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <select
            className="rounded-sm border border-theme-outline bg-theme-secondary px-2 py-2 body-xs-regular text-theme-primary"
            value={executionMode}
            onChange={(event) => {
              const nextMode = event.target.value;
              setExecutionMode(nextMode);
              void handleUpdateExecutionMode(nextMode);
            }}
            disabled={isLoading || !baseUrl}
          >
            <option value="paper">paper</option>
            <option value="shadow_live">shadow_live</option>
            <option value="live_adapter">live_adapter</option>
          </select>
          {lastRefreshed ? <p className="body-xxs-regular text-theme-muted">Last refresh: {lastRefreshed}</p> : null}
          <button
            type="button"
            className="button-neutral rounded-sm px-3 py-2 body-xs-medium"
            onClick={() => void handleRunCycle()}
            disabled={isLoading || Boolean(activationMessage)}
          >
            {isLoading ? "Running..." : "Run Scan Cycle"}
          </button>
          <button
            type="button"
            className="button-secondary rounded-sm px-3 py-2 body-xs-medium"
            onClick={() => void refreshAll(baseUrl)}
            disabled={isLoading || !baseUrl}
          >
            Refresh
          </button>
        </div>
      </div>

      {errorMessage ? (
        <div className="mb-2 rounded-sm border border-red-500/60 bg-red-500/10 p-2">
          <p className="body-xs-medium text-red-400">{errorMessage}</p>
        </div>
      ) : null}
      {activationMessage ? (
        <div className="mb-2 rounded-sm border border-amber-500/60 bg-amber-500/10 p-2">
          <p className="body-xs-medium text-amber-300">{activationMessage}</p>
        </div>
      ) : null}
      {actionMessage ? (
        <div className="mb-2 rounded-sm border border-emerald-500/60 bg-emerald-500/10 p-2">
          <p className="body-xs-medium text-emerald-300">{actionMessage}</p>
        </div>
      ) : null}

      <div className="mb-4 grid grid-cols-2 gap-3 xl:grid-cols-6">
        <SummaryCard label="Mode" value={executionMode} />
        <SummaryCard
          label="Runtime"
          value={status?.runtime_status ?? "stopped"}
          status={status?.runtime_status === "running" ? "ok" : status?.runtime_status === "paused" ? "warning" : "critical"}
        />
        <SummaryCard label="Last Scan" value={formatDateTime(status?.last_scan_at)} />
        <SummaryCard label="Last Order" value={formatDateTime(status?.last_order_at)} />
        <SummaryCard label="Signals Today" value={status?.today_signal_count ?? 0} />
        <SummaryCard label="Orders Today" value={status?.today_order_count ?? 0} />
        <SummaryCard label="Open Positions" value={status?.open_position_count ?? 0} />
        <SummaryCard label="Available Cash" value={formatMoney(status?.available_cash)} />
        <SummaryCard label="Used Capital" value={formatMoney(status?.used_capital)} />
        <SummaryCard label="Today Realized" value={formatMoney(status?.today_realized_pnl)} status={(status?.today_realized_pnl ?? 0) >= 0 ? "ok" : "warning"} />
        <SummaryCard label="Cumulative PnL" value={formatMoney(status?.cumulative_pnl)} status={(status?.cumulative_pnl ?? 0) >= 0 ? "ok" : "warning"} />
        <SummaryCard label="Drawdown" value={formatPct(status?.intraday_drawdown)} status={(status?.intraday_drawdown ?? 0) > -0.05 ? "ok" : "warning"} />
      </div>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-[320px_minmax(0,1fr)_380px]">
        <div className="space-y-4">
          <PanelCard title="Strategy Settings" description="Trading runtime controls.">
            <div className="space-y-2">
              <label className="body-xs-medium text-theme-muted">
                Lookback Days
                <input type="number" className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary px-2 py-2 body-xs-regular text-theme-primary" value={form.lookbackDays} onChange={(event) => setForm((prev) => ({ ...prev, lookbackDays: Number(event.target.value) }))} />
              </label>
              <label className="flex items-center justify-between rounded-sm bg-theme-secondary px-2 py-2">
                <span className="body-xs-regular text-theme-primary">Signal Generation</span>
                <input type="checkbox" checked={form.signalGeneration} onChange={(event) => setForm((prev) => ({ ...prev, signalGeneration: event.target.checked }))} />
              </label>
              <label className="flex items-center justify-between rounded-sm bg-theme-secondary px-2 py-2">
                <span className="body-xs-regular text-theme-primary">Auto Order</span>
                <input type="checkbox" checked={form.autoOrder} onChange={(event) => setForm((prev) => ({ ...prev, autoOrder: event.target.checked }))} />
              </label>
              <label className="flex items-center justify-between rounded-sm bg-theme-secondary px-2 py-2">
                <span className="body-xs-regular text-theme-primary">Manual Approval</span>
                <input type="checkbox" checked={form.manualApproval} onChange={(event) => setForm((prev) => ({ ...prev, manualApproval: event.target.checked }))} />
              </label>
              <label className="body-xs-medium text-theme-muted">
                Max Concurrent Positions
                <input type="number" className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary px-2 py-2 body-xs-regular text-theme-primary" value={form.maxConcurrentPositions} onChange={(event) => setForm((prev) => ({ ...prev, maxConcurrentPositions: Number(event.target.value) }))} />
              </label>
              <label className="body-xs-medium text-theme-muted">
                Position Size
                <input type="number" step="0.01" className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary px-2 py-2 body-xs-regular text-theme-primary" value={form.positionSizeValue} onChange={(event) => setForm((prev) => ({ ...prev, positionSizeValue: Number(event.target.value) }))} />
              </label>
              <label className="body-xs-medium text-theme-muted">
                Max Daily Entries
                <input type="number" className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary px-2 py-2 body-xs-regular text-theme-primary" value={form.maxDailyNewEntries} onChange={(event) => setForm((prev) => ({ ...prev, maxDailyNewEntries: Number(event.target.value) }))} />
              </label>
              <label className="body-xs-medium text-theme-muted">
                Stop Loss
                <input type="number" step="0.01" className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary px-2 py-2 body-xs-regular text-theme-primary" value={form.stopLossPct} onChange={(event) => setForm((prev) => ({ ...prev, stopLossPct: Number(event.target.value) }))} />
              </label>
              <label className="body-xs-medium text-theme-muted">
                Take Profit
                <input type="number" step="0.01" className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary px-2 py-2 body-xs-regular text-theme-primary" value={form.takeProfitPct} onChange={(event) => setForm((prev) => ({ ...prev, takeProfitPct: Number(event.target.value) }))} />
              </label>
              <label className="flex items-center justify-between rounded-sm bg-theme-secondary px-2 py-2">
                <span className="body-xs-regular text-theme-primary">Trailing Stop</span>
                <input type="checkbox" checked={form.trailingStopEnabled} onChange={(event) => setForm((prev) => ({ ...prev, trailingStopEnabled: event.target.checked }))} />
              </label>
            </div>
            <button type="button" className="mt-3 button-secondary rounded-sm px-3 py-2 body-xs-medium" onClick={() => void handleSaveSettings()} disabled={!baseUrl}>
              Save Settings
            </button>
          </PanelCard>

          <PanelCard title="Custom Algorithms" description="Registry, sandbox state, and validation.">
            <div className="space-y-2">
              {algorithms.map((row) => (
                <div key={`${row.name}-${row.version}`} className="rounded-sm bg-theme-secondary p-2">
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <p className="body-xs-medium text-theme-primary">{row.name}</p>
                      <p className="body-xxs-regular text-theme-muted">{row.version} | {row.status}</p>
                    </div>
                    <button type="button" className="rounded-sm border border-theme-outline px-2 py-1 body-xxs-medium text-theme-primary" onClick={() => void handleToggleAlgorithm(row)}>
                      {row.active ? "Pause" : "Activate"}
                    </button>
                  </div>
                  <div className="mt-2 flex gap-2">
                    <button type="button" className="rounded-sm border border-theme-outline px-2 py-1 body-xxs-medium text-theme-primary" onClick={() => void handleValidateAlgorithm(row)}>
                      Validate
                    </button>
                    <span className={`rounded-sm px-2 py-1 body-xxs-medium ${row.sandbox_mode ? "bg-amber-500/15 text-amber-300" : "bg-theme-primary text-theme-muted"}`}>{row.sandbox_mode ? "sandbox" : "runtime"}</span>
                    <span className={`rounded-sm px-2 py-1 body-xxs-medium ${row.signal_only ? "bg-slate-500/20 text-theme-muted" : "bg-emerald-500/15 text-emerald-300"}`}>{row.signal_only ? "signal-only" : "order-enabled"}</span>
                  </div>
                </div>
              ))}
            </div>
          </PanelCard>
        </div>

        <div className="space-y-4">
          <PanelCard title="Scan Results" description="Shared universe scan output for built-in and custom strategies.">
            <div className="max-h-80 overflow-auto">
              <table className="w-full text-left">
                <thead className="sticky top-0 bg-theme-primary">
                  <tr className="body-xxs-medium text-theme-muted">
                    <th className="pb-2">Ticker</th>
                    <th className="pb-2">Signal</th>
                    <th className="pb-2">Strategy</th>
                    <th className="pb-2">Strength</th>
                    <th className="pb-2">RSI</th>
                    <th className="pb-2">Action</th>
                    <th className="pb-2">Risk</th>
                  </tr>
                </thead>
                <tbody>
                  {(scan?.items ?? []).map((row) => (
                    <tr key={row.signal_id ?? `${row.ticker}-${row.timestamp}`} className={`cursor-pointer border-t border-theme-outline body-xs-regular ${selectedTicker === row.ticker ? "bg-theme-secondary" : ""}`} onClick={() => setSelectedTicker(row.ticker)}>
                      <td className="py-2 pr-2 text-theme-primary">{row.ticker}</td>
                      <td className="py-2 pr-2 text-theme-primary">{row.signal_type}</td>
                      <td className="py-2 pr-2 text-theme-primary">{row.strategy_name}</td>
                      <td className="py-2 pr-2 text-theme-primary">{formatNum(row.signal_strength)}</td>
                      <td className="py-2 pr-2 text-theme-primary">{formatNum(row.rsi)}</td>
                      <td className="py-2 pr-2"><span className={`rounded-sm px-2 py-0.5 body-xxs-medium ${badgeClass(row.recommended_action)}`}>{row.recommended_action}</span></td>
                      <td className="py-2 pr-2"><span className={`rounded-sm px-2 py-0.5 body-xxs-medium ${badgeClass(row.risk_check_status)}`}>{row.risk_check_status}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </PanelCard>

          <PanelCard title={`Order Queue (${orders.length})`} description="Signal, risk, order intent, and paper execution state.">
            <div className="mb-2 flex items-center justify-between">
              <p className="body-xxs-regular text-theme-muted">Pending approvals: {pendingOrders.length} | Fills: {fillsCount}</p>
              <span className={`rounded-sm px-2 py-1 body-xxs-medium ${badgeClass(executionMode)}`}>{executionMode}</span>
            </div>
            <div className="max-h-72 overflow-auto">
              <table className="w-full text-left">
                <thead className="sticky top-0 bg-theme-primary">
                  <tr className="body-xxs-medium text-theme-muted">
                    <th className="pb-2">Ticker</th>
                    <th className="pb-2">Side</th>
                    <th className="pb-2">Qty</th>
                    <th className="pb-2">Price</th>
                    <th className="pb-2">Status</th>
                    <th className="pb-2">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {orders.slice().reverse().slice(0, 30).map((row) => (
                    <tr key={row.order_id} className="border-t border-theme-outline body-xs-regular">
                      <td className="py-2 pr-2 text-theme-primary">{row.ticker}</td>
                      <td className="py-2 pr-2 text-theme-primary">{row.side}</td>
                      <td className="py-2 pr-2 text-theme-primary">{formatNum(row.quantity, 0)}</td>
                      <td className="py-2 pr-2 text-theme-primary">{formatMoney(row.requested_price)}</td>
                      <td className="py-2 pr-2"><span className={`rounded-sm px-2 py-0.5 body-xxs-medium ${badgeClass(row.status)}`}>{row.status}</span></td>
                      <td className="py-2 pr-2">
                        <div className="flex gap-1">
                          {row.status === "pending" ? (
                            <button type="button" className="rounded-sm border border-emerald-500/40 px-2 py-1 body-xxs-medium text-emerald-300" onClick={() => void handleApproveOrder(row.order_id)}>
                              Approve
                            </button>
                          ) : null}
                          {row.status === "pending" || row.status === "submitted" ? (
                            <button type="button" className="rounded-sm border border-red-500/40 px-2 py-1 body-xxs-medium text-red-300" onClick={() => void handleCancelOrder(row.order_id)}>
                              Cancel
                            </button>
                          ) : null}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </PanelCard>

          <PanelCard title={`Open Positions (${positions.length})`} description="Current paper positions and manual exits.">
            <div className="max-h-72 overflow-auto">
              <table className="w-full text-left">
                <thead className="sticky top-0 bg-theme-primary">
                  <tr className="body-xxs-medium text-theme-muted">
                    <th className="pb-2">Ticker</th>
                    <th className="pb-2">Entry</th>
                    <th className="pb-2">Current</th>
                    <th className="pb-2">PnL</th>
                    <th className="pb-2">Hold</th>
                    <th className="pb-2">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {positions.map((row) => (
                    <tr key={`${String(row.ticker ?? "")}-${String(row.entry_time ?? "")}`} className={`cursor-pointer border-t border-theme-outline body-xs-regular ${selectedTicker === String(row.ticker ?? "") ? "bg-theme-secondary" : ""}`} onClick={() => setSelectedTicker(String(row.ticker ?? ""))}>
                      <td className="py-2 pr-2 text-theme-primary">{String(row.ticker ?? "-")}</td>
                      <td className="py-2 pr-2 text-theme-primary">{formatMoney(numberFrom(row.entry_price, 0))}</td>
                      <td className="py-2 pr-2 text-theme-primary">{formatMoney(numberFrom(row.current_price, 0))}</td>
                      <td className={`py-2 pr-2 ${numberFrom(row.unrealized_pnl, 0) >= 0 ? "text-emerald-300" : "text-red-300"}`}>{formatMoney(numberFrom(row.unrealized_pnl, 0))}</td>
                      <td className="py-2 pr-2 text-theme-primary">{String(row.holding_period_days ?? 0)}d</td>
                      <td className="py-2 pr-2">
                        <button type="button" className="rounded-sm border border-red-500/40 px-2 py-1 body-xxs-medium text-red-300" onClick={(event) => { event.stopPropagation(); void handleClosePosition(String(row.ticker ?? "")); }}>
                          Force Close
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </PanelCard>

          <PanelCard title="Performance" description="Paper-trading runtime metrics and equity trace.">
            <div className="mb-3 grid grid-cols-2 gap-2 lg:grid-cols-4">
              <SummaryCard label="Cumulative Return" value={formatPct(performance?.cumulative_return)} />
              <SummaryCard label="Win Rate" value={formatPct(performance?.win_rate)} />
              <SummaryCard label="Sharpe" value={formatNum(performance?.sharpe)} />
              <SummaryCard label="Max Drawdown" value={formatPct(performance?.max_drawdown)} />
            </div>
            <div className="grid grid-cols-1 gap-3 lg:grid-cols-3">
              <div className="rounded-sm bg-theme-secondary p-2">
                <p className="mb-2 body-xs-medium text-theme-primary">Equity Curve</p>
                <DashboardLineChart points={performance?.equity_curve ?? []} height={150} formatValue={(value) => formatNum(value, 0)} primaryLabel="Equity" />
              </div>
              <div className="rounded-sm bg-theme-secondary p-2">
                <p className="mb-2 body-xs-medium text-theme-primary">Drawdown Curve</p>
                <DashboardLineChart points={performance?.drawdown_curve ?? []} height={150} formatValue={(value) => formatPct(value)} primaryLabel="Drawdown" color="#f59e0b" />
              </div>
              <div className="rounded-sm bg-theme-secondary p-2">
                <p className="mb-2 body-xs-medium text-theme-primary">Daily PnL</p>
                <DashboardLineChart points={performance?.daily_pnl ?? []} height={150} formatValue={(value) => formatNum(value, 0)} primaryLabel="Daily PnL" color="#22c55e" />
              </div>
            </div>
          </PanelCard>
        </div>

        <div className="space-y-4">
          <PanelCard title={selectedTicker ? `${selectedTicker} Detail` : "Symbol Detail"} description="Selected symbol context, chart, and explanation.">
            {selectedTicker ? (
              <div className="space-y-3">
                <div className="grid grid-cols-2 gap-2">
                  <SummaryCard label="Current Price" value={formatMoney(selectedSignal?.current_price ?? numberFrom(selectedPosition?.current_price, 0))} />
                  <SummaryCard label="Position Held" value={selectedSignal?.position_held || Boolean(selectedPosition) ? "Yes" : "No"} />
                  <SummaryCard label="RSI" value={formatNum(selectedSignal?.rsi)} />
                  <SummaryCard label="Volume Change" value={formatPct(selectedSignal?.volume_change_pct)} />
                </div>
                <div className="rounded-sm bg-theme-secondary p-2">
                  <p className="mb-2 body-xs-medium text-theme-primary">Price / EMA</p>
                  <DashboardLineChart points={pricePoints} secondaryPoints={emaPoints} height={165} primaryLabel="Close" secondaryLabel="EMA Fast" formatValue={(value) => formatNum(value, 2)} />
                </div>
                <div className="rounded-sm bg-theme-secondary p-2">
                  <p className="mb-2 body-xs-medium text-theme-primary">RSI</p>
                  <DashboardLineChart points={rsiPoints} height={120} primaryLabel="RSI" color="#a78bfa" formatValue={(value) => formatNum(value, 1)} />
                </div>
                <div className="rounded-sm bg-theme-secondary p-3">
                  <p className="body-xs-medium text-theme-primary">Signal Interpretation</p>
                  <p className="mt-2 body-xs-regular text-theme-muted">{symbolDetail?.explanation || selectedSignal?.reason || "No human-readable explanation is available for the latest signal."}</p>
                </div>
              </div>
            ) : (
              <p className="body-xs-regular text-theme-muted">Select a scan row or an open position to load symbol detail.</p>
            )}
          </PanelCard>

          <PanelCard title="Risk Control" description="Current limits and recent risk events.">
            <div className="mb-3 grid grid-cols-2 gap-2">
              <SummaryCard label="Max Position Weight" value={formatPct(numberFrom(asRecord(risk?.limits).max_position_weight, 0))} />
              <SummaryCard label="Daily Loss Limit" value={formatMoney(numberFrom(asRecord(risk?.limits).daily_loss_limit, 0))} />
              <SummaryCard label="Max Positions" value={numberFrom(asRecord(risk?.limits).max_concurrent_positions, 0)} />
              <SummaryCard label="Stop Loss" value={formatPct(numberFrom(asRecord(risk?.limits).stop_loss_pct, 0))} />
              <SummaryCard label="Broker Ready" value={String(executionModePayload?.broker_ready ?? false)} />
              <SummaryCard label="Kill Switch" value={String(executionModePayload?.kill_switch ?? false)} />
            </div>
            <div className="space-y-2">
              {riskEvents.slice().reverse().slice(0, 8).map((row, index) => (
                <div key={`${String(row.created_at ?? row.timestamp ?? index)}`} className="rounded-sm bg-theme-secondary p-2">
                  <div className="flex items-center justify-between gap-2">
                    <span className="body-xs-medium text-theme-primary">{String(row.reason_code ?? row.event_type ?? "risk_event")}</span>
                    <span className={`rounded-sm px-2 py-0.5 body-xxs-medium ${badgeClass(String(row.status ?? row.severity ?? "warning"))}`}>{String(row.status ?? row.severity ?? "warning")}</span>
                  </div>
                  <p className="mt-1 body-xxs-regular text-theme-muted">{String(row.message ?? row.reason ?? "Risk event captured by runtime.")}</p>
                </div>
              ))}
              {riskEvents.length === 0 ? <p className="body-xs-regular text-theme-muted">No recent risk events.</p> : null}
            </div>
          </PanelCard>

          <PanelCard title="Scan History" description="Recent normalized scan activity for runtime comparison.">
            <div className="max-h-72 space-y-2 overflow-auto">
              {recentScanEvents.slice(0, 12).map((row) => (
                <div key={row.signal_id ?? `${row.ticker}-${row.timestamp}`} className="rounded-sm bg-theme-secondary p-2">
                  <div className="flex items-center justify-between gap-2">
                    <p className="body-xs-medium text-theme-primary">{row.ticker} | {row.strategy_name}</p>
                    <span className={`rounded-sm px-2 py-0.5 body-xxs-medium ${badgeClass(row.risk_check_status)}`}>{row.risk_check_status}</span>
                  </div>
                  <p className="mt-1 body-xxs-regular text-theme-muted">
                    {formatDateTime(row.timestamp)} | {row.signal_type} | confidence {formatNum(row.confidence ?? row.signal_strength)}
                  </p>
                </div>
              ))}
              {recentScanEvents.length === 0 ? <p className="body-xs-regular text-theme-muted">No historical scans available.</p> : null}
            </div>
          </PanelCard>

          <PanelCard title="Audit Log" description="Signal, order, risk, and system events.">
            <div className="max-h-80 space-y-2 overflow-auto">
              {events.slice().reverse().slice(0, 25).map((row, index) => (
                <div key={`${String(row.timestamp ?? row.created_at ?? index)}`} className="rounded-sm bg-theme-secondary p-2">
                  <div className="flex items-center justify-between gap-2">
                    <div>
                      <p className="body-xs-medium text-theme-primary">
                        {String(row.event_type ?? "event")}
                        {row.ticker ? ` | ${String(row.ticker)}` : ""}
                        {row.strategy ? ` | ${String(row.strategy)}` : ""}
                      </p>
                      <p className="body-xxs-regular text-theme-muted">{formatDateTime(String(row.timestamp ?? row.created_at ?? ""))}</p>
                    </div>
                    <span className={`rounded-sm px-2 py-0.5 body-xxs-medium ${badgeClass(String(row.status ?? "info"))}`}>{String(row.status ?? "info")}</span>
                  </div>
                  <p className="mt-1 body-xxs-regular text-theme-muted">{String(row.message ?? "Runtime event")}</p>
                </div>
              ))}
              {events.length === 0 ? <p className="body-xs-regular text-theme-muted">No runtime events logged yet.</p> : null}
            </div>
          </PanelCard>
        </div>
      </div>
    </div>
  );
}

export const Route = createFileRoute("/trading")({
  component: TradingPage,
});
