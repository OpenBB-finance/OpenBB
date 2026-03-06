import { useEffect } from "react";
import type { Dispatch, SetStateAction } from "react";
import { createRunLogStreamUrl, fetchArtifactSummary, fetchRunStatus } from "../lib/quantApi";
import type { ArtifactSummaryPayload, ModelName, RunStatusPayload } from "../types/quant";

type BackendConnection = { connected: boolean; baseUrl: string } | null;
type SessionPatch = {
  run_id?: string;
  model_name?: ModelName;
  run_status?: RunStatusPayload["status"];
  run_stage?: string;
  run_progress?: number;
  updated_at?: string;
};

const MAX_LIVE_LOG_LINES = 200;

function parseSsePayload(raw: string): Record<string, unknown> | null {
  try {
    const parsed: unknown = JSON.parse(raw);
    return parsed && typeof parsed === "object" ? (parsed as Record<string, unknown>) : null;
  } catch {
    return null;
  }
}

function appendLiveLog(logs: string[], line: string, maxLines = MAX_LIVE_LOG_LINES): string[] {
  const trimmed = line.trim();
  if (!trimmed) {
    return logs;
  }
  if (logs.length > 0 && logs[logs.length - 1] === line) {
    return logs;
  }
  const next = [...logs, line];
  if (next.length <= maxLines) {
    return next;
  }
  return next.slice(next.length - maxLines);
}

export interface UseQuantRunStreamOptions {
  backend: BackendConnection;
  runId: string | null;
  runStatus: RunStatusPayload | null;
  selectedModel: ModelName;
  patchSession: (patch: SessionPatch) => void;
  markArtifactReady: (artifact: "predictions", ready?: boolean) => void;
  setRunStatus: Dispatch<SetStateAction<RunStatusPayload | null>>;
  setRunStreamState: Dispatch<
    SetStateAction<"idle" | "connecting" | "ready" | "streaming" | "fallback" | "done" | "timeout" | "error">
  >;
  setActiveTrainingRunId: Dispatch<SetStateAction<string | null>>;
  setSummary: Dispatch<SetStateAction<ArtifactSummaryPayload | null>>;
  setErrorMessage: Dispatch<SetStateAction<string | null>>;
}

export function useQuantRunStream({
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
}: UseQuantRunStreamOptions): void {
  useEffect(() => {
    if (!backend?.connected || !runId || !runStatus) {
      return;
    }

    if (runStatus.status !== "queued" && runStatus.status !== "running") {
      return;
    }

    let disposed = false;
    let fallbackTimer: number | null = null;
    let stream: EventSource | null = null;
    let terminalHandled = false;

    const closeStream = () => {
      if (stream) {
        stream.close();
        stream = null;
      }
    };

    const setSessionFromRun = (latest: RunStatusPayload) => {
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
    };

    const handleTerminal = async (status: RunStatusPayload["status"]) => {
      if (terminalHandled) {
        return;
      }
      terminalHandled = true;
      setRunStreamState("done");
      setActiveTrainingRunId((prev) => (prev === runId ? null : prev));
      if (status === "completed") {
        try {
          const latestSummary = await fetchArtifactSummary(backend.baseUrl, runId, selectedModel);
          if (disposed) {
            return;
          }
          setSummary(latestSummary);
          markArtifactReady("predictions", true);
        } catch {
          // summary fetch failure should not interrupt live status updates.
        }
      }
    };

    const refreshFromApi = async () => {
      try {
        const latest = await fetchRunStatus(backend.baseUrl, runId);
        if (disposed) {
          return;
        }
        setRunStatus(latest);
        setSessionFromRun(latest);
        if (latest.status === "completed" || latest.status === "failed") {
          await handleTerminal(latest.status);
          closeStream();
          if (fallbackTimer != null) {
            window.clearInterval(fallbackTimer);
            fallbackTimer = null;
          }
        }
      } catch (error) {
        if (disposed) {
          return;
        }
        setRunStreamState("error");
        setErrorMessage(error instanceof Error ? error.message : "Failed to refresh run status.");
      }
    };

    const startFallbackPolling = () => {
      if (fallbackTimer != null) {
        return;
      }
      setRunStreamState("fallback");
      fallbackTimer = window.setInterval(() => {
        void refreshFromApi();
      }, 3000);
    };

    if (typeof window !== "undefined" && typeof window.EventSource !== "undefined") {
      setRunStreamState("connecting");
      stream = new EventSource(createRunLogStreamUrl(backend.baseUrl, runId, 1.0, 600));

      stream.addEventListener("ready", () => {
        setRunStreamState("ready");
      });

      stream.onmessage = (event) => {
        const payload = parseSsePayload(event.data);
        if (!payload) {
          return;
        }
        const line = typeof payload.line === "string" ? payload.line : null;
        const eventStatus =
          typeof payload.status === "string" ? (payload.status as RunStatusPayload["status"]) : null;
        const eventStage = typeof payload.stage === "string" ? payload.stage : null;
        if (!line && !eventStatus && !eventStage) {
          return;
        }
        setRunStreamState("streaming");
        setRunStatus((prev) => {
          if (!prev) {
            return prev;
          }
          const nextLogs = line ? appendLiveLog(prev.logs_tail, line) : prev.logs_tail;
          return {
            ...prev,
            status: eventStatus ?? prev.status,
            stage: eventStage ?? prev.stage,
            logs_tail: nextLogs,
            updated_at: new Date().toISOString(),
          };
        });
      };

      stream.addEventListener("status", (event: Event) => {
        const payload = parseSsePayload((event as MessageEvent<string>).data ?? "");
        if (!payload) {
          return;
        }
        const eventStatus =
          typeof payload.status === "string" ? (payload.status as RunStatusPayload["status"]) : null;
        const eventStage = typeof payload.stage === "string" ? payload.stage : null;
        const eventProgress = typeof payload.progress === "number" ? payload.progress : null;
        if (!eventStatus || eventProgress == null) {
          return;
        }
        setRunStreamState("streaming");
        const updatedAt = new Date().toISOString();
        setRunStatus((prev) => {
          if (!prev) {
            return prev;
          }
          return {
            ...prev,
            status: eventStatus,
            stage: eventStage ?? prev.stage,
            progress: eventProgress,
            updated_at: updatedAt,
          };
        });
        patchSession({
          run_id: runId,
          model_name: selectedModel,
          run_status: eventStatus,
          run_stage: eventStage ?? runStatus.stage,
          run_progress: eventProgress,
          updated_at: updatedAt,
        });
        if (eventStatus === "queued" || eventStatus === "running") {
          setActiveTrainingRunId(runId);
        } else {
          void handleTerminal(eventStatus);
          closeStream();
        }
      });

      stream.addEventListener("done", (event: Event) => {
        setRunStreamState("done");
        const payload = parseSsePayload((event as MessageEvent<string>).data ?? "");
        const eventStatus =
          payload && typeof payload.status === "string"
            ? (payload.status as RunStatusPayload["status"])
            : runStatus.status;
        void handleTerminal(eventStatus);
        closeStream();
        void refreshFromApi();
      });

      stream.addEventListener("timeout", () => {
        setRunStreamState("timeout");
        closeStream();
        startFallbackPolling();
      });

      stream.addEventListener("error", (event: Event) => {
        setRunStreamState("error");
        const payload = parseSsePayload((event as MessageEvent<string>).data ?? "");
        if (payload && typeof payload.message === "string") {
          setErrorMessage(payload.message);
        }
      });

      stream.onerror = () => {
        if (disposed) {
          return;
        }
        setRunStreamState("error");
        closeStream();
        startFallbackPolling();
      };
    } else {
      startFallbackPolling();
    }

    void refreshFromApi();

    return () => {
      disposed = true;
      closeStream();
      if (fallbackTimer != null) {
        window.clearInterval(fallbackTimer);
      }
    };
  }, [
    backend,
    markArtifactReady,
    patchSession,
    runId,
    runStatus?.stage,
    runStatus?.status,
    selectedModel,
    setActiveTrainingRunId,
    setErrorMessage,
    setRunStatus,
    setRunStreamState,
    setSummary,
  ]);
}
