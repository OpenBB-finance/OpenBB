interface RegimeLiveIndicatorProps {
  connected: boolean;
  lastUpdated?: string | null;
}

export function RegimeLiveIndicator({ connected, lastUpdated }: RegimeLiveIndicatorProps) {
  return (
    <div className="flex items-center gap-2 rounded-sm border border-theme-outline bg-theme-secondary px-2 py-1">
      <span className={`inline-block h-2 w-2 rounded-full ${connected ? "bg-emerald-400" : "bg-slate-500"}`} />
      <span className="body-xxs-medium text-theme-primary">{connected ? "LIVE" : "OFFLINE"}</span>
      {lastUpdated ? <span className="body-xxs-regular text-theme-muted">{lastUpdated}</span> : null}
    </div>
  );
}
