import type { ArtifactSummaryPayload } from "../../types/quant";
import { PanelCard } from "./PanelCard";

interface ExplainabilityCardProps {
  summary: ArtifactSummaryPayload | null;
}

export function ExplainabilityCard({ summary }: ExplainabilityCardProps) {
  return (
    <PanelCard
      title="Explainability"
      description="Feature importance, validation error, and artifact summary"
    >
      {!summary ? (
        <p className="body-sm-regular text-theme-muted">Run training to load explainability data.</p>
      ) : (
        <div className="space-y-3">
          <div className="rounded-sm bg-theme-secondary p-2">
            <p className="body-xs-regular text-theme-muted">Latest validation error</p>
            <p className="body-sm-medium text-theme-primary">{summary.latest_validation_error ?? "-"}</p>
          </div>

          <div>
            <p className="body-xs-medium text-theme-muted">Top features</p>
            <ul className="mt-1 space-y-1">
              {summary.feature_importance.slice(0, 8).map((item) => (
                <li
                  key={item.feature}
                  className="flex items-center justify-between rounded-sm bg-theme-secondary px-2 py-1"
                >
                  <span className="body-xs-regular text-theme-primary">{item.feature}</span>
                  <span className="body-xs-regular text-theme-muted">{item.importance.toFixed(4)}</span>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <p className="body-xs-medium text-theme-muted">Artifacts</p>
            <p className="body-xs-regular text-theme-primary">
              {summary.available_artifacts.length > 0
                ? summary.available_artifacts.join(", ")
                : "No artifacts found."}
            </p>
          </div>
        </div>
      )}
    </PanelCard>
  );
}
