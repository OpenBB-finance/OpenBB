import { useCallback, useEffect, useState } from "react";
import type { Dispatch, SetStateAction } from "react";
import {
  fetchArtifactSummary,
  fetchWalkforwardBacktestStatus,
  invalidateQuantCaches,
  runBacktest,
  runBacktestWalkforward,
} from "../lib/quantApi";
import type {
  AlphaMappingMode,
  ArtifactSummaryPayload,
  BacktestResponsePayload,
  CovarianceMethod,
  MVOptimizerEngine,
  ModelName,
  RebalanceHistoryItem,
  WalkForwardBacktestStatusPayload,
  WorkflowArtifactsReadyPayload,
} from "../types/quant";

type BackendConnection = { connected: boolean; baseUrl: string } | null;
type SessionPatch = {
  data_timestamp?: string | null;
  run_stage?: string;
  run_progress?: number;
  artifacts_ready?: Partial<WorkflowArtifactsReadyPayload>;
};

interface PortfolioPolicyShape {
  single_name_max_abs_weight: number;
  sector_concentration_max: number;
  turnover_max: number;
  gross_exposure_max: number;
  net_exposure_abs_max: number;
}

interface BacktestAdvancedShape {
  mv_optimizer_engine: MVOptimizerEngine;
  optimizer_strict: boolean;
  cov_method: CovarianceMethod;
  cov_pca_components: number;
  cov_pca_idio_floor: number;
  alpha_mapping_mode: AlphaMappingMode;
  ic_lookback_days: number;
  ic_ewma_halflife: number;
  ic_clip_min: number;
  ic_clip_max: number;
  ic_fallback: number;
  alpha_ema_halflife_days: number;
  trigger_rebalance_enabled: boolean;
  trigger_threshold_bps: number;
  trigger_cost_multiplier: number;
}

interface UseQuantBacktestOptions {
  backend: BackendConnection;
  runId: string | null;
  selectedModel: ModelName;
  dateStart: string;
  dateEnd: string;
  summary: ArtifactSummaryPayload | null;
  portfolioPolicy: PortfolioPolicyShape;
  backtestAdvanced: BacktestAdvancedShape;
  sessionHasPredictions: boolean;
  modelHasPredictions: boolean;
  markArtifactReady: (
    artifact: keyof WorkflowArtifactsReadyPayload,
    ready?: boolean,
  ) => void;
  patchSession: (patch: SessionPatch) => void;
  setIsSubmittingBacktest: Dispatch<SetStateAction<boolean>>;
  setBacktest: Dispatch<SetStateAction<BacktestResponsePayload | null>>;
  setRebalanceHistory: Dispatch<SetStateAction<RebalanceHistoryItem[]>>;
  setRebalanceHistoryError: Dispatch<SetStateAction<string | null>>;
  setSummary: Dispatch<SetStateAction<ArtifactSummaryPayload | null>>;
  setErrorMessage: Dispatch<SetStateAction<string | null>>;
  loadPortfolioCurrent: (options?: {
    suppressNotReady?: boolean;
    useCache?: boolean;
  }) => Promise<void>;
  loadRebalanceHistory: (options?: { useCache?: boolean }) => Promise<void>;
  setWalkforwardStatus: Dispatch<
    SetStateAction<WalkForwardBacktestStatusPayload | null>
  >;
  setIsSubmittingWalkforward: Dispatch<SetStateAction<boolean>>;
  toBacktestErrorMessage: (error: unknown) => string;
}

export function useQuantBacktest({
  backend,
  runId,
  selectedModel,
  dateStart,
  dateEnd,
  summary,
  portfolioPolicy,
  backtestAdvanced,
  sessionHasPredictions,
  modelHasPredictions,
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
}: UseQuantBacktestOptions) {
  const [walkforwardJobId, setWalkforwardJobId] = useState<string | null>(null);
  const [walkforwardElapsed, setWalkforwardElapsed] = useState(0);

  const handleBacktest = useCallback(async () => {
    if (!backend?.connected || !runId) {
      return;
    }
    if (!sessionHasPredictions && !modelHasPredictions) {
      setErrorMessage(
        "Selected model artifacts are not ready. Choose a completed run or generate signals again.",
      );
      return;
    }

    setIsSubmittingBacktest(true);
    setErrorMessage(null);

    try {
      let effectiveStart = dateStart;
      let effectiveEnd = dateEnd;
      if (summary?.params) {
        const params = summary.params as Record<string, unknown>;
        const req = params.request as Record<string, unknown> | undefined;
        const dateRange = req?.date_range as
          | { start?: string; end?: string }
          | undefined;
        if (dateRange?.start && effectiveStart < dateRange.start) {
          effectiveStart = dateRange.start;
        }
        if (dateRange?.end && effectiveEnd > dateRange.end) {
          effectiveEnd = dateRange.end;
        }
      }

      const response = await runBacktest(backend.baseUrl, {
        run_id: runId,
        model_name: selectedModel,
        start: effectiveStart,
        end: effectiveEnd,
        rebalance: "monthly",
        constraints: {
          max_weight: portfolioPolicy.single_name_max_abs_weight,
          long_only: true,
          risk_aversion: 3.0,
          lookback_days: 126,
          optimizer_mode: "mv",
          mv_optimizer_engine: backtestAdvanced.mv_optimizer_engine,
          optimizer_strict: backtestAdvanced.optimizer_strict,
          cvar_alpha: 0.05,
          cvar_lambda: 3.0,
          scenario_lookback_days: 252,
          cov_method: backtestAdvanced.cov_method,
          cov_ewma_halflife: 42,
          cov_shrinkage: 0.15,
          cov_pca_components: backtestAdvanced.cov_pca_components,
          cov_pca_idio_floor: backtestAdvanced.cov_pca_idio_floor,
          alpha_mapping_mode: backtestAdvanced.alpha_mapping_mode,
          ic_lookback_days: backtestAdvanced.ic_lookback_days,
          ic_ewma_halflife: backtestAdvanced.ic_ewma_halflife,
          ic_clip_min: backtestAdvanced.ic_clip_min,
          ic_clip_max: backtestAdvanced.ic_clip_max,
          ic_fallback: backtestAdvanced.ic_fallback,
          alpha_ema_halflife_days: backtestAdvanced.alpha_ema_halflife_days,
          trigger_rebalance_enabled: backtestAdvanced.trigger_rebalance_enabled,
          trigger_threshold_bps: backtestAdvanced.trigger_threshold_bps,
          trigger_cost_multiplier: backtestAdvanced.trigger_cost_multiplier,
          turnover_limit: portfolioPolicy.turnover_max,
          gross_exposure_max: portfolioPolicy.gross_exposure_max,
          net_exposure_min: 0.0,
          net_exposure_max: portfolioPolicy.net_exposure_abs_max,
          sector_max_weight: portfolioPolicy.sector_concentration_max,
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

      const latestSummary = await fetchArtifactSummary(
        backend.baseUrl,
        runId,
        selectedModel,
      );
      setSummary(latestSummary);
      await loadPortfolioCurrent({ suppressNotReady: false, useCache: false });
      if (
        !response.rebalance_history_summary ||
        response.rebalance_history_summary.length === 0
      ) {
        await loadRebalanceHistory({ useCache: false });
      }
    } catch (error) {
      setErrorMessage(toBacktestErrorMessage(error));
    } finally {
      setIsSubmittingBacktest(false);
    }
  }, [
    backend,
    backtestAdvanced.alpha_ema_halflife_days,
    backtestAdvanced.alpha_mapping_mode,
    backtestAdvanced.cov_method,
    backtestAdvanced.cov_pca_components,
    backtestAdvanced.cov_pca_idio_floor,
    backtestAdvanced.ic_clip_max,
    backtestAdvanced.ic_clip_min,
    backtestAdvanced.ic_ewma_halflife,
    backtestAdvanced.ic_fallback,
    backtestAdvanced.ic_lookback_days,
    backtestAdvanced.mv_optimizer_engine,
    backtestAdvanced.optimizer_strict,
    backtestAdvanced.trigger_cost_multiplier,
    backtestAdvanced.trigger_rebalance_enabled,
    backtestAdvanced.trigger_threshold_bps,
    dateEnd,
    dateStart,
    loadPortfolioCurrent,
    loadRebalanceHistory,
    markArtifactReady,
    patchSession,
    portfolioPolicy.gross_exposure_max,
    portfolioPolicy.net_exposure_abs_max,
    portfolioPolicy.sector_concentration_max,
    portfolioPolicy.single_name_max_abs_weight,
    portfolioPolicy.turnover_max,
    runId,
    selectedModel,
    sessionHasPredictions,
    modelHasPredictions,
    setBacktest,
    setErrorMessage,
    setIsSubmittingBacktest,
    setRebalanceHistory,
    setRebalanceHistoryError,
    setSummary,
    summary,
    toBacktestErrorMessage,
  ]);

  const handleWalkforwardBacktest = useCallback(async () => {
    if (!backend?.connected || !runId) {
      setErrorMessage("Run training first.");
      return;
    }
    if (!sessionHasPredictions && !modelHasPredictions) {
      setErrorMessage(
        "Selected model artifacts are not ready. Choose a completed run or generate signals again.",
      );
      return;
    }

    setIsSubmittingWalkforward(true);
    setErrorMessage(null);
    setWalkforwardStatus(null);
    setWalkforwardElapsed(0);
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
          optimizer_mode: "mv",
          mv_optimizer_engine: backtestAdvanced.mv_optimizer_engine,
          optimizer_strict: backtestAdvanced.optimizer_strict,
          cvar_alpha: 0.05,
          cvar_lambda: 3.0,
          scenario_lookback_days: 252,
          cov_method: backtestAdvanced.cov_method,
          cov_ewma_halflife: 42,
          cov_shrinkage: 0.15,
          cov_pca_components: backtestAdvanced.cov_pca_components,
          cov_pca_idio_floor: backtestAdvanced.cov_pca_idio_floor,
          alpha_mapping_mode: backtestAdvanced.alpha_mapping_mode,
          ic_lookback_days: backtestAdvanced.ic_lookback_days,
          ic_ewma_halflife: backtestAdvanced.ic_ewma_halflife,
          ic_clip_min: backtestAdvanced.ic_clip_min,
          ic_clip_max: backtestAdvanced.ic_clip_max,
          ic_fallback: backtestAdvanced.ic_fallback,
          alpha_ema_halflife_days: backtestAdvanced.alpha_ema_halflife_days,
          trigger_rebalance_enabled: backtestAdvanced.trigger_rebalance_enabled,
          trigger_threshold_bps: backtestAdvanced.trigger_threshold_bps,
          trigger_cost_multiplier: backtestAdvanced.trigger_cost_multiplier,
          turnover_limit: portfolioPolicy.turnover_max,
          gross_exposure_max: portfolioPolicy.gross_exposure_max,
          net_exposure_min: 0.0,
          net_exposure_max: portfolioPolicy.net_exposure_abs_max,
          sector_max_weight: portfolioPolicy.sector_concentration_max,
        },
        cost_bps: 10,
        slippage_bps: 2,
        entry_price: "next_open",
        exit_price: "close",
        portfolio_mode: "long_only",
        regime_policy: "mixed",
        min_history_days: 126,
      });
      setWalkforwardJobId(submit.job_id);
      const initial = await fetchWalkforwardBacktestStatus(
        backend.baseUrl,
        submit.job_id,
      );
      setWalkforwardStatus(initial);
    } catch (error) {
      setErrorMessage(toBacktestErrorMessage(error));
      setIsSubmittingWalkforward(false);
    }
  }, [
    backend,
    backtestAdvanced.alpha_ema_halflife_days,
    backtestAdvanced.alpha_mapping_mode,
    backtestAdvanced.cov_method,
    backtestAdvanced.cov_pca_components,
    backtestAdvanced.cov_pca_idio_floor,
    backtestAdvanced.ic_clip_max,
    backtestAdvanced.ic_clip_min,
    backtestAdvanced.ic_ewma_halflife,
    backtestAdvanced.ic_fallback,
    backtestAdvanced.ic_lookback_days,
    backtestAdvanced.mv_optimizer_engine,
    backtestAdvanced.optimizer_strict,
    backtestAdvanced.trigger_cost_multiplier,
    backtestAdvanced.trigger_rebalance_enabled,
    backtestAdvanced.trigger_threshold_bps,
    dateEnd,
    dateStart,
    portfolioPolicy.gross_exposure_max,
    portfolioPolicy.net_exposure_abs_max,
    portfolioPolicy.sector_concentration_max,
    portfolioPolicy.single_name_max_abs_weight,
    portfolioPolicy.turnover_max,
    runId,
    selectedModel,
    sessionHasPredictions,
    modelHasPredictions,
    setErrorMessage,
    setIsSubmittingWalkforward,
    setWalkforwardStatus,
    toBacktestErrorMessage,
  ]);

  useEffect(() => {
    if (!walkforwardJobId || !backend?.connected) {
      return;
    }
    const interval = window.setInterval(async () => {
      try {
        const latest = await fetchWalkforwardBacktestStatus(
          backend.baseUrl,
          walkforwardJobId,
        );
        setWalkforwardStatus(latest);
        setWalkforwardElapsed((prev) => prev + 3);
        if (latest.status === "completed") {
          markArtifactReady("backtest", true);
          patchSession({
            run_stage: "walkforward_completed",
            run_progress: 100,
            artifacts_ready: { backtest: true },
          });
          setWalkforwardJobId(null);
          setIsSubmittingWalkforward(false);
        } else if (latest.status === "failed") {
          setErrorMessage(
            toBacktestErrorMessage(
              new Error(latest.message || "Walk-forward backtest failed."),
            ),
          );
          setWalkforwardJobId(null);
          setIsSubmittingWalkforward(false);
        }
      } catch (error) {
        setErrorMessage(toBacktestErrorMessage(error));
        setWalkforwardJobId(null);
        setIsSubmittingWalkforward(false);
      }
    }, 3000);
    return () => window.clearInterval(interval);
  }, [
    backend,
    markArtifactReady,
    patchSession,
    setErrorMessage,
    setIsSubmittingWalkforward,
    setWalkforwardStatus,
    toBacktestErrorMessage,
    walkforwardJobId,
  ]);

  return {
    handleBacktest,
    handleWalkforwardBacktest,
    walkforwardElapsed,
  };
}
