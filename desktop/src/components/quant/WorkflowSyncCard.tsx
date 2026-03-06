import type { ModelName, WorkflowArtifactsReadyPayload } from "../../types/quant";
import { PanelCard } from "./PanelCard";

interface WorkflowSyncCardProps {
  runId: string | null;
  selectedModel: ModelName;
  dashboardLink: string;
  sessionRunId: string;
  sessionModelName: ModelName;
  sessionDataTimestamp?: string | null;
  artifactsReady: WorkflowArtifactsReadyPayload;
}

function StatusBadge({ label, ready }: { label: string; ready: boolean }) {
  return (
    <div className="rounded-sm bg-theme-secondary p-2">
      <p className="body-xxs-regular text-theme-muted">{label}</p>
      <p className="body-xs-medium text-theme-primary">{ready ? "Ready" : "Not Ready"}</p>
    </div>
  );
}

export function WorkflowSyncCard({
  runId,
  selectedModel,
  dashboardLink,
  sessionRunId,
  sessionModelName,
  sessionDataTimestamp,
  artifactsReady,
}: WorkflowSyncCardProps) {
  return (
    <PanelCard title="Workflow Sync" description="Shared run/model session with Dashboard">
      <div className="space-y-2">
        <div className="rounded-sm bg-theme-secondary p-2">
          <p className="body-xs-regular text-theme-muted">
            Run: <span className="text-theme-primary">{sessionRunId || "-"}</span>
          </p>
          <p className="body-xs-regular text-theme-muted">
            Model: <span className="text-theme-primary">{sessionModelName}</span>
          </p>
          <p className="body-xs-regular text-theme-muted">
            Dashboard timestamp:{" "}
            <span className="text-theme-primary">{sessionDataTimestamp || "-"}</span>
          </p>
        </div>
        <div className="grid grid-cols-2 gap-2">
          <StatusBadge label="Predictions" ready={artifactsReady.predictions} />
          <StatusBadge label="Backtest" ready={artifactsReady.backtest} />
          <StatusBadge label="Signals" ready={artifactsReady.signals} />
          <StatusBadge label="Portfolio Rationale" ready={artifactsReady.portfolio_current} />
        </div>
        <a
          className="button-secondary inline-flex rounded-sm px-3 py-2 body-xs-medium"
          href={dashboardLink}
          aria-label={`View this run in Dashboard (run: ${runId || "none"}, model: ${selectedModel})`}
        >
          View In Dashboard
        </a>
      </div>
    </PanelCard>
  );
}
