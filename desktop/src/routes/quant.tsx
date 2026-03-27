import { createFileRoute, useRouter } from "@tanstack/react-router";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { PanelCard } from "../components/quant/PanelCard";
import { QuantControlsColumn } from "../components/quant/QuantControlsColumn";
import { QuantPageHeader } from "../components/quant/QuantPageHeader";
import { QuantResultsColumn } from "../components/quant/QuantResultsColumn";
import {
  StrategyLabStepper,
  type StrategyLabStep,
  type StrategyLabStepId,
} from "../components/quant/StrategyLabStepper";
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
import { fetchRunsCompare } from "../lib/quantApi";
import {
  clearMacroStudyHandoff,
  readMacroStudyHandoff,
} from "../lib/macroStudyHandoff";
import { buildSymbolLabHref } from "../lib/symbolLabNavigation";
import { writeRunHandoff } from "../lib/runHandoff";
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
  RunComparePayload,
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
  const autoRecoveredRunRef = useRef<string | null>(null);
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
  const [activeLabStep, setActiveLabStep] = useState<StrategyLabStepId>("setup");
  const [macroStudyHandoff, setMacroStudyHandoff] = useState(() => readMacroStudyHandoff());
  const [runCompare, setRunCompare] = useState<RunComparePayload | null>(null);
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

  useEffect(() => {
    if (!backend?.connected || recentRuns.length === 0) {
      return;
    }
    const currentRunId = runIdInput.trim() || session.run_id.trim();
    const currentStatus = String(runStatus?.status ?? "").toLowerCase();
    const shouldRecover =
      !currentRunId || currentStatus === "failed" || currentStatus === "error" || currentStatus === "cancelled";

    if (!shouldRecover) {
      return;
    }

    const fallbackRun =
      recentRuns.find((run) => run.actionable_backtest) ??
      recentRuns.find((run) => String(run.status).toLowerCase() === "completed");

    if (!fallbackRun || fallbackRun.run_id === currentRunId || autoRecoveredRunRef.current === fallbackRun.run_id) {
      return;
    }

    autoRecoveredRunRef.current = fallbackRun.run_id;
    setRunIdInput(fallbackRun.run_id);
    void loadExistingRun(fallbackRun.run_id);
  }, [backend?.connected, loadExistingRun, recentRuns, runIdInput, runStatus?.status, session.run_id]);

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
  const executionHandoffHref =
    runIdInput.trim()
      ? `/execution?runId=${encodeURIComponent(runIdInput.trim())}&modelName=${encodeURIComponent(selectedModel)}`
      : "/execution";
  const strategyWorkflowSteps = useMemo<StrategyLabStep[]>(
    () => [
      {
        id: "setup",
        label: "Setup",
        hint: "Universe, dates, and runtime defaults.",
        complete: parsedSymbols.length > 0 || isUniverseSetMode,
      },
      {
        id: "features",
        label: "Features",
        hint: "Macro study handoff and feature lineage.",
        complete: Boolean(macroStudyHandoff?.featureArtifactPath),
      },
      {
        id: "train",
        label: "Train",
        hint: "Fit the model and inspect run status.",
        complete: runStatus?.status === "completed",
      },
      {
        id: "backtest",
        label: "Backtest",
        hint: "Generate signals and test portfolio policy.",
        complete: (backtest?.equity_curve?.length ?? 0) > 0,
      },
      {
        id: "compare",
        label: "Compare",
        hint: "Review diagnostics and recent runs.",
        complete: recentRuns.length > 1,
      },
      {
        id: "promote",
        label: "Promote",
        hint: "Confirm artifacts and runtime handoff.",
        complete: Boolean(promotedModel?.ready),
      },
    ],
    [
      backtest?.equity_curve?.length,
      isUniverseSetMode,
      macroStudyHandoff?.featureArtifactPath,
      parsedSymbols.length,
      promotedModel?.ready,
      recentRuns.length,
      runStatus?.status,
    ],
  );
  const workflowNarrative = useMemo(() => {
    switch (activeLabStep) {
      case "setup":
        return {
          title: "Define the experiment scope",
          body:
            "Pick the universe, time window, and default runtime assumptions before changing model parameters. This keeps later diagnostics comparable.",
        };
      case "features":
        return {
          title: "Lock feature lineage",
          body:
            "Use Macro Lab exports as an explicit feature handoff so the run records where the macro thesis came from and which as-of policy was used.",
        };
      case "train":
        return {
          title: "Run the model",
          body:
            "Training should happen only after the universe and feature lineage are stable. Watch the run status and logs before generating signals.",
        };
      case "backtest":
        return {
          title: "Validate portfolio construction",
          body:
            "Backtest against the current portfolio policy, check turnover and max weight constraints, and only then move to execution review.",
        };
      case "compare":
        return {
          title: "Compare runs and diagnostics",
          body:
            "Use diagnostics, regime panels, and recent-run metadata to compare experimental changes rather than reading a single metric in isolation.",
        };
      case "promote":
        return {
          title: "Prepare handoff to execution",
          body:
            "Promotion means the run is ready to become the execution candidate. Confirm artifacts, policy fit, and runtime pointers before leaving Strategy Lab.",
        };
      default:
        return {
          title: "Strategy workflow",
          body: "Move from setup to promotion in a fixed sequence so research, features, and execution artifacts stay linked.",
        };
    }
  }, [activeLabStep]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const hintedRunId = params.get("runId");
    if (!hintedRunId || runIdInput.trim()) {
      return;
    }
    setRunIdInput(hintedRunId);
  }, [runIdInput]);

  useEffect(() => {
    if (!backend?.connected || recentRuns.length === 0) {
      setRunCompare(null);
      return;
    }
    const runIds = recentRuns.slice(0, 5).map((item) => item.run_id);
    const loadCompare = async () => {
      try {
        setRunCompare(await fetchRunsCompare(backend.baseUrl, { runIds, limit: 5 }));
      } catch {
        setRunCompare(null);
      }
    };
    void loadCompare();
  }, [backend?.baseUrl, backend?.connected, recentRuns]);

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

      <StrategyLabStepper
        steps={strategyWorkflowSteps}
        activeStep={activeLabStep}
        onStepChange={setActiveLabStep}
      />

      <div className="mb-4 grid grid-cols-1 gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
        <PanelCard
          title={workflowNarrative.title}
          description="Stage-aware guidance so the lab behaves like a workflow, not a long parameter form."
        >
          <div className="space-y-3">
            <p className="body-sm-regular text-theme-muted">{workflowNarrative.body}</p>
            <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
              <div className="rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2">
                <div className="body-xxs-regular text-theme-muted">Current run</div>
                <div className="body-sm-medium text-theme-primary">{runIdInput.trim() || "Not selected"}</div>
              </div>
              <div className="rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2">
                <div className="body-xxs-regular text-theme-muted">Model</div>
                <div className="body-sm-medium text-theme-primary">{selectedModel}</div>
              </div>
              <div className="rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2">
                <div className="body-xxs-regular text-theme-muted">Recent runs</div>
                <div className="body-sm-medium text-theme-primary">{recentRuns.length}</div>
              </div>
            </div>
          </div>
        </PanelCard>

        <PanelCard
          title="Macro Feature Handoff"
          description="Latest study export available to Strategy Lab and execution review."
        >
          {macroStudyHandoff ? (
            <div className="space-y-3">
              <div>
                <div className="body-sm-medium text-theme-primary">{macroStudyHandoff.name}</div>
                <div className="body-xxs-regular text-theme-muted">
                  {macroStudyHandoff.studyId ?? "draft"} | {macroStudyHandoff.asOfPolicy}
                </div>
              </div>
              <p className="body-xs-regular text-theme-muted">
                {macroStudyHandoff.conclusionSummary || macroStudyHandoff.objective || "No conclusion summary saved."}
              </p>
              <div className="rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2">
                <div className="body-xxs-regular text-theme-muted">Feature artifact</div>
                <div className="body-xs-medium text-theme-primary break-all">
                  {macroStudyHandoff.featureArtifactPath ?? "Not exported yet"}
                </div>
              </div>
              <div className="flex flex-wrap gap-2">
                {macroStudyHandoff.linkedAssets.slice(0, 3).map((asset) => (
                  <a
                    key={asset}
                    className="rounded-full border border-theme-outline px-3 py-1 body-xs-medium text-theme-primary"
                    href={buildSymbolLabHref({
                      symbol: asset,
                      source: "macro",
                      studyId: macroStudyHandoff.studyId ?? undefined,
                    })}
                  >
                    {asset}
                  </a>
                ))}
              </div>
              <button
                type="button"
                className="rounded-sm border border-theme-outline px-3 py-2 body-xs-medium text-theme-primary"
                onClick={() => {
                  clearMacroStudyHandoff();
                  setMacroStudyHandoff(null);
                }}
              >
                Clear Handoff
              </button>
            </div>
          ) : (
            <p className="body-xs-regular text-theme-muted">
              Export feature lineage from Macro Lab to pin a macro study into this strategy workflow.
            </p>
          )}
        </PanelCard>
      </div>

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

      <div className="mt-4 grid grid-cols-1 gap-4 xl:grid-cols-2">
        <PanelCard
          title="Compare"
          description="Run-level comparison for the latest strategy candidates."
        >
          {runCompare?.items?.length ? (
            <div className="max-h-72 overflow-auto">
              <table className="w-full text-left">
                <thead className="sticky top-0 bg-theme-primary">
                  <tr className="body-xxs-medium text-theme-muted">
                    <th className="pb-2">Run</th>
                    <th className="pb-2">Model</th>
                    <th className="pb-2">Training Window</th>
                    <th className="pb-2">Feature Set</th>
                    <th className="pb-2">Promotion</th>
                  </tr>
                </thead>
                <tbody>
                  {runCompare.items.map((item) => (
                    <tr key={item.run_id} className="border-t border-theme-outline body-xs-regular">
                      <td className="py-2 pr-2 text-theme-primary">{item.run_id}</td>
                      <td className="py-2 pr-2 text-theme-primary">{item.model_name ?? "-"}</td>
                      <td className="py-2 pr-2 text-theme-primary">{item.training_window ?? "-"}</td>
                      <td className="py-2 pr-2 text-theme-primary">{item.feature_set_version ?? "-"}</td>
                      <td className="py-2 pr-2 text-theme-primary">{item.promotion_state ?? "-"}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <p className="body-xs-regular text-theme-muted">
              Compare requires at least two recent runs from the experiment registry.
            </p>
          )}
        </PanelCard>

        <PanelCard
          title="Promote"
          description="Pin the execution handoff to the active run, model, and linked studies."
        >
          <div className="space-y-3">
            <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
              <div className="rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2">
                <div className="body-xxs-regular text-theme-muted">Run</div>
                <div className="body-sm-medium text-theme-primary">{runIdInput.trim() || "Not selected"}</div>
              </div>
              <div className="rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2">
                <div className="body-xxs-regular text-theme-muted">Model</div>
                <div className="body-sm-medium text-theme-primary">{selectedModel}</div>
              </div>
            </div>
            <div className="rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2 body-xs-regular text-theme-muted">
              Promotion readiness: {promotedModel?.ready ? "ready" : "not ready"}
              {macroStudyHandoff?.studyId ? ` | linked study ${macroStudyHandoff.studyId}` : ""}
            </div>
            <a
              href={executionHandoffHref}
              className="inline-flex rounded-sm border border-theme-outline px-3 py-2 body-xs-medium text-theme-primary hover:text-theme-accent"
              onClick={() => {
                if (!runIdInput.trim()) {
                  return;
                }
                writeRunHandoff({
                  runId: runIdInput.trim(),
                  modelName: selectedModel,
                  source: "strategy",
                  studyIds: macroStudyHandoff?.studyId ? [macroStudyHandoff.studyId] : [],
                });
              }}
            >
              Send to Portfolio &amp; Execution
            </a>
          </div>
        </PanelCard>
      </div>
    </div>
  );
}

export const Route = createFileRoute("/quant")({ component: QuantPage });
