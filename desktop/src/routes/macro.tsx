import { createFileRoute } from "@tanstack/react-router";
import MacroPage from "../components/macro/MacroPage";

const VIEW_MODES = new Set(["explorer", "compare", "relationship", "release", "report"]);

export const Route = createFileRoute("/macro")({
  validateSearch: (search: Record<string, unknown>) => ({
    studyId: typeof search.studyId === "string" ? search.studyId : undefined,
    view:
      typeof search.view === "string" && VIEW_MODES.has(search.view)
        ? (search.view as "explorer" | "compare" | "relationship" | "release" | "report")
        : undefined,
    seriesKey: typeof search.seriesKey === "string" ? search.seriesKey : undefined,
    query: typeof search.query === "string" ? search.query : undefined,
    domain: typeof search.domain === "string" ? search.domain : undefined,
    asOfDate:
      typeof search.asOfDate === "string" && /^\d{4}-\d{2}-\d{2}$/.test(search.asOfDate)
        ? search.asOfDate
        : undefined,
  }),
  component: MacroPage,
});
