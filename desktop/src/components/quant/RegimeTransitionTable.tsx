import type { RegimeTransitionItem } from "../../types/macro";

interface RegimeTransitionTableProps {
  transitions: RegimeTransitionItem[];
}

export function RegimeTransitionTable({ transitions }: RegimeTransitionTableProps) {
  return (
    <div className="rounded-sm border border-theme-outline bg-theme-primary p-3">
      <p className="body-xs-medium text-theme-muted">Recent Transitions</p>
      {transitions.length === 0 ? (
        <p className="mt-2 body-xxs-regular text-theme-muted">No transition events</p>
      ) : (
        <div className="mt-2 max-h-[220px] overflow-auto">
          <table className="min-w-full text-left">
            <thead>
              <tr className="border-b border-theme-outline">
                <th className="px-2 py-1 body-xxs-medium text-theme-muted">Date</th>
                <th className="px-2 py-1 body-xxs-medium text-theme-muted">Axis</th>
                <th className="px-2 py-1 body-xxs-medium text-theme-muted">Delta</th>
                <th className="px-2 py-1 body-xxs-medium text-theme-muted">Severity</th>
              </tr>
            </thead>
            <tbody>
              {transitions.slice(0, 40).map((row, idx) => (
                <tr key={`${row.date}-${row.axis}-${idx}`} className="border-b border-theme-outline/30">
                  <td className="px-2 py-1 body-xxs-regular text-theme-primary">{row.date}</td>
                  <td className="px-2 py-1 body-xxs-regular text-theme-primary">{row.axis}</td>
                  <td className="px-2 py-1 body-xxs-regular text-theme-primary">{row.delta.toFixed(1)}</td>
                  <td className="px-2 py-1 body-xxs-regular text-theme-primary">{row.severity}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
