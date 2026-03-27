import type { FeatureActivation } from "../../types/feature-activation";
import type { TrainRunStatus } from "../../types/quant";

interface QuantPageHeaderProps {
  parsedSymbolsCount: number;
  isUniverseSetMode: boolean;
  runStatus: TrainRunStatus | null;
  signalsCount: number;
  backtestPointsCount: number;
  errorMessage: string | null;
  quantActivation: FeatureActivation | null;
}

export function QuantPageHeader({
  parsedSymbolsCount,
  isUniverseSetMode,
  runStatus,
  signalsCount,
  backtestPointsCount,
  errorMessage,
  quantActivation,
}: QuantPageHeaderProps) {
  return (
    <>
      <div className="mb-4">
        <h1 className="body-lg-medium text-theme-primary" id="quant-lab-title">
          Strategy Lab
        </h1>
        <p className="body-sm-regular text-theme-muted">
          Step through setup, features, training, backtest review, and promotion for a local-first strategy workflow.
        </p>
        <div
          className="mt-2 flex flex-wrap gap-2 body-xs-regular text-theme-muted"
          role="status"
          aria-label="Workflow steps"
        >
          <span
            className={parsedSymbolsCount > 0 || isUniverseSetMode ? "text-emerald-400" : "text-theme-muted"}
          >
            1. Universe
          </span>
          <span aria-hidden>/</span>
          <span className={runStatus === "completed" ? "text-emerald-400" : "text-theme-muted"}>2. Train</span>
          <span aria-hidden>/</span>
          <span className={signalsCount > 0 ? "text-emerald-400" : "text-theme-muted"}>3. Review</span>
          <span aria-hidden>/</span>
          <span className={backtestPointsCount > 0 ? "text-emerald-400" : "text-theme-muted"}>4. Backtest</span>
        </div>
      </div>

      {errorMessage ? (
        <div className="mb-3 rounded-sm border border-red-500/60 bg-red-500/10 p-2">
          <p className="body-xs-medium text-red-400">{errorMessage}</p>
        </div>
      ) : null}
      {quantActivation && !quantActivation.available ? (
        <div className="mb-3 rounded-sm border border-amber-500/60 bg-amber-500/10 p-2">
          <p className="body-xs-medium text-amber-300">
            quant_ml extension unavailable: {quantActivation.detail || "Install/enable openbb-quant-ml."}
          </p>
        </div>
      ) : null}
    </>
  );
}
