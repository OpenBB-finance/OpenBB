import { createFileRoute } from "@tanstack/react-router";
import { PortfolioExecutionPage } from "./trading";

export const Route = createFileRoute("/execution")({
  component: () => <PortfolioExecutionPage initialTab="orders" />,
  validateSearch: (search: Record<string, unknown>) => ({
    runId: typeof search.runId === "string" ? search.runId : undefined,
    modelName: typeof search.modelName === "string" ? search.modelName : undefined,
    signalId: typeof search.signalId === "string" ? search.signalId : undefined,
    reportPath: typeof search.reportPath === "string" ? search.reportPath : undefined,
  }),
});
