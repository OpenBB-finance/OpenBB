import { useCallback } from "react";
import type { Dispatch, SetStateAction } from "react";
import {
  createSignals,
  fetchArtifactSummary,
  fetchRunStatus,
  invalidateQuantCaches,
  startTrain,
} from "../lib/quantApi";
import type {
  ArtifactSummaryPayload,
  BacktestResponsePayload,
  ModelConfigInput,
  ModelName,
  RankerConfigInput,
  RebalanceHistoryItem,
  RunStatusPayload,
  SignalsResponsePayload,
  TrainRequestPayload,
  WalkForwardConfigInput,
  PortfolioCurrentPayload,
  WorkflowRunStatus,
  WorkflowArtifactsReadyPayload,
} from "../types/quant";

type BackendConnection = { connected: boolean; baseUrl: string } | null;
type RunStreamState =
  | "idle"
  | "connecting"
  | "ready"
  | "streaming"
  | "fallback"
  | "done"
  | "timeout"
  | "error";

type SessionPatch = {
  run_id?: string;
  model_name?: ModelName;
  run_status?: WorkflowRunStatus;
  run_stage?: string;
  run_progress?: number;
  updated_at?: string;
  data_timestamp?: string | null;
  artifacts_ready?: Partial<WorkflowArtifactsReadyPayload>;
};

export interface TrainingPresetConfig {
  featureLags: number[];
  thetaGrid: number[];
  rankerConfig: RankerConfigInput;
  quickMode: boolean;
  featurePruning: boolean;
  walkForwardCompact: boolean;
}

interface UseQuantTrainingOptions {
  backend: BackendConnection;
  selectedModel: ModelName;
  dateStart: string;
  dateEnd: string;
  modelConfig: ModelConfigInput;
  walkForwardConfig: WalkForwardConfigInput;
  dataProvider: string;
  includeFundamentals: boolean;
  fundamentalProvider: string;
  includeSentiment: boolean;
  speedPresetId: string;
  speedPresetConfig: TrainingPresetConfig;
  parsedSymbols: string[];
  selectedUniverseSet: string;
  resolvedUniverseId: string;
  universeResolveStatus: "idle" | "loading" | "ok" | "error";
  universeResolveMessage: string | null;
  universeMeetsMinimum: boolean;
  runId: string | null;
  topK: number;
  scoreThreshold: number;
  balancedLongShort: boolean;
  patchSession: (patch: SessionPatch) => void;
  setRunId: (runId: string) => void;
  setRunIdInput: Dispatch<SetStateAction<string>>;
  markArtifactReady: (
    artifact: keyof WorkflowArtifactsReadyPayload,
    ready?: boolean,
  ) => void;
  setIsSubmittingTrain: Dispatch<SetStateAction<boolean>>;
  setRunStatus: Dispatch<SetStateAction<RunStatusPayload | null>>;
  setRunStreamState: Dispatch<SetStateAction<RunStreamState>>;
  setSignals: Dispatch<SetStateAction<SignalsResponsePayload | null>>;
  setBacktest: Dispatch<SetStateAction<BacktestResponsePayload | null>>;
  setRebalanceHistory: Dispatch<SetStateAction<RebalanceHistoryItem[]>>;
  setRebalanceHistoryError: Dispatch<SetStateAction<string | null>>;
  setSummary: Dispatch<SetStateAction<ArtifactSummaryPayload | null>>;
  setPortfolioCurrent: Dispatch<SetStateAction<PortfolioCurrentPayload | null>>;
  setPortfolioError: Dispatch<SetStateAction<string | null>>;
  setActiveTrainingRunId: Dispatch<SetStateAction<string | null>>;
  setErrorMessage: Dispatch<SetStateAction<string | null>>;
  setIsSubmittingSignals: Dispatch<SetStateAction<boolean>>;
}

export function useQuantTraining({
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
  speedPresetId,
  speedPresetConfig,
  parsedSymbols,
  selectedUniverseSet,
  resolvedUniverseId,
  universeResolveStatus,
  universeResolveMessage,
  universeMeetsMinimum,
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
}: UseQuantTrainingOptions) {
  const handleTrain = useCallback(async () => {
    if (!backend?.connected) {
      setErrorMessage("OpenBB API is not connected.");
      return;
    }
    if (selectedUniverseSet !== "default") {
      if (universeResolveStatus === "loading") {
        setErrorMessage(
          "Universe set is still resolving. Retry after resolution completes.",
        );
        return;
      }
      if (universeResolveStatus !== "ok" || universeMeetsMinimum === false) {
        setErrorMessage(
          universeResolveMessage ??
            "Selected universe set is unavailable or undersized. Run refresh_universes and retry.",
        );
        return;
      }
    }

    setIsSubmittingTrain(true);
    setErrorMessage(null);
    setRunStatus(null);
    setRunStreamState("idle");
    setSignals(null);
    setBacktest(null);
    setRebalanceHistory([]);
    setRebalanceHistoryError(null);
    setSummary(null);
    setPortfolioCurrent(null);
    setPortfolioError(null);
    setActiveTrainingRunId(null);

    try {
      const trainPayloadBase: Omit<TrainRequestPayload, "symbols" | "universe_id"> =
        {
          date_range: { start: dateStart, end: dateEnd },
          horizon_days: 1,
          target_mode: "next_open_to_close",
          close_to_next_open_horizon_policy: "fixed_1",
          include_macro_features: true,
          macro_feature_subset: ["z_252", "yoy", "mom_3", "slope"],
          provider: dataProvider,
          fundamental_provider: fundamentalProvider || undefined,
          model_config: modelConfig,
          feature_config: {
            lags: speedPresetConfig.featureLags,
            vol_windows: [5, 20],
            momentum_windows: [5, 20],
            include_rsi: true,
            include_macd: speedPresetId !== "turbo",
            include_bollinger: false,
            include_atr: false,
            include_adx: false,
            include_obv: false,
            include_fundamentals: includeFundamentals,
            include_sentiment: includeSentiment,
            include_regime_features: true,
          },
          training_mode: "dual_compare",
          model_set: ["xgb_lstm", "lgbm_ranker"],
          walk_forward_config: walkForwardConfig,
          ranker_config: speedPresetConfig.rankerConfig,
          signal_config: {
            theta_grid: speedPresetConfig.thetaGrid,
            selection_metric: "val_sharpe",
          },
          portfolio_mode: "long_only",
          mu_mapping: "quantile_mean_return",
          quick_mode: speedPresetConfig.quickMode,
          model_choice: "dual",
          early_stopping: true,
          feature_pruning: speedPresetConfig.featurePruning,
          walk_forward_compact: speedPresetConfig.walkForwardCompact,
          enable_hpo: speedPresetId === "thorough",
          hpo_n_trials: speedPresetId === "thorough" ? 25 : undefined,
          hpo_config: {
            enabled: speedPresetId === "thorough",
            n_trials: 25,
            timeout_sec: 1800,
            objective_metric: "val_ic",
            random_state: 42,
          },
        };
      const trainPayload: TrainRequestPayload =
        selectedUniverseSet === "default"
          ? { ...trainPayloadBase, symbols: parsedSymbols }
          : { ...trainPayloadBase, universe_id: resolvedUniverseId };
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
      setRunStreamState("connecting");
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
        setRunStreamState("connecting");
      } else if (latest.status === "completed" || latest.status === "failed") {
        setActiveTrainingRunId(null);
        setRunStreamState("done");
      }
      setRunIdInput(response.run_id);
      setRunId(response.run_id);
      invalidateQuantCaches(backend.baseUrl, response.run_id, selectedModel);
    } catch (error) {
      setRunStreamState("error");
      setErrorMessage(
        error instanceof Error ? error.message : "Failed to start training.",
      );
    } finally {
      setIsSubmittingTrain(false);
    }
  }, [
    backend,
    dateEnd,
    dateStart,
    dataProvider,
    fundamentalProvider,
    includeFundamentals,
    includeSentiment,
    modelConfig,
    parsedSymbols,
    patchSession,
    resolvedUniverseId,
    selectedModel,
    selectedUniverseSet,
    setActiveTrainingRunId,
    setBacktest,
    setErrorMessage,
    setIsSubmittingTrain,
    setPortfolioCurrent,
    setPortfolioError,
    setRebalanceHistory,
    setRebalanceHistoryError,
    setRunId,
    setRunIdInput,
    setRunStatus,
    setRunStreamState,
    setSignals,
    setSummary,
    speedPresetConfig.featureLags,
    speedPresetConfig.featurePruning,
    speedPresetConfig.quickMode,
    speedPresetConfig.rankerConfig,
    speedPresetConfig.thetaGrid,
    speedPresetConfig.walkForwardCompact,
    speedPresetId,
    universeMeetsMinimum,
    universeResolveMessage,
    universeResolveStatus,
    walkForwardConfig,
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
        balanced_long_short: balancedLongShort,
      });
      setSignals(response);
      markArtifactReady("signals", true);
      markArtifactReady("predictions", true);
      patchSession({
        data_timestamp: response.as_of_date,
      });
      invalidateQuantCaches(backend.baseUrl, runId, selectedModel);

      const latestSummary = await fetchArtifactSummary(
        backend.baseUrl,
        runId,
        selectedModel,
      );
      setSummary(latestSummary);
    } catch (error) {
      setErrorMessage(
        error instanceof Error ? error.message : "Failed to generate signals.",
      );
    } finally {
      setIsSubmittingSignals(false);
    }
  }, [
    backend,
    balancedLongShort,
    markArtifactReady,
    patchSession,
    runId,
    scoreThreshold,
    selectedModel,
    setErrorMessage,
    setIsSubmittingSignals,
    setSignals,
    setSummary,
    topK,
  ]);

  return {
    handleTrain,
    handleSignals,
  };
}
