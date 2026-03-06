interface WorkflowStep {
  id: string;
  label: string;
  done: boolean;
  current: boolean;
  href?: string;
}

interface WorkflowStepsProps {
  runId: string | null;
  artifactsReady?: {
    predictions?: boolean;
    signals?: boolean;
    backtest?: boolean;
    portfolio_current?: boolean;
  };
}

export function WorkflowSteps({ runId, artifactsReady }: WorkflowStepsProps) {
  const hasRun = Boolean(runId?.trim());
  const hasPredictions = artifactsReady?.predictions ?? false;
  const hasSignals = artifactsReady?.signals ?? false;
  const hasBacktest = artifactsReady?.backtest ?? false;

  const step1Done = hasRun;
  const step2Done = hasRun && (hasPredictions || hasSignals || hasBacktest);
  const step2Current = hasRun && !step2Done;
  const step1Current = !hasRun;

  const steps: WorkflowStep[] = [
    {
      id: "quant-lab",
      label: "Quant Lab",
      done: step1Done,
      current: step1Current,
      href: "/quant",
    },
    {
      id: "dashboard",
      label: "Dashboard",
      done: step2Done,
      current: step2Current,
      href: "/dashboard",
    },
    {
      id: "execution",
      label: "Execution",
      done: false,
      current: step2Done && !step2Current,
      href: "/execution",
    },
  ];

  return (
    <div className="flex items-center gap-2" role="navigation" aria-label="Workflow steps">
      {steps.map((step, index) => (
        <div key={step.id} className="flex items-center gap-2">
          {index > 0 ? <div className="h-px w-4 bg-theme-outline" aria-hidden="true" /> : null}
          <a
            href={step.href}
            className={`flex items-center gap-1.5 rounded-sm px-2 py-1 body-xxs-medium transition-colors ${
              step.current
                ? "bg-sky-500/20 text-sky-300 ring-1 ring-sky-500/50"
                : step.done
                  ? "bg-emerald-500/10 text-emerald-400"
                  : "bg-theme-secondary text-theme-muted"
            }`}
            aria-current={step.current ? "step" : undefined}
          >
            <span
              className={`flex h-5 w-5 items-center justify-center rounded-full text-[10px] font-bold ${
                step.done
                  ? "bg-emerald-500/30 text-emerald-300"
                  : step.current
                    ? "bg-sky-500/40 text-sky-200"
                    : "bg-theme-outline/50 text-theme-muted"
              }`}
            >
              {step.done ? "OK" : index + 1}
            </span>
            {step.label}
          </a>
        </div>
      ))}
    </div>
  );
}
