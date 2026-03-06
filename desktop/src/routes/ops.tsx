import { createFileRoute } from "@tanstack/react-router";
import { useCallback, useEffect, useState, type ReactNode } from "react";
import { resolveOpenBBBackend } from "../lib/openbbBackend";
import {
  fetchDataQualityHistory,
  fetchDataQualityLatest,
  fetchExperimentDetail,
  fetchExperimentList,
  fetchModelRegistryChallenger,
  fetchModelRegistryChampion,
  fetchModelRegistryHistory,
  fetchNotificationsHistory,
  fetchOpsStatus,
  fetchReportsHistory,
  fetchReportsLatest,
  fetchSchedulerStatus,
  probeQuantMlActivation,
} from "../lib/quantApi";
import type {
  DataQualityHistoryPayload,
  DataQualityLatestPayload,
  ExperimentListPayload,
  ExperimentRunItemPayload,
  ModelRegistryEntryPayload,
  ModelRegistryHistoryPayload,
  NotificationsHistoryPayload,
  OpsJobStatePayload,
  OpsStatusPayload,
  ReportsHistoryPayload,
  ReportsLatestPayload,
  SchedulerStatusPayload,
} from "../types/quant";

function toErrorMessage(error: unknown): string {
  return error instanceof Error ? error.message : "Request failed";
}

function StatusDot({ ok }: { ok: boolean }) {
  return (
    <span
      className={`inline-block h-2.5 w-2.5 rounded-full ${ok ? "bg-emerald-500" : "bg-amber-500"}`}
    />
  );
}

function Card({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <section className="rounded-sm border border-theme-outline bg-theme-primary p-3">
      <h3 className="mb-2 body-sm-medium text-theme-primary">{title}</h3>
      {children}
    </section>
  );
}

function RegistryRow({
  label,
  entry,
}: {
  label: string;
  entry?: ModelRegistryEntryPayload | null;
}) {
  if (!entry) {
    return (
      <div className="rounded-sm bg-theme-secondary p-2">
        <p className="body-xs-medium text-theme-primary">{label}</p>
        <p className="body-xxs-regular text-theme-muted">No entry</p>
      </div>
    );
  }
  return (
    <div className="rounded-sm bg-theme-secondary p-2">
      <p className="body-xs-medium text-theme-primary">{label}</p>
      <p className="body-xxs-regular text-theme-muted">
        {entry.model_name ?? "unknown"}
        {entry.model_version ? ` | ${entry.model_version}` : ""}
        {entry.run_id ? ` | ${entry.run_id}` : ""}
      </p>
    </div>
  );
}

function OpsPage() {
  const [baseUrl, setBaseUrl] = useState("");
  const [payload, setPayload] = useState<OpsStatusPayload | null>(null);
  const [dataQualityLatest, setDataQualityLatest] = useState<DataQualityLatestPayload | null>(null);
  const [dataQualityHistory, setDataQualityHistory] = useState<DataQualityHistoryPayload | null>(null);
  const [champion, setChampion] = useState<ModelRegistryEntryPayload | null>(null);
  const [challenger, setChallenger] = useState<ModelRegistryEntryPayload | null>(null);
  const [registryHistory, setRegistryHistory] = useState<ModelRegistryHistoryPayload | null>(null);
  const [reportsLatest, setReportsLatest] = useState<ReportsLatestPayload | null>(null);
  const [reportsHistory, setReportsHistory] = useState<ReportsHistoryPayload | null>(null);
  const [notificationsHistory, setNotificationsHistory] = useState<NotificationsHistoryPayload | null>(null);
  const [schedulerStatus, setSchedulerStatus] = useState<SchedulerStatusPayload | null>(null);
  const [experimentList, setExperimentList] = useState<ExperimentListPayload | null>(null);
  const [selectedExperiment, setSelectedExperiment] = useState<ExperimentRunItemPayload | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [activationMessage, setActivationMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [lastRefreshed, setLastRefreshed] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    if (!baseUrl) return;
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const next = await fetchOpsStatus(baseUrl);
      setPayload(next);
      const [
        nextDataQualityLatest,
        nextDataQualityHistory,
        nextChampion,
        nextChallenger,
        nextRegistryHistory,
        nextReportsLatest,
        nextReportsHistory,
        nextNotificationsHistory,
        nextSchedulerStatus,
        nextExperimentList,
      ] = await Promise.all([
        fetchDataQualityLatest(baseUrl),
        fetchDataQualityHistory(baseUrl),
        fetchModelRegistryChampion(baseUrl).catch(() => null),
        fetchModelRegistryChallenger(baseUrl).catch(() => null),
        fetchModelRegistryHistory(baseUrl).catch(() => ({ items: [] })),
        fetchReportsLatest(baseUrl).catch(() => ({ item: null })),
        fetchReportsHistory(baseUrl).catch(() => ({ items: [] })),
        fetchNotificationsHistory(baseUrl).catch(() => ({ items: [] })),
        fetchSchedulerStatus(baseUrl).catch(() => null),
        fetchExperimentList(baseUrl).catch(() => ({ items: [] })),
      ]);
      setDataQualityLatest(nextDataQualityLatest);
      setDataQualityHistory(nextDataQualityHistory);
      setChampion(nextChampion);
      setChallenger(nextChallenger);
      setRegistryHistory(nextRegistryHistory);
      setReportsLatest(nextReportsLatest);
      setReportsHistory(nextReportsHistory);
      setNotificationsHistory(nextNotificationsHistory);
      setSchedulerStatus(nextSchedulerStatus);
      setExperimentList(nextExperimentList);
      const latestExperimentRunId = nextExperimentList.items[0]?.run_id;
      if (latestExperimentRunId) {
        setSelectedExperiment(await fetchExperimentDetail(baseUrl, latestExperimentRunId));
      } else {
        setSelectedExperiment(null);
      }
      setLastRefreshed(new Date().toLocaleTimeString());
    } catch (error) {
      setErrorMessage(toErrorMessage(error));
    } finally {
      setIsLoading(false);
    }
  }, [baseUrl]);

  useEffect(() => {
    void (async () => {
      try {
        const backend = await resolveOpenBBBackend();
        setBaseUrl(backend.baseUrl);
        const activation = await probeQuantMlActivation(backend.baseUrl);
        if (!activation.available) {
          setActivationMessage(activation.detail || "quant_ml extension unavailable.");
        }
      } catch (error) {
        setErrorMessage(toErrorMessage(error));
      }
    })();
  }, []);

  useEffect(() => {
    if (!baseUrl) return;
    void refresh();
    const timer = window.setInterval(() => {
      void refresh();
    }, 5000);
    return () => window.clearInterval(timer);
  }, [baseUrl, refresh]);

  const jobs = payload?.jobs ?? [];
  const latestRuns = payload?.latest_runs ?? [];
  const reports = payload?.reports ?? [];
  const notificationFailures = payload?.notification_failures ?? [];
  const dataQuality = (dataQualityLatest ?? payload?.data_quality) as Record<string, unknown> | undefined;
  const modelRegistry = payload?.model_registry as Record<string, unknown> | undefined;
  const scheduler = (schedulerStatus ?? payload?.scheduler) as Record<string, unknown> | undefined;
  const executionMode = payload?.execution_mode as Record<string, unknown> | undefined;
  const directReports = reportsHistory?.items ?? [];
  const directNotifications = notificationsHistory?.items ?? [];

  return (
    <div className="h-full min-h-0 overflow-auto py-4">
      <div className="mb-3 flex items-center justify-between">
        <div>
          <h1 className="body-lg-medium text-theme-primary">Ops</h1>
          <p className="body-sm-regular text-theme-muted">
            Scheduler, quality gate, registry, reporting, and execution health.
          </p>
        </div>
        <div className="flex items-center gap-3">
          {lastRefreshed ? (
            <p className="body-xxs-regular text-theme-muted">Last: {lastRefreshed}</p>
          ) : null}
          <button
            type="button"
            className="button-secondary rounded-sm px-3 py-2 body-xs-medium"
            onClick={() => void refresh()}
            disabled={isLoading}
          >
            {isLoading ? "Refreshing..." : "Refresh"}
          </button>
        </div>
      </div>

      {errorMessage ? (
        <div className="mb-2 rounded-sm border border-red-500/60 bg-red-500/10 p-2">
          <p className="body-xs-medium text-red-400">{errorMessage}</p>
        </div>
      ) : null}
      {activationMessage ? (
        <div className="mb-2 rounded-sm border border-amber-500/60 bg-amber-500/10 p-2">
          <p className="body-xs-medium text-amber-300">{activationMessage}</p>
        </div>
      ) : null}

      <div className="grid grid-cols-1 gap-3 xl:grid-cols-2">
        <Card title="Jobs">
          <div className="space-y-1.5">
            {jobs.map((job: OpsJobStatePayload) => {
              const ok = String(job.last_status).toLowerCase() === "ok";
              return (
                <div key={job.job} className="flex items-center justify-between rounded-sm bg-theme-secondary p-2">
                  <div className="flex items-center gap-2">
                    <StatusDot ok={ok} />
                    <span className="body-xs-regular text-theme-primary">{job.job}</span>
                  </div>
                  <span className="body-xxs-regular text-theme-muted">
                    {job.last_status}
                    {job.last_run_id ? ` | ${job.last_run_id}` : ""}
                  </span>
                </div>
              );
            })}
          </div>
        </Card>

        <Card title="Data Quality">
          <div className="space-y-1.5">
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xs-medium text-theme-primary">
                {String(dataQuality?.qc_status ?? "UNKNOWN")}
              </p>
              <p className="body-xxs-regular text-theme-muted">
                {String(dataQuality?.gate_name ?? "No gate")}{" "}
                {dataQuality?.as_of_date ? `| ${String(dataQuality.as_of_date)}` : ""}
              </p>
            </div>
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">History Samples</p>
              <p className="body-xs-medium text-theme-primary">{dataQualityHistory?.items.length ?? 0}</p>
            </div>
          </div>
        </Card>

        <Card title="Model Registry">
          <div className="space-y-1.5">
            <RegistryRow
              label="Champion"
              entry={champion ?? (modelRegistry?.champion as ModelRegistryEntryPayload | undefined)}
            />
            <RegistryRow
              label="Challenger"
              entry={challenger ?? (modelRegistry?.challenger as ModelRegistryEntryPayload | undefined)}
            />
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">History Entries</p>
              <p className="body-xs-medium text-theme-primary">{registryHistory?.items.length ?? 0}</p>
            </div>
          </div>
        </Card>

        <Card title="Scheduler">
          <div className="space-y-1.5">
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Market Schedule</p>
              <p className="body-xs-medium text-theme-primary">
                {String((scheduler?.market_schedule as Record<string, unknown> | undefined)?.run_phase ?? "n/a")}
                {" | "}
                {String((scheduler?.market_schedule as Record<string, unknown> | undefined)?.primary_calendar ?? "n/a")}
              </p>
            </div>
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Timezone</p>
              <p className="body-xs-medium text-theme-primary">{String(schedulerStatus?.timezone ?? scheduler?.timezone ?? "n/a")}</p>
            </div>
          </div>
        </Card>

        <Card title="Execution Mode">
          <div className="rounded-sm bg-theme-secondary p-2">
            <p className="body-xs-medium text-theme-primary">
              {String(executionMode?.mode ?? "paper")}
            </p>
            <p className="body-xxs-regular text-theme-muted">
              {executionMode?.run_id ? `Run ${String(executionMode.run_id)} | ` : ""}
              kill_switch={String(executionMode?.kill_switch ?? false)}
            </p>
          </div>
        </Card>

        <Card title="Latest Runs">
          <div className="space-y-1.5">
            {latestRuns.slice(0, 6).map((run, index) => {
              const row = run as Record<string, unknown>;
              return (
                <div key={`${row.run_id ?? index}`} className="rounded-sm bg-theme-secondary p-2">
                  <p className="body-xs-medium text-theme-primary">{String(row.run_id ?? "unknown")}</p>
                  <p className="body-xxs-regular text-theme-muted">
                    {String(row.status ?? "unknown")}
                    {row.updated_at ? ` | ${String(row.updated_at)}` : ""}
                  </p>
                </div>
              );
            })}
          </div>
        </Card>

        <Card title="Reports">
          <div className="space-y-1.5">
            {reportsLatest?.item ? (
              <div className="rounded-sm bg-theme-secondary p-2">
                <p className="body-xs-medium text-theme-primary">{reportsLatest.item.report_type}</p>
                <p className="body-xxs-regular text-theme-muted break-all">{reportsLatest.item.report_path}</p>
              </div>
            ) : null}
            {(directReports.length > 0 ? directReports : reports).slice(0, 5).map((report, index) => {
              const row = report as Record<string, unknown>;
              return (
                <div key={`${row.report_path ?? index}`} className="rounded-sm bg-theme-secondary p-2">
                  <p className="body-xs-medium text-theme-primary">{String(row.report_type ?? "report")}</p>
                  <p className="body-xxs-regular text-theme-muted break-all">
                    {String(row.report_path ?? "")}
                  </p>
                </div>
              );
            })}
          </div>
        </Card>

        <Card title="Notification Failures">
          <div className="space-y-1.5">
            {(directNotifications.length === 0 && notificationFailures.length === 0) ? (
              <div className="rounded-sm bg-theme-secondary p-2">
                <p className="body-xs-regular text-theme-muted">No recent failures.</p>
              </div>
            ) : (
              (directNotifications.length > 0 ? directNotifications : notificationFailures).map((item, index) => {
                const row = item as Record<string, unknown>;
                return (
                  <div key={`${row.id ?? index}`} className="rounded-sm bg-theme-secondary p-2">
                    <p className="body-xs-medium text-theme-primary">
                      {String(row.channel ?? "channel")} | {String(row.status ?? "status")}
                    </p>
                    <p className="body-xxs-regular text-theme-muted">
                      {String(row.last_error ?? row.event_type ?? "")}
                    </p>
                  </div>
                );
              })
            )}
          </div>
        </Card>

        <Card title="Experiment Registry">
          <div className="space-y-1.5">
            <div className="rounded-sm bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Experiments</p>
              <p className="body-xs-medium text-theme-primary">{experimentList?.items.length ?? 0}</p>
            </div>
            {selectedExperiment ? (
              <div className="rounded-sm bg-theme-secondary p-2">
                <p className="body-xs-medium text-theme-primary">{selectedExperiment.run_id}</p>
                <p className="body-xxs-regular text-theme-muted">
                  {selectedExperiment.model_type ?? "unknown"}{" | "}
                  {selectedExperiment.dataset_version ?? "dataset:n/a"}
                </p>
              </div>
            ) : (
              <div className="rounded-sm bg-theme-secondary p-2">
                <p className="body-xs-regular text-theme-muted">No experiment detail available.</p>
              </div>
            )}
          </div>
        </Card>
      </div>

      {payload ? (
        <div className="mt-3 rounded-sm border border-theme-outline bg-theme-primary p-3">
          <h3 className="mb-2 body-sm-medium text-theme-primary">Raw Payload</h3>
          <pre className="max-h-64 overflow-auto rounded-sm border border-theme-outline bg-theme-secondary p-3 text-[11px] text-theme-muted">
            {JSON.stringify(payload, null, 2)}
          </pre>
        </div>
      ) : null}
    </div>
  );
}

export const Route = createFileRoute("/ops")({
  component: OpsPage,
});
