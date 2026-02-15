import type { RunStatusPayload } from "../../types/quant";
import { PanelCard } from "./PanelCard";

interface RunStatusCardProps {
  run: RunStatusPayload | null;
  isLiveRun?: boolean;
}

export function RunStatusCard({ run, isLiveRun = false }: RunStatusCardProps) {
  const isLive = isLiveRun || run?.status === "queued" || run?.status === "running";

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
