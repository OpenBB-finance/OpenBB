import type { BackendResolution } from "../../types/quant";
import { formatBackendDetail } from "../../lib/openbbBackend";
import { PanelCard } from "./PanelCard";

interface ConnectionStatusCardProps {
  resolution: BackendResolution | null;
  isLoading: boolean;
  onRetry: () => void;
  onGoBackends: () => void;
}

export function ConnectionStatusCard({
  resolution,
  isLoading,
  onRetry,
  onGoBackends,
}: ConnectionStatusCardProps) {
  const connected = resolution?.connected ?? false;

  return (
    <PanelCard title="Connection" description="OpenBB API health and resolver result">
      {isLoading ? (
        <p className="body-sm-regular text-theme-muted">Checking backend connection...</p>
      ) : (
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <span
              className={`inline-flex h-2 w-2 rounded-full ${connected ? "bg-green-500" : "bg-red-500"}`}
            />
            <span className="body-sm-medium text-theme-primary">
              {connected ? "OpenBB API connected" : "OpenBB API not connected"}
            </span>
          </div>

          {resolution ? (
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xs-regular text-theme-muted">
                URL: <span className="text-theme-primary">{resolution.baseUrl}</span>
              </p>
              <p className="body-xs-regular text-theme-muted">
                Source: <span className="text-theme-primary">{resolution.source}</span>
              </p>
              <p className="body-xs-regular text-theme-muted">
                Detail: <span className="text-theme-primary">{formatBackendDetail(resolution.detail, connected)}</span>
              </p>
            </div>
          ) : null}

          <div className="flex gap-2">
            <button
              type="button"
              className="button-secondary rounded-sm px-3 py-1 body-xs-medium"
              onClick={onRetry}
            >
              Retry
            </button>
            {!connected ? (
              <button
                type="button"
                className="button-neutral rounded-sm px-3 py-1 body-xs-medium"
                onClick={onGoBackends}
              >
                Go to Backends
              </button>
            ) : null}
          </div>
        </div>
      )}
    </PanelCard>
  );
}


