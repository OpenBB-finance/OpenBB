import { createFileRoute } from "@tanstack/react-router";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { PanelCard } from "../components/quant/PanelCard";
import { ScoreGauge } from "../components/macro/ScoreGauge";
import { DashboardHistogramChart } from "../components/quant/DashboardHistogramChart";
import { DashboardLineChart } from "../components/quant/DashboardLineChart";
import { RegimeMonitorTab } from "../components/quant/RegimeMonitorTab";
import type { DashboardTabId } from "../components/quant/DashboardTabs";
import { MetricTooltip } from "../components/quant/MetricTooltip";
import { SummaryCard } from "../components/quant/SummaryCard";
import { WorkflowSteps } from "../components/quant/WorkflowSteps";
import { fetchMacroRegime, fetchMacroRegimeState, probeMacroActivation } from "../lib/macroApi";
import type { MacroRegimePoint, MacroRegimeStateResponse } from "../types/macro";
import {
  createSignals,
  fetchAlertsCurrent,
  fetchAlertsHistory,
  fetchArtifactSummary,
  fetchDashboardBootstrap,
  fetchDashboardHealth,
  fetchFeatureImportance,
  fetchModelIcDecay,
  fetchModelPerformance,
  fetchPortfolioPolicy,
  fetchPerformanceRegime,
  fetchPerformanceRolling,
  fetchPortfolioExposure,
  fetchPortfolioRisk,
  fetchPredictionDistribution,
  fetchPredictionsLatest,
  fetchRegimeCurrent,
  fetchRegimeHistory,
  fetchRunLatestConstraints,
  fetchRunLatestExposures,
  fetchRunLatestMeta,
  fetchRunLatestRisk,
  fetchRunSnapshot,
  invalidateQuantCaches,
  runBacktest,
} from "../lib/quantApi";
import { formatBackendDetail, resolveOpenBBBackend } from "../lib/openbbBackend";
import { useQuantSession } from "../contexts/QuantSessionContext";
import type {
  AlertsPayload,
  ArtifactSummaryPayload,
  DashboardHealthPayload,
  DashboardMode,
  FeatureImportancePayload,
  ICDecayPayload,
  ModelName,
  ModelPerformancePayload,
  PortfolioPolicyPayload,
  PerformanceRegimePayload,
  PortfolioExposurePayload,
  PortfolioRiskPayload,
  PredictionDistributionPayload,
  PredictionsLatestPayload,
  RegimeCurrentPayload,
  RegimeHistoryPayload,
  RunLatestConstraintsPayload,
  RunLatestExposuresPayload,
  RunLatestMetaPayload,
  RunLatestRiskPayload,
  RunSnapshotPayload,
  RollingPerformancePayload,
} from "../types/quant";

type DashboardModelTab = ModelName | "transformer" | "ensemble";

const MODEL_TABS: Array<{ id: DashboardModelTab; label: string; implemented: boolean }> = [
  { id: "lgbm_ranker", label: "Ranker", implemented: true },
  { id: "xgb_lstm", label: "XGB+LSTM", implemented: true },
  { id: "catboost_ranker", label: "CatBoost Ranker", implemented: true },
  { id: "transformer", label: "Transformer", implemented: false },
  { id: "ensemble", label: "Ensemble", implemented: false },
];

const POLL_MS = 20_000;
const DEFAULT_TOP_K = 20;
const DEFAULT_SCORE_THRESHOLD = 0.5;
const DEFAULT_PORTFOLIO_POLICY: PortfolioPolicyPayload = {
  template: "diversified_long_only",
  single_name_max_abs_weight: 0.06,
  small_universe_policy: "cash_buffer",
  sector_concentration_max: 0.35,
  turnover_max: 1.0,
  gross_exposure_max: 1.0,
  net_exposure_abs_max: 1.0,
  cash_symbol: "CASH",
  cash_category: "cash_proxy",
};

interface SummaryDateRangeMeta {
  start?: string;
  end?: string;
}

interface SummaryWalkForwardMeta {
  train_months?: number;
  val_months?: number;
}

interface SummaryRequestMeta {
  date_range?: SummaryDateRangeMeta;
  walk_forward_config?: SummaryWalkForwardMeta;
}

function extractSummaryRequestMeta(input: unknown): SummaryRequestMeta | undefined {
  if (!input || typeof input !== "object") {
    return undefined;
  }
  const root = input as { request?: unknown };
  if (!root.request || typeof root.request !== "object") {
    return undefined;
  }
  const request = root.request as { date_range?: unknown; walk_forward_config?: unknown };
  const date_range =
    request.date_range && typeof request.date_range === "object"
      ? (request.date_range as SummaryDateRangeMeta)
      : undefined;
  const walk_forward_config =
    request.walk_forward_config && typeof request.walk_forward_config === "object"
      ? (request.walk_forward_config as SummaryWalkForwardMeta)
      : undefined;
  return {
    date_range,
    walk_forward_config,
  };
}

function toNumber(value: unknown): number {
  if (typeof value !== "number" || Number.isNaN(value)) {
    return 0;
  }
  return value;
}

function formatNumber(value: number | null | undefined, digits = 3): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "-";
  }
  return value.toFixed(digits);
}

function formatPct(value: number | null | undefined, digits = 2): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "-";
  }
  return `${(value * 100).toFixed(digits)}%`;
}

function SeverityBadge({ severity }: { severity: "info" | "warning" | "critical" }) {
  const className =
    severity === "critical"
      ? "border-red-500/60 bg-red-500/20 text-red-300"
      : severity === "warning"
        ? "border-amber-500/60 bg-amber-500/20 text-amber-300"
        : "border-sky-500/60 bg-sky-500/20 text-sky-300";
  return <span className={`rounded-sm border px-2 py-[2px] body-xxs-medium ${className}`}>{severity.toUpperCase()}</span>;
}

function zColor(z: number): string {
  if (z >= 1.2) return "rgb(16 185 129 / 0.85)";
  if (z >= 0.4) return "rgb(34 197 94 / 0.7)";
  if (z <= -1.2) return "rgb(239 68 68 / 0.85)";
  if (z <= -0.4) return "rgb(248 113 113 / 0.7)";
  return "rgb(71 85 105 / 0.6)";
}

export default function DashboardPage() {
  const { session, setRunId, setModelName, setMode: setSessionMode, syncFromHealth, patchSession, markArtifactReady } =
    useQuantSession();
  const [backend, setBackend] = useState<Awaited<ReturnType<typeof resolveOpenBBBackend>> | null>(null);
  const [isLoadingBackend, setIsLoadingBackend] = useState(false);
  const [isLoadingData, setIsLoadingData] = useState(false);

  const [runIdInput, setRunIdInput] = useState<string>(() => session.run_id);
  const [mode, setMode] = useState<DashboardMode>(() => session.mode);
  const [modelTab, setModelTab] = useState<DashboardModelTab>(() => session.model_name);
  const [tradingViewTab, setTradingViewTab] = useState<"market" | "etf" | "global">("market");
  const [showHeaderDetails, setShowHeaderDetails] = useState(false);
  const [activeTab, setActiveTab] = useState<DashboardTabId>("summary");
  const [isSubmittingSignals, setIsSubmittingSignals] = useState(false);
  const [isSubmittingBacktest, setIsSubmittingBacktest] = useState(false);

  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [warningMessage, setWarningMessage] = useState<string | null>(null);

  const [health, setHealth] = useState<DashboardHealthPayload | null>(null);
  const [summary, setSummary] = useState<ArtifactSummaryPayload | null>(null);
  const [performance, setPerformance] = useState<ModelPerformancePayload | null>(null);
  const [rolling, setRolling] = useState<RollingPerformancePayload | null>(null);
  const [regimePerf, setRegimePerf] = useState<PerformanceRegimePayload | null>(null);
  const [regimeCurrent, setRegimeCurrent] = useState<RegimeCurrentPayload | null>(null);
  const [regimeHistory, setRegimeHistory] = useState<RegimeHistoryPayload | null>(null);
  const [portfolioExposure, setPortfolioExposure] = useState<PortfolioExposurePayload | null>(null);
  const [portfolioRisk, setPortfolioRisk] = useState<PortfolioRiskPayload | null>(null);
  const [featureImportance, setFeatureImportance] = useState<FeatureImportancePayload | null>(null);
  const [predictionDistribution, setPredictionDistribution] = useState<PredictionDistributionPayload | null>(null);
  const [icDecay, setIcDecay] = useState<ICDecayPayload | null>(null);
  const [predictionsLatest, setPredictionsLatest] = useState<PredictionsLatestPayload | null>(null);
  const [alertsCurrent, setAlertsCurrent] = useState<AlertsPayload | null>(null);
  const [alertsHistory, setAlertsHistory] = useState<AlertsPayload | null>(null);
  const [runLatestMeta, setRunLatestMeta] = useState<RunLatestMetaPayload | null>(null);
  const [runLatestRisk, setRunLatestRisk] = useState<RunLatestRiskPayload | null>(null);
  const [runLatestExposures, setRunLatestExposures] = useState<RunLatestExposuresPayload | null>(null);
  const [runLatestConstraints, setRunLatestConstraints] = useState<RunLatestConstraintsPayload | null>(null);
  const [runSnapshot, setRunSnapshot] = useState<RunSnapshotPayload | null>(null);
  const [portfolioPolicy, setPortfolioPolicy] = useState<PortfolioPolicyPayload>(DEFAULT_PORTFOLIO_POLICY);

  const [macroRegime, setMacroRegime] = useState<MacroRegimePoint | null>(null);
  const [macroRegimeState, setMacroRegimeState] = useState<MacroRegimeStateResponse | null>(null);
  const [macroAvailable, setMacroAvailable] = useState(false);

  const abortRef = useRef<AbortController | null>(null);
  const tabAbortRef = useRef<AbortController | null>(null);
  const loadedTabCacheRef = useRef<Record<string, boolean>>({});
  const dataScopeRef = useRef<string>("");
  const [isVisible, setIsVisible] = useState<boolean>(document.visibilityState === "visible");
  const healthRef = useRef<HTMLDivElement | null>(null);
  const regimeRef = useRef<HTMLDivElement | null>(null);
  const portfolioRef = useRef<HTMLDivElement | null>(null);
  const hasScrolledFocusRef = useRef(false);
  const activeTabRef = useRef<DashboardTabId>("summary");

  const isImplementedModel =
    modelTab === "lgbm_ranker" || modelTab === "xgb_lstm" || modelTab === "catboost_ranker";
  const effectiveModel: ModelName = isImplementedModel ? modelTab : "lgbm_ranker";
  const normalizedRunId = session.run_id.trim();

  useEffect(() => {
    setRunIdInput(session.run_id);
  }, [session.run_id]);

  useEffect(() => {
    setMode(session.mode);
  }, [session.mode]);

  useEffect(() => {
    setModelTab(session.model_name);
  }, [session.model_name]);

  const resolveBackend = useCallback(async () => {
    setIsLoadingBackend(true);
    try {
      const resolved = await resolveOpenBBBackend();
      setBackend(resolved);
      if (resolved.connected) {
        try {
          const fetchedPolicy = await fetchPortfolioPolicy(resolved.baseUrl);
          setPortfolioPolicy(fetchedPolicy);
        } catch {
          setPortfolioPolicy(DEFAULT_PORTFOLIO_POLICY);
        }
      }
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to resolve backend.");
    } finally {
      setIsLoadingBackend(false);
    }
  }, []);

  useEffect(() => {
    void resolveBackend();
  }, [resolveBackend]);

  useEffect(() => {
    if (!backend?.connected) return;
    void (async () => {
      try {
        const activation = await probeMacroActivation(backend.baseUrl);
        setMacroAvailable(activation.available);
        if (!activation.available) return;
        const today = new Date().toISOString().slice(0, 10);
        const twoYearsAgo = (() => { const d = new Date(); d.setFullYear(d.getFullYear() - 2); return d.toISOString().slice(0, 10); })();
        const [regime, state] = await Promise.allSettled([
          fetchMacroRegime(backend.baseUrl, { start: twoYearsAgo, end: today, freq: "W", fill: "ffill" }),
          fetchMacroRegimeState(backend.baseUrl, today),
        ]);
        if (regime.status === "fulfilled") {
          const pts = Array.isArray(regime.value.data) ? regime.value.data : [];
          setMacroRegime(regime.value.latest || (pts.length > 0 ? pts[pts.length - 1] : null));
        }
        if (state.status === "fulfilled") setMacroRegimeState(state.value);
      } catch { /* macro is optional for dashboard */ }
    })();
  }, [backend]);

  useEffect(() => {
    const onVisibilityChange = () => setIsVisible(document.visibilityState === "visible");
    document.addEventListener("visibilitychange", onVisibilityChange);
    return () => document.removeEventListener("visibilitychange", onVisibilityChange);
  }, []);

  useEffect(() => {
    const search = new URLSearchParams(window.location.search);
    const queryRunId = search.get("run_id")?.trim();
    const queryModel = search.get("model") || search.get("model_name");
    const queryMode = search.get("mode");
    const queryTab = search.get("tab");
    if (queryRunId) {
      setRunId(queryRunId);
      setRunIdInput(queryRunId);
    }
    if (queryModel === "lgbm_ranker" || queryModel === "xgb_lstm" || queryModel === "catboost_ranker") {
      setModelName(queryModel);
      setModelTab(queryModel);
    }
    if (queryMode === "backtest" || queryMode === "live") {
      setMode(queryMode);
      setSessionMode(queryMode);
    }
    if (
      queryTab === "summary" ||
      queryTab === "performance" ||
      queryTab === "risk" ||
      queryTab === "portfolio" ||
      queryTab === "model" ||
      queryTab === "regime"
    ) {
      setActiveTab(queryTab);
    }
  }, [setMode, setModelName, setRunId, setSessionMode]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const currentTab = params.get("tab");
    if (currentTab !== activeTab) {
      params.set("tab", activeTab);
      const newUrl = `${window.location.pathname}?${params.toString()}`;
      window.history.replaceState(null, "", newUrl);
    }
  }, [activeTab]);

  useEffect(() => {
    activeTabRef.current = activeTab;
  }, [activeTab]);

  const clearTabPayloads = useCallback(() => {
    setRolling(null);
    setRegimePerf(null);
    setRegimeCurrent(null);
    setRegimeHistory(null);
    setPortfolioExposure(null);
    setPortfolioRisk(null);
    setFeatureImportance(null);
    setPredictionDistribution(null);
    setIcDecay(null);
    setPredictionsLatest(null);
    setAlertsCurrent(null);
    setAlertsHistory(null);
    setRunLatestRisk(null);
    setRunLatestExposures(null);
    setRunLatestConstraints(null);
  }, []);

  const loadTabData = useCallback(
    async (
      runToUse: string,
      tabId: DashboardTabId,
      options: { signal: AbortSignal; mode: DashboardMode; force?: boolean },
    ) => {
      if (!backend?.connected || !runToUse) {
        return;
      }
      if (tabId === "summary" || tabId === "regime") {
        return;
      }
      const cacheKey = `${runToUse}:${effectiveModel}:${options.mode}:${tabId}`;
      if (!options.force && loadedTabCacheRef.current[cacheKey]) {
        return;
      }
      const tabErrors: string[] = [];
      if (tabId === "risk") {
        const [regimeCurrentResult, alertsCurrentResult, alertsHistoryResult] =
          await Promise.allSettled([
            fetchRegimeCurrent(backend.baseUrl, runToUse, effectiveModel, {
              mode: options.mode,
              signal: options.signal,
            }),
            fetchAlertsCurrent(backend.baseUrl, runToUse, effectiveModel, {
              mode: options.mode,
              signal: options.signal,
            }),
            fetchAlertsHistory(backend.baseUrl, runToUse, effectiveModel, 200, {
              mode: options.mode,
              signal: options.signal,
            }),
          ]);
        if (options.signal.aborted) {
          return;
        }
        if (regimeCurrentResult.status === "fulfilled") setRegimeCurrent(regimeCurrentResult.value);
        else tabErrors.push("regime current unavailable");
        if (alertsCurrentResult.status === "fulfilled") setAlertsCurrent(alertsCurrentResult.value);
        else tabErrors.push("alerts unavailable");
        if (alertsHistoryResult.status === "fulfilled") setAlertsHistory(alertsHistoryResult.value);
        else tabErrors.push("alerts history unavailable");
      } else if (tabId === "performance") {
        const [
          rollingResult,
          regimePerfResult,
          regimeHistoryResult,
          icDecayResult,
          predictionDistributionResult,
        ] = await Promise.allSettled([
          fetchPerformanceRolling(
            backend.baseUrl,
            runToUse,
            effectiveModel,
            63,
            126,
            { mode: options.mode, signal: options.signal },
          ),
          fetchPerformanceRegime(backend.baseUrl, runToUse, effectiveModel, {
            mode: options.mode,
            signal: options.signal,
          }),
          fetchRegimeHistory(backend.baseUrl, runToUse, effectiveModel, {
            mode: options.mode,
            signal: options.signal,
          }),
          fetchModelIcDecay(backend.baseUrl, runToUse, effectiveModel, 20, {
            mode: options.mode,
            signal: options.signal,
          }),
          fetchPredictionDistribution(
            backend.baseUrl,
            runToUse,
            effectiveModel,
            30,
            { mode: options.mode, signal: options.signal },
          ),
        ]);
        if (options.signal.aborted) {
          return;
        }
        if (rollingResult.status === "fulfilled") setRolling(rollingResult.value);
        else tabErrors.push("rolling unavailable");
        if (regimePerfResult.status === "fulfilled") setRegimePerf(regimePerfResult.value);
        else tabErrors.push("regime performance unavailable");
        if (regimeHistoryResult.status === "fulfilled") setRegimeHistory(regimeHistoryResult.value);
        else tabErrors.push("regime history unavailable");
        if (icDecayResult.status === "fulfilled") setIcDecay(icDecayResult.value);
        else tabErrors.push("ic decay unavailable");
        if (predictionDistributionResult.status === "fulfilled") {
          setPredictionDistribution(predictionDistributionResult.value);
        } else {
          tabErrors.push("prediction distribution unavailable");
        }
      } else if (tabId === "portfolio") {
        const [
          portfolioExposureResult,
          portfolioRiskResult,
          latestPredictionResult,
          runLatestRiskResult,
          runLatestExposuresResult,
          runLatestConstraintsResult,
        ] = await Promise.allSettled([
          fetchPortfolioExposure(backend.baseUrl, runToUse, effectiveModel, {
            mode: options.mode,
            signal: options.signal,
          }),
          fetchPortfolioRisk(backend.baseUrl, runToUse, effectiveModel, 126, {
            mode: options.mode,
            signal: options.signal,
          }),
          fetchPredictionsLatest(backend.baseUrl, runToUse, effectiveModel, 60),
          fetchRunLatestRisk(backend.baseUrl, effectiveModel, runToUse, 126),
          fetchRunLatestExposures(backend.baseUrl, effectiveModel, runToUse),
          fetchRunLatestConstraints(backend.baseUrl, effectiveModel, runToUse),
        ]);
        if (options.signal.aborted) {
          return;
        }
        if (portfolioExposureResult.status === "fulfilled") setPortfolioExposure(portfolioExposureResult.value);
        else tabErrors.push("portfolio exposure unavailable");
        if (portfolioRiskResult.status === "fulfilled") setPortfolioRisk(portfolioRiskResult.value);
        else tabErrors.push("portfolio risk unavailable");
        if (latestPredictionResult.status === "fulfilled") setPredictionsLatest(latestPredictionResult.value);
        else tabErrors.push("latest predictions unavailable");
        if (runLatestRiskResult.status === "fulfilled") setRunLatestRisk(runLatestRiskResult.value);
        else tabErrors.push("run latest risk unavailable");
        if (runLatestExposuresResult.status === "fulfilled") setRunLatestExposures(runLatestExposuresResult.value);
        else tabErrors.push("run latest exposures unavailable");
        if (runLatestConstraintsResult.status === "fulfilled") setRunLatestConstraints(runLatestConstraintsResult.value);
        else tabErrors.push("run latest constraints unavailable");

        const needSnapshotFallback =
          runLatestRiskResult.status !== "fulfilled" || runLatestConstraintsResult.status !== "fulfilled";
        if (needSnapshotFallback) {
          try {
            const snapshotPayload = await fetchRunSnapshot(
              backend.baseUrl,
              runToUse,
              effectiveModel,
              { profile: "full" },
            );
            if (!options.signal.aborted) {
              setRunSnapshot(snapshotPayload);
            }
          } catch {
            tabErrors.push("run snapshot unavailable");
          }
        }
      } else {
        const [featureResult] = await Promise.allSettled([
          fetchFeatureImportance(backend.baseUrl, runToUse, effectiveModel),
        ]);
        if (options.signal.aborted) {
          return;
        }
        if (featureResult.status === "fulfilled") setFeatureImportance(featureResult.value);
        else tabErrors.push("feature importance unavailable");
      }

      if (tabErrors.length > 0) {
        setWarningMessage((prev) => prev ?? `Some panels are using partial data: ${tabErrors[0]}`);
      }
      loadedTabCacheRef.current[cacheKey] = true;
    },
    [backend, effectiveModel],
  );

  const loadDashboard = useCallback(
    async (
      options: {
        includeTabData?: boolean;
        forceTabRefresh?: boolean;
        targetTab?: DashboardTabId;
      } = {},
    ) => {
      if (!backend?.connected) {
        return;
      }
      const includeTabData = options.includeTabData ?? true;
      abortRef.current?.abort();
      const controller = new AbortController();
      abortRef.current = controller;
      setIsLoadingData(true);
      setErrorMessage(null);
      setWarningMessage(null);

      try {
        let healthPayload: DashboardHealthPayload;
        let bootstrapSnapshot: RunSnapshotPayload | null = null;
        if (includeTabData) {
          const bootstrapPayload = await fetchDashboardBootstrap(
            backend.baseUrl,
            normalizedRunId || undefined,
            effectiveModel,
            { mode, signal: controller.signal, snapshotProfile: "core" },
          );
          if (controller.signal.aborted) {
            return;
          }
          healthPayload = bootstrapPayload.health;
          bootstrapSnapshot = bootstrapPayload.snapshot ?? null;
        } else {
          healthPayload = await fetchDashboardHealth(
            backend.baseUrl,
            normalizedRunId || undefined,
            effectiveModel,
            { mode, signal: controller.signal },
          );
        }
        if (controller.signal.aborted) {
          return;
        }
        setHealth(healthPayload);
        syncFromHealth(healthPayload);

        let runToUse = normalizedRunId;
        if (!runToUse) {
          runToUse = (healthPayload.resolved_run_id || healthPayload.latest_run_id || "").trim();
          if (runToUse) {
            setRunIdInput(runToUse);
            setRunId(runToUse);
          }
        }

        if (healthPayload.status === "not_found") {
          setErrorMessage(healthPayload.message || "Run not found");
        } else if (healthPayload.message) {
          setWarningMessage(healthPayload.message);
        }

        if (!runToUse) {
          setWarningMessage(healthPayload.message || "No run available. Train a model first.");
          setSummary(null);
          setPerformance(null);
          setRunLatestMeta(null);
          setRunSnapshot(null);
          clearTabPayloads();
          loadedTabCacheRef.current = {};
          dataScopeRef.current = "";
          return;
        }

        const scopeKey = `${runToUse}:${effectiveModel}:${mode}`;
        if (dataScopeRef.current !== scopeKey) {
          dataScopeRef.current = scopeKey;
          loadedTabCacheRef.current = {};
          clearTabPayloads();
          setRunSnapshot(null);
        }

        if (includeTabData) {
          const coreErrors: string[] = [];
          let snapshotPayload = bootstrapSnapshot;
          if (!snapshotPayload) {
            try {
              snapshotPayload = await fetchRunSnapshot(
                backend.baseUrl,
                runToUse,
                effectiveModel,
                { profile: "core" },
              );
              if (controller.signal.aborted) {
                return;
              }
            } catch {
              coreErrors.push("run snapshot unavailable");
            }
          }
          setRunSnapshot(snapshotPayload ?? null);

          const snapshotSummary = snapshotPayload?.artifact_summary ?? null;
          const snapshotPerformance = snapshotPayload?.model_performance ?? null;
          const snapshotRunLatestMeta = snapshotPayload?.run_latest_meta ?? null;
          if (snapshotSummary) {
            setSummary(snapshotSummary);
          }
          if (snapshotPerformance) {
            setPerformance(snapshotPerformance);
          }
          if (snapshotRunLatestMeta) {
            setRunLatestMeta(snapshotRunLatestMeta);
          }

          const fallbackTasks: Array<Promise<unknown>> = [];
          const fallbackKinds: Array<"summary" | "performance" | "run_latest_meta"> = [];
          if (!snapshotSummary) {
            fallbackKinds.push("summary");
            fallbackTasks.push(fetchArtifactSummary(backend.baseUrl, runToUse, effectiveModel));
          }
          if (!snapshotPerformance) {
            fallbackKinds.push("performance");
            fallbackTasks.push(fetchModelPerformance(backend.baseUrl, runToUse));
          }
          if (!snapshotRunLatestMeta) {
            fallbackKinds.push("run_latest_meta");
            fallbackTasks.push(fetchRunLatestMeta(backend.baseUrl, effectiveModel, runToUse));
          }
          if (fallbackTasks.length > 0) {
            const fallbackSettled = await Promise.allSettled(fallbackTasks);
            if (controller.signal.aborted) {
              return;
            }
            fallbackSettled.forEach((result, idx) => {
              const kind = fallbackKinds[idx];
              if (result.status !== "fulfilled") {
                if (kind === "summary") coreErrors.push("summary unavailable");
                else if (kind === "performance") coreErrors.push("performance unavailable");
                else coreErrors.push("run latest meta unavailable");
                return;
              }
              if (kind === "summary") setSummary(result.value as typeof snapshotSummary);
              else if (kind === "performance") setPerformance(result.value as typeof snapshotPerformance);
              else setRunLatestMeta(result.value as typeof snapshotRunLatestMeta);
            });
          }

          const blockingCoreErrors = coreErrors.filter((item) => item !== "summary unavailable");
          if (blockingCoreErrors.length > 0) {
            setWarningMessage(`Some panels are using partial data: ${blockingCoreErrors[0]}`);
          }
        }

        const workflow = healthPayload.workflow_state;
        patchSession({
          run_id: runToUse,
          model_name: effectiveModel,
          mode,
          data_timestamp: healthPayload.data_timestamp ?? null,
          ...(workflow
            ? {
                run_status: workflow.run_status,
                run_stage: workflow.run_stage,
                run_progress: workflow.run_progress,
                updated_at: workflow.updated_at ?? null,
                artifacts_ready: workflow.artifacts_ready,
              }
            : {}),
        });

        if (includeTabData) {
          const tabToLoad = options.targetTab ?? activeTabRef.current;
          await loadTabData(runToUse, tabToLoad, {
            signal: controller.signal,
            mode,
            force: options.forceTabRefresh ?? false,
          });
        }
      } catch (error) {
        if (error instanceof DOMException && error.name === "AbortError") {
          return;
        }
        setErrorMessage(error instanceof Error ? error.message : "Failed to load dashboard data.");
      } finally {
        if (abortRef.current === controller) {
          setIsLoadingData(false);
        }
      }
    },
    [
      backend,
      clearTabPayloads,
      effectiveModel,
      loadTabData,
      mode,
      normalizedRunId,
      patchSession,
      setRunId,
      syncFromHealth,
    ],
  );

  useEffect(() => {
    if (!backend?.connected) {
      return;
    }
    void loadDashboard({ includeTabData: true, forceTabRefresh: true });
    return () => {
      abortRef.current?.abort();
      tabAbortRef.current?.abort();
    };
  }, [backend, loadDashboard]);

  useEffect(() => {
    if (!backend?.connected || mode !== "live") {
      return;
    }
    const timer = window.setInterval(() => {
      if (!isVisible) {
        return;
      }
      void loadDashboard({ includeTabData: false });
    }, POLL_MS);
    if (isVisible) {
      void loadDashboard({ includeTabData: false });
    }
    return () => window.clearInterval(timer);
  }, [backend, mode, isVisible, loadDashboard]);

  useEffect(() => {
    if (!backend?.connected) {
      return;
    }
    if (activeTab === "summary" || activeTab === "regime") {
      return;
    }
    const runToUse = (normalizedRunId || health?.resolved_run_id || health?.latest_run_id || "").trim();
    if (!runToUse) {
      return;
    }
    tabAbortRef.current?.abort();
    const controller = new AbortController();
    tabAbortRef.current = controller;
    void loadTabData(runToUse, activeTab, {
      signal: controller.signal,
      mode,
      force: false,
    });
    return () => controller.abort();
  }, [activeTab, backend, health?.latest_run_id, health?.resolved_run_id, loadTabData, mode, normalizedRunId]);

  const selectedModelSummary = useMemo(
    () => performance?.models.find((item) => item.model_name === effectiveModel) ?? null,
    [performance, effectiveModel],
  );

  const summaryRequestMeta = extractSummaryRequestMeta(summary?.params);
  const wfConfig = summaryRequestMeta?.walk_forward_config;
  const trainingWindow = wfConfig ? `${wfConfig.train_months ?? "-"}M` : "-";
  const validationWindow = wfConfig ? `${wfConfig.val_months ?? "-"}M` : "-";

  const rollingIc3m = rolling?.rolling_ic_3m.map((item) => toNumber(item.value)) ?? [];
  const icHistogram = useMemo(() => rollingIc3m.slice(-252), [rollingIc3m]);

  const connectionDetail = backend ? formatBackendDetail(backend.detail, backend.connected) : "Resolving backend...";
  const exposureView = runLatestExposures ?? portfolioExposure;
  const riskTop10 =
    runLatestRisk?.position_risk_contrib_top10 ??
    runSnapshot?.risk_contrib_top10 ??
    portfolioRisk?.position_risk_contrib_top10 ??
    portfolioRisk?.position_risk_contrib_top5 ??
    [];
  const constraintBindings = runLatestConstraints?.items ?? runSnapshot?.constraint_bindings ?? [];
  const advLiquidityCaps = runLatestConstraints?.liquidity_adv_top ?? [];

  const latestPredRows =
    predictionsLatest?.predictions
      .map((row) => ({
        symbol: String(row.symbol ?? "-"),
        z: toNumber(row.z_score),
        score: toNumber(row.predicted_return),
      }))
      .slice(0, 30) ?? [];

  const heatmapUrl =
    tradingViewTab === "etf"
      ? "https://s.tradingview.com/embed-widget/etf-heatmap/"
      : tradingViewTab === "global"
        ? "https://s.tradingview.com/embed-widget/world-market-map/"
        : "https://s.tradingview.com/embed-widget/market-overview/";

  const focusSection = useMemo(() => new URLSearchParams(window.location.search).get("focus"), []);
  const requestedStart = typeof summaryRequestMeta?.date_range?.start === "string" ? summaryRequestMeta.date_range.start : "";
  const requestedEnd = typeof summaryRequestMeta?.date_range?.end === "string" ? summaryRequestMeta.date_range.end : "";
  const rollingDates = rolling?.cumulative_return ?? [];
  const fallbackStart = rollingDates.length > 0 ? String(rollingDates[0]?.date ?? "") : "";
  const fallbackEnd = rollingDates.length > 0 ? String(rollingDates[rollingDates.length - 1]?.date ?? "") : "";
  const backtestStart = requestedStart || fallbackStart || "2021-01-01";
  const backtestEnd = requestedEnd || health?.data_timestamp || fallbackEnd || new Date().toISOString().slice(0, 10);

  useEffect(() => {
    if (!focusSection || hasScrolledFocusRef.current) {
      return;
    }
    const targetRef =
      focusSection === "portfolio"
        ? portfolioRef
        : focusSection === "regime"
          ? regimeRef
          : focusSection === "health"
            ? healthRef
            : null;
    if (!targetRef?.current) {
      return;
    }
    hasScrolledFocusRef.current = true;
    targetRef.current.scrollIntoView({ behavior: "smooth", block: "start" });
  }, [focusSection]);

  const handleDashboardSignals = useCallback(async () => {
    if (!backend?.connected || !normalizedRunId || !isImplementedModel) {
      setWarningMessage("Select an implemented model and valid run_id first.");
      return;
    }
    setIsSubmittingSignals(true);
    setErrorMessage(null);
    try {
      const payload = await createSignals(backend.baseUrl, {
        run_id: normalizedRunId,
        model_name: effectiveModel,
        top_k: DEFAULT_TOP_K,
        score_threshold: DEFAULT_SCORE_THRESHOLD,
        balanced_long_short: false,
      });
      markArtifactReady("predictions", true);
      markArtifactReady("signals", true);
      patchSession({
        data_timestamp: payload.as_of_date,
      });
      invalidateQuantCaches(backend.baseUrl, normalizedRunId, effectiveModel);
      await loadDashboard();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to generate signals.");
    } finally {
      setIsSubmittingSignals(false);
    }
  }, [
    backend,
    effectiveModel,
    isImplementedModel,
    loadDashboard,
    markArtifactReady,
    normalizedRunId,
    patchSession,
  ]);

  const handleDashboardBacktest = useCallback(async () => {
    if (!backend?.connected || !normalizedRunId || !isImplementedModel) {
      setWarningMessage("Select an implemented model and valid run_id first.");
      return;
    }
    setIsSubmittingBacktest(true);
    setErrorMessage(null);
    try {
      await runBacktest(backend.baseUrl, {
        run_id: normalizedRunId,
        model_name: effectiveModel,
        start: backtestStart,
        end: backtestEnd,
        rebalance: "monthly",
        constraints: {
          max_weight: portfolioPolicy.single_name_max_abs_weight,
          long_only: true,
          risk_aversion: 3.0,
          lookback_days: 126,
        },
        cost_bps: 10,
        portfolio_mode: "long_only",
        mu_mapping: "quantile_mean_return",
      });
      markArtifactReady("backtest", true);
      markArtifactReady("portfolio_current", true);
      invalidateQuantCaches(backend.baseUrl, normalizedRunId, effectiveModel);
      await loadDashboard();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to run backtest.");
    } finally {
      setIsSubmittingBacktest(false);
    }
  }, [
    backend,
    backtestEnd,
    backtestStart,
    effectiveModel,
    isImplementedModel,
    loadDashboard,
    markArtifactReady,
    normalizedRunId,
    portfolioPolicy.single_name_max_abs_weight,
  ]);

  return (
    <div className="h-full min-h-0 overflow-auto py-4">
      <div className="mb-4 rounded-sm border border-theme-outline bg-theme-primary p-3">
        <div className="flex flex-wrap items-end gap-3">
          <div className="min-w-52 flex-1">
            <h1 className="body-lg-medium text-theme-primary">Quant Dashboard v3</h1>
            <p className="body-xs-regular text-theme-muted">Strategy monitoring, risk control, and model validation console.</p>
          </div>
          <label className="body-xs-medium text-theme-muted">
            Run ID
            <div className="mt-1 flex gap-2">
              <input
                className="w-72 rounded-sm border border-theme-outline bg-theme-secondary p-2 body-xs-regular text-theme-primary"
                value={runIdInput}
                onChange={(event) => setRunIdInput(event.target.value)}
                placeholder="Auto-detected when empty"
              />
              <button
                type="button"
                className="button-secondary rounded-sm px-3 py-2 body-xs-medium"
                onClick={() => {
                  const next = runIdInput.trim();
                  setRunId(next);
                }}
              >
                Apply
              </button>
            </div>
          </label>
          <div className="min-w-44">
            <p className="body-xs-medium text-theme-muted">Mode</p>
            <div className="mt-1 flex gap-2">
              <button
                type="button"
                className={`rounded-sm px-3 py-2 body-xs-medium ${mode === "backtest" ? "bg-sky-500/30 text-sky-300" : "bg-theme-secondary text-theme-muted"}`}
                onClick={() => {
                  setMode("backtest");
                  setSessionMode("backtest");
                }}
              >
                Backtest
              </button>
              <button
                type="button"
                className={`rounded-sm px-3 py-2 body-xs-medium ${mode === "live" ? "bg-emerald-500/30 text-emerald-300" : "bg-theme-secondary text-theme-muted"}`}
                onClick={() => {
                  setMode("live");
                  setSessionMode("live");
                }}
              >
                Live
              </button>
            </div>
          </div>
          <button
            type="button"
            className="button-secondary rounded-sm px-3 py-2 body-xs-medium"
            onClick={() => void loadDashboard({ includeTabData: true, forceTabRefresh: true })}
            disabled={isLoadingData || !backend?.connected}
            aria-label="Refresh dashboard data"
          >
            {isLoadingData ? "Refreshing..." : "Refresh"}
          </button>
        </div>

        <div className="mt-3 flex flex-wrap gap-2">
          {MODEL_TABS.map((tab) => (
            <button
              key={tab.id}
              type="button"
              className={`rounded-sm border px-3 py-1.5 body-xs-medium ${
                modelTab === tab.id
                  ? "border-sky-500/70 bg-sky-500/20 text-sky-300"
                  : "border-theme-outline bg-theme-secondary text-theme-muted"
              }`}
              onClick={() => {
                setModelTab(tab.id);
                if (tab.implemented) {
                  setModelName(tab.id as ModelName);
                }
              }}
            >
              {tab.label}
              {!tab.implemented ? " (Coming Soon)" : ""}
            </button>
          ))}
        </div>

        <div className="mt-3 flex flex-wrap items-center gap-2">
          <div className="grid grid-cols-2 gap-2 md:grid-cols-4 xl:grid-cols-6">
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Data Timestamp</p>
              <p className="body-xs-medium text-theme-primary">{health?.data_timestamp ?? "-"}</p>
            </div>
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Staleness (days)</p>
              <p className={`body-xs-medium ${(health?.staleness_days ?? 0) > 1 ? "text-amber-400" : "text-theme-primary"}`}>
                {health?.staleness_days ?? 0}
              </p>
            </div>
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Recommended Mode</p>
              <p className="body-xs-medium text-theme-primary">{health?.recommended_portfolio_mode ?? "-"}</p>
            </div>
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Connection</p>
              <p className="body-xs-medium text-theme-primary">{backend?.connected ? "Connected" : "Disconnected"}</p>
            </div>
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Artifact Status</p>
              <p className="body-xs-medium text-theme-primary">
                {runLatestMeta?.required_artifacts_ready ? "Ready" : "Pending"}
              </p>
            </div>
          </div>
          <button
            type="button"
            className="body-xxs-medium text-theme-muted hover:text-theme-primary"
            onClick={() => setShowHeaderDetails(!showHeaderDetails)}
          >
            {showHeaderDetails ? "Hide details" : "Show details"}
          </button>
        </div>
        {showHeaderDetails && (
          <div className="mt-2 grid grid-cols-2 gap-2 md:grid-cols-4 xl:grid-cols-8">
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Latest Market Date</p>
              <p className="body-xs-medium text-theme-primary">{health?.latest_market_date ?? "-"}</p>
            </div>
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Universe Size</p>
              <p className="body-xs-medium text-theme-primary">{health?.universe_size ?? 0}</p>
            </div>
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Cost (bps)</p>
              <p className="body-xs-medium text-theme-primary">{formatNumber(health?.cost_bps ?? 0, 1)}</p>
            </div>
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Cash Exposure</p>
              <p className="body-xs-medium text-theme-primary">{formatPct(health?.cash_exposure ?? 0, 1)}</p>
            </div>
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Gross Exposure</p>
              <p className="body-xs-medium text-theme-primary">{formatPct(health?.gross_exposure ?? 0, 1)}</p>
            </div>
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Net Exposure</p>
              <p className="body-xs-medium text-theme-primary">{formatPct(health?.net_exposure ?? 0, 1)}</p>
            </div>
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Workflow</p>
              <p className="body-xs-medium text-theme-primary">
                {health?.workflow_state?.run_status ?? "unknown"} ({health?.workflow_state?.run_progress ?? 0}%)
              </p>
              <p className="body-xxs-regular text-theme-muted">{health?.workflow_state?.run_stage ?? "-"}</p>
            </div>
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Run UID</p>
              <p className="body-xs-medium text-theme-primary">{runLatestMeta?.run_uid ?? "-"}</p>
            </div>
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Artifact Contract</p>
              <p className="body-xs-medium text-theme-primary">{runLatestMeta?.artifact_contract_version ?? "v1"}</p>
            </div>
          </div>
        )}
        <p className="mt-2 body-xxs-regular text-theme-muted">{connectionDetail}</p>
      </div>

      {!isImplementedModel ? (
        <div className="mb-3 rounded-sm border border-amber-500/50 bg-amber-500/10 p-2">
          <p className="body-xs-medium text-amber-300">
            {MODEL_TABS.find((item) => item.id === modelTab)?.label} is coming soon. Showing latest available metrics from {effectiveModel}.
          </p>
        </div>
      ) : null}

      {errorMessage ? (
        <div className="mb-3 rounded-sm border border-red-500/60 bg-red-500/10 p-2">
          <p className="body-xs-medium text-red-400">{errorMessage}</p>
        </div>
      ) : null}
      {warningMessage ? (
        <div className="mb-3 rounded-sm border border-amber-500/60 bg-amber-500/10 p-2">
          <p className="body-xs-medium text-amber-300">{warningMessage}</p>
        </div>
      ) : null}

      <div className="mb-4 flex flex-wrap gap-1 border-b border-theme-outline pb-2" role="tablist" aria-label="Dashboard sections">
        {(["summary", "performance", "risk", "portfolio", "model", "regime"] as const).map((tabId) => (
          <button
            key={tabId}
            type="button"
            role="tab"
            aria-selected={activeTab === tabId}
            className={`rounded-sm px-3 py-2 body-xs-medium transition-colors ${
              activeTab === tabId
                ? "bg-sky-500/20 text-sky-300 border border-sky-500/50"
                : "bg-theme-secondary text-theme-muted hover:bg-theme-outline/30 hover:text-theme-primary"
            }`}
            onClick={() => setActiveTab(tabId)}
          >
            {tabId === "summary" ? "Summary" : tabId === "performance" ? "Performance" : tabId === "risk" ? "Risk" : tabId === "portfolio" ? "Portfolio" : tabId === "model" ? "Model" : "Regime"}
          </button>
        ))}
      </div>

      <div className="min-h-0">
      {activeTab === "summary" && (
      <div className="space-y-4">
      <div className="rounded-sm border border-theme-outline bg-theme-primary p-4">
        <h3 className="body-sm-medium text-theme-primary mb-3">Today's Summary</h3>
        <div className="mb-3">
          <WorkflowSteps
            runId={normalizedRunId}
            artifactsReady={health?.workflow_state?.artifacts_ready ?? session.artifacts_ready}
          />
        </div>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 md:grid-cols-4">
          <SummaryCard
            label="Model Status"
            value={health?.status ?? "unknown"}
            status={health?.status === "ok" ? "ok" : health?.status === "not_found" ? "critical" : "warning"}
          />
          <SummaryCard
            label="Data Freshness"
            value={`${health?.staleness_days ?? 0}d`}
            status={(health?.staleness_days ?? 0) > 1 ? "warning" : "ok"}
          />
          <SummaryCard
            label="Recommended Mode"
            value={health?.recommended_portfolio_mode ?? "-"}
          />
          <SummaryCard
            label="Next Step"
            value={
              !normalizedRunId
                ? "Create a run in Quant Lab"
                : !(health?.workflow_state?.artifacts_ready?.predictions ?? session.artifacts_ready?.predictions)
                  ? "Generate signals"
                  : !(health?.workflow_state?.artifacts_ready?.backtest ?? session.artifacts_ready?.backtest)
                    ? "Run backtest"
                    : "Monitor portfolio"
            }
            actionLabel={!normalizedRunId ? "Go to Quant Lab" : undefined}
            actionHref={!normalizedRunId ? "/quant" : undefined}
          />
        </div>
      </div>

      <div className="mb-4 grid grid-cols-1 gap-4 xl:grid-cols-2">
        <PanelCard title="Run Action Center" description="Run signals/backtest directly from dashboard">
          <div className="grid grid-cols-2 gap-2">
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Default Top K</p>
              <p className="body-xs-medium text-theme-primary">{DEFAULT_TOP_K}</p>
            </div>
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Score Threshold</p>
              <p className="body-xs-medium text-theme-primary">{DEFAULT_SCORE_THRESHOLD.toFixed(1)}</p>
            </div>
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Backtest Start</p>
              <p className="body-xs-medium text-theme-primary">{backtestStart}</p>
            </div>
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Backtest End</p>
              <p className="body-xs-medium text-theme-primary">{backtestEnd}</p>
            </div>
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Policy Cap</p>
              <p className="body-xs-medium text-theme-primary">
                Single-name {(portfolioPolicy.single_name_max_abs_weight * 100).toFixed(0)}% (Hard)
              </p>
            </div>
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Small Universe</p>
              <p className="body-xs-medium text-theme-primary">{portfolioPolicy.small_universe_policy}</p>
            </div>
          </div>
          <div className="mt-2 rounded-sm bg-theme-secondary p-2">
            <p className="body-xxs-regular text-theme-muted">Artifact Status</p>
            <p className="body-xs-regular text-theme-primary">
              Predictions: {session.artifacts_ready?.predictions ? "Ready" : "Pending"} | Signals:{" "}
              {session.artifacts_ready?.signals ? "Ready" : "Pending"} | Backtest:{" "}
              {session.artifacts_ready?.backtest ? "Ready" : "Pending"}
            </p>
          </div>
          <div className="mt-3 flex flex-wrap gap-2">
            <div>
              <button
                type="button"
                className="button-secondary rounded-sm px-3 py-2 body-xs-medium"
                onClick={() => void handleDashboardSignals()}
                disabled={!backend?.connected || !normalizedRunId || isSubmittingSignals || !isImplementedModel}
              >
                {isSubmittingSignals ? "Generating..." : "Generate Signals"}
              </button>
              <p className="mt-1 body-xxs-regular text-theme-muted">Create buy/sell signals from the latest predictions.</p>
            </div>
            <div>
              <button
                type="button"
                className="button-secondary rounded-sm px-3 py-2 body-xs-medium"
                onClick={() => void handleDashboardBacktest()}
                disabled={!backend?.connected || !normalizedRunId || isSubmittingBacktest || !isImplementedModel}
              >
                {isSubmittingBacktest ? "Running..." : "Run Backtest"}
              </button>
              <p className="mt-1 body-xxs-regular text-theme-muted">Validate historical performance from stored predictions.</p>
            </div>
          </div>
        </PanelCard>

        <PanelCard title="Workflow Link" description="Jump between setup and monitoring">
          <p className="body-xs-regular text-theme-muted">
            Training and universe editing are still handled in Quant Lab. Dashboard actions reuse the same run and model session.
          </p>
          <div className="mt-3 flex flex-wrap gap-2">
            <a
              className="button-secondary rounded-sm px-3 py-2 body-xs-medium"
              href={`/quant?run_id=${encodeURIComponent(normalizedRunId)}&model=${encodeURIComponent(effectiveModel)}`}
            >
              Configure training and universe in Quant Lab
            </a>
          </div>
          <div className="mt-2 rounded-sm bg-theme-secondary p-2">
            <p className="body-xxs-regular text-theme-muted">Session</p>
            <p className="body-xs-regular text-theme-primary">
              run_id: {normalizedRunId || "-"} | model: {effectiveModel} | mode: {mode}
            </p>
          </div>
        </PanelCard>
      </div>

      {macroAvailable && macroRegime && (
        <div className="mb-4 rounded-sm border border-theme-outline bg-theme-primary p-3">
          <div className="flex items-center justify-between mb-2">
            <div>
              <h3 className="body-sm-medium text-theme-primary">Macro Regime (from Macro tab)</h3>
              <p className="body-xxs-regular text-theme-muted">
                Macro regime score summary. Open the Macro page for detailed analysis.
              </p>
            </div>
            <div className="flex items-center gap-2">
              {macroRegimeState && (
                <div className="flex gap-1.5">
                  <span className={`rounded-sm border px-2 py-0.5 body-xxs-medium ${macroRegimeState.inflation_up ? "border-amber-500/50 bg-amber-500/15 text-amber-300" : "border-zinc-500/50 bg-zinc-500/10 text-zinc-400"}`}>
                    Inflation {macroRegimeState.inflation_up ? "UP" : "OK"}
                  </span>
                  <span className={`rounded-sm border px-2 py-0.5 body-xxs-medium ${macroRegimeState.growth_down ? "border-red-500/50 bg-red-500/15 text-red-300" : "border-zinc-500/50 bg-zinc-500/10 text-zinc-400"}`}>
                    Growth {macroRegimeState.growth_down ? "DOWN" : "OK"}
                  </span>
                  <span className={`rounded-sm border px-2 py-0.5 body-xxs-medium ${macroRegimeState.risk_off_proxy ? "border-red-500/50 bg-red-500/15 text-red-300" : "border-zinc-500/50 bg-zinc-500/10 text-zinc-400"}`}>
                    {macroRegimeState.risk_off_proxy ? "Risk OFF" : "Risk ON"}
                  </span>
                </div>
              )}
              <a
                href="/macro"
                className="button-secondary rounded-sm px-2 py-1 body-xxs-medium"
              >
                Open Macro
              </a>
            </div>
          </div>
          <div className="grid grid-cols-5 gap-2">
            <ScoreGauge label="Risk-On" value={macroRegime.risk_on_score} />
            <ScoreGauge label="Inflation" value={macroRegime.inflation_score} invert />
            <ScoreGauge label="Growth" value={macroRegime.growth_score} />
            <ScoreGauge label="Liquidity" value={macroRegime.liquidity_score} />
            <ScoreGauge label="Credit Stress" value={macroRegime.credit_stress_score} invert />
          </div>
        <div className="mt-3 rounded-sm border border-theme-outline bg-theme-secondary p-2">
            <p className="body-xxs-medium text-theme-muted">Action Hint</p>
            <p className="body-xs-regular text-theme-primary">
              {macroRegimeState?.risk_off_proxy
                ? "Risk-off regime: prioritize defensive exposure and liquidity."
                : macroRegimeState?.inflation_up
                  ? "Inflation-up regime: consider inflation-hedge allocation."
                  : macroRegimeState?.growth_down
                    ? "Growth-down regime: reduce cyclicals and focus on quality."
                    : health?.recommended_portfolio_mode === "long_short"
                      ? "Risk-on score strong: long_short mode may be preferred."
                      : "Current condition is suitable for long_only baseline."}
            </p>
          </div>
        </div>
      )}
      </div>
      )}

      {activeTab === "risk" && (
      <div className="space-y-4">
      <div
        ref={healthRef}
        className={`grid grid-cols-1 gap-4 xl:grid-cols-3 ${focusSection === "health" ? "ring-2 ring-sky-500/50 rounded-lg p-1 -m-1" : ""}`}
      >
        <PanelCard title="Strategy Health" description="Signal dispersion, crowding, correlation, mismatch, confidence">
          <div className="grid grid-cols-2 gap-2">
            {Object.entries(health?.strategy_health ?? {}).map(([key, value]) => (
              <MetricTooltip
                key={key}
                label={key}
                value={formatNumber(value, 3)}
                definitionKey={key}
              />
            ))}
          </div>
        </PanelCard>

        <PanelCard title="Model Status" description="Prediction quality and OOS profile">
          <div className="grid grid-cols-2 gap-2">
            <MetricTooltip label="Training Window" value={trainingWindow} definitionKey="training_window" />
            <MetricTooltip label="Validation Window" value={validationWindow} definitionKey="validation_window" />
            <MetricTooltip
              label="Current IC"
              value={formatNumber(rollingIc3m.slice(-1)[0], 3)}
              definitionKey="ic"
            />
            <MetricTooltip
              label="Latest NDCG"
              value={formatNumber(selectedModelSummary?.ndcg ?? null, 3)}
              definitionKey="ndcg"
            />
            <MetricTooltip
              label="OOS Sharpe"
              value={formatNumber(selectedModelSummary?.sharpe ?? null, 3)}
              definitionKey="sharpe"
            />
            <MetricTooltip
              label="Max Drawdown"
              value={formatPct(selectedModelSummary?.max_dd ?? null, 2)}
              definitionKey="max_drawdown"
            />
            <MetricTooltip
              label="Turnover"
              value={formatNumber(selectedModelSummary?.turnover ?? null, 3)}
              definitionKey="turnover"
            />
            <MetricTooltip
              label="Hit Ratio"
              value={formatPct(selectedModelSummary?.hit_rate ?? null, 2)}
              definitionKey="hit_rate"
            />
            <MetricTooltip
              label="Prediction Dispersion"
              value={formatNumber(health?.strategy_health?.signal_dispersion ?? null, 3)}
              definitionKey="signal_dispersion"
            />
          </div>
        </PanelCard>

        <div
          ref={regimeRef}
          className={focusSection === "regime" ? "ring-2 ring-sky-500/50 rounded-lg p-1 -m-1" : ""}
        >
          <PanelCard title="Current Regime" description="Trend, volatility, liquidity, breadth">
            <div className="grid grid-cols-2 gap-2">
              <MetricTooltip
                label="Trend"
                value={regimeCurrent?.trend_regime ?? "-"}
                definitionKey="trend_regime"
              />
              <MetricTooltip
                label="Volatility"
                value={regimeCurrent?.vol_regime ?? "-"}
                definitionKey="vol_regime"
              />
              <MetricTooltip
                label="Liquidity"
                value={regimeCurrent?.liquidity_regime ?? "-"}
                definitionKey="liquidity_regime"
              />
              <MetricTooltip
                label="VIX Level"
                value={formatNumber(regimeCurrent?.vix_level ?? null, 2)}
                definitionKey="vix_level"
              />
              <MetricTooltip
                label="Breadth"
                value={formatPct(regimeCurrent?.breadth ?? null, 1)}
                definitionKey="breadth"
              />
              <MetricTooltip
                label="SPX vs 200MA"
                value={formatPct(regimeCurrent?.spx_distance_200ma ?? null, 2)}
                definitionKey="spx_distance_200ma"
              />
            </div>
          </PanelCard>
        </div>
      </div>

      <div className="mt-4 grid grid-cols-1 gap-4">
        <PanelCard title="Strategy Alerts" description="IC, drawdown, turnover, beta warnings">
          {!alertsCurrent || alertsCurrent.alerts.length === 0 ? (
            <p className="body-xs-regular text-theme-muted">No active alerts.</p>
          ) : (
            <div className="space-y-2">
              {alertsCurrent.alerts.map((item, idx) => (
                <div key={`${item.rule_id}-${idx}`} className="flex items-start justify-between rounded-sm bg-theme-secondary p-2">
                  <div>
                    <p className="body-xs-medium text-theme-primary">{item.message}</p>
                    <p className="body-xxs-regular text-theme-muted">{item.rule_id} | {item.triggered_at}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <p className="body-xs-regular text-theme-muted">{formatNumber(item.value, 3)}</p>
                    <SeverityBadge severity={item.severity} />
                  </div>
                </div>
              ))}
            </div>
          )}
          <p className="mt-2 body-xxs-regular text-theme-muted">History points: {alertsHistory?.alerts.length ?? 0}</p>
        </PanelCard>
      </div>
      </div>
      )}

      {activeTab === "performance" && (
      <div className="mt-4 grid grid-cols-1 gap-4 xl:grid-cols-2">
        <PanelCard title="Cumulative Performance" description="Return, rolling Sharpe, drawdown, turnover">
          <DashboardLineChart
            points={rolling?.cumulative_return ?? []}
            color="#0ea5e9"
            height={120}
            formatValue={(v) => (Math.abs(v) >= 1 ? v.toFixed(2) : (v * 100).toFixed(2) + "%")}
          />
          <div className="mt-2 grid grid-cols-2 gap-2">
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Rolling Sharpe 3M</p>
              <DashboardLineChart points={rolling?.rolling_sharpe_3m ?? []} color="#22c55e" height={90} />
            </div>
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Rolling MaxDD</p>
              <DashboardLineChart
                points={rolling?.rolling_maxdd ?? []}
                color="#ef4444"
                height={90}
                formatValue={(v) => (v * 100).toFixed(2) + "%"}
              />
            </div>
            <div className="col-span-2 rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Turnover Time Series</p>
              <DashboardLineChart points={rolling?.turnover_ts ?? []} color="#f59e0b" height={90} />
            </div>
          </div>
        </PanelCard>

        <PanelCard title="Rolling IC Analysis" description="3M/6M IC, histogram, IC decay, decile spread">
          <DashboardLineChart
            points={rolling?.rolling_ic_3m ?? []}
            secondaryPoints={rolling?.rolling_ic_6m ?? []}
            color="#38bdf8"
            secondaryColor="#22c55e"
            height={120}
            primaryLabel="IC 3M"
            secondaryLabel="IC 6M"
          />
          <div className="mt-2 grid grid-cols-2 gap-2">
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">IC Histogram (12M)</p>
              <DashboardHistogramChart values={icHistogram} height={90} />
            </div>
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">IC Decay (1-20)</p>
              <DashboardLineChart
                points={(icDecay?.ic_decay ?? []).map((d, i) => ({ date: String(i + 1), value: toNumber(d.ic) }))}
                color="#a855f7"
                height={90}
              />
              <p className="mt-1 body-xxs-regular text-theme-muted">IC t-stat: {formatNumber(icDecay?.ic_t_stat ?? null, 2)}</p>
            </div>
            <div className="col-span-2 rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Top Decile - Bottom Decile Spread</p>
              <DashboardLineChart
                points={(predictionDistribution?.decile_spread_ts ?? []).map((d) => ({ date: d.date ?? "", value: toNumber(d.spread) }))}
                color="#14b8a6"
                height={90}
              />
            </div>
          </div>
        </PanelCard>

      <div className="mt-4 grid grid-cols-1 gap-4 xl:grid-cols-2">
        <PanelCard title="Regime Matrix" description="Trend x Vol matrix">
          {regimePerf?.matrix_2d && regimePerf.matrix_2d.length > 0 ? (
            <div className="overflow-auto">
              <table className="min-w-full text-left">
                <thead>
                  <tr className="border-b border-theme-outline">
                    <th className="px-2 py-2 body-xxs-medium text-theme-muted">Trend</th>
                    <th className="px-2 py-2 body-xxs-medium text-theme-muted">Vol</th>
                    <th className="px-2 py-2 body-xxs-medium text-theme-muted">Sharpe</th>
                    <th className="px-2 py-2 body-xxs-medium text-theme-muted">IC</th>
                    <th className="px-2 py-2 body-xxs-medium text-theme-muted">Count</th>
                  </tr>
                </thead>
                <tbody>
                  {regimePerf.matrix_2d.map((row, idx) => (
                    <tr key={`matrix-${idx}`} className="border-b border-theme-outline/30">
                      <td className="px-2 py-2 body-xxs-regular text-theme-primary">{row.trend_regime}</td>
                      <td className="px-2 py-2 body-xxs-regular text-theme-primary">{row.vol_regime}</td>
                      <td className="px-2 py-2 body-xxs-regular text-theme-primary">{formatNumber(row.sharpe, 2)}</td>
                      <td className="px-2 py-2 body-xxs-regular text-theme-primary">{formatNumber(row.ic, 3)}</td>
                      <td className="px-2 py-2 body-xxs-regular text-theme-primary">{row.count}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="body-xs-regular text-theme-muted">No regime matrix data.</p>
          )}
        </PanelCard>

        <PanelCard title="Prediction Distribution" description="Histogram and decile summary">
          <DashboardHistogramChart
            values={predictionDistribution?.histogram.flatMap((item) => new Array(item.count).fill(item.bin_left)) ?? []}
            height={120}
          />
          <div className="mt-2 grid grid-cols-2 gap-2">
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Top Decile Mean</p>
              <p className="body-xs-medium text-theme-primary">{formatNumber(predictionDistribution?.top_decile_mean ?? null, 4)}</p>
            </div>
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Bottom Decile Mean</p>
              <p className="body-xs-medium text-theme-primary">{formatNumber(predictionDistribution?.bottom_decile_mean ?? null, 4)}</p>
            </div>
            <div className="col-span-2 rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Regime History Points</p>
              <p className="body-xs-medium text-theme-primary">{regimeHistory?.history.length ?? 0}</p>
            </div>
          </div>
        </PanelCard>
      </div>
      </div>
      )}

      {activeTab === "portfolio" && (
      <div className="mt-4 grid grid-cols-1 gap-4">
        <div
          ref={portfolioRef}
          className={focusSection === "portfolio" ? "ring-2 ring-sky-500/50 rounded-lg p-1 -m-1" : ""}
        >
          <PanelCard title="Portfolio Structure" description="Sector/factor exposure and position risk">
            <div className="grid grid-cols-2 gap-2">
            <div className="col-span-2 rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Sector Exposure</p>
              <ul className="mt-1 space-y-1">
                {(exposureView?.sector_exposure ?? []).map((item) => (
                  <li key={item.category} className="flex items-center justify-between">
                    <span className="body-xs-regular text-theme-primary">{item.category}</span>
                    <span className="body-xs-regular text-theme-muted">{formatPct(item.weight, 1)}</span>
                  </li>
                ))}
              </ul>
            </div>
            <div className="space-y-2">
              <MetricTooltip
                label="Beta SPY"
                value={formatNumber(exposureView?.beta_spy ?? null, 3)}
                definitionKey="beta_spy"
              />
              <MetricTooltip
                label="Beta QQQ"
                value={formatNumber(exposureView?.beta_qqq ?? null, 3)}
                definitionKey="beta_qqq"
              />
            </div>
            <div className="space-y-2">
              <MetricTooltip
                label="Ex-Ante Vol"
                value={formatPct(portfolioRisk?.vol_ex_ante ?? null, 2)}
                definitionKey="vol_ex_ante"
              />
              <MetricTooltip
                label="CVaR 95%"
                value={formatPct(portfolioRisk?.cvar_95 ?? null, 2)}
                definitionKey="cvar_95"
              />
            </div>
            <div className="col-span-2 rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Top 10 Long / Top 10 Short</p>
              <div className="mt-1 grid grid-cols-2 gap-2">
                <ul className="space-y-1">
                  {(exposureView?.top10_long ?? []).slice(0, 10).map((item) => (
                    <li key={`long-${item.symbol}`} className="flex items-center justify-between">
                      <span className="body-xs-regular text-theme-primary">{item.symbol}</span>
                      <span className="body-xs-regular text-theme-muted">{formatPct(item.weight, 1)}</span>
                    </li>
                  ))}
                </ul>
                <ul className="space-y-1">
                  {(exposureView?.top10_short ?? []).slice(0, 10).map((item) => (
                    <li key={`short-${item.symbol}`} className="flex items-center justify-between">
                      <span className="body-xs-regular text-theme-primary">{item.symbol}</span>
                      <span className="body-xs-regular text-theme-muted">{formatPct(item.weight, 1)}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
            <div className="col-span-2 rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Constraint Binding Frequency</p>
              {constraintBindings.length === 0 ? (
                <p className="mt-1 body-xs-regular text-theme-muted">No binding constraints recorded.</p>
              ) : (
                <ul className="mt-1 space-y-1">
                  {constraintBindings.slice(0, 8).map((item) => (
                    <li key={`bind-${item.constraint_type}`} className="flex items-center justify-between">
                      <span className="body-xs-regular text-theme-primary">{item.constraint_type}</span>
                      <span className="body-xs-regular text-theme-muted">
                        {item.binding_count} ({formatPct(item.binding_ratio, 1)})
                      </span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
            <div className="col-span-2 rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">ADV Participation Cap Heatmap</p>
              {advLiquidityCaps.length === 0 ? (
                <p className="mt-1 body-xs-regular text-theme-muted">No liquidity cap records.</p>
              ) : (
                <div className="mt-2 grid grid-cols-5 gap-1">
                  {advLiquidityCaps.slice(0, 20).map((item) => (
                    <div
                      key={`adv-${item.symbol}`}
                      className="rounded-sm p-1 text-center"
                      style={{ backgroundColor: zColor(Math.min(2, item.adv_weight_cap * 50)) }}
                    >
                      <p className="body-xxs-medium text-slate-100">{item.symbol}</p>
                      <p className="body-xxs-regular text-slate-100">{formatPct(item.adv_weight_cap, 1)}</p>
                    </div>
                  ))}
                </div>
              )}
            </div>
            <div className="col-span-2 rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Risk Contribution Top 10</p>
              {riskTop10.length === 0 ? (
                <p className="mt-1 body-xs-regular text-theme-muted">No risk contribution rows.</p>
              ) : (
                <ul className="mt-1 grid grid-cols-2 gap-1">
                  {riskTop10.slice(0, 10).map((item) => (
                    <li key={`rc-${item.symbol}`} className="flex items-center justify-between">
                      <span className="body-xs-regular text-theme-primary">{item.symbol}</span>
                      <span className="body-xs-regular text-theme-muted">{formatPct(item.contribution, 2)}</span>
                    </li>
                  ))}
                </ul>
              )}
            </div>
            <div className="col-span-2 rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Z-Score Heatmap</p>
              <div className="mt-2 grid grid-cols-5 gap-1">
                {latestPredRows.map((item) => (
                  <div key={`heat-${item.symbol}`} className="rounded-sm p-1 text-center" style={{ backgroundColor: zColor(item.z) }}>
                    <p className="body-xxs-medium text-slate-100">{item.symbol}</p>
                    <p className="body-xxs-regular text-slate-100">{item.z.toFixed(2)}</p>
                  </div>
                ))}
              </div>
            </div>
            </div>
          </PanelCard>
        </div>
      </div>
      )}

      {activeTab === "model" && (
      <div className="mt-4 grid grid-cols-1 gap-4 xl:grid-cols-2">
        <PanelCard title="Feature Analysis" description="Gain importance + SHAP phase split">
          {!featureImportance || featureImportance.items.length === 0 ? (
            <p className="body-xs-regular text-theme-muted">No feature importance data.</p>
          ) : (
            <ul className="space-y-1">
              {featureImportance.items.slice(0, 12).map((item, index) => (
                <li key={`fi-${index}`} className="flex items-center justify-between rounded-sm bg-theme-secondary px-2 py-1">
                  <span className="body-xs-regular text-theme-primary">{String(item.feature ?? `feature_${index}`)}</span>
                  <span className="body-xs-regular text-theme-muted">{formatNumber(item.importance as number, 3)}</span>
                </li>
              ))}
            </ul>
          )}
          <div className="mt-3 rounded-sm border border-theme-outline bg-theme-secondary p-2">
            <p className="body-xs-medium text-theme-primary">SHAP (Phase 2)</p>
            <p className="body-xxs-regular text-theme-muted">Summary/dependence/stability plots are reserved for phase 2 endpoints.</p>
          </div>
        </PanelCard>

        <PanelCard title="TradingView Heatmap" description="Dark mode widget with tab filters">
          <div className="mb-2 flex gap-2">
            <button
              type="button"
              className={`rounded-sm px-2 py-1 body-xxs-medium ${tradingViewTab === "market" ? "bg-sky-500/20 text-sky-300" : "bg-theme-secondary text-theme-muted"}`}
              onClick={() => setTradingViewTab("market")}
            >
              Market
            </button>
            <button
              type="button"
              className={`rounded-sm px-2 py-1 body-xxs-medium ${tradingViewTab === "etf" ? "bg-sky-500/20 text-sky-300" : "bg-theme-secondary text-theme-muted"}`}
              onClick={() => setTradingViewTab("etf")}
            >
              ETF
            </button>
            <button
              type="button"
              className={`rounded-sm px-2 py-1 body-xxs-medium ${tradingViewTab === "global" ? "bg-sky-500/20 text-sky-300" : "bg-theme-secondary text-theme-muted"}`}
              onClick={() => setTradingViewTab("global")}
            >
              Global
            </button>
          </div>
          <div className="relative h-[360px] w-full overflow-hidden rounded-sm border border-theme-outline">
            <iframe
              src={heatmapUrl}
              title="TradingView Market Overview"
              className="h-full w-full bg-black"
              loading="lazy"
            />
          </div>
        </PanelCard>
      </div>
      )}

      {activeTab === "regime" && (
      <div className="mt-4">
        <RegimeMonitorTab baseUrl={backend?.connected ? backend.baseUrl : null} />
      </div>
      )}

      </div>

      {isLoadingBackend ? <p className="mt-3 body-xs-regular text-theme-muted">Resolving backend...</p> : null}
      {isLoadingData ? <p className="mt-1 body-xs-regular text-theme-muted">Loading dashboard data...</p> : null}
    </div>
  );
}

export const Route = createFileRoute("/dashboard")({
  component: DashboardPage,
});
