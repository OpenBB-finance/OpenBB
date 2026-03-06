import type { RunStatusPayload } from "../../types/quant";
import { PanelCard } from "./PanelCard";

type RunStreamState =
  | "idle"
  | "connecting"
  | "ready"
  | "streaming"
  | "fallback"
  | "done"
  | "timeout"
  | "error";

interface RunStatusCardProps {
  run: RunStatusPayload | null;
  isLiveRun?: boolean;
  streamState?: RunStreamState;
}

function streamBadge(state: RunStreamState): { label: string; className: string } {
  switch (state) {
    case "connecting":
      return { label: "Stream: connecting", className: "bg-blue-500/20 text-blue-300 border-blue-500/30" };
    case "ready":
      return { label: "Stream: ready", className: "bg-cyan-500/20 text-cyan-300 border-cyan-500/30" };
    case "streaming":
      return { label: "Stream: live", className: "bg-emerald-500/20 text-emerald-300 border-emerald-500/30" };
    case "fallback":
      return { label: "Stream: polling fallback", className: "bg-amber-500/20 text-amber-300 border-amber-500/30" };
    case "done":
      return { label: "Stream: done", className: "bg-green-500/20 text-green-300 border-green-500/30" };
    case "timeout":
      return { label: "Stream: timeout", className: "bg-orange-500/20 text-orange-300 border-orange-500/30" };
    case "error":
      return { label: "Stream: error", className: "bg-red-500/20 text-red-300 border-red-500/30" };
    case "idle":
    default:
      return { label: "Stream: idle", className: "bg-theme-secondary text-theme-muted border-theme-outline" };
  }
}

export function RunStatusCard({ run, isLiveRun = false, streamState = "idle" }: RunStatusCardProps) {
  const isLive = isLiveRun || run?.status === "queued" || run?.status === "running";
  const badge = streamBadge(streamState);

  return (
    <PanelCard title="Training Status" description="Run state and latest logs">
      {!run ? (
        <p className="body-sm-regular text-theme-muted">Start training to see run status.</p>
      ) : (
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <div>
              <p className="body-sm-medium text-theme-primary">Run ID: {run.run_id}</p>
              <p className="body-xs-regular text-theme-muted">
                Status: {run.status} / Stage: {run.stage}
              </p>
              <p className="body-xs-regular text-theme-muted">
                Mode: {isLive ? "Live training" : "Loaded snapshot"}
              </p>
              <p className="body-xs-regular text-theme-muted">
                <span className={`inline-flex rounded border px-1.5 py-0.5 ${badge.className}`}>{badge.label}</span>
              </p>
            </div>
            <p className="body-sm-medium text-theme-primary">{run.progress}%</p>
          </div>

          {!isLive && run.status === "completed" ? (
            <p className="body-xs-regular text-theme-muted">
              This run is already completed. Progress stays at 100% for snapshots. Start training to create a new run.
            </p>
          ) : null}

          <div className="h-2 w-full rounded bg-theme-secondary">
            <div
              className={`h-2 rounded ${
                run.status === "failed"
                  ? "bg-red-500"
                  : run.status === "completed"
                    ? "bg-green-500"
                    : "bg-theme-accent"
              }`}
              style={{ width: `${run.progress}%` }}
            />
          </div>

          {run.error ? <p className="body-xs-medium text-red-400">Error: {run.error}</p> : null}

          <div className="max-h-32 overflow-auto rounded-sm bg-theme-secondary p-2">
            <ul className="space-y-1">
              {run.logs_tail.length === 0 ? (
                <li className="body-xs-regular text-theme-muted">No logs yet.</li>
              ) : (
                run.logs_tail.map((line, index) => (
                  <li key={`${line}-${index}`} className="body-xs-regular text-theme-primary">
                    {line}
                  </li>
                ))
              )}
            </ul>
          </div>
        </div>
      )}
    </PanelCard>
  );
}
