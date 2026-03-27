import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { PanelCard } from "../components/quant/PanelCard";
import { resolveOpenBBBackend } from "../lib/openbbBackend";
import { fetchWorkspaceBrief } from "../lib/quantApi";
import { buildSymbolLabHref } from "../lib/symbolLabNavigation";
import type {
  WorkspaceActionItem,
  WorkspaceBriefPayload,
  WorkspacePortfolioContributorPayload,
} from "../types/quant";

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

function formatPct(value: number | null | undefined, digits = 2): string {
  if (typeof value !== "number" || Number.isNaN(value)) {
    return "n/a";
  }
  return `${(value * 100).toFixed(digits)}%`;
}

function buildSymbolLabRouteSearch(symbol: string, source: string, studyId?: string) {
  return {
    symbol,
    source,
    studyId: studyId ?? undefined,
    runId: undefined,
    signalId: undefined,
    reportPath: undefined,
  };
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

function ActionLink({ item }: { item: WorkspaceActionItem }) {
  return (
    <InternalRouteLink
      route={item.target_route}
      search={item.target_search}
      className="block rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2 hover:text-theme-accent"
    >
      <div className="body-xs-medium text-theme-primary">{item.title}</div>
      <div className="body-xxs-regular text-theme-muted">{item.detail}</div>
    </InternalRouteLink>
  );
}

function ContributorLinks({ items }: { items: WorkspacePortfolioContributorPayload[] }) {
  const navigate = useNavigate();
  if (!items.length) {
    return <div className="body-xs-regular text-theme-muted">No top contributors.</div>;
  }
  return (
    <div className="flex flex-wrap gap-2">
      {items.map((item) => (
        <a
          key={item.symbol}
          href={buildSymbolLabHref({ symbol: item.symbol, source: "workspace" })}
          className="rounded-full border border-theme-outline px-3 py-1 body-xs-medium text-theme-primary hover:text-theme-accent"
          onClick={(event) => {
            event.preventDefault();
            void navigate({
              to: "/finance",
              search: buildSymbolLabRouteSearch(item.symbol, "workspace"),
            });
          }}
        >
          {item.symbol} | {formatPct(item.contribution)}
        </a>
      ))}
    </div>
  );
}

function WorkspacePage() {
  const navigate = useNavigate();
  const [brief, setBrief] = useState<WorkspaceBriefPayload | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        setIsLoading(true);
        const backend = await resolveOpenBBBackend();
        if (!backend.connected) {
          setErrorMessage("OpenBB backend is not connected.");
          setBrief(null);
          return;
        }
        const payload = await fetchWorkspaceBrief(backend.baseUrl);
        setBrief(payload);
        setErrorMessage(null);
      } catch (error) {
        setErrorMessage(error instanceof Error ? error.message : "Failed to load workspace brief.");
        setBrief(null);
      } finally {
        setIsLoading(false);
      }
    };
    void load();
  }, []);

  return (
    <div className="h-full min-h-0 overflow-auto py-4">
      <div className="mb-4">
        <h1 className="body-lg-medium text-theme-primary">Workspace</h1>
        <p className="body-sm-regular text-theme-muted">
          Today&apos;s brief across macro research, strategy promotion, execution readiness, and ops exceptions.
        </p>
      </div>

      {errorMessage ? (
        <div className="mb-4 rounded-md border border-red-500/40 bg-red-500/10 px-4 py-3 body-sm-regular text-red-200">
          {errorMessage}
        </div>
      ) : null}

      {isLoading && !brief ? (
        <div className="rounded-md border border-theme-outline bg-theme-primary px-4 py-3 body-sm-regular text-theme-muted">
          Loading workspace brief...
        </div>
      ) : null}

      {brief ? (
        <div className="grid grid-cols-1 gap-4 xl:grid-cols-2 2xl:grid-cols-3">
          <PanelCard title="Active Macro Study" description="Latest study, conclusion, linked assets, and exported feature lineage.">
            <div className="space-y-3">
              <div>
                <div className="body-sm-medium text-theme-primary">{brief.active_macro_study.name ?? "No active study"}</div>
                <div className="body-xxs-regular text-theme-muted">{brief.active_macro_study.objective ?? "Create a study to start the research loop."}</div>
              </div>
              <div className="rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2 body-xs-regular text-theme-muted">
                {brief.active_macro_study.conclusion_summary ?? "No conclusion summary saved yet."}
              </div>
              <div className="flex flex-wrap gap-2">
                {(brief.active_macro_study.linked_assets ?? []).slice(0, 4).map((asset) => (
                  <a
                    key={asset}
                    href={buildSymbolLabHref({
                      symbol: asset,
                      source: "macro",
                      studyId: brief.active_macro_study.study_id ?? undefined,
                    })}
                    className="rounded-full border border-theme-outline px-3 py-1 body-xs-medium text-theme-primary hover:text-theme-accent"
                    onClick={(event) => {
                      event.preventDefault();
                      void navigate({
                        to: "/finance",
                        search: buildSymbolLabRouteSearch(
                          asset,
                          "macro",
                          brief.active_macro_study.study_id ?? undefined,
                        ),
                      });
                    }}
                  >
                    {asset}
                  </a>
                ))}
              </div>
              <div className="body-xxs-regular text-theme-muted break-all">
                Feature export: {brief.active_macro_study.latest_feature_export ?? "n/a"}
              </div>
              <div className="body-xxs-regular text-theme-muted break-all">
                Latest attached report: {brief.active_macro_study.latest_attached_report ?? "n/a"}
              </div>
              <InternalRouteLink
                route="/macro"
                search={brief.active_macro_study.study_id ? { studyId: brief.active_macro_study.study_id } : undefined}
                className="body-xs-medium text-theme-accent"
              >
                Open Macro Lab
              </InternalRouteLink>
            </div>
          </PanelCard>

          <PanelCard title="Current Strategy Candidate" description="Current run candidate, feature lineage, and promotion readiness.">
            <div className="space-y-3">
              <div className="body-sm-medium text-theme-primary">
                {brief.current_strategy_candidate.run_id ?? "No candidate run"}
              </div>
              <div className="body-xs-regular text-theme-muted">
                {brief.current_strategy_candidate.model_name ?? "unknown model"}
                {brief.current_strategy_candidate.as_of_date ? ` | as of ${brief.current_strategy_candidate.as_of_date}` : ""}
              </div>
              <div className="body-xs-regular text-theme-muted">
                Promotion: {brief.current_strategy_candidate.promotion_readiness ?? "n/a"}
                {brief.current_strategy_candidate.training_window ? ` | ${brief.current_strategy_candidate.training_window}` : ""}
              </div>
              <div className="rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2">
                <div className="body-xxs-regular text-theme-muted">Feature lineage</div>
                <div className="mt-1 body-xs-regular text-theme-primary">
                  {(brief.current_strategy_candidate.feature_lineage ?? []).join(", ") || "n/a"}
                </div>
              </div>
              <InternalRouteLink
                route="/quant"
                search={brief.current_strategy_candidate.run_id ? { runId: brief.current_strategy_candidate.run_id } : undefined}
                className="body-xs-medium text-theme-accent"
              >
                Open Strategy Lab
              </InternalRouteLink>
            </div>
          </PanelCard>

          <PanelCard title="Portfolio Snapshot" description="Current ex-ante risk and blocking constraints before execution.">
            <div className="space-y-3">
              <div className="grid grid-cols-2 gap-2">
                <div className="rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2">
                  <div className="body-xxs-regular text-theme-muted">Ex-ante vol</div>
                  <div className="body-sm-medium text-theme-primary">{formatPct(brief.portfolio_snapshot.vol_ex_ante)}</div>
                </div>
                <div className="rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2">
                  <div className="body-xxs-regular text-theme-muted">CVaR 95</div>
                  <div className="body-sm-medium text-theme-primary">{formatPct(brief.portfolio_snapshot.cvar_95)}</div>
                </div>
              </div>
              <ContributorLinks items={brief.portfolio_snapshot.top_risk_contributors ?? []} />
              {(brief.portfolio_snapshot.blocked_constraints ?? []).length ? (
                <div className="rounded-sm border border-amber-500/40 bg-amber-500/10 px-3 py-2 body-xs-regular text-amber-200">
                  {brief.portfolio_snapshot.blocked_constraints[0]}
                </div>
              ) : (
                <div className="body-xs-regular text-theme-muted">No execution blocker is currently attached.</div>
              )}
              <InternalRouteLink
                route="/execution"
                search={brief.portfolio_snapshot.run_id ? { runId: brief.portfolio_snapshot.run_id } : undefined}
                className="body-xs-medium text-theme-accent"
              >
                Open Portfolio &amp; Execution
              </InternalRouteLink>
            </div>
          </PanelCard>

          <PanelCard title="Ops Issue Queue" description="Top severity issues that need an operator response.">
            <div className="space-y-2">
              {(brief.ops_issue_queue ?? []).length ? (
                brief.ops_issue_queue.map((item) => <ActionLink key={item.id} item={{ ...item, detail: item.suggested_action }} />)
              ) : (
                <div className="rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2 body-xs-regular text-theme-muted">
                  No active ops issue was returned by the workspace brief.
                </div>
              )}
              <InternalRouteLink route="/ops" className="body-xs-medium text-theme-accent">Open Ops</InternalRouteLink>
            </div>
          </PanelCard>

          <PanelCard title="Latest Report" description="Most recent HTML report artifact linked into the workstation.">
            <div className="space-y-3">
              <div className="body-sm-medium text-theme-primary">{brief.latest_report.title ?? brief.latest_report.report_type ?? "No report"}</div>
              <div className="body-xs-regular text-theme-muted break-all">
                {brief.latest_report.report_path ?? "No report artifact available."}
              </div>
              {brief.latest_report.report_path ? (
                <InternalRouteLink
                  route="/ops"
                  search={{ reportPath: brief.latest_report.report_path }}
                  className="body-xs-medium text-theme-accent"
                >
                  Open Report
                </InternalRouteLink>
              ) : null}
            </div>
          </PanelCard>

          <PanelCard title="Pending Actions" description="Server-generated next steps for the current workstation state.">
            <div className="space-y-2">
              {(brief.pending_actions ?? []).length ? (
                brief.pending_actions.map((item) => <ActionLink key={item.id} item={item} />)
              ) : (
                <div className="rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2 body-xs-regular text-theme-muted">
                  No pending action was generated by the workspace brief.
                </div>
              )}
            </div>
          </PanelCard>
        </div>
      ) : null}
    </div>
  );
}

export const Route = createFileRoute("/workspace")({
  component: WorkspacePage,
});
