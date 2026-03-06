import type { RunListItemPayload } from "../../types/quant";

interface RunSelectorCardProps {
  runIdInput: string;
  recentRuns: RunListItemPayload[];
  canUseApi: boolean;
  onRunIdInputChange: (value: string) => void;
  onLoadRun: () => void;
}

export function RunSelectorCard({
  runIdInput,
  recentRuns,
  canUseApi,
  onRunIdInputChange,
  onLoadRun,
}: RunSelectorCardProps) {
  const actionableRuns = recentRuns.filter((run) => run.actionable_backtest);
  const nonActionableRuns = recentRuns.filter((run) => !run.actionable_backtest);

  return (
    <>
      <div className="grid grid-cols-[minmax(0,1fr)_auto] gap-2">
        <label className="body-xs-medium text-theme-muted">
          Run ID
          <input
            type="text"
            className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary p-2 body-xs-regular text-theme-primary"
            value={runIdInput}
            onChange={(event) => onRunIdInputChange(event.target.value)}
            placeholder="Paste existing run_id"
          />
        </label>
        <button
          type="button"
          className="button-secondary mb-0.5 self-end rounded-sm px-3 py-2 body-xs-medium"
          onClick={onLoadRun}
          disabled={!canUseApi || !runIdInput.trim()}
        >
          Load Run
        </button>
      </div>
      {recentRuns.length > 0 ? (
        <label className="body-xs-medium text-theme-muted">
          Recent Runs
          <select
            className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary p-2 body-xs-regular text-theme-primary"
            value={runIdInput}
            onChange={(event) => onRunIdInputChange(event.target.value)}
          >
            <option value="">Select a recent run...</option>
            {actionableRuns.length > 0 ? (
              <optgroup label="Actionable (completed)">
                {actionableRuns.map((run) => (
                  <option key={run.run_id} value={run.run_id}>
                    {run.run_id} | {run.status} | {run.stage || "-"}
                  </option>
                ))}
              </optgroup>
            ) : null}
            {nonActionableRuns.length > 0 ? (
              <optgroup label="Non-actionable">
                {nonActionableRuns.map((run) => (
                  <option key={run.run_id} value={run.run_id} disabled>
                    {run.run_id} | {run.status} | {run.stage || "-"} (not ready)
                  </option>
                ))}
              </optgroup>
            ) : null}
          </select>
        </label>
      ) : null}
    </>
  );
}
