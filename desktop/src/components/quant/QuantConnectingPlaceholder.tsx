import { PanelCard } from "./PanelCard";

function SkeletonBlock({ className }: { className: string }) {
  return <div className={`animate-pulse rounded-sm bg-theme-secondary/70 ${className}`} />;
}

export function QuantConnectingPlaceholder() {
  return (
    <div className="space-y-4" aria-label="Connecting to Strategy Lab backend">
      <PanelCard title="Connecting to Strategy Lab" description="Resolving backend, activation, and baseline runtime metadata.">
        <div className="space-y-4">
          <SkeletonBlock className="h-5 w-48" />
          <SkeletonBlock className="h-16 w-full" />
        </div>
      </PanelCard>
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[360px_minmax(0,1fr)]">
        <PanelCard title="Controls" description="Universe, training, and backtest controls will appear once the backend is ready.">
          <div className="space-y-3">
            <SkeletonBlock className="h-10 w-full" />
            <SkeletonBlock className="h-20 w-full" />
            <SkeletonBlock className="h-20 w-full" />
          </div>
        </PanelCard>
        <div className="space-y-4">
          <PanelCard title="Results" description="Connection health, run status, and artifacts will hydrate after bootstrap completes.">
            <div className="space-y-3">
              <SkeletonBlock className="h-24 w-full" />
              <SkeletonBlock className="h-40 w-full" />
              <SkeletonBlock className="h-40 w-full" />
            </div>
          </PanelCard>
        </div>
      </div>
    </div>
  );
}
