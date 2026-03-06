import { useCallback, useEffect } from "react";
import type { Dispatch, SetStateAction } from "react";
import {
  fetchArtifactSummary,
  fetchPortfolioCurrent,
  fetchRebalanceHistory,
} from "../lib/quantApi";
import type {
  ArtifactSummaryPayload,
  ModelName,
  PortfolioCurrentPayload,
  RebalanceHistoryItem,
  WorkflowArtifactsReadyPayload,
} from "../types/quant";

type BackendConnection = { connected: boolean; baseUrl: string } | null;
type SessionPatch = {
  data_timestamp?: string | null;
  artifacts_ready?: Partial<WorkflowArtifactsReadyPayload>;
};

interface UseQuantPortfolioOptions {
  backend: BackendConnection;
  runId: string | null;
  selectedModel: ModelName;
  markArtifactReady: (
    artifact: keyof WorkflowArtifactsReadyPayload,
    ready?: boolean,
  ) => void;
  patchSession: (patch: SessionPatch) => void;
  setPortfolioCurrent: Dispatch<SetStateAction<PortfolioCurrentPayload | null>>;
  setPortfolioError: Dispatch<SetStateAction<string | null>>;
  setIsLoadingPortfolio: Dispatch<SetStateAction<boolean>>;
  setRebalanceHistory: Dispatch<SetStateAction<RebalanceHistoryItem[]>>;
  setRebalanceHistoryError: Dispatch<SetStateAction<string | null>>;
  setIsLoadingRebalanceHistory: Dispatch<SetStateAction<boolean>>;
  setSummary: Dispatch<SetStateAction<ArtifactSummaryPayload | null>>;
}

export function useQuantPortfolio({
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
}: UseQuantPortfolioOptions) {
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
        const response = await fetchPortfolioCurrent(
          backend.baseUrl,
          runId,
          selectedModel,
          useCache,
        );
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
          error instanceof Error
            ? error.message
            : "Failed to load portfolio rationale.";
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
    [
      backend,
      markArtifactReady,
      patchSession,
      runId,
      selectedModel,
      setIsLoadingPortfolio,
      setPortfolioCurrent,
      setPortfolioError,
    ],
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
        const response = await fetchRebalanceHistory(
          backend.baseUrl,
          runId,
          selectedModel,
          useCache,
        );
        setRebalanceHistory(response.items ?? []);
      } catch (error) {
        const rawMessage =
          error instanceof Error
            ? error.message
            : "Failed to load rebalance history.";
        const message =
          rawMessage.includes("404") ||
          rawMessage.toLowerCase().includes("not found")
            ? "Run backtest first."
            : rawMessage;
        setRebalanceHistoryError(message);
      } finally {
        setIsLoadingRebalanceHistory(false);
      }
    },
    [
      backend,
      runId,
      selectedModel,
      setIsLoadingRebalanceHistory,
      setRebalanceHistory,
      setRebalanceHistoryError,
    ],
  );

  useEffect(() => {
    if (!backend?.connected || !runId) {
      return;
    }
    void (async () => {
      try {
        const latestSummary = await fetchArtifactSummary(
          backend.baseUrl,
          runId,
          selectedModel,
        );
        setSummary(latestSummary);
        const hasPredictions = latestSummary.available_artifacts.some((name) =>
          name.startsWith("predictions"),
        );
        markArtifactReady("predictions", hasPredictions);
      } catch {
        // Summary is optional for model-switching UX.
      }
      await loadPortfolioCurrent({ suppressNotReady: true, useCache: true });
      await loadRebalanceHistory({ useCache: true });
    })();
  }, [
    backend,
    loadPortfolioCurrent,
    loadRebalanceHistory,
    markArtifactReady,
    runId,
    selectedModel,
    setSummary,
  ]);

  return {
    loadPortfolioCurrent,
    loadRebalanceHistory,
  };
}
