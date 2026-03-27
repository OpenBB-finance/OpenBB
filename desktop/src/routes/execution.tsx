import { createFileRoute } from "@tanstack/react-router";
import { PortfolioExecutionPage } from "./trading";

function parseModelName(value: string | null): "lgbm_ranker" | "xgb_lstm" | "catboost_ranker" | undefined {
  if (value === "lgbm_ranker" || value === "xgb_lstm" || value === "catboost_ranker") {
    return value;
  }
  return undefined;
}

export const Route = createFileRoute("/execution")({
  component: () => {
    const params = new URLSearchParams(window.location.search);
    return (
      <PortfolioExecutionPage
        variant="execution"
        initialTab="orders"
        initialRunId={params.get("runId") ?? ""}
        initialModelName={parseModelName(params.get("modelName"))}
        initialSignalId={params.get("signalId") ?? undefined}
      />
    );
  },
  validateSearch: (search: Record<string, unknown>) => ({
    runId: typeof search.runId === "string" ? search.runId : undefined,
    modelName: typeof search.modelName === "string" ? search.modelName : undefined,
    signalId: typeof search.signalId === "string" ? search.signalId : undefined,
    reportPath: typeof search.reportPath === "string" ? search.reportPath : undefined,
  }),
});
