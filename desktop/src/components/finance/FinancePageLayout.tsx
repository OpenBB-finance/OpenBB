import { useEffect, useState } from "react";
import { useNavigate } from "@tanstack/react-router";
import { PanelCard } from "../quant/PanelCard";
import { FinanceControlsCard } from "./FinanceControlsCard";
import { FinanceFundamentalsPanel } from "./FinanceFundamentalsPanel";
import { FinanceSymbolPicker } from "./FinanceSymbolPicker";
import { TradingViewWidgetEmbed } from "./TradingViewWidgetEmbed";
import type { TradingViewThemeMode } from "../../types/finance";
import type { SymbolContextPayload, SymbolLabSearch } from "../../types/quant";

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

interface FinancePageLayoutProps {
  activeSymbol: string;
  baseUrl: string;
  symbolInput: string;
  recentSymbols: string[];
  theme: TradingViewThemeMode;
  contextRail: SymbolContextPayload | null;
  contextError?: string | null;
  symbolSearch: SymbolLabSearch;
  onSymbolInputChange: (value: string) => void;
  onSubmit: () => void;
  onSelectRecentSymbol: (symbol: string) => void;
}

export function FinancePageLayout({
  activeSymbol,
  baseUrl,
  symbolInput,
  recentSymbols,
  theme,
  contextRail,
  contextError,
  symbolSearch,
  onSymbolInputChange,
  onSubmit,
  onSelectRecentSymbol,
}: FinancePageLayoutProps) {
  const navigate = useNavigate();
  const [chartHeight, setChartHeight] = useState(720);
  const [fundamentalHeight, setFundamentalHeight] = useState(920);

  useEffect(() => {
    const syncHeights = () => {
      if (typeof window === "undefined") return;
      setChartHeight(Math.max(560, Math.min(window.innerHeight - 220, 780)));
      setFundamentalHeight(Math.max(760, Math.min(window.innerHeight + 80, 1120)));
    };
    syncHeights();
    window.addEventListener("resize", syncHeights);
    return () => window.removeEventListener("resize", syncHeights);
  }, []);

  return (
    <div className="grid grid-cols-1 gap-4 2xl:grid-cols-[320px_minmax(0,1fr)_320px] xl:grid-cols-[320px_minmax(0,1fr)]">
      <div className="space-y-4 xl:sticky xl:top-4 xl:self-start">
        <FinanceControlsCard
          activeSymbol={activeSymbol}
          symbolInput={symbolInput}
          recentSymbols={recentSymbols}
          onSymbolInputChange={onSymbolInputChange}
          onSubmit={onSubmit}
          onSelectRecentSymbol={onSelectRecentSymbol}
        />
      </div>
      <div className="space-y-4">
        <PanelCard title="Advanced Chart" description="TradingView advanced chart with detailed timeframe and indicator controls.">
          <div className="mb-4">
            <FinanceSymbolPicker
              activeSymbol={activeSymbol}
              inputId="finance-chart-symbol-input"
              label="Chart Symbol Search"
              symbolInput={symbolInput}
              recentSymbols={recentSymbols}
              submitLabel="Update"
              compact
              onSymbolInputChange={onSymbolInputChange}
              onSubmit={onSubmit}
              onSelectSymbol={onSelectRecentSymbol}
            />
          </div>
          <TradingViewWidgetEmbed
            widgetType="advanced-chart"
            symbol={activeSymbol}
            theme={theme}
            title="Advanced Chart"
            minHeight={chartHeight}
            frameHeight={chartHeight}
          />
        </PanelCard>
        <FinanceFundamentalsPanel
          baseUrl={baseUrl}
          symbol={activeSymbol}
          theme={theme}
          overviewHeight={fundamentalHeight}
        />
        <div className="grid grid-cols-1 gap-4 xl:grid-cols-[320px_minmax(0,1fr)]">
          <PanelCard title="Symbol Info" description="TradingView summary snapshot and headline market data.">
            <TradingViewWidgetEmbed
              widgetType="symbol-info"
              symbol={activeSymbol}
              theme={theme}
              title="Symbol Info"
              lazy
              minHeight={420}
              frameHeight={420}
            />
          </PanelCard>
          <PanelCard title="Company Profile" description="TradingView company description, sector, and industry metadata.">
            <TradingViewWidgetEmbed
              widgetType="company-profile"
              symbol={activeSymbol}
              theme={theme}
              title="Company Profile"
              lazy
              minHeight={320}
              frameHeight={320}
            />
          </PanelCard>
        </div>
      </div>
      <div className="space-y-4 2xl:sticky 2xl:top-4 2xl:self-start">
        <PanelCard title="Context Rail" description="Cross-workflow context for the selected symbol.">
          {contextError ? (
            <div className="rounded-sm border border-amber-500/40 bg-amber-500/10 px-3 py-2 body-xs-regular text-amber-200">
              {contextError}
            </div>
          ) : null}
          <div className="space-y-3">
            <div className="rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2">
              <div className="body-xxs-regular text-theme-muted">Source workflow</div>
              <div className="body-sm-medium text-theme-primary">{contextRail?.source ?? symbolSearch.source ?? "direct"}</div>
            </div>
            <div className="rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2">
              <div className="body-xxs-regular text-theme-muted">Linked macro studies</div>
              <div className="mt-2 space-y-2">
                {(contextRail?.linked_studies ?? []).length ? (
                  contextRail?.linked_studies.map((study) => (
                    <a
                      key={`${study.study_id ?? "study"}-${study.name ?? ""}`}
                      href={buildRouteHref("/macro", study.study_id ? { studyId: study.study_id } : undefined)}
                      className="block rounded-sm border border-theme-outline px-2 py-2 body-xs-regular text-theme-primary hover:text-theme-accent"
                      onClick={(event) => {
                        event.preventDefault();
                        void navigate({
                          to: "/macro",
                          search: {
                            studyId: study.study_id ?? undefined,
                            view: undefined,
                            seriesKey: undefined,
                            query: undefined,
                            domain: undefined,
                            asOfDate: undefined,
                          },
                        });
                      }}
                    >
                      <div className="body-xs-medium">{study.name ?? study.study_id ?? "Study"}</div>
                      <div className="body-xxs-regular text-theme-muted">{study.objective ?? "No objective saved."}</div>
                    </a>
                  ))
                ) : (
                  <div className="body-xs-regular text-theme-muted">No linked macro study for this symbol.</div>
                )}
              </div>
            </div>
            <div className="rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2">
              <div className="body-xxs-regular text-theme-muted">Related runs</div>
              <div className="mt-2 space-y-2">
                {(contextRail?.related_runs ?? []).length ? (
                  contextRail?.related_runs.map((run) => (
                    <a
                      key={run.run_id ?? "run"}
                      href={buildRouteHref("/quant", run.run_id ? { runId: run.run_id } : undefined)}
                      className="block rounded-sm border border-theme-outline px-2 py-2 body-xs-regular text-theme-primary hover:text-theme-accent"
                      onClick={(event) => {
                        event.preventDefault();
                        void navigate({
                          to: "/quant",
                          search: run.run_id ? { runId: run.run_id } : {},
                        });
                      }}
                    >
                      <div className="body-xs-medium">{run.run_id ?? "Run"}</div>
                      <div className="body-xxs-regular text-theme-muted">
                        {run.model_name ?? "unknown model"} {run.promotion_state ? `| ${run.promotion_state}` : ""}
                      </div>
                    </a>
                  ))
                ) : (
                  <div className="body-xs-regular text-theme-muted">No related strategy run found.</div>
                )}
              </div>
            </div>
            <div className="grid grid-cols-1 gap-2">
              <div className="rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2">
                <div className="body-xxs-regular text-theme-muted">Latest signal</div>
                <div className="body-xs-medium text-theme-primary">
                  {String(contextRail?.latest_signal?.signal_type ?? contextRail?.latest_signal?.side ?? "n/a")}
                </div>
              </div>
              <div className="rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2">
                <div className="body-xxs-regular text-theme-muted">Latest order</div>
                <div className="body-xs-medium text-theme-primary">
                  {String(contextRail?.latest_order?.status ?? "n/a")}
                </div>
              </div>
              <div className="rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2">
                <div className="body-xxs-regular text-theme-muted">Position</div>
                <div className="body-xs-medium text-theme-primary">
                  {contextRail?.latest_position ? "Open position" : "No open position"}
                </div>
              </div>
            </div>
            <div className="rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2">
              <div className="body-xxs-regular text-theme-muted">Attached reports</div>
              <div className="mt-2 space-y-2">
                {(contextRail?.attached_reports ?? []).length ? (
                  contextRail?.attached_reports.map((report) => (
                    <a
                      key={report.report_path}
                      href={buildRouteHref("/ops", { reportPath: report.report_path })}
                      className="block rounded-sm border border-theme-outline px-2 py-2 body-xs-regular text-theme-primary hover:text-theme-accent"
                      onClick={(event) => {
                        event.preventDefault();
                        void navigate({
                          to: "/ops",
                          search: { reportPath: report.report_path },
                        });
                      }}
                    >
                      <div className="body-xs-medium">{report.title ?? report.report_type}</div>
                      <div className="body-xxs-regular text-theme-muted break-all">{report.report_path}</div>
                    </a>
                  ))
                ) : (
                  <div className="body-xs-regular text-theme-muted">No attached reports for this symbol.</div>
                )}
              </div>
            </div>
            {(contextRail?.back_links ?? []).length ? (
              <div className="rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2">
                <div className="body-xxs-regular text-theme-muted">Back links</div>
                <div className="mt-2 flex flex-wrap gap-2">
                  {contextRail?.back_links.map((link) => (
                    <a
                      key={`${link.label}-${link.target_route}`}
                      href={buildRouteHref(link.target_route, link.target_search)}
                      className="rounded-sm border border-theme-outline px-3 py-1 body-xs-medium text-theme-primary hover:text-theme-accent"
                      onClick={(event) => {
                        event.preventDefault();
                        void navigate({
                          to: link.target_route,
                          search: link.target_search ?? {},
                        });
                      }}
                    >
                      {link.label}
                    </a>
                  ))}
                </div>
              </div>
            ) : null}
          </div>
        </PanelCard>
      </div>
    </div>
  );
}
