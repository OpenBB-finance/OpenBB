import { useCallback, useEffect } from "react";
import type { Dispatch, SetStateAction } from "react";
import { fetchArtifactSummary, fetchRunBacktest, fetchRunStatus } from "../lib/quantApi";
import type {
  ArtifactSummaryPayload,
  BacktestResponsePayload,
  ModelName,
  PortfolioCurrentPayload,
  RebalanceHistoryItem,
  RunStatusPayload,
  SignalsResponsePayload,
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
  run_status?: RunStatusPayload["status"];
  run_stage?: string;
  run_progress?: number;
  updated_at?: string;
  artifacts_ready?: {
    predictions?: boolean;
    signals?: boolean;
    backtest?: boolean;
    portfolio_current?: boolean;
  };
};

function hasArtifact(
  names: string[],
  model: ModelName,
  kind: "predictions" | "signals" | "backtest",
): boolean {
  const fallback =
    kind === "predictions"
      ? "predictions.parquet"
      : kind === "signals"
        ? "signals.parquet"
        : "backtest.json";
  const prefix = `${kind}_${model}`.toLowerCase();
  return names.some((name) => {
    const normalized = String(name).toLowerCase();
    return normalized.startsWith(prefix) || (model === "lgbm_ranker" && normalized === fallback);
  });
}

interface UseQuantRunLoaderOptions {
  backend: BackendConnection;
  runStatus: RunStatusPayload | null;
  runIdInput: string;
  selectedModel: ModelName;
  sessionRunId: string;
  setRunId: (runId: string) => void;
  setRunIdInput: Dispatch<SetStateAction<string>>;
  patchSession: (patch: SessionPatch) => void;
  setRunStatus: Dispatch<SetStateAction<RunStatusPayload | null>>;
  setActiveTrainingRunId: Dispatch<SetStateAction<string | null>>;
  setRunStreamState: Dispatch<SetStateAction<RunStreamState>>;
  setSignals: Dispatch<SetStateAction<SignalsResponsePayload | null>>;
  setBacktest: Dispatch<SetStateAction<BacktestResponsePayload | null>>;
  setRebalanceHistory: Dispatch<SetStateAction<RebalanceHistoryItem[]>>;
  setRebalanceHistoryError: Dispatch<SetStateAction<string | null>>;
  setSummary: Dispatch<SetStateAction<ArtifactSummaryPayload | null>>;
  setPortfolioCurrent: Dispatch<SetStateAction<PortfolioCurrentPayload | null>>;
  setErrorMessage: Dispatch<SetStateAction<string | null>>;
  setPortfolioError: Dispatch<SetStateAction<string | null>>;
}

export function useQuantRunLoader({
  backend,
  runStatus,
  runIdInput,
  selectedModel,
  sessionRunId,
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
}: UseQuantRunLoaderOptions) {
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
        let artifactSummary: ArtifactSummaryPayload | null = null;
        try {
          artifactSummary = await fetchArtifactSummary(
            backend.baseUrl,
            targetRunId,
            selectedModel,
          );
          setSummary(artifactSummary);
        } catch {
          artifactSummary = null;
          setSummary(null);
        }
        const availableArtifacts = artifactSummary?.available_artifacts ?? [];
        const predictionsReady = hasArtifact(
          availableArtifacts,
          selectedModel,
          "predictions",
        );
        const signalsReady = hasArtifact(availableArtifacts, selectedModel, "signals");
        const backtestReady = hasArtifact(
          availableArtifacts,
          selectedModel,
          "backtest",
        );
        if (backtestReady) {
          try {
            const backtestPayload = await fetchRunBacktest(
              backend.baseUrl,
              targetRunId,
              selectedModel,
            );
            setBacktest(backtestPayload);
            setRebalanceHistory(backtestPayload.rebalance_history_summary ?? []);
            setRebalanceHistoryError(null);
          } catch {
            setBacktest(null);
            setRebalanceHistory([]);
            setRebalanceHistoryError(null);
          }
        } else {
          setBacktest(null);
          setRebalanceHistory([]);
          setRebalanceHistoryError(null);
        }
        setRunStatus(latest);
        setActiveTrainingRunId(
          latest.status === "queued" || latest.status === "running" ? latest.run_id : null,
        );
        setRunStreamState(
          latest.status === "queued" || latest.status === "running" ? "connecting" : "idle",
        );
        setRunIdInput(targetRunId);
        setRunId(targetRunId);
        patchSession({
          run_id: targetRunId,
          model_name: selectedModel,
          run_status: latest.status,
          run_stage: latest.stage,
          run_progress: latest.progress,
          updated_at: latest.updated_at,
          artifacts_ready: {
            predictions: predictionsReady,
            signals: signalsReady,
            backtest: backtestReady,
            portfolio_current: backtestReady,
          },
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
        setRunStreamState("idle");
        setErrorMessage(error instanceof Error ? error.message : "Failed to load run by ID.");
      }
    },
    [
      backend,
      patchSession,
      runIdInput,
      selectedModel,
      setActiveTrainingRunId,
      setBacktest,
      setErrorMessage,
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
    ],
  );

  useEffect(() => {
    if (!backend?.connected || runStatus) {
      return;
    }
    const existingRunId = sessionRunId.trim();
    if (!existingRunId) {
      return;
    }
    setRunIdInput(existingRunId);
    void loadExistingRun(existingRunId);
  }, [backend, runStatus, loadExistingRun, sessionRunId, setRunIdInput]);

  return {
    loadExistingRun,
  };
}
