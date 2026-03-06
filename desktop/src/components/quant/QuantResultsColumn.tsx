import type { ComponentProps } from "react";
import { ConnectionStatusCard } from "./ConnectionStatusCard";
import { DiagnosticsPanels } from "./DiagnosticsPanels";
import { EquityCurveChart } from "./EquityCurveChart";
import { ExplainabilityCard } from "./ExplainabilityCard";
import { MetricsCards } from "./MetricsCards";
import { MonthlyReturnsHeatmap } from "./MonthlyReturnsHeatmap";
import { PortfolioRationaleCard } from "./PortfolioRationaleCard";
import { RebalanceTimelineCard } from "./RebalanceTimelineCard";
import { RunStatusCard } from "./RunStatusCard";
import { SignalsTable } from "./SignalsTable";
import { WorkflowSyncCard } from "./WorkflowSyncCard";

type ConnectionStatusCardProps = ComponentProps<typeof ConnectionStatusCard>;
type WorkflowSyncCardProps = ComponentProps<typeof WorkflowSyncCard>;
type RunStatusCardProps = ComponentProps<typeof RunStatusCard>;
type SignalsTableProps = ComponentProps<typeof SignalsTable>;
type MetricsCardsProps = ComponentProps<typeof MetricsCards>;
type MonthlyReturnsHeatmapProps = ComponentProps<typeof MonthlyReturnsHeatmap>;
type PortfolioRationaleCardProps = ComponentProps<typeof PortfolioRationaleCard>;
type RebalanceTimelineCardProps = ComponentProps<typeof RebalanceTimelineCard>;
type EquityCurveChartProps = ComponentProps<typeof EquityCurveChart>;
type DiagnosticsPanelsProps = ComponentProps<typeof DiagnosticsPanels>;
type ExplainabilityCardProps = ComponentProps<typeof ExplainabilityCard>;

interface QuantResultsColumnProps {
  connection: ConnectionStatusCardProps;
  workflowSync: WorkflowSyncCardProps;
  runStatus: RunStatusCardProps;
  signals: SignalsTableProps;
  metrics: MetricsCardsProps;
  monthlyReturns: MonthlyReturnsHeatmapProps;
  portfolioRationale: PortfolioRationaleCardProps;
  showPortfolioTimeline: boolean;
  rebalanceTimeline: RebalanceTimelineCardProps;
  equityCurve: EquityCurveChartProps;
  diagnostics: DiagnosticsPanelsProps;
  explainability: ExplainabilityCardProps;
}

export function QuantResultsColumn({
  connection,
  workflowSync,
  runStatus,
  signals,
  metrics,
  monthlyReturns,
  portfolioRationale,
  showPortfolioTimeline,
  rebalanceTimeline,
  equityCurve,
  diagnostics,
  explainability,
}: QuantResultsColumnProps) {
  return (
    <div className="space-y-4">
      <ConnectionStatusCard {...connection} />
      <WorkflowSyncCard {...workflowSync} />
      <RunStatusCard {...runStatus} />
      <SignalsTable {...signals} />
      <MetricsCards {...metrics} />
      <MonthlyReturnsHeatmap {...monthlyReturns} />
      <PortfolioRationaleCard {...portfolioRationale} />
      {showPortfolioTimeline ? <RebalanceTimelineCard {...rebalanceTimeline} /> : null}
      <EquityCurveChart {...equityCurve} />
      <DiagnosticsPanels {...diagnostics} />
      <ExplainabilityCard {...explainability} />
    </div>
  );
}
