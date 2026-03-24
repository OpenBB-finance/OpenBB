import { useCallback, useEffect, useRef, useState } from "react";
import type { Dispatch, SetStateAction } from "react";
import {
  fetchDashboardHealth,
  fetchPromotedModel,
  fetchPortfolioPolicy,
  fetchRunsList,
  fetchUniverse,
  fetchUniverseList,
} from "../lib/quantApi";
import { resolveOpenBBBackend } from "../lib/openbbBackend";
import {
  DEFAULT_PORTFOLIO_POLICY,
  UNIVERSE_SET_OPTIONS_DEFAULT,
  formatSymbolsForTextarea,
  mergeUniverseSetOptions,
  symbolsByProfile,
} from "../lib/quantConfig";
import type {
  RunStreamState,
  UniverseProfileId,
  UniverseSetOption,
} from "../lib/quantConfig";
import type { FeatureActivation } from "../types/feature-activation";
import type {
  DashboardHealthPayload,
  ModelName,
  PortfolioPolicyPayload,
  PromotedModelPayload,
  RunListItemPayload,
  RunStatusPayload,
  UniverseResponse,
} from "../types/quant";

type BackendResolution = Awaited<ReturnType<typeof resolveOpenBBBackend>> | null;

interface UseQuantBackendRuntimeOptions {
  selectedModel: ModelName;
  runId: string | null;
  runStatus: RunStatusPayload | null;
  sessionRunId: string;
  setPortfolioPolicy: Dispatch<SetStateAction<PortfolioPolicyPayload>>;
  setSelectedProfile: Dispatch<SetStateAction<UniverseProfileId>>;
  setSymbolsInput: Dispatch<SetStateAction<string>>;
  setRunStreamState: Dispatch<SetStateAction<RunStreamState>>;
  setErrorMessage: Dispatch<SetStateAction<string | null>>;
}

export function useQuantBackendRuntime({
  selectedModel,
  runId,
  runStatus,
  sessionRunId,
  setPortfolioPolicy,
  setSelectedProfile,
  setSymbolsInput,
  setRunStreamState,
  setErrorMessage,
}: UseQuantBackendRuntimeOptions) {
  const [isResolvingBackend, setIsResolvingBackend] = useState(false);
  const [backend, setBackend] = useState<BackendResolution>(null);
  const [quantActivation, setQuantActivation] = useState<FeatureActivation | null>(null);
  const [universe, setUniverse] = useState<UniverseResponse | null>(null);
  const [universeSetOptions, setUniverseSetOptions] = useState<UniverseSetOption[]>(
    UNIVERSE_SET_OPTIONS_DEFAULT,
  );
  const [recentRuns, setRecentRuns] = useState<RunListItemPayload[]>([]);
  const [promotedModel, setPromotedModel] = useState<PromotedModelPayload | null>(null);
  const [dashboardHealth, setDashboardHealth] = useState<DashboardHealthPayload | null>(null);
  const [isLoadingHealth, setIsLoadingHealth] = useState(false);
  const [healthError, setHealthError] = useState<string | null>(null);
  const bootstrapLoadId = useRef(0);

  const resolveBackendAndUniverse = useCallback(async () => {
    const loadId = bootstrapLoadId.current + 1;
    bootstrapLoadId.current = loadId;
    setIsResolvingBackend(true);
    setErrorMessage(null);
    setHealthError(null);

    try {
      const resolved = await resolveOpenBBBackend();
      if (bootstrapLoadId.current !== loadId) {
        return;
      }
      setBackend(resolved);

      if (!resolved.connected) {
        setQuantActivation({
          featureName: "quant_ml",
          available: false,
          detail: "OpenBB API is not connected.",
          lastCheckedAt: new Date().toISOString(),
        });
        setUniverse(null);
        setRecentRuns([]);
        setPromotedModel(null);
        setPortfolioPolicy(DEFAULT_PORTFOLIO_POLICY);
        setUniverseSetOptions(UNIVERSE_SET_OPTIONS_DEFAULT);
        setRunStreamState("idle");
        setDashboardHealth(null);
        setHealthError(null);
        return;
      }

      setIsResolvingBackend(false);

      const universePromise = fetchUniverse(resolved.baseUrl)
        .then((value) => ({ ok: true as const, value }))
        .catch((reason) => ({ ok: false as const, reason }));

      void (async () => {
        try {
          const fetchedUniverseList = await fetchUniverseList(resolved.baseUrl);
          if (bootstrapLoadId.current !== loadId) {
            return;
          }

          setQuantActivation({
            featureName: "quant_ml",
            available: true,
            detail: null,
            lastCheckedAt: new Date().toISOString(),
          });
          setUniverseSetOptions(mergeUniverseSetOptions(fetchedUniverseList.universes));

          const universeResult = await universePromise;
          if (bootstrapLoadId.current !== loadId) {
            return;
          }

          const fetchedUniverse = universeResult.ok ? universeResult.value : null;
          setUniverse(fetchedUniverse);
          setSymbolsInput((prev) => {
            if (prev.trim() || !fetchedUniverse) {
              return prev;
            }
            return formatSymbolsForTextarea(
              symbolsByProfile(fetchedUniverse.assets, "all"),
            );
          });
          setSelectedProfile((prev) => (prev === "custom" ? prev : "all"));

          window.setTimeout(() => {
            void (async () => {
              const [policyResult, promotedResult, runListResult] = await Promise.allSettled([
                fetchPortfolioPolicy(resolved.baseUrl),
                fetchPromotedModel(resolved.baseUrl, selectedModel),
                fetchRunsList(resolved.baseUrl, 20, {
                  completedFirst: true,
                  actionableOnly: false,
                }),
              ]);

              if (bootstrapLoadId.current !== loadId) {
                return;
              }

              setPortfolioPolicy(
                policyResult.status === "fulfilled"
                  ? policyResult.value
                  : DEFAULT_PORTFOLIO_POLICY,
              );
              setPromotedModel(
                promotedResult.status === "fulfilled" ? promotedResult.value : null,
              );
              setRecentRuns(
                runListResult.status === "fulfilled" ? runListResult.value.runs : [],
              );
            })();
          }, 0);
        } catch (error) {
          if (bootstrapLoadId.current !== loadId) {
            return;
          }

          setQuantActivation({
            featureName: "quant_ml",
            available: false,
            detail: error instanceof Error ? error.message : "quant_ml extension unavailable",
            lastCheckedAt: new Date().toISOString(),
          });
          setUniverse(null);
          setRecentRuns([]);
          setPromotedModel(null);
          setPortfolioPolicy(DEFAULT_PORTFOLIO_POLICY);
          setUniverseSetOptions(UNIVERSE_SET_OPTIONS_DEFAULT);
          setRunStreamState("idle");
          setDashboardHealth(null);
          setErrorMessage(
            error instanceof Error
              ? error.message
              : "quant_ml extension is unavailable. Install/enable openbb-quant-ml.",
          );
        }
      })();
    } catch (error) {
      if (bootstrapLoadId.current !== loadId) {
        return;
      }
      setQuantActivation({
        featureName: "quant_ml",
        available: false,
        detail: error instanceof Error ? error.message : "Failed to resolve quant_ml activation.",
        lastCheckedAt: new Date().toISOString(),
      });
      setPromotedModel(null);
      setRecentRuns([]);
      setPortfolioPolicy(DEFAULT_PORTFOLIO_POLICY);
      setRunStreamState("idle");
      setDashboardHealth(null);
      setErrorMessage(error instanceof Error ? error.message : "Failed to resolve backend connection.");
    } finally {
      if (bootstrapLoadId.current === loadId) {
        setIsResolvingBackend(false);
      }
    }
  }, [
    selectedModel,
    setErrorMessage,
    setPortfolioPolicy,
    setRunStreamState,
    setSelectedProfile,
    setSymbolsInput,
  ]);

  useEffect(() => {
    void resolveBackendAndUniverse();
  }, [resolveBackendAndUniverse]);

  useEffect(() => {
    if (!backend?.connected) {
      setDashboardHealth(null);
      setIsLoadingHealth(false);
      setHealthError(null);
      return;
    }

    let cancelled = false;
    const targetRunId = (runId ?? sessionRunId.trim()) || undefined;
    const hasTargetRun = Boolean(targetRunId);
    const mode =
      runStatus?.status === "queued" ||
      runStatus?.status === "running" ||
      !hasTargetRun
        ? "live"
        : "backtest";
    const intervalMs = mode === "live" ? 5_000 : 30_000;
    let firstLoad = true;

    const refreshHealth = async () => {
      if (firstLoad) {
        setIsLoadingHealth(true);
      }
      try {
        const health = await fetchDashboardHealth(backend.baseUrl, targetRunId, selectedModel, { mode });
        if (cancelled) {
          return;
        }
        setDashboardHealth(health);
        setHealthError(null);
      } catch (error) {
        if (cancelled) {
          return;
        }
        setHealthError(error instanceof Error ? error.message : "Failed to fetch dashboard health.");
      } finally {
        if (firstLoad && !cancelled) {
          setIsLoadingHealth(false);
          firstLoad = false;
        }
      }
    };

    void refreshHealth();
    const timer = window.setInterval(() => {
      void refreshHealth();
    }, intervalMs);

    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, [backend, runId, runStatus?.status, selectedModel, sessionRunId]);

  return {
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
  };
}
