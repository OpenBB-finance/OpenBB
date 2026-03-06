import type { MacroAlertsResponse } from "../../types/macro";

interface MacroAlertsPanelProps {
  alerts: MacroAlertsResponse | null;
}

export function MacroAlertsPanel({ alerts }: MacroAlertsPanelProps) {
  const current = alerts?.current ?? [];
  const historyCount = alerts?.history?.length ?? 0;

  return (
    <div className="rounded-sm border border-theme-outline bg-theme-primary p-3">
      <p className="body-xs-medium text-theme-muted">Macro Alerts</p>
      {current.length === 0 ? (
        <p className="mt-2 body-xxs-regular text-theme-muted">No active alerts</p>
      ) : (
        <ul className="mt-2 space-y-1">
          {current.slice(0, 8).map((item, idx) => (
            <li key={`${item.rule_id}-${idx}`} className="rounded-sm bg-theme-secondary px-2 py-1">
              <p className="body-xxs-medium text-theme-primary">{item.message}</p>
              <p className="body-xxs-regular text-theme-muted">{item.severity} | {item.triggered_at}</p>
            </li>
          ))}
        </ul>
      )}
      <p className="mt-2 body-xxs-regular text-theme-muted">History: {historyCount}</p>
    </div>
  );
}
