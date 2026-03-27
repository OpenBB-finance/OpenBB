import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useCallback, useEffect, useMemo, useState, type ReactNode } from "react";
import { attachMacroStudyReport, fetchMacroStudies } from "../lib/macroApi";
import { resolveOpenBBBackend } from "../lib/openbbBackend";
import { openPathSafely } from "../lib/pathOpener";
import {
  fetchModelRegistryChallenger,
  fetchModelRegistryChampion,
  fetchNotificationsHistory,
  fetchOpsIssues,
  fetchReportsHistory,
  fetchReportsLatest,
  fetchSchedulerStatus,
} from "../lib/quantApi";
import type {
  ModelRegistryEntryPayload,
  NotificationItemPayload,
  OpsIssueItemPayload,
  OpsIssueQueuePayload,
  ReportRunItemPayload,
  SchedulerStatusPayload,
} from "../types/quant";
import type { MacroStudyPayload } from "../types/macro";

function toErrorMessage(error: unknown): string {
  return error instanceof Error ? error.message : "Request failed";
}

function buildRouteHref(route: string, search?: Record<string, string>): string {
  const params = new URLSearchParams();
  Object.entries(search ?? {}).forEach(([key, value]) => {
    if (value) {
      params.set(key, value);
    }
  });
  const query = params.toString();
  return `${route}${query ? `?${query}` : ""}`;
}

function folderFromPath(path: string): string {
  const normalized = path.replace(/\\/g, "/");
  const index = normalized.lastIndexOf("/");
  return index > 0 ? normalized.slice(0, index) : path;
}

async function copyText(value: string): Promise<void> {
  if (typeof navigator !== "undefined" && navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(value);
    return;
  }
  if (typeof document === "undefined") {
    throw new Error("Clipboard is unavailable in this runtime.");
  }
  const textArea = document.createElement("textarea");
  textArea.value = value;
  textArea.style.position = "fixed";
  textArea.style.opacity = "0";
  document.body.appendChild(textArea);
  textArea.select();
  document.execCommand("copy");
  document.body.removeChild(textArea);
}

function Card({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="rounded-sm border border-theme-outline bg-theme-primary p-3">
      <h3 className="mb-2 body-sm-medium text-theme-primary">{title}</h3>
      {children}
    </section>
  );
}

function badgeClass(severity: string): string {
  if (severity === "critical") return "bg-red-500/15 text-red-300";
  if (severity === "warning") return "bg-amber-500/15 text-amber-300";
  return "bg-theme-secondary text-theme-muted";
}

function buildSymbolLabRouteSearch(symbol: string, source: string, reportPath?: string) {
  return {
    symbol,
    source,
    studyId: undefined,
    runId: undefined,
    signalId: undefined,
    reportPath: reportPath ?? undefined,
  };
}

function RegistryRow({ label, entry }: { label: string; entry?: ModelRegistryEntryPayload | null }) {
  return (
    <div className="rounded-sm bg-theme-secondary p-2">
      <p className="body-xs-medium text-theme-primary">{label}</p>
      <p className="body-xxs-regular text-theme-muted">
        {entry?.model_name ?? "No entry"}
        {entry?.model_version ? ` | ${entry.model_version}` : ""}
        {entry?.run_id ? ` | ${entry.run_id}` : ""}
      </p>
    </div>
  );
}

function InternalRouteLink({
  route,
  search,
  className,
  children,
}: {
  route: string;
  search?: Record<string, string>;
  className?: string;
  children: React.ReactNode;
}) {
  const navigate = useNavigate();
  const href = buildRouteHref(route, search);

  return (
    <a
      href={href}
      className={className}
      onClick={(event) => {
        event.preventDefault();
        void navigate({
          to: route,
          search: search ?? {},
        });
      }}
    >
      {children}
    </a>
  );
}

function OpsPage() {
  const navigate = useNavigate();
  const [baseUrl, setBaseUrl] = useState("");
  const [issues, setIssues] = useState<OpsIssueQueuePayload | null>(null);
  const [reports, setReports] = useState<ReportRunItemPayload[]>([]);
  const [latestReport, setLatestReport] = useState<ReportRunItemPayload | null>(null);
  const [champion, setChampion] = useState<ModelRegistryEntryPayload | null>(null);
  const [challenger, setChallenger] = useState<ModelRegistryEntryPayload | null>(null);
  const [scheduler, setScheduler] = useState<SchedulerStatusPayload | null>(null);
  const [notifications, setNotifications] = useState<NotificationItemPayload[]>([]);
  const [macroStudies, setMacroStudies] = useState<MacroStudyPayload[]>([]);
  const [selectedStudyId, setSelectedStudyId] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const [pathActionError, setPathActionError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const refresh = useCallback(async () => {
    if (!baseUrl) return;
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const [
        nextIssues,
        nextReportsLatest,
        nextReportsHistory,
        nextChampion,
        nextChallenger,
        nextScheduler,
        nextNotifications,
        nextStudies,
      ] = await Promise.all([
        fetchOpsIssues(baseUrl, 8),
        fetchReportsLatest(baseUrl).catch(() => ({ item: null })),
        fetchReportsHistory(baseUrl, { limit: 8 }).catch(() => ({ items: [] })),
        fetchModelRegistryChampion(baseUrl).catch(() => null),
        fetchModelRegistryChallenger(baseUrl).catch(() => null),
        fetchSchedulerStatus(baseUrl).catch(() => null),
        fetchNotificationsHistory(baseUrl).catch(() => ({ items: [] })),
        fetchMacroStudies(baseUrl).catch(() => ({ items: [], status: "error" })),
      ]);
      setIssues(nextIssues);
      setLatestReport(nextReportsLatest.item ?? null);
      setReports(nextReportsHistory.items ?? []);
      setChampion(nextChampion);
      setChallenger(nextChallenger);
      setScheduler(nextScheduler);
      setNotifications(nextNotifications.items ?? []);
      setMacroStudies(nextStudies.items ?? []);
      if (!selectedStudyId && (nextStudies.items?.length ?? 0) > 0) {
        setSelectedStudyId(nextStudies.items[0].id ?? "");
      }
    } catch (error) {
      setErrorMessage(toErrorMessage(error));
    } finally {
      setIsLoading(false);
    }
  }, [baseUrl, selectedStudyId]);

  useEffect(() => {
    void (async () => {
      try {
        const backend = await resolveOpenBBBackend();
        if (!backend.connected) {
          setErrorMessage("OpenBB backend is not connected.");
          return;
        }
        setBaseUrl(backend.baseUrl);
      } catch (error) {
        setErrorMessage(toErrorMessage(error));
      }
    })();
  }, []);

  useEffect(() => {
    if (!baseUrl) return;
    void refresh();
  }, [baseUrl, refresh]);

  const reportItems = useMemo(() => {
    const seen = new Set<string>();
    return [latestReport, ...reports].filter((item): item is ReportRunItemPayload => {
      if (!item?.report_path || seen.has(item.report_path)) {
        return false;
      }
      seen.add(item.report_path);
      return true;
    });
  }, [latestReport, reports]);

  async function handleAttachReport(report: ReportRunItemPayload) {
    if (!baseUrl || !selectedStudyId) {
      setErrorMessage("Select a macro study before attaching a report.");
      return;
    }
    try {
      setActionMessage(null);
      await attachMacroStudyReport(baseUrl, selectedStudyId, {
        report_id: report.id ?? undefined,
        report_path: report.report_path,
        title: report.title ?? report.report_type,
        source_run_id: report.run_id ?? undefined,
        symbols: report.symbols ?? [],
      });
      setActionMessage(`Attached ${report.title ?? report.report_type} to macro study ${selectedStudyId}.`);
      await refresh();
    } catch (error) {
      setErrorMessage(toErrorMessage(error));
    }
  }

  async function handleOpenReportPath(path: string) {
    try {
      setPathActionError(null);
      await openPathSafely(path);
    } catch (error) {
      setPathActionError(toErrorMessage(error));
    }
  }

  async function handleCopyReportPath(path: string) {
    try {
      await copyText(path);
      setPathActionError(null);
      setActionMessage(`Copied path: ${path}`);
    } catch (error) {
      setPathActionError(toErrorMessage(error));
    }
  }

  return (
    <div className="h-full min-h-0 overflow-auto py-4">
      <div className="mb-3 flex items-center justify-between">
        <div>
          <h1 className="body-lg-medium text-theme-primary">Ops</h1>
          <p className="body-sm-regular text-theme-muted">
            Issue queue, report center, registry, scheduler state, and notification failures.
          </p>
        </div>
        <button
          type="button"
          className="button-secondary rounded-sm px-3 py-2 body-xs-medium"
          onClick={() => void refresh()}
          disabled={isLoading}
        >
          {isLoading ? "Refreshing..." : "Refresh"}
        </button>
      </div>

      {errorMessage ? (
        <div className="mb-3 rounded-sm border border-red-500/60 bg-red-500/10 p-2">
          <p className="body-xs-medium text-red-400">{errorMessage}</p>
        </div>
      ) : null}
      {actionMessage ? (
        <div className="mb-3 rounded-sm border border-emerald-500/40 bg-emerald-500/10 p-2">
          <p className="body-xs-medium text-emerald-300">{actionMessage}</p>
        </div>
      ) : null}

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-[minmax(0,1.2fr)_minmax(0,0.8fr)]">
        <Card title="Issue Queue">
          <div className="space-y-2">
            {(issues?.items ?? []).length ? (
              issues?.items.map((item: OpsIssueItemPayload) => (
                <div key={item.id} className="rounded-sm border border-theme-outline bg-theme-secondary p-3">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <p className="body-xs-medium text-theme-primary">{item.title}</p>
                      <p className="mt-1 body-xxs-regular text-theme-muted">{item.impact}</p>
                    </div>
                    <span className={`rounded-sm px-2 py-0.5 body-xxs-medium ${badgeClass(item.severity)}`}>
                      {item.severity}
                    </span>
                  </div>
                  <p className="mt-2 body-xs-regular text-theme-muted">{item.suggested_action}</p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <InternalRouteLink
                      route={item.target_route}
                      search={item.target_search}
                      className="rounded-sm border border-theme-outline px-3 py-1 body-xs-medium text-theme-primary hover:text-theme-accent"
                    >
                      Open target
                    </InternalRouteLink>
                    <span className="body-xxs-regular text-theme-muted">
                      source: {item.source ?? "ops"} | status: {item.status}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="rounded-sm border border-theme-outline bg-theme-secondary p-3 body-xs-regular text-theme-muted">
                No issue was returned by the current ops queue.
              </div>
            )}
          </div>
        </Card>

        <div className="space-y-4">
          <Card title="Report Center">
            <div className="mb-3">
              <label className="body-xxs-regular text-theme-muted" htmlFor="ops-study-attach">
                Attach reports to macro study
              </label>
              <select
                id="ops-study-attach"
                value={selectedStudyId}
                onChange={(event) => setSelectedStudyId(event.target.value)}
                className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary px-2 py-2 body-xs-regular text-theme-primary"
              >
                <option value="">Select study</option>
                {macroStudies.map((study) => (
                  <option key={study.id ?? study.name} value={study.id ?? ""}>
                    {study.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="space-y-2">
              {reportItems.length ? (
                reportItems.map((report) => (
                  <div key={report.report_path} className="rounded-sm border border-theme-outline bg-theme-secondary p-3">
                    <p className="body-xs-medium text-theme-primary">{report.title ?? report.report_type}</p>
                    <p className="mt-1 body-xxs-regular break-all text-theme-muted">{report.report_path}</p>
                    {pathActionError ? (
                      <div className="mt-2 rounded-sm border border-amber-500/40 bg-amber-500/10 px-2 py-2">
                        <p className="body-xxs-regular text-amber-200">{pathActionError}</p>
                      </div>
                    ) : null}
                    <div className="mt-3 flex flex-wrap gap-2">
                      <button
                        type="button"
                        className="rounded-sm border border-theme-outline px-3 py-1 body-xs-medium text-theme-primary"
                        onClick={() => void handleOpenReportPath(report.report_path)}
                      >
                        Open Report
                      </button>
                      <button
                        type="button"
                        className="rounded-sm border border-theme-outline px-3 py-1 body-xs-medium text-theme-primary"
                        onClick={() => void handleOpenReportPath(folderFromPath(report.report_path))}
                      >
                        Open Folder
                      </button>
                      <button
                        type="button"
                        className="rounded-sm border border-theme-outline px-3 py-1 body-xs-medium text-theme-primary"
                        onClick={() => void handleCopyReportPath(report.report_path)}
                      >
                        Copy Path
                      </button>
                      <button
                        type="button"
                        className="rounded-sm border border-theme-outline px-3 py-1 body-xs-medium text-theme-primary"
                        onClick={() => void handleAttachReport(report)}
                      >
                        Attach to Study
                      </button>
                      {report.symbols?.map((symbol) => (
                        <a
                          key={`${report.report_path}-${symbol}`}
                          href={buildRouteHref("/finance", {
                            symbol,
                            source: "ops",
                            reportPath: report.report_path,
                          })}
                          className="rounded-full border border-theme-outline px-3 py-1 body-xxs-medium text-theme-primary hover:text-theme-accent"
                          onClick={(event) => {
                            event.preventDefault();
                            void navigate({
                              to: "/finance",
                              search: buildSymbolLabRouteSearch(symbol, "ops", report.report_path),
                            });
                          }}
                        >
                          {symbol}
                        </a>
                      ))}
                    </div>
                  </div>
                ))
              ) : (
                <div className="rounded-sm border border-theme-outline bg-theme-secondary p-3 body-xs-regular text-theme-muted">
                  No report artifact is available yet.
                </div>
              )}
            </div>
          </Card>

          <Card title="Registry">
            <div className="space-y-2">
              <RegistryRow label="Champion" entry={champion} />
              <RegistryRow label="Challenger" entry={challenger} />
            </div>
          </Card>

          <Card title="Scheduler">
            <div className="space-y-2">
              <div className="rounded-sm bg-theme-secondary p-2">
                <p className="body-xxs-regular text-theme-muted">Timezone</p>
                <p className="body-xs-medium text-theme-primary">{scheduler?.timezone ?? "n/a"}</p>
              </div>
              <div className="rounded-sm bg-theme-secondary p-2">
                <p className="body-xxs-regular text-theme-muted">Market phase</p>
                <p className="body-xs-medium text-theme-primary">
                  {String(scheduler?.market_schedule?.run_phase ?? "n/a")}
                </p>
              </div>
            </div>
          </Card>

          <Card title="Notifications">
            <div className="space-y-2">
              {notifications.length ? (
                notifications.slice(0, 6).map((item) => (
                  <details key={item.id} className="rounded-sm bg-theme-secondary p-2">
                    <summary className="cursor-pointer body-xs-medium text-theme-primary">
                      {item.channel ?? "channel"} | {item.status ?? "status"}
                    </summary>
                    <p className="mt-2 body-xxs-regular text-theme-muted">
                      {item.last_error ?? item.event_type ?? "No extra detail"}
                    </p>
                  </details>
                ))
              ) : (
                <div className="rounded-sm border border-theme-outline bg-theme-secondary p-3 body-xs-regular text-theme-muted">
                  No recent notification failure was returned.
                </div>
              )}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}

export const Route = createFileRoute("/ops")({
  component: OpsPage,
});
