import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from "react";
import type { ReactNode } from "react";
import { fetchDashboardHealth } from "../lib/quantApi";
import { resolveOpenBBBackend } from "../lib/openbbBackend";
import type {
  DashboardHealthPayload,
  DashboardMode,
  ModelName,
  QuantSessionState,
  WorkflowArtifactsReadyPayload,
} from "../types/quant";

type QuantSessionPatch = Omit<Partial<QuantSessionState>, "artifacts_ready"> & {
  artifacts_ready?: Partial<WorkflowArtifactsReadyPayload>;
};

interface QuantSessionContextValue {
  session: QuantSessionState;
  setRunId: (runId: string) => void;
  setModelName: (modelName: ModelName) => void;
  setMode: (mode: DashboardMode) => void;
  patchSession: (patch: QuantSessionPatch) => void;
  markArtifactReady: (artifact: keyof WorkflowArtifactsReadyPayload, ready?: boolean) => void;
  syncFromHealth: (payload: DashboardHealthPayload) => void;
  resetSession: () => void;
}

const DEFAULT_ARTIFACTS: WorkflowArtifactsReadyPayload = {
  predictions: false,
  signals: false,
  backtest: false,
  portfolio_current: false,
};

const DEFAULT_SESSION: QuantSessionState = {
  run_id: "",
  model_name: "lgbm_ranker",
  mode: "backtest",
  run_status: "unknown",
  run_stage: "",
  run_progress: 0,
  artifacts_ready: { ...DEFAULT_ARTIFACTS },
  data_timestamp: null,
  updated_at: null,
};

function normalizeModel(value: string | null | undefined): ModelName | null {
  if (value === "lgbm_ranker" || value === "xgb_lstm") {
    return value;
  }
  return null;
}

function normalizeMode(value: string | null | undefined): DashboardMode | null {
  if (value === "backtest" || value === "live") {
    return value;
  }
  return null;
}

function loadInitialSession(): QuantSessionState {
  if (typeof window === "undefined") {
    return { ...DEFAULT_SESSION, artifacts_ready: { ...DEFAULT_ARTIFACTS } };
  }

  const search = new URLSearchParams(window.location.search);
  const queryRunId = search.get("run_id")?.trim() || "";
  const queryModel = normalizeModel(search.get("model") || search.get("model_name"));
  const queryMode = normalizeMode(search.get("mode"));

  const storedRunId = localStorage.getItem("quant_latest_run_id")?.trim() || "";
  const storedModel = normalizeModel(localStorage.getItem("quant_latest_model"));
  const storedMode = normalizeMode(localStorage.getItem("quant_latest_mode"));

  return {
    ...DEFAULT_SESSION,
    run_id: queryRunId || storedRunId || "",
    model_name: queryModel || storedModel || DEFAULT_SESSION.model_name,
    mode: queryMode || storedMode || DEFAULT_SESSION.mode,
    artifacts_ready: { ...DEFAULT_ARTIFACTS },
  };
}

const QuantSessionContext = createContext<QuantSessionContextValue | null>(null);

const FALLBACK_CONTEXT: QuantSessionContextValue = {
  session: { ...DEFAULT_SESSION, artifacts_ready: { ...DEFAULT_ARTIFACTS } },
  setRunId: () => undefined,
  setModelName: () => undefined,
  setMode: () => undefined,
  patchSession: () => undefined,
  markArtifactReady: () => undefined,
  syncFromHealth: () => undefined,
  resetSession: () => undefined,
};

export function QuantSessionProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<QuantSessionState>(() => loadInitialSession());
  const hydratedFromHealth = useRef(false);

  const setRunId = useCallback((runId: string) => {
    setSession((prev) => ({ ...prev, run_id: runId.trim() }));
  }, []);

  const setModelName = useCallback((modelName: ModelName) => {
    setSession((prev) => ({ ...prev, model_name: modelName }));
  }, []);

  const setMode = useCallback((mode: DashboardMode) => {
    setSession((prev) => ({ ...prev, mode }));
  }, []);

  const patchSession = useCallback((patch: QuantSessionPatch) => {
    setSession((prev) => ({
      ...prev,
      ...patch,
      artifacts_ready: {
        ...prev.artifacts_ready,
        ...(patch.artifacts_ready || {}),
      },
    }));
  }, []);

  const markArtifactReady = useCallback((artifact: keyof WorkflowArtifactsReadyPayload, ready = true) => {
    setSession((prev) => ({
      ...prev,
      artifacts_ready: {
        ...prev.artifacts_ready,
        [artifact]: ready,
      },
    }));
  }, []);

  const syncFromHealth = useCallback((payload: DashboardHealthPayload) => {
    setSession((prev) => {
      const workflow = payload.workflow_state;
      const resolvedRun = (payload.resolved_run_id || payload.latest_run_id || prev.run_id || "").trim();
      return {
        ...prev,
        run_id: resolvedRun || prev.run_id,
        model_name: payload.model_name || prev.model_name,
        data_timestamp: payload.data_timestamp ?? prev.data_timestamp ?? null,
        run_status: workflow?.run_status ?? prev.run_status,
        run_stage: workflow?.run_stage ?? prev.run_stage,
        run_progress: typeof workflow?.run_progress === "number" ? workflow.run_progress : prev.run_progress,
        artifacts_ready: {
          ...prev.artifacts_ready,
          ...(workflow?.artifacts_ready || {}),
        },
        updated_at: workflow?.updated_at ?? prev.updated_at ?? null,
      };
    });
  }, []);

  const resetSession = useCallback(() => {
    setSession({ ...DEFAULT_SESSION, artifacts_ready: { ...DEFAULT_ARTIFACTS } });
  }, []);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    localStorage.setItem("quant_latest_model", session.model_name);
    localStorage.setItem("quant_latest_mode", session.mode);
    if (session.run_id.trim()) {
      localStorage.setItem("quant_latest_run_id", session.run_id.trim());
    }
  }, [session.model_name, session.mode, session.run_id]);

  useEffect(() => {
    if (session.run_id.trim() || hydratedFromHealth.current) {
      return;
    }
    hydratedFromHealth.current = true;
    let cancelled = false;

    void (async () => {
      try {
        const backend = await resolveOpenBBBackend();
        if (!backend.connected) {
          return;
        }
        const payload = await fetchDashboardHealth(backend.baseUrl, undefined, session.model_name, {
          mode: session.mode,
        });
        if (cancelled) {
          return;
        }
        syncFromHealth(payload);
      } catch {
        // Non-blocking hydration fallback.
      }
    })();

    return () => {
      cancelled = true;
    };
  }, [session.mode, session.model_name, session.run_id, syncFromHealth]);

  const value = useMemo<QuantSessionContextValue>(
    () => ({
      session,
      setRunId,
      setModelName,
      setMode,
      patchSession,
      markArtifactReady,
      syncFromHealth,
      resetSession,
    }),
    [markArtifactReady, patchSession, resetSession, session, setMode, setModelName, setRunId, syncFromHealth],
  );

  return <QuantSessionContext.Provider value={value}>{children}</QuantSessionContext.Provider>;
}

export function useQuantSession(): QuantSessionContextValue {
  return useContext(QuantSessionContext) ?? FALLBACK_CONTEXT;
}



