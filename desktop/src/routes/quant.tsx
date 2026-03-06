import { createFileRoute, useRouter } from "@tanstack/react-router";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { QuantControlsColumn } from "../components/quant/QuantControlsColumn";
import { QuantPageHeader } from "../components/quant/QuantPageHeader";
import { QuantResultsColumn } from "../components/quant/QuantResultsColumn";
import {
  DEFAULT_PORTFOLIO_POLICY,
  PROFILE_LIST,
  SPEED_PRESETS,
  defaultModelConfig,
  fiveYearsAgoIso,
  formatSymbolsForTextarea,
  parseSymbolsText,
  profileLabel,
  symbolsByProfile,
  toApiUniverseId,
  todayIso,
  toBacktestErrorMessage,
} from "../lib/quantConfig";
import type {
  RunStreamState,
  SpeedPresetId,
  UniverseProfileId,
  UniverseSetId,
} from "../lib/quantConfig";
import { useQuantSession } from "../contexts/QuantSessionContext";
import { useQuantBacktest } from "../hooks/useQuantBacktest";
import { useQuantBackendRuntime } from "../hooks/useQuantBackendRuntime";
import { useQuantDiagnostics } from "../hooks/useQuantDiagnostics";
import { useQuantPortfolio } from "../hooks/useQuantPortfolio";
import { useQuantRunLoader } from "../hooks/useQuantRunLoader";
import { useQuantSessionSync } from "../hooks/useQuantSessionSync";
import { useQuantRunStream } from "../hooks/useQuantRunStream";
import { useQuantTraining } from "../hooks/useQuantTraining";
import { useQuantUniverseResolve } from "../hooks/useQuantUniverseResolve";
import type {
  ArtifactSummaryPayload,
  AlertsPayload,
  AlphaMappingMode,
  BacktestResponsePayload,
  CovarianceMethod,
  MVOptimizerEngine,
  ModelICPayload,
  ModelName,
  ModelPerformancePayload,
  ModelConfigInput,
  ModelRegimePayload,
  ModelShapPayload,
  WalkForwardConfigInput,
  PortfolioPolicyPayload,
  PortfolioExposurePayload,
  PortfolioRiskPayload,
  RegimeCurrentPayload,
  RebalanceHistoryItem,
  PortfolioCurrentPayload,
  RunStatusPayload,
  SignalsResponsePayload,
  UniverseResponse,
  WalkForwardBacktestStatusPayload,
} from "../types/quant";

const TRAINABLE_MODELS: ModelName[] = ["lgbm_ranker", "xgb_lstm"];

function hasModelArtifact(
  availableArtifacts: string[] | undefined,
  modelName: ModelName,
  kind: "predictions" | "signals" | "backtest",
): boolean {
  if (!availableArtifacts || availableArtifacts.length === 0) {
    return false;
  }
  const fallbackName =
    kind === "predictions"
      ? "predictions.parquet"
      : kind === "signals"
        ? "signals.parquet"
        : "backtest.json";
  const modelNamePrefix = `${kind}_${modelName}`;
  return availableArtifacts.some((name) => {
    const normalized = String(name).toLowerCase();
    return (
      normalized.startsWith(modelNamePrefix) ||
      (modelName === "lgbm_ranker" && normalized === fallbackName)
    );
  });
}

export default function QuantPage() {
  const router = useRouter();
  const { session, setRunId, setModelName, patchSession, markArtifactReady } = useQuantSession();
  const [selectedUniverseSet, setSelectedUniverseSet] = useState<UniverseSetId>("default");
  const [selectedProfile, setSelectedProfile] = useState<UniverseProfileId>("all");
  const [symbolsInput, setSymbolsInput] = useState("");
  const [dateStart, setDateStart] = useState(fiveYearsAgoIso);
  const [dateEnd, setDateEnd] = useState(todayIso);
  const [modelConfig, setModelConfig] = useState<ModelConfigInput>(defaultModelConfig);
  const [walkForwardConfig, setWalkForwardConfig] = useState<WalkForwardConfigInput>(SPEED_PRESETS.standard.walkForward);
  const [dataProvider, setDataProvider] = useState("yfinance");
  const [includeFundamentals, setIncludeFundamentals] = useState(false);
  const [fundamentalProvider, setFundamentalProvider] = useState("");
  const [includeSentiment, setIncludeSentiment] = useState(false);
  const [selectedModel, setSelectedModel] = useState<ModelName>(() => session.model_name);
  const [speedPreset, setSpeedPreset] = useState<SpeedPresetId>("standard");
  const [showAdvancedConfig, setShowAdvancedConfig] = useState(false);
  const [runStatus, setRunStatus] = useState<RunStatusPayload | null>(null);
  const [runStreamState, setRunStreamState] = useState<RunStreamState>("idle");
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
  const [modelPerformancePayload, setModelPerformancePayload] = useState<ModelPerformancePayload | null>(null);
  const [portfolioExposurePayload, setPortfolioExposurePayload] = useState<PortfolioExposurePayload | null>(null);
  const [portfolioRiskPayload, setPortfolioRiskPayload] = useState<PortfolioRiskPayload | null>(null);
  const [regimeCurrentPayload, setRegimeCurrentPayload] = useState<RegimeCurrentPayload | null>(null);
  const [currentAlertsPayload, setCurrentAlertsPayload] = useState<AlertsPayload | null>(null);
  const [portfolioPolicy, setPortfolioPolicy] = useState<PortfolioPolicyPayload>(DEFAULT_PORTFOLIO_POLICY);
  const [walkforwardStatus, setWalkforwardStatus] = useState<WalkForwardBacktestStatusPayload | null>(null);
  const [diagnosticsError, setDiagnosticsError] = useState<string | null>(null);
  const [topK, setTopK] = useState(20);
  const [scoreThreshold, setScoreThreshold] = useState(0.5);
  const [balancedLongShort, setBalancedLongShort] = useState(false);
  const [backtestAdvanced, setBacktestAdvanced] = useState({
    mv_optimizer_engine: "legacy_slsqp" as MVOptimizerEngine,
    optimizer_strict: false,
    cov_method: "ewma_shrink" as CovarianceMethod,
    cov_pca_components: 10,
    cov_pca_idio_floor: 1e-6,
    alpha_mapping_mode: "legacy_score" as AlphaMappingMode,
    ic_lookback_days: 252,
    ic_ewma_halflife: 63,
    ic_clip_min: -0.2,
    ic_clip_max: 0.2,
    ic_fallback: 0.03,
    alpha_ema_halflife_days: 0,
    trigger_rebalance_enabled: false,
    trigger_threshold_bps: 10,
    trigger_cost_multiplier: 1.0,
  });
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
  const macroHintAppliedRef = useRef<string | null>(null);
  const isUniverseSetMode = selectedUniverseSet !== "default";
  const speedPresetOptions = useMemo(() => Object.values(SPEED_PRESETS), []);
  const updatePortfolioPolicy = useCallback((patch: Partial<PortfolioPolicyPayload>) => {
    setPortfolioPolicy((previous) => ({ ...previous, ...patch }));
  }, []);
  const updateModelConfig = useCallback((patch: Partial<ModelConfigInput>) => {
    setModelConfig((previous) => ({ ...previous, ...patch }));
  }, []);
  const applySpeedPreset = useCallback(
    (presetId: string) => {
      const preset = SPEED_PRESETS[presetId as SpeedPresetId];
      if (!preset) {
        return;
      }
      setSpeedPreset(preset.id);
      setModelConfig(preset.modelConfig);
      setWalkForwardConfig(preset.walkForward);
      const d = new Date();
      d.setFullYear(d.getFullYear() - preset.datePeriodYears);
      setDateStart(d.toISOString().slice(0, 10));
    },
    [],
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

  const runId = (runStatus?.run_id ?? "").trim() || null;
  const {
    isResolvingBackend,
    backend,
    quantActivation,
    universe,
    universeSetOptions,
    recentRuns,
    promotedModel,
    dashboardHealth,
    isLoadingHealth,
    healthError,
    resolveBackendAndUniverse,
  } = useQuantBackendRuntime({
    selectedModel,
    runId,
    runStatus,
    sessionRunId: session.run_id,
    setPortfolioPolicy,
    setSelectedProfile,
    setSymbolsInput,
    setRunStreamState,
    setErrorMessage,
  });
  const selectedUniverseOption = useMemo(
    () => universeSetOptions.find((option) => option.id === selectedUniverseSet) ?? null,
    [selectedUniverseSet, universeSetOptions],
  );
  useQuantSessionSync({
    sessionRunId: session.run_id,
    sessionModelName: session.model_name,
    runId,
    selectedModel,
    setSelectedModel,
    setRunIdInput,
    setRunId,
    setModelName,
    patchSession,
  });

  useEffect(() => {
    if (TRAINABLE_MODELS.includes(selectedModel)) {
      return;
    }
    setSelectedModel("lgbm_ranker");
    setModelName("lgbm_ranker");
  }, [selectedModel, setModelName]);

  useEffect(() => {
    const search = new URLSearchParams(window.location.search);
    const macroHint = search.get("macro_hint");
    if (macroHint !== "aggressive" && macroHint !== "defensive") {
      return;
    }
    if (macroHintAppliedRef.current === macroHint) {
      return;
    }
    if (!universe || selectedUniverseSet !== "default") {
      return;
    }
    applyProfile(macroHint, universe);
    macroHintAppliedRef.current = macroHint;
  }, [applyProfile, selectedUniverseSet, universe]);

  const { loadExistingRun } = useQuantRunLoader({
    backend,
    runStatus,
    runIdInput,
    selectedModel,
    sessionRunId: session.run_id,
    setRunId,
    setRunIdInput,
    patchSession,
    setRunStatus,
    setActiveTrainingRunId,
    setRunStreamState,
    setSignals,
    setBacktest,
    setRebalanceHistory,
    setRebalanceHistoryError,
    setSummary,
    setPortfolioCurrent,
    setErrorMessage,
    setPortfolioError,
  });

  useQuantRunStream({
    backend,
    runId,
    runStatus,
    selectedModel,
    patchSession,
    markArtifactReady,
    setRunStatus,
    setRunStreamState,
    setActiveTrainingRunId,
    setSummary,
    setErrorMessage,
  });

  const parsedSymbols = useMemo(() => {
    const explicit = parseSymbolsText(symbolsInput);

    if (explicit.length > 0) {
      return explicit;
    }

    return universe?.assets.map((asset) => asset.symbol) ?? [];
  }, [symbolsInput, universe]);

  const { universeResolveState, isTrainBlockedByUniverse } = useQuantUniverseResolve({
    backend,
    isUniverseSetMode,
    selectedUniverseSet,
    minimumRequired: selectedUniverseOption?.minimumRequired ?? 0,
  });

  const canUseApi = backend?.connected === true;
  const canGenerateSignals = canUseApi && runStatus?.status === "completed";
  const hasSelectedModelPredictions = hasModelArtifact(
    summary?.available_artifacts,
    selectedModel,
    "predictions",
  );
  const canRunBacktest =
    canGenerateSignals &&
    (session.artifacts_ready.predictions || hasSelectedModelPredictions);
  const dashboardLink = runId
    ? `/dashboard?run_id=${encodeURIComponent(runId)}&model=${encodeURIComponent(selectedModel)}&mode=backtest&focus=portfolio`
    : "/dashboard";

  const { loadPortfolioCurrent, loadRebalanceHistory } = useQuantPortfolio({
    backend,
    runId,
    selectedModel,
    markArtifactReady,
    patchSession,
    setPortfolioCurrent,
    setPortfolioError,
    setIsLoadingPortfolio,
    setRebalanceHistory,
    setRebalanceHistoryError,
    setIsLoadingRebalanceHistory,
    setSummary,
  });

  useQuantDiagnostics({
    backend,
    runId,
    runStatus,
    selectedModel,
    setModelIcPayload,
    setModelRegimePayload,
    setModelShapPayload,
    setModelPerformancePayload,
    setPortfolioExposurePayload,
    setPortfolioRiskPayload,
    setRegimeCurrentPayload,
    setCurrentAlertsPayload,
    setDiagnosticsError,
  });

  const activeSpeedPreset = SPEED_PRESETS[speedPreset];

  const { handleTrain, handleSignals } = useQuantTraining({
    backend,
    selectedModel,
    dateStart,
    dateEnd,
    modelConfig,
    walkForwardConfig,
    dataProvider,
    includeFundamentals,
    fundamentalProvider,
    includeSentiment,
    speedPresetId: speedPreset,
    speedPresetConfig: activeSpeedPreset,
    parsedSymbols,
    selectedUniverseSet,
    resolvedUniverseId: toApiUniverseId(selectedUniverseSet),
    universeResolveStatus: universeResolveState.status,
    universeResolveMessage: universeResolveState.message,
    universeMeetsMinimum: universeResolveState.meetsMinimum,
    runId,
    topK,
    scoreThreshold,
    balancedLongShort,
    patchSession,
    setRunId,
    setRunIdInput,
    markArtifactReady,
    setIsSubmittingTrain,
    setRunStatus,
    setRunStreamState,
    setSignals,
    setBacktest,
    setRebalanceHistory,
    setRebalanceHistoryError,
    setSummary,
    setPortfolioCurrent,
    setPortfolioError,
    setActiveTrainingRunId,
    setErrorMessage,
    setIsSubmittingSignals,
  });

  const {
    handleBacktest,
    handleWalkforwardBacktest,
    walkforwardElapsed,
  } = useQuantBacktest({
    backend,
    runId,
    selectedModel,
    dateStart,
    dateEnd,
    summary,
    portfolioPolicy,
    backtestAdvanced,
    sessionHasPredictions: session.artifacts_ready.predictions,
    modelHasPredictions: hasSelectedModelPredictions,
    markArtifactReady,
    patchSession,
    setIsSubmittingBacktest,
    setBacktest,
    setRebalanceHistory,
    setRebalanceHistoryError,
    setSummary,
    setErrorMessage,
    loadPortfolioCurrent,
    loadRebalanceHistory,
    setWalkforwardStatus,
    setIsSubmittingWalkforward,
    toBacktestErrorMessage,
  });

  return (
    <div className="h-full min-h-0 overflow-auto py-4">
      <QuantPageHeader
        parsedSymbolsCount={parsedSymbols.length}
        isUniverseSetMode={isUniverseSetMode}
        runStatus={runStatus?.status ?? null}
        signalsCount={signals?.signals?.length ?? 0}
        backtestPointsCount={backtest?.equity_curve?.length ?? 0}
        errorMessage={errorMessage}
        quantActivation={quantActivation}
      />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[360px_minmax(0,1fr)]">
        <QuantControlsColumn
          universeSection={{
            universeSetOptions,
            selectedUniverseSet,
            onUniverseSetChange: (value) => {
              setSelectedUniverseSet(value as UniverseSetId);
              setErrorMessage(null);
            },
            isUniverseSetMode,
            universeResolveState,
            profiles: PROFILE_LIST,
            selectedProfile,
            profileLabel: profileLabel(selectedProfile),
            onProfileSelect: (profileId) =>
              applyProfile(profileId as Exclude<UniverseProfileId, "custom">, universe),
            universe,
            symbolsInput,
            onSymbolsInputChange: (value) => {
              setSelectedProfile("custom");
              setSymbolsInput(value);
            },
            onFormatSymbols: () => {
              setSelectedProfile("custom");
              setSymbolsInput(formatSymbolsForTextarea(parsedSymbols));
            },
            onClearSymbols: () => {
              setSelectedProfile("custom");
              setSymbolsInput("");
            },
            parsedSymbolsCount: parsedSymbols.length,
            dateStart,
            dateEnd,
            onDateStartChange: setDateStart,
            onDateEndChange: setDateEnd,
          }}
          trainingSection={{
            runIdInput,
            recentRuns,
            canUseApi,
            onRunIdInputChange: setRunIdInput,
            onLoadRun: () => {
              void loadExistingRun();
            },
            speedPreset,
            speedPresetOptions,
            onApplySpeedPreset: applySpeedPreset,
            selectedModel,
            onSelectedModelChange: (next) => {
              setSelectedModel(next);
              setModelName(next);
            },
            dataProvider,
            onDataProviderChange: setDataProvider,
            includeFundamentals,
            onIncludeFundamentalsChange: setIncludeFundamentals,
            fundamentalProvider,
            onFundamentalProviderChange: setFundamentalProvider,
            includeSentiment,
            onIncludeSentimentChange: setIncludeSentiment,
            topK,
            onTopKChange: setTopK,
            scoreThreshold,
            onScoreThresholdChange: setScoreThreshold,
            balancedLongShort,
            onBalancedLongShortChange: setBalancedLongShort,
            showAdvancedConfig,
            onToggleAdvancedConfig: () => setShowAdvancedConfig((prev) => !prev),
            modelConfig,
            onModelConfigChange: updateModelConfig,
            walkForwardConfig,
            onWalkForwardConfigChange: (patch) =>
              setWalkForwardConfig((previous) => ({ ...previous, ...patch })),
            backtestAdvanced,
            onBacktestAdvancedChange: (patch) =>
              setBacktestAdvanced((previous) => ({ ...previous, ...patch })),
            isSubmittingTrain,
            isTrainBlockedByUniverse,
            onTrain: handleTrain,
            canGenerateSignals,
            isSubmittingSignals,
            onSignals: handleSignals,
            canRunBacktest,
            isSubmittingBacktest,
            onBacktest: handleBacktest,
            isSubmittingWalkforward,
            walkforwardElapsed,
            onWalkforwardBacktest: handleWalkforwardBacktest,
          }}
          policySection={{
            policy: portfolioPolicy,
            backtest,
            promotedModel,
            walkforwardStatus,
            showPortfolioTimeline,
            onPolicyChange: updatePortfolioPolicy,
            onShowPortfolioTimelineChange: setShowPortfolioTimeline,
          }}
        />

        <QuantResultsColumn
          connection={{
            resolution: backend,
            isLoading: isResolvingBackend,
            health: dashboardHealth,
            isHealthLoading: isLoadingHealth,
            healthError,
            onRetry: () => void resolveBackendAndUniverse(),
            onGoBackends: () => router.navigate({ to: "/backends" }),
          }}
          workflowSync={{
            runId,
            selectedModel,
            dashboardLink,
            sessionRunId: session.run_id,
            sessionModelName: session.model_name,
            sessionDataTimestamp: session.data_timestamp,
            artifactsReady: session.artifacts_ready,
          }}
          runStatus={{
            run: runStatus,
            isLiveRun: runStatus?.run_id === activeTrainingRunId,
            streamState: runStreamState,
          }}
          signals={{
            asOfDate: signals?.as_of_date,
            signals: signals?.signals ?? [],
          }}
          metrics={{
            metrics: backtest?.metrics ?? null,
          }}
          monthlyReturns={{
            points: backtest?.monthly_returns ?? [],
          }}
          portfolioRationale={{
            portfolio: portfolioCurrent,
            isLoading: isLoadingPortfolio,
            errorMessage: portfolioError,
            onRetry: () => {
              void loadPortfolioCurrent({ suppressNotReady: false, useCache: false });
            },
          }}
          showPortfolioTimeline={showPortfolioTimeline}
          rebalanceTimeline={{
            history: rebalanceHistory,
            isLoading: isLoadingRebalanceHistory,
            errorMessage: rebalanceHistoryError,
            onRetry: () => {
              void loadRebalanceHistory({ useCache: false });
            },
          }}
          equityCurve={{
            points: backtest?.equity_curve ?? [],
            benchmarkPoints: backtest?.benchmark_curve ?? [],
            benchmarkSymbol: backtest?.benchmark_symbol ?? "SPY",
            baseIndex: backtest?.base_index ?? 100,
          }}
          diagnostics={{
            diagnosticsError,
            modelIcPayload,
            modelRegimePayload,
            modelShapPayload,
            modelPerformancePayload,
            currentAlertsPayload,
            portfolioExposurePayload,
            portfolioRiskPayload,
            regimeCurrentPayload,
          }}
          explainability={{
            summary,
          }}
        />
      </div>
    </div>
  );
}

export const Route = createFileRoute("/quant")({ component: QuantPage });

