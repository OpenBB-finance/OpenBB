export type StrategyLabStepId =
  | "setup"
  | "features"
  | "train"
  | "backtest"
  | "compare"
  | "promote";

export interface StrategyLabStep {
  id: StrategyLabStepId;
  label: string;
  hint: string;
  complete: boolean;
}

interface StrategyLabStepperProps {
  steps: StrategyLabStep[];
  activeStep: StrategyLabStepId;
  onStepChange: (stepId: StrategyLabStepId) => void;
}

export function StrategyLabStepper({
  steps,
  activeStep,
  onStepChange,
}: StrategyLabStepperProps) {
  return (
    <div
      className="mb-4 grid grid-cols-1 gap-2 xl:grid-cols-6"
      role="tablist"
      aria-label="Strategy Lab workflow"
    >
      {steps.map((step, index) => {
        const isActive = step.id === activeStep;
        return (
          <button
            key={step.id}
            type="button"
            role="tab"
            aria-selected={isActive}
            onClick={() => onStepChange(step.id)}
            className={`rounded-md border px-3 py-3 text-left transition ${
              isActive
                ? "border-sky-400/60 bg-sky-500/10 text-sky-200"
                : step.complete
                  ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-200"
                  : "border-theme-outline bg-theme-primary text-theme-muted"
            }`}
          >
            <div className="mb-1 body-xxs-medium uppercase tracking-wide">
              {index + 1}. {step.label}
            </div>
            <div className="body-xxs-regular">{step.hint}</div>
          </button>
        );
      })}
    </div>
  );
}
