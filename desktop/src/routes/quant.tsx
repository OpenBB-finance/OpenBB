import { createFileRoute, useRouter } from "@tanstack/react-router";
import { useCallback, useEffect, useMemo, useState } from "react";
import { ConnectionStatusCard } from "../components/quant/ConnectionStatusCard";
import { EquityCurveChart } from "../components/quant/EquityCurveChart";
import { ExplainabilityCard } from "../components/quant/ExplainabilityCard";
import { MetricsCards } from "../components/quant/MetricsCards";
import { PanelCard } from "../components/quant/PanelCard";
import { PortfolioRationaleCard } from "../components/quant/PortfolioRationaleCard";
import { RebalanceTimelineCard } from "../components/quant/RebalanceTimelineCard";
import { RunStatusCard } from "../components/quant/RunStatusCard";
import { SignalsTable } from "../components/quant/SignalsTable";
import {
  createSignals,
  fetchArtifactSummary,
  fetchRebalanceHistory,
  fetchModelIc,
  fetchPromotedModel,
  fetchModelRegime,
  fetchModelShap,
  fetchPortfolioPolicy,
  fetchPortfolioCurrent,
  fetchRunStatus,
  fetchUniverse,
  fetchUniverseList,
  invalidateQuantCaches,
  resolveUniverse,
  runBacktest,
  runBacktestWalkforward,
  fetchWalkforwardBacktestStatus,
  startTrain,
} from "../lib/quantApi";
import { resolveOpenBBBackend } from "../lib/openbbBackend";
import { useQuantSession } from "../contexts/QuantSessionContext";
import type { FeatureActivation } from "../types/feature-activation";
import type {
  ArtifactSummaryPayload,
  BacktestResponsePayload,
  ModelICPayload,
  ModelName,
  ModelConfigInput,
  ModelRegimePayload,
  ModelShapPayload,
  PortfolioPolicyPayload,
  PromotedModelPayload,
  RebalanceHistoryItem,
  RankerConfigInput,
  PortfolioCurrentPayload,
  RunStatusPayload,
  SignalsResponsePayload,
  TrainRequestPayload,
  UniverseAsset,
  UniverseListItemPayload,
  UniverseResponse,
  WalkForwardBacktestStatusPayload,
} from "../types/quant";

type UniverseProfileId = "all" | "aggressive" | "defensive" | "custom";
type UniverseSetId =
  | "default"
  | "global_core_equity";

interface UniverseProfile {
  id: Exclude<UniverseProfileId, "custom">;
  label: string;
  description: string;
}

interface UniverseSetOption {
  id: UniverseSetId;
  label: string;
  countHint?: number;
  hasFile?: boolean;
  minimumRequired?: number;
}

interface UniverseResolveState {
  status: "idle" | "loading" | "ok" | "error";
  message: string | null;
  count: number | null;
  minimumRequired: number;
  meetsMinimum: boolean;
}

const PROFILE_LIST: UniverseProfile[] = [
  { id: "all", label: "All", description: "Use every symbol in universe." },
  {
    id: "aggressive",
    label: "Aggressive",
    description: "Equity/sector/factor-focused basket.",
  },
  {
    id: "defensive",
    label: "Defensive",
    description: "Bonds, commodities, and defensive assets.",
  },
];

const UNIVERSE_SET_OPTIONS_DEFAULT: UniverseSetOption[] = [
  { id: "default", label: "Default (manual symbols)" },
  {
    id: "global_core_equity",
    label: "Global Core Equity (U0/U1/U2)",
    minimumRequired: 1200,
  },
];

function isUniverseSetId(value: string): value is UniverseSetId {
  return UNIVERSE_SET_OPTIONS_DEFAULT.some((option) => option.id === value);
}

function mergeUniverseSetOptions(items: UniverseListItemPayload[]): UniverseSetOption[] {
  const byId = new Map<UniverseSetId, UniverseSetOption>(
    UNIVERSE_SET_OPTIONS_DEFAULT.map((option) => [option.id, option]),
  );

  for (const item of items) {
    if (!isUniverseSetId(item.id)) {
      continue;
    }
    const base = byId.get(item.id);
    if (!base) {
      continue;
    }
    byId.set(item.id, {
      ...base,
      countHint: item.count_hint,
      hasFile: item.has_file,
      minimumRequired: item.minimum_required ?? base.minimumRequired,
    });
  }

  return UNIVERSE_SET_OPTIONS_DEFAULT.map((option) => byId.get(option.id) ?? option);
}

const AGGRESSIVE_CATEGORIES = new Set([
  "korea_index",
  "korea_etf",
  "us_index",
  "us_equity_etf",
  "us_tech_index",
  "us_tech_etf",
  "us_sector_etf",
  "semiconductor_etf",
  "software_etf",
  "global_equity_etf",
  "developed_market_etf",
  "emerging_market_etf",
  "factor_etf",
  "us_large_cap_equity",
  "ai_semiconductor_equity",
  "kospi200_constituent",
]);

const DEFENSIVE_CATEGORIES = new Set([
  "bond_etf",
  "cash_proxy",
  "commodity_etf",
  "reit_etf",
  "currency_etf",
]);

const todayIso = new Date().toISOString().slice(0, 10);
const fiveYearsAgoIso = (() => {
  const base = new Date();
  base.setFullYear(base.getFullYear() - 5);
  return base.toISOString().slice(0, 10);
})();

const defaultModelConfig: ModelConfigInput = {
  seq_len: 60,
  xgb_n_estimators: 400,
  xgb_max_depth: 4,
  xgb_learning_rate: 0.03,
  xgb_subsample: 0.9,
  xgb_colsample_bytree: 0.9,
  lstm_hidden_size: 64,
  lstm_num_layers: 2,
  lstm_dropout: 0.1,
  lstm_epochs: 30,
  lstm_batch_size: 128,
  lstm_learning_rate: 0.001,
  train_val_split: 0.8,
};

const defaultWalkForwardConfig = {
  train_months: 36,
  embargo_months: 1,
  val_months: 1,
  step_months: 1,
};

const defaultRankerConfig: RankerConfigInput = {
  objective: "rank_xendcg",
  metric: "ndcg",
  ndcg_eval_at: [5, 10, 20],
  learning_rate: 0.03,
  n_estimators: 6000,
  num_leaves: 63,
  min_data_in_leaf: 300,
  subsample: 0.8,
  colsample_bytree: 0.8,
  reg_lambda: 10.0,
  random_state: 42,
  early_stopping_rounds: 200,
};

const defaultThetaGrid = [0.8, 1.0, 1.2, 1.5];
const DEFAULT_PORTFOLIO_POLICY: PortfolioPolicyPayload = {
  template: "diversified_long_only",
  single_name_max_abs_weight: 0.1,
  small_universe_policy: "cash_buffer",
  sector_concentration_max: 0.35,
  turnover_max: 0.8,
  gross_exposure_max: 1.0,
  net_exposure_abs_max: 1.0,
  cash_symbol: "CASH",
  cash_category: "cash_proxy",
};

function parseSymbolsText(text: string): string[] {
  const seen = new Set<string>();
  const parsed: string[] = [];
  const items = text
    .split(/[\s,;]+/)
    .map((item) => item.trim())
    .filter(Boolean);

  for (const item of items) {
    const normalized = item.toUpperCase();
    if (!seen.has(normalized)) {
      seen.add(normalized);
      parsed.push(normalized);
    }
  }

  return parsed;
}

function formatSymbolsForTextarea(symbols: string[], perLine = 6): string {
  if (symbols.length === 0) {
    return "";
  }
  const lines: string[] = [];
  for (let idx = 0; idx < symbols.length; idx += perLine) {
    lines.push(symbols.slice(idx, idx + perLine).join(", "));
  }
  return lines.join("\n");
}

function symbolsByProfile(assets: UniverseAsset[], profileId: UniverseProfileId): string[] {
  if (profileId === "all" || profileId === "custom") {
    return assets.map((asset) => asset.symbol);
  }

  if (profileId === "aggressive") {
    return assets
      .filter((asset) => AGGRESSIVE_CATEGORIES.has(asset.category))
      .map((asset) => asset.symbol);
  }

  return assets
    .filter((asset) => DEFENSIVE_CATEGORIES.has(asset.category))
    .map((asset) => asset.symbol);
}

function profileLabel(profileId: UniverseProfileId): string {
  if (profileId === "custom") {
    return "Custom";
  }
  return PROFILE_LIST.find((profile) => profile.id === profileId)?.label ?? "Custom";
}

export default function QuantPage() {
  const router = useRouter();
  const { session, setRunId, setModelName, patchSession, markArtifactReady } = useQuantSession();

  const [isResolvingBackend, setIsResolvingBackend] = useState(false);
  const [backend, setBackend] = useState<Awaited<ReturnType<typeof resolveOpenBBBackend>> | null>(null);
  const [quantActivation, setQuantActivation] = useState<FeatureActivation | null>(null);
  const [universe, setUniverse] = useState<UniverseResponse | null>(null);
  const [universeSetOptions, setUniverseSetOptions] = useState<UniverseSetOption[]>(
    UNIVERSE_SET_OPTIONS_DEFAULT,
  );
  const [selectedUniverseSet, setSelectedUniverseSet] = useState<UniverseSetId>("default");
  const [universeResolveState, setUniverseResolveState] = useState<UniverseResolveState>({
    status: "idle",
    message: null,
    count: null,
    minimumRequired: 0,
    meetsMinimum: true,
  });

  const [selectedProfile, setSelectedProfile] = useState<UniverseProfileId>("all");
  const [symbolsInput, setSymbolsInput] = useState("");

  const [dateStart, setDateStart] = useState(fiveYearsAgoIso);
  const [dateEnd, setDateEnd] = useState(todayIso);
  const [modelConfig, setModelConfig] = useState<ModelConfigInput>(defaultModelConfig);
  const [selectedModel, setSelectedModel] = useState<ModelName>(() => session.model_name);

  const [runStatus, setRunStatus] = useState<RunStatusPayload | null>(null);
  const [runIdInput, setRunIdInput] = useState(() => session.run_id);
  const [activeTrainingRunId, setActiveTrainingRunId] = useState<string | null>(null);
  const [signals, setSignals] = useState<SignalsResponsePayload | null>(null);
  const [backtest, setBacktest] = useState<BacktestResponsePayload | null>(null);
  const [summary, setSummary] = useState<ArtifactSummaryPayload | null>(null);
  const [portfolioCurrent, setPortfolioCurrent] = useState<PortfolioCurrentPayload | null>(null);
  const [rebalanceHistory, setRebalanceHistory] = useState<RebalanceHistoryItem[]>([]);
  const [modelIcPayload, setModelIcPayload] = useState<ModelICPayload | null>(null);
  const [modelRegimePayload, setModelRegimePayload] = useState<ModelRegimePayload | null>(null);
  const [modelShapPayload, setModelShapPayload] = useState<ModelShapPayload | null>(null);
  const [portfolioPolicy, setPortfolioPolicy] = useState<PortfolioPolicyPayload>(DEFAULT_PORTFOLIO_POLICY);
  const [promotedModel, setPromotedModel] = useState<PromotedModelPayload | null>(null);
  const [walkforwardStatus, setWalkforwardStatus] = useState<WalkForwardBacktestStatusPayload | null>(null);
  const [diagnosticsError, setDiagnosticsError] = useState<string | null>(null);

  const [topK, setTopK] = useState(20);
  const [scoreThreshold, setScoreThreshold] = useState(0.5);

  const [isSubmittingTrain, setIsSubmittingTrain] = useState(false);
  const [isSubmittingSignals, setIsSubmittingSignals] = useState(false);
  const [isSubmittingBacktest, setIsSubmittingBacktest] = useState(false);
  const [isSubmittingWalkforward, setIsSubmittingWalkforward] = useState(false);
  const [isLoadingPortfolio, setIsLoadingPortfolio] = useState(false);
  const [isLoadingRebalanceHistory, setIsLoadingRebalanceHistory] = useState(false);
  const [portfolioError, setPortfolioError] = useState<string | null>(null);
  const [rebalanceHistoryError, setRebalanceHistoryError] = useState<string | null>(null);
  const [showPortfolioTimeline, setShowPortfolioTimeline] = useState(true);

  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const isUniverseSetMode = selectedUniverseSet !== "default";
  const selectedUniverseOption = useMemo(
    () => universeSetOptions.find((option) => option.id === selectedUniverseSet) ?? null,
    [selectedUniverseSet, universeSetOptions],
  );

  const applyProfile = useCallback(
    (profileId: Exclude<UniverseProfileId, "custom">, sourceUniverse: UniverseResponse | null) => {
      if (!sourceUniverse) {
        return;
      }

      const symbols = symbolsByProfile(sourceUniverse.assets, profileId);
      setSelectedProfile(profileId);
      setSymbolsInput(formatSymbolsForTextarea(symbols));
    },
    [],
  );

  const resolveBackendAndUniverse = useCallback(async () => {
    setIsResolvingBackend(true);
    setErrorMessage(null);

    try {
      const resolved = await resolveOpenBBBackend();
      setBackend(resolved);

      if (!resolved.connected) {
        setQuantActivation({
          featureName: "quant_ml",
          available: false,
          detail: "OpenBB API is not connected.",
          lastCheckedAt: new Date().toISOString(),
        });
        setUniverse(null);
        setUniverseSetOptions(UNIVERSE_SET_OPTIONS_DEFAULT);
        return;
      }

      let fetchedUniverseList: { universes: UniverseListItemPayload[] } | null = null;
      try {
        fetchedUniverseList = await fetchUniverseList(resolved.baseUrl);
        setQuantActivation({
          featureName: "quant_ml",
          available: true,
          detail: null,
          lastCheckedAt: new Date().toISOString(),
        });
      } catch (error) {
        setQuantActivation({
          featureName: "quant_ml",
          available: false,
          detail: error instanceof Error ? error.message : "quant_ml extension unavailable",
          lastCheckedAt: new Date().toISOString(),
        });
        setUniverse(null);
        setUniverseSetOptions(UNIVERSE_SET_OPTIONS_DEFAULT);
        setErrorMessage(
          error instanceof Error
            ? error.message
            : "quant_ml extension is unavailable. Install/enable openbb-quant-ml.",
        );
        return;
      }

      if (!fetchedUniverseList) {
        setUniverse(null);
        setUniverseSetOptions(UNIVERSE_SET_OPTIONS_DEFAULT);
        setErrorMessage(
          "quant_ml extension is unavailable. Install/enable openbb-quant-ml.",
        );
        return;
      }

      const fetchedUniverse = await fetchUniverse(resolved.baseUrl);
      setUniverse(fetchedUniverse);
      setUniverseSetOptions(mergeUniverseSetOptions(fetchedUniverseList.universes));
      try {
        const fetchedPolicy = await fetchPortfolioPolicy(resolved.baseUrl);
        setPortfolioPolicy(fetchedPolicy);
      } catch {
        setPortfolioPolicy(DEFAULT_PORTFOLIO_POLICY);
      }
      try {
        const promoted = await fetchPromotedModel(resolved.baseUrl, selectedModel);
        setPromotedModel(promoted);
      } catch {
        setPromotedModel(null);
      }

      setSymbolsInput((prev) => {
        if (prev.trim()) {
          return prev;
        }
        return formatSymbolsForTextarea(symbolsByProfile(fetchedUniverse.assets, "all"));
      });
      setSelectedProfile((prev) => (prev === "custom" ? prev : "all"));
    } catch (error) {
      setQuantActivation({
        featureName: "quant_ml",
        available: false,
        detail: error instanceof Error ? error.message : "Failed to resolve quant_ml activation.",
        lastCheckedAt: new Date().toISOString(),
      });
      setErrorMessage(error instanceof Error ? error.message : "Failed to resolve backend connection.");
    } finally {
      setIsResolvingBackend(false);
    }
  }, []);

  useEffect(() => {
    void resolveBackendAndUniverse();
  }, [resolveBackendAndUniverse]);

  useEffect(() => {
    setSelectedModel(session.model_name);
  }, [session.model_name]);

  useEffect(() => {
    setRunIdInput(session.run_id);
  }, [session.run_id]);

  useEffect(() => {
    const search = new URLSearchParams(window.location.search);
    const queryRunId = search.get("run_id")?.trim();
    const queryModel = search.get("model") || search.get("model_name");
    if (queryRunId) {
      setRunId(queryRunId);
      setRunIdInput(queryRunId);
    }
    if (queryModel === "lgbm_ranker" || queryModel === "xgb_lstm") {
      setSelectedModel(queryModel);
      setModelName(queryModel);
    }
  }, [setModelName, setRunId]);

  const runId = (runStatus?.run_id ?? "").trim() || null;

  useEffect(() => {
    if (runId) {
      setRunId(runId);
      patchSession({
        run_id: runId,
        model_name: selectedModel,
      });
      setRunIdInput(runId);
    }
  }, [patchSession, runId, selectedModel, setRunId]);

  const loadExistingRun = useCallback(
    async (candidateRunId?: string) => {
      if (!backend?.connected) {
        return;
      }

      const targetRunId = (candidateRunId ?? runIdInput).trim();
      if (!targetRunId) {
        setErrorMessage("Enter a run ID to load artifacts.");
        return;
      }

      setErrorMessage(null);
      setPortfolioError(null);
      try {
        const latest = await fetchRunStatus(backend.baseUrl, targetRunId);
        setRunStatus(latest);
        setActiveTrainingRunId(latest.status === "queued" || latest.status === "running" ? latest.run_id : null);
        setRunIdInput(targetRunId);
        setRunId(targetRunId);
        patchSession({
          run_id: targetRunId,
          model_name: selectedModel,
          run_status: latest.status,
          run_stage: latest.stage,
          run_progress: latest.progress,
          updated_at: latest.updated_at,
        });
      } catch (error) {
        setRunStatus(null);
        setActiveTrainingRunId(null);
        setSignals(null);
        setBacktest(null);
        setRebalanceHistory([]);
        setRebalanceHistoryError(null);
        setSummary(null);
        setPortfolioCurrent(null);
        setErrorMessage(error instanceof Error ? error.message : "Failed to load run by ID.");
      }
    },
    [backend, patchSession, runIdInput, selectedModel, setRunId],
  );

  useEffect(() => {
    if (!backend?.connected || runStatus) {
      return;
    }
    const existingRunId = session.run_id.trim();
    if (!existingRunId) {
      return;
    }
    setRunIdInput(existingRunId);
    void loadExistingRun(existingRunId);
  }, [backend, runStatus, loadExistingRun, session.run_id]);

  useEffect(() => {
    if (!backend?.connected || !runId || !runStatus) {
      return;
    }

    if (runStatus.status !== "queued" && runStatus.status !== "running") {
      return;
    }

    const timer = window.setInterval(async () => {
      try {
        const latest = await fetchRunStatus(backend.baseUrl, runId);
        setRunStatus(latest);
        patchSession({
          run_id: latest.run_id,
          model_name: selectedModel,
          run_status: latest.status,
          run_stage: latest.stage,
          run_progress: latest.progress,
          updated_at: latest.updated_at,
        });
        if (latest.status === "queued" || latest.status === "running") {
          setActiveTrainingRunId(latest.run_id);
        } else if (latest.status === "completed" || latest.status === "failed") {
          setActiveTrainingRunId((prev) => (prev === latest.run_id ? null : prev));
        }

        if (latest.status === "completed") {
          const latestSummary = await fetchArtifactSummary(backend.baseUrl, runId, selectedModel);
          setSummary(latestSummary);
          markArtifactReady("predictions", true);
        }
      } catch (error) {
        setErrorMessage(error instanceof Error ? error.message : "Failed to refresh run status.");
      }
    }, 3000);

    return () => window.clearInterval(timer);
  }, [backend, markArtifactReady, patchSession, runId, runStatus, selectedModel]);

  const parsedSymbols = useMemo(() => {
    const explicit = parseSymbolsText(symbolsInput);

    if (explicit.length > 0) {
      return explicit;
    }

    return universe?.assets.map((asset) => asset.symbol) ?? [];
  }, [symbolsInput, universe]);

  useEffect(() => {
    if (!isUniverseSetMode) {
      setUniverseResolveState({
        status: "idle",
        message: null,
        count: null,
        minimumRequired: 0,
        meetsMinimum: true,
      });
      return;
    }
    if (!backend?.connected) {
      setUniverseResolveState({
        status: "error",
        message: "OpenBB API is not connected.",
        count: null,
        minimumRequired: selectedUniverseOption?.minimumRequired ?? 0,
        meetsMinimum: false,
      });
      return;
    }

    let cancelled = false;
    setUniverseResolveState((prev) => ({
      ...prev,
      status: "loading",
      message: null,
      count: null,
      minimumRequired: selectedUniverseOption?.minimumRequired ?? 0,
      meetsMinimum: false,
    }));

    void (async () => {
      try {
        const resolved = await resolveUniverse(backend.baseUrl, selectedUniverseSet, "train", false);
        if (cancelled) {
          return;
        }
        const minimumRequired = Number(
          resolved.minimum_required ?? selectedUniverseOption?.minimumRequired ?? 0,
        );
        const meetsMinimum =
          typeof resolved.meets_minimum === "boolean"
            ? resolved.meets_minimum
            : minimumRequired <= 0 || Number(resolved.count) >= minimumRequired;
        setUniverseResolveState({
          status: "ok",
          message: null,
          count: Number(resolved.count),
          minimumRequired,
          meetsMinimum,
        });
      } catch (error) {
        if (cancelled) {
          return;
        }
        setUniverseResolveState({
          status: "error",
          message: error instanceof Error ? error.message : "Failed to resolve selected universe set.",
          count: null,
          minimumRequired: selectedUniverseOption?.minimumRequired ?? 0,
          meetsMinimum: false,
        });
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [backend, isUniverseSetMode, selectedUniverseOption?.minimumRequired, selectedUniverseSet]);

  const canUseApi = backend?.connected === true;
  const isTrainBlockedByUniverse =
    isUniverseSetMode &&
    (universeResolveState.status === "loading" ||
      universeResolveState.status === "error" ||
      universeResolveState.meetsMinimum === false);
  const canGenerateSignals = canUseApi && runStatus?.status === "completed";
  const dashboardLink = runId
    ? `/dashboard?run_id=${encodeURIComponent(runId)}&model=${encodeURIComponent(selectedModel)}&mode=backtest&focus=portfolio`
    : "/dashboard";

  const loadPortfolioCurrent = useCallback(
    async (options?: { suppressNotReady?: boolean; useCache?: boolean }) => {
      if (!backend?.connected || !runId) {
        return;
      }

      const suppressNotReady = options?.suppressNotReady ?? false;
      const useCache = options?.useCache ?? false;
      setIsLoadingPortfolio(true);
      setPortfolioError(null);
      try {
        const response = await fetchPortfolioCurrent(backend.baseUrl, runId, selectedModel, useCache);
        setPortfolioCurrent(response);
        const hasPortfolio = response.asset_class_weights.length > 0;
        markArtifactReady("portfolio_current", hasPortfolio);
        patchSession({
          data_timestamp: response.as_of_date ?? null,
          artifacts_ready: {
            portfolio_current: hasPortfolio,
          },
        });
      } catch (error) {
        const message =
          error instanceof Error ? error.message : "Failed to load portfolio rationale.";
        if (suppressNotReady && /Run backtest first/i.test(message)) {
          setPortfolioCurrent(null);
          setPortfolioError(null);
        } else {
          setPortfolioError(message);
        }
      } finally {
        setIsLoadingPortfolio(false);
      }
    },
    [backend, markArtifactReady, patchSession, runId, selectedModel],
  );

  const loadRebalanceHistory = useCallback(
    async (options?: { useCache?: boolean }) => {
      if (!backend?.connected || !runId) {
        return;
      }
      const useCache = options?.useCache ?? false;
      setIsLoadingRebalanceHistory(true);
      setRebalanceHistoryError(null);
      try {
        const response = await fetchRebalanceHistory(backend.baseUrl, runId, selectedModel, useCache);
        setRebalanceHistory(response.items ?? []);
      } catch (error) {
        const message = error instanceof Error ? error.message : "Failed to load rebalance history.";
        setRebalanceHistoryError(message);
      } finally {
        setIsLoadingRebalanceHistory(false);
      }
    },
    [backend, runId, selectedModel],
  );

  useEffect(() => {
    if (!backend?.connected || !runId) {
      return;
    }
    void (async () => {
      try {
        const latestSummary = await fetchArtifactSummary(backend.baseUrl, runId, selectedModel);
        setSummary(latestSummary);
        const hasPredictions = latestSummary.available_artifacts.some((name) => name.startsWith("predictions"));
        markArtifactReady("predictions", hasPredictions);
      } catch {
        // summary is optional for model-switching UX.
      }
      await loadPortfolioCurrent({ suppressNotReady: true, useCache: true });
      await loadRebalanceHistory({ useCache: true });
    })();
  }, [backend, loadPortfolioCurrent, loadRebalanceHistory, markArtifactReady, runId, selectedModel]);

  useEffect(() => {
    if (!backend?.connected || !runId || runStatus?.status !== "completed") {
      setModelIcPayload(null);
      setModelRegimePayload(null);
      setModelShapPayload(null);
      setDiagnosticsError(null);
      return;
    }

    let disposed = false;
    void (async () => {
      const [icRes, regimeRes, shapRes] = await Promise.allSettled([
        fetchModelIc(backend.baseUrl, runId, selectedModel),
        fetchModelRegime(backend.baseUrl, runId, selectedModel),
        fetchModelShap(backend.baseUrl, runId, selectedModel),
      ]);

      if (disposed) {
        return;
      }

      const errors: string[] = [];
      if (icRes.status === "fulfilled") {
        setModelIcPayload(icRes.value);
      } else {
        setModelIcPayload(null);
        errors.push(icRes.reason instanceof Error ? icRes.reason.message : "model/ic failed");
      }
      if (regimeRes.status === "fulfilled") {
        setModelRegimePayload(regimeRes.value);
      } else {
        setModelRegimePayload(null);
        errors.push(regimeRes.reason instanceof Error ? regimeRes.reason.message : "model/regime failed");
      }
      if (shapRes.status === "fulfilled") {
        setModelShapPayload(shapRes.value);
      } else {
        setModelShapPayload(null);
        errors.push(shapRes.reason instanceof Error ? shapRes.reason.message : "model/shap failed");
      }
      setDiagnosticsError(errors.length > 0 ? errors.join(" | ") : null);
    })();

    return () => {
      disposed = true;
    };
  }, [backend, runId, runStatus?.status, selectedModel]);

  const handleTrain = useCallback(async () => {
    if (!backend?.connected) {
      setErrorMessage("OpenBB API is not connected.");
      return;
    }
    if (selectedUniverseSet !== "default") {
      if (universeResolveState.status === "loading") {
        setErrorMessage("Universe set is still resolving. Retry after resolution completes.");
        return;
      }
      if (
        universeResolveState.status !== "ok" ||
        universeResolveState.meetsMinimum === false
      ) {
        setErrorMessage(
          universeResolveState.message ??
            "Selected universe set is unavailable or undersized. Run refresh_universes and retry.",
        );
        return;
      }
    }

    setIsSubmittingTrain(true);
    setErrorMessage(null);
    setRunStatus(null);
    setSignals(null);
    setBacktest(null);
    setRebalanceHistory([]);
    setRebalanceHistoryError(null);
    setSummary(null);
    setPortfolioCurrent(null);
    setPortfolioError(null);
    setActiveTrainingRunId(null);

    try {
      const trainPayloadBase: Omit<TrainRequestPayload, "symbols" | "universe_id"> = {
        date_range: { start: dateStart, end: dateEnd },
        horizon_days: 1,
        target_mode: "next_open_to_close",
        close_to_next_open_horizon_policy: "fixed_1",
        include_macro_features: true,
        macro_feature_subset: ["z_252", "yoy", "mom_3", "slope"],
        model_config: modelConfig,
        feature_config: {
          lags: [1, 2, 3, 5, 10, 20],
          vol_windows: [5, 20],
          momentum_windows: [5, 20],
          include_rsi: true,
          include_macd: true,
          include_regime_features: true,
        },
        training_mode: "dual_compare",
        model_set: ["xgb_lstm", "lgbm_ranker"],
        walk_forward_config: defaultWalkForwardConfig,
        ranker_config: defaultRankerConfig,
        signal_config: {
          theta_grid: defaultThetaGrid,
          selection_metric: "val_sharpe",
        },
        portfolio_mode: "long_only",
        mu_mapping: "quantile_mean_return",
        quick_mode: false,
        model_choice: "dual",
        early_stopping: true,
      };
      const trainPayload: TrainRequestPayload =
        selectedUniverseSet === "default"
          ? { ...trainPayloadBase, symbols: parsedSymbols }
          : { ...trainPayloadBase, universe_id: selectedUniverseSet };
      const response = await startTrain(backend.baseUrl, trainPayload);

      setRunStatus({
        run_id: response.run_id,
        status: "queued",
        progress: 0,
        stage: "queued",
        created_at: response.created_at,
        updated_at: response.created_at,
        logs_tail: ["Training job queued."],
        error: null,
      });
      setActiveTrainingRunId(response.run_id);
      patchSession({
        run_id: response.run_id,
        model_name: selectedModel,
        run_status: "queued",
        run_stage: "queued",
        run_progress: 0,
        updated_at: response.created_at,
        artifacts_ready: {
          predictions: false,
          signals: false,
          backtest: false,
          portfolio_current: false,
        },
      });
      const latest = await fetchRunStatus(backend.baseUrl, response.run_id);
      setRunStatus(latest);
      if (latest.status === "queued" || latest.status === "running") {
        setActiveTrainingRunId(latest.run_id);
      } else if (latest.status === "completed" || latest.status === "failed") {
        setActiveTrainingRunId(null);
      }
      setRunIdInput(response.run_id);
      setRunId(response.run_id);
      invalidateQuantCaches(backend.baseUrl, response.run_id, selectedModel);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to start training.");
    } finally {
      setIsSubmittingTrain(false);
    }
  }, [
    backend,
    dateEnd,
    dateStart,
    modelConfig,
    parsedSymbols,
    patchSession,
    selectedModel,
    universeResolveState.meetsMinimum,
    universeResolveState.message,
    universeResolveState.status,
    selectedUniverseSet,
    setRunId,
  ]);

  const handleSignals = useCallback(async () => {
    if (!backend?.connected || !runId) {
      return;
    }

    setIsSubmittingSignals(true);
    setErrorMessage(null);

    try {
      const response = await createSignals(backend.baseUrl, {
        run_id: runId,
        model_name: selectedModel,
        top_k: topK,
        score_threshold: scoreThreshold,
      });
      setSignals(response);
      markArtifactReady("signals", true);
      markArtifactReady("predictions", true);
      patchSession({
        data_timestamp: response.as_of_date,
      });
      invalidateQuantCaches(backend.baseUrl, runId, selectedModel);

      const latestSummary = await fetchArtifactSummary(backend.baseUrl, runId, selectedModel);
      setSummary(latestSummary);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to generate signals.");
    } finally {
      setIsSubmittingSignals(false);
    }
  }, [backend, markArtifactReady, patchSession, runId, scoreThreshold, selectedModel, topK]);

  const handleBacktest = useCallback(async () => {
    if (!backend?.connected || !runId) {
      return;
    }

    setIsSubmittingBacktest(true);
    setErrorMessage(null);

    try {
      const response = await runBacktest(backend.baseUrl, {
        run_id: runId,
        model_name: selectedModel,
        start: dateStart,
        end: dateEnd,
        rebalance: "monthly",
        constraints: {
          max_weight: portfolioPolicy.single_name_max_abs_weight,
          long_only: true,
          risk_aversion: 3.0,
          lookback_days: 126,
        },
        cost_bps: 10,
        slippage_bps: 2,
        entry_price: "next_open",
        exit_price: "close",
        portfolio_mode: "long_only",
        mu_mapping: "quantile_mean_return",
      });
      setBacktest(response);
      setRebalanceHistory(response.rebalance_history_summary ?? []);
      setRebalanceHistoryError(null);
      markArtifactReady("backtest", true);
      patchSession({
        data_timestamp: response.end_date,
        artifacts_ready: {
          backtest: true,
        },
      });
      invalidateQuantCaches(backend.baseUrl, runId, selectedModel);

      const latestSummary = await fetchArtifactSummary(backend.baseUrl, runId, selectedModel);
      setSummary(latestSummary);
      await loadPortfolioCurrent({ suppressNotReady: false, useCache: false });
      if (!response.rebalance_history_summary || response.rebalance_history_summary.length === 0) {
        await loadRebalanceHistory({ useCache: false });
      }
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to run backtest.");
    } finally {
      setIsSubmittingBacktest(false);
    }
  }, [
    backend,
    dateEnd,
    dateStart,
    loadPortfolioCurrent,
    loadRebalanceHistory,
    markArtifactReady,
    patchSession,
    portfolioPolicy.single_name_max_abs_weight,
    runId,
    selectedModel,
  ]);

  const handleWalkforwardBacktest = useCallback(async () => {
    if (!backend?.connected || !runId) {
      setErrorMessage("Training run must be completed before walk-forward backtest.");
      return;
    }

    setIsSubmittingWalkforward(true);
    setErrorMessage(null);
    setWalkforwardStatus(null);
    try {
      const submit = await runBacktestWalkforward(backend.baseUrl, {
        run_id: runId,
        model_name: selectedModel,
        start: dateStart,
        end: dateEnd,
        rebalance: "monthly",
        constraints: {
          max_weight: portfolioPolicy.single_name_max_abs_weight,
          long_only: true,
          risk_aversion: 3.0,
          lookback_days: 126,
        },
        cost_bps: 10,
        slippage_bps: 2,
        entry_price: "next_open",
        exit_price: "close",
        portfolio_mode: "long_only",
        regime_policy: "mixed",
        min_history_days: 126,
      });

      let latest = await fetchWalkforwardBacktestStatus(backend.baseUrl, submit.job_id);
      setWalkforwardStatus(latest);
      const startedAt = Date.now();
      while ((latest.status === "queued" || latest.status === "running") && Date.now() - startedAt < 180_000) {
        await new Promise((resolve) => window.setTimeout(resolve, 1500));
        latest = await fetchWalkforwardBacktestStatus(backend.baseUrl, submit.job_id);
        setWalkforwardStatus(latest);
      }

      if (latest.status === "failed") {
        throw new Error(latest.message || "Walk-forward backtest failed.");
      }

      if (latest.status === "completed") {
        markArtifactReady("backtest", true);
        patchSession({
          run_stage: "walkforward_completed",
          run_progress: 100,
          artifacts_ready: { backtest: true },
        });
      }
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to run walk-forward backtest.");
    } finally {
      setIsSubmittingWalkforward(false);
    }
  }, [
    backend,
    dateEnd,
    dateStart,
    markArtifactReady,
    patchSession,
    portfolioPolicy.single_name_max_abs_weight,
    runId,
    selectedModel,
  ]);

  return (
    <div className="h-full min-h-0 overflow-auto py-4">
      <div className="mb-4">
        <h1 className="body-lg-medium text-theme-primary">Quant Lab</h1>
        <p className="body-sm-regular text-theme-muted">
          Local ML/DL quant workflow: train, signal generation, backtest, and SPY benchmark comparison.
        </p>
      </div>

      {errorMessage ? (
        <div className="mb-3 rounded-sm border border-red-500/60 bg-red-500/10 p-2">
          <p className="body-xs-medium text-red-400">{errorMessage}</p>
        </div>
      ) : null}
      {quantActivation && !quantActivation.available ? (
        <div className="mb-3 rounded-sm border border-amber-500/60 bg-amber-500/10 p-2">
          <p className="body-xs-medium text-amber-300">
            quant_ml extension unavailable: {quantActivation.detail || "Install/enable openbb-quant-ml."}
          </p>
        </div>
      ) : null}

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[360px_minmax(0,1fr)]">
        <div className="space-y-4">
          <PanelCard title="Controls" description="Universe, period, model, and run actions">
            <div className="space-y-3">
              <div>
                <label htmlFor="quant-universe-set" className="body-xs-medium text-theme-muted">
                  Universe Set
                </label>
                <select
                  id="quant-universe-set"
                  className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary p-2 body-xs-regular text-theme-primary"
                  value={selectedUniverseSet}
                  onChange={(event) => {
                    setSelectedUniverseSet(event.target.value as UniverseSetId);
                    setErrorMessage(null);
                  }}
                >
                  {universeSetOptions.map((option) => {
                    const suffix =
                      option.countHint !== undefined
                        ? ` (${option.countHint}${
                            option.minimumRequired ? ` / min ${option.minimumRequired}` : ""
                          })`
                        : option.minimumRequired
                          ? ` (min ${option.minimumRequired})`
                          : "";
                    const missing =
                      option.id !== "default" && option.hasFile === false ? " [missing]" : "";
                    return (
                      <option key={option.id} value={option.id}>
                        {option.label}
                        {suffix}
                        {missing}
                      </option>
                    );
                  })}
                </select>
                <p className="mt-1 body-xs-regular text-theme-muted">
                  {isUniverseSetMode
                    ? "Universe set mode is active. Train request will send universe_id only."
                    : "Default mode is active. Train request will use symbols from textarea."}
                </p>
                {isUniverseSetMode && universeResolveState.status === "loading" ? (
                  <p className="mt-1 body-xs-regular text-theme-muted">
                    Resolving universe set symbols...
                  </p>
                ) : null}
                {isUniverseSetMode && universeResolveState.status === "ok" ? (
                  <p className="mt-1 body-xs-regular text-emerald-300">
                    Resolved {universeResolveState.count ?? 0} symbols
                    {universeResolveState.minimumRequired > 0
                      ? ` (minimum ${universeResolveState.minimumRequired})`
                      : ""}
                    .
                  </p>
                ) : null}
                {isUniverseSetMode && universeResolveState.status === "error" ? (
                  <p className="mt-1 body-xs-medium text-amber-300">
                    {universeResolveState.message ??
                      "Selected universe set is invalid or undersized. Run refresh_universes --all --no-validate."}
                  </p>
                ) : null}
              </div>

              <div>
                <p className="body-xs-medium text-theme-muted">Universe Profile</p>
                <div className="mt-1 flex flex-wrap gap-2">
                  {PROFILE_LIST.map((profile) => (
                    <button
                      key={profile.id}
                      type="button"
                      className={`rounded-sm px-2 py-1 body-xs-medium ${
                        selectedProfile === profile.id ? "button-neutral" : "button-secondary"
                      }`}
                      onClick={() => applyProfile(profile.id, universe)}
                      disabled={!universe || isUniverseSetMode}
                      title={profile.description}
                    >
                      {profile.id === "all" && universe ? `All (${universe.assets.length})` : profile.label}
                    </button>
                  ))}
                  <span className="rounded-sm bg-theme-secondary px-2 py-1 body-xs-regular text-theme-muted">
                    Current: {profileLabel(selectedProfile)}
                  </span>
                </div>
              </div>

              <div>
                <label htmlFor="quant-symbols" className="body-xs-medium text-theme-muted">
                  Symbols (comma/newline separated)
                </label>
                <textarea
                  id="quant-symbols"
                  className="mt-1 h-28 w-full resize-y rounded-sm border border-theme-outline bg-theme-secondary p-2 font-mono text-[13px] !leading-6 tracking-normal text-theme-primary"
                  value={symbolsInput}
                  spellCheck={false}
                  placeholder="SPY, QQQ, TLT ..."
                  onChange={(event) => {
                    setSelectedProfile("custom");
                    setSymbolsInput(event.target.value);
                  }}
                  disabled={isUniverseSetMode}
                />
                <div className="mt-2 flex gap-2">
                  <button
                    type="button"
                    className="button-secondary rounded-sm px-2 py-1 body-xs-medium"
                    onClick={() => {
                      setSelectedProfile("custom");
                      setSymbolsInput(formatSymbolsForTextarea(parsedSymbols));
                    }}
                    disabled={isUniverseSetMode}
                  >
                    Format
                  </button>
                  <button
                    type="button"
                    className="button-secondary rounded-sm px-2 py-1 body-xs-medium"
                    onClick={() => {
                      setSelectedProfile("custom");
                      setSymbolsInput("");
                    }}
                    disabled={isUniverseSetMode}
                  >
                    Clear
                  </button>
                </div>
                <p className="mt-1 body-xs-regular text-theme-muted">
                  Parsed symbols: {parsedSymbols.length}
                  {universe ? ` / Universe version: ${universe.version}` : ""}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <label className="body-xs-medium text-theme-muted">
                  Start
                  <input
                    type="date"
                    className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary p-2 body-xs-regular text-theme-primary"
                    value={dateStart}
                    onChange={(event) => setDateStart(event.target.value)}
                  />
                </label>
                <label className="body-xs-medium text-theme-muted">
                  End
                  <input
                    type="date"
                    className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary p-2 body-xs-regular text-theme-primary"
                    value={dateEnd}
                    onChange={(event) => setDateEnd(event.target.value)}
                  />
                </label>
              </div>

              <div className="grid grid-cols-[minmax(0,1fr)_auto] gap-2">
                <label className="body-xs-medium text-theme-muted">
                  Run ID
                  <input
                    type="text"
                    className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary p-2 body-xs-regular text-theme-primary"
                    value={runIdInput}
                    onChange={(event) => setRunIdInput(event.target.value)}
                    placeholder="Paste existing run_id"
                  />
                </label>
                <button
                  type="button"
                  className="button-secondary mb-0.5 self-end rounded-sm px-3 py-2 body-xs-medium"
                  onClick={() => {
                    void loadExistingRun();
                  }}
                  disabled={!canUseApi || !runIdInput.trim()}
                >
                  Load Run
                </button>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <label className="body-xs-medium text-theme-muted">
                  LSTM Seq Len
                  <input
                    type="number"
                    min={20}
                    max={240}
                    className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary p-2 body-xs-regular text-theme-primary"
                    value={modelConfig.seq_len}
                    onChange={(event) =>
                      setModelConfig((prev) => ({ ...prev, seq_len: Number(event.target.value) }))
                    }
                  />
                </label>
                <label className="body-xs-medium text-theme-muted">
                  LSTM Epochs
                  <input
                    type="number"
                    min={5}
                    max={300}
                    className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary p-2 body-xs-regular text-theme-primary"
                    value={modelConfig.lstm_epochs}
                    onChange={(event) =>
                      setModelConfig((prev) => ({ ...prev, lstm_epochs: Number(event.target.value) }))
                    }
                  />
                </label>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <label className="body-xs-medium text-theme-muted">
                  Model
                  <select
                    className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary p-2 body-xs-regular text-theme-primary"
                    value={selectedModel}
                    onChange={(event) => {
                      const next = event.target.value as ModelName;
                      setSelectedModel(next);
                      setModelName(next);
                    }}
                  >
                    <option value="lgbm_ranker">LGBM Ranker</option>
                    <option value="xgb_lstm">XGB + LSTM</option>
                  </select>
                </label>
                <label className="body-xs-medium text-theme-muted">
                  Top K
                  <input
                    type="number"
                    min={1}
                    max={200}
                    className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary p-2 body-xs-regular text-theme-primary"
                    value={topK}
                    onChange={(event) => setTopK(Number(event.target.value))}
                  />
                </label>
                <label className="body-xs-medium text-theme-muted">
                  Score Threshold
                  <input
                    type="number"
                    step={0.1}
                    min={0}
                    max={5}
                    className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary p-2 body-xs-regular text-theme-primary"
                    value={scoreThreshold}
                    onChange={(event) => setScoreThreshold(Number(event.target.value))}
                  />
                </label>
              </div>

              <div className="grid grid-cols-1 gap-2">
                <button
                  type="button"
                  className="button-neutral rounded-sm px-3 py-2 body-xs-medium"
                  onClick={handleTrain}
                  disabled={!canUseApi || isSubmittingTrain || isTrainBlockedByUniverse}
                >
                  {isSubmittingTrain ? "Submitting..." : "Start Training"}
                </button>
                <button
                  type="button"
                  className="button-secondary rounded-sm px-3 py-2 body-xs-medium"
                  onClick={handleSignals}
                  disabled={!canGenerateSignals || isSubmittingSignals}
                >
                  {isSubmittingSignals ? "Generating..." : "Generate Signals"}
                </button>
                <button
                  type="button"
                  className="button-secondary rounded-sm px-3 py-2 body-xs-medium"
                  onClick={handleBacktest}
                  disabled={!canGenerateSignals || isSubmittingBacktest}
                >
                  {isSubmittingBacktest ? "Running..." : "Run Backtest"}
                </button>
                <button
                  type="button"
                  className="button-secondary rounded-sm px-3 py-2 body-xs-medium"
                  onClick={handleWalkforwardBacktest}
                  disabled={!canGenerateSignals || isSubmittingWalkforward}
                >
                  {isSubmittingWalkforward ? "Running..." : "Run Walk-forward Backtest"}
                </button>
              </div>
              <div className="rounded-sm border border-theme-outline bg-theme-secondary p-2">
                <p className="body-xs-medium text-theme-primary">
                  Single-name cap {(portfolioPolicy.single_name_max_abs_weight * 100).toFixed(0)}% (Hard)
                </p>
                <p className="body-xxs-regular text-theme-muted">
                  Template: {portfolioPolicy.template} | Small universe: {portfolioPolicy.small_universe_policy}
                </p>
                {backtest?.effective_constraints ? (
                  <p className="body-xxs-regular text-theme-muted">
                    Applied cap:{" "}
                    {(
                      Number(backtest.effective_constraints.max_weight ?? portfolioPolicy.single_name_max_abs_weight) * 100
                    ).toFixed(1)}
                    % | Cash buffer: {(Number(backtest.cash_weight ?? 0) * 100).toFixed(1)}%
                  </p>
                ) : null}
                {promotedModel?.run_id ? (
                  <p className="body-xxs-regular text-theme-muted">
                    Promoted model: {promotedModel.run_id} ({promotedModel.ready ? "ready" : "not ready"})
                  </p>
                ) : null}
                {walkforwardStatus ? (
                  <p className="body-xxs-regular text-theme-muted">
                    Walk-forward: {walkforwardStatus.status} ({walkforwardStatus.progress}%)
                  </p>
                ) : null}
                <label className="mt-2 inline-flex items-center gap-2 body-xxs-regular text-theme-muted">
                  <input
                    type="checkbox"
                    checked={showPortfolioTimeline}
                    onChange={(event) => setShowPortfolioTimeline(event.target.checked)}
                  />
                  Portfolio Timeline
                </label>
              </div>
            </div>
          </PanelCard>
        </div>

        <div className="space-y-4">
          <ConnectionStatusCard
            resolution={backend}
            isLoading={isResolvingBackend}
            onRetry={() => void resolveBackendAndUniverse()}
            onGoBackends={() => router.navigate({ to: "/backends" })}
          />
          <PanelCard title="Workflow Sync" description="Shared run/model session with Dashboard">
            <div className="space-y-2">
              <div className="rounded-sm bg-theme-secondary p-2">
                <p className="body-xs-regular text-theme-muted">
                  Run: <span className="text-theme-primary">{session.run_id || "-"}</span>
                </p>
                <p className="body-xs-regular text-theme-muted">
                  Model: <span className="text-theme-primary">{session.model_name}</span>
                </p>
                <p className="body-xs-regular text-theme-muted">
                  Dashboard timestamp: <span className="text-theme-primary">{session.data_timestamp || "-"}</span>
                </p>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div className="rounded-sm bg-theme-secondary p-2">
                  <p className="body-xxs-regular text-theme-muted">Predictions</p>
                  <p className="body-xs-medium text-theme-primary">{session.artifacts_ready.predictions ? "Ready" : "Not Ready"}</p>
                </div>
                <div className="rounded-sm bg-theme-secondary p-2">
                  <p className="body-xxs-regular text-theme-muted">Backtest</p>
                  <p className="body-xs-medium text-theme-primary">{session.artifacts_ready.backtest ? "Ready" : "Not Ready"}</p>
                </div>
                <div className="rounded-sm bg-theme-secondary p-2">
                  <p className="body-xxs-regular text-theme-muted">Signals</p>
                  <p className="body-xs-medium text-theme-primary">{session.artifacts_ready.signals ? "Ready" : "Not Ready"}</p>
                </div>
                <div className="rounded-sm bg-theme-secondary p-2">
                  <p className="body-xxs-regular text-theme-muted">Portfolio Rationale</p>
                  <p className="body-xs-medium text-theme-primary">{session.artifacts_ready.portfolio_current ? "Ready" : "Not Ready"}</p>
                </div>
              </div>
              <a className="button-secondary inline-flex rounded-sm px-3 py-2 body-xs-medium" href={dashboardLink}>
                Dashboard에서 리스크 구조 보기
              </a>
            </div>
          </PanelCard>
          <RunStatusCard run={runStatus} isLiveRun={runStatus?.run_id === activeTrainingRunId} />
          <SignalsTable asOfDate={signals?.as_of_date} signals={signals?.signals ?? []} />
          <MetricsCards metrics={backtest?.metrics ?? null} />
          <PortfolioRationaleCard
            portfolio={portfolioCurrent}
            isLoading={isLoadingPortfolio}
            errorMessage={portfolioError}
            onRetry={() => {
              void loadPortfolioCurrent({ suppressNotReady: false, useCache: false });
            }}
          />
          {showPortfolioTimeline ? (
            <RebalanceTimelineCard
              history={rebalanceHistory}
              isLoading={isLoadingRebalanceHistory}
              errorMessage={rebalanceHistoryError}
              onRetry={() => {
                void loadRebalanceHistory({ useCache: false });
              }}
            />
          ) : null}
          <EquityCurveChart
            points={backtest?.equity_curve ?? []}
            benchmarkPoints={backtest?.benchmark_curve ?? []}
            benchmarkSymbol={backtest?.benchmark_symbol ?? "SPY"}
            baseIndex={backtest?.base_index ?? 100}
          />
          <PanelCard title="Model Diagnostics" description="IC / regime / SHAP payloads">
            {diagnosticsError ? (
              <p className="mb-2 body-xs-medium text-amber-300">{diagnosticsError}</p>
            ) : null}
            <pre className="max-h-56 overflow-auto rounded-sm border border-theme-outline bg-theme-secondary p-2 text-[11px] text-theme-muted">
              {JSON.stringify(
                {
                  model_ic_points: modelIcPayload?.points?.length ?? 0,
                  model_regimes: Object.keys(modelRegimePayload?.regimes ?? {}).length,
                  model_shap_status: modelShapPayload?.status ?? "not_loaded",
                  model_shap_summary_points: modelShapPayload?.summary_points?.length ?? 0,
                },
                null,
                2,
              )}
            </pre>
          </PanelCard>
          <ExplainabilityCard summary={summary} />
        </div>
      </div>
    </div>
  );
}

export const Route = createFileRoute("/quant")({
  component: QuantPage,
});
