import type { BackendResolution, DashboardHealthPayload } from "../../types/quant";
import { formatBackendDetail } from "../../lib/openbbBackend";
import { PanelCard } from "./PanelCard";

interface ConnectionStatusCardProps {
  resolution: BackendResolution | null;
  isLoading: boolean;
  health: DashboardHealthPayload | null;
  isHealthLoading?: boolean;
  healthError?: string | null;
  onRetry: () => void;
  onGoBackends: () => void;
}

function formatIsoLike(value?: string | null): string {
  if (!value) {
    return "-";
  }
  const asDate = new Date(value);
  if (!Number.isFinite(asDate.getTime())) {
    return value;
  }
  return asDate.toLocaleString();
}

function formatDateOrIso(value?: string | null): string {
  if (!value) {
    return "-";
  }
  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) {
    return value;
  }
  return formatIsoLike(value);
}

function formatPct(value?: number | null): string {
  if (typeof value !== "number") {
    return "-";
  }
  return `${(value * 100).toFixed(1)}%`;
}

type HealthSeverity = "ok" | "warn" | "critical";

function severityClass(severity: HealthSeverity): string {
  if (severity === "critical") {
    return "text-red-300";
  }
  if (severity === "warn") {
    return "text-amber-300";
  }
  return "text-emerald-300";
}

export function ConnectionStatusCard({
  resolution,
  isLoading,
  health,
  isHealthLoading = false,
  healthError = null,
  onRetry,
  onGoBackends,
}: ConnectionStatusCardProps) {
  const connected = resolution?.connected ?? false;
  const diskFreeLabel = typeof health?.disk_free_gb === "number" ? `${health.disk_free_gb.toFixed(1)} GB` : "-";
  const freshnessDays = health?.data_freshness_days ?? health?.staleness_days ?? null;
  const freshnessLabel = freshnessDays == null ? "-" : `${freshnessDays} day(s)`;
  const supportedModes =
    health?.mode_supported && health.mode_supported.length > 0 ? health.mode_supported.join(", ") : "-";
  const strategyScore =
    health && typeof health.strategy_health?.score === "number"
      ? health.strategy_health.score
      : null;
  const statusSeverity: HealthSeverity = !health || health.status === "ok" ? "ok" : "warn";
  const freshnessSeverity: HealthSeverity =
    freshnessDays == null ? "ok" : freshnessDays > 7 ? "critical" : freshnessDays > 3 ? "warn" : "ok";
  const diskSeverity: HealthSeverity =
    typeof health?.disk_free_gb !== "number"
      ? "ok"
      : health.disk_free_gb < 5
        ? "critical"
        : health.disk_free_gb < 10
          ? "warn"
          : "ok";
  const fredSeverity: HealthSeverity =
    !health || health.fred_api_status === "ok"
      ? "ok"
      : health.fred_api_status === "degraded"
        ? "warn"
        : "critical";

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

          {connected ? (
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xs-medium text-theme-primary">Dashboard Health</p>
              {isHealthLoading ? (
                <p className="body-xs-regular text-theme-muted">Loading health metrics...</p>
              ) : null}
              {health ? (
                <div className="space-y-0.5">
                  <p className="body-xs-regular text-theme-muted">
                    Status: <span className={severityClass(statusSeverity)}>{health.status}</span>
                  </p>
                  <p className="body-xs-regular text-theme-muted">
                    Data freshness: <span className={severityClass(freshnessSeverity)}>{freshnessLabel}</span>
                  </p>
                  <p className="body-xs-regular text-theme-muted">
                    Latest market date: <span className="text-theme-primary">{formatDateOrIso(health.latest_market_date)}</span>
                  </p>
                  <p className="body-xs-regular text-theme-muted">
                    Disk free: <span className={severityClass(diskSeverity)}>{diskFreeLabel}</span>
                  </p>
                  <p className="body-xs-regular text-theme-muted">
                    Cache warm ratio: <span className="text-theme-primary">{formatPct(health.cache_warm_ratio)}</span>
                  </p>
                  <p className="body-xs-regular text-theme-muted">
                    Supported modes: <span className="text-theme-primary">{supportedModes}</span>
                  </p>
                  <p className="body-xs-regular text-theme-muted">
                    Strategy score: <span className="text-theme-primary">{strategyScore == null ? "-" : strategyScore.toFixed(2)}</span>
                  </p>
                  <p className="body-xs-regular text-theme-muted">
                    FRED API: <span className={severityClass(fredSeverity)}>{health.fred_api_status ?? "unavailable"}</span>
                  </p>
                  <p className="body-xs-regular text-theme-muted">
                    Last successful run: <span className="text-theme-primary">{formatIsoLike(health.last_successful_run_at)}</span>
                  </p>
                </div>
              ) : null}
              {!health && healthError ? (
                <p className="body-xs-regular text-amber-300">Health details unavailable: {healthError}</p>
              ) : null}
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
