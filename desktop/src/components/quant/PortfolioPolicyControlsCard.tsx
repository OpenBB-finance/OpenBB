import type {
  BacktestResponsePayload,
  PortfolioPolicyPayload,
  PromotedModelPayload,
  WalkForwardBacktestStatusPayload,
} from "../../types/quant";

interface PortfolioPolicyControlsCardProps {
  policy: PortfolioPolicyPayload;
  backtest: BacktestResponsePayload | null;
  promotedModel: PromotedModelPayload | null;
  walkforwardStatus: WalkForwardBacktestStatusPayload | null;
  showPortfolioTimeline: boolean;
  onPolicyChange: (patch: Partial<PortfolioPolicyPayload>) => void;
  onShowPortfolioTimelineChange: (checked: boolean) => void;
}

interface SliderFieldProps {
  label: string;
  value: number;
  min: number;
  max: number;
  step: number;
  onChange: (value: number) => void;
}

function clamp(value: number, min: number, max: number): number {
  return Math.min(max, Math.max(min, value));
}

function SliderField({ label, value, min, max, step, onChange }: SliderFieldProps) {
  const safeValue = clamp(value, min, max);

  return (
    <label className="body-xxs-regular text-theme-muted">
      <div className="mb-1 flex items-center justify-between">
        <span>{label}</span>
        <span className="body-xxs-medium text-theme-primary">{(safeValue * 100).toFixed(1)}%</span>
      </div>
      <div className="flex items-center gap-2">
        <input
          type="range"
          min={min}
          max={max}
          step={step}
          value={safeValue}
          onChange={(event) => onChange(clamp(Number(event.target.value), min, max))}
          className="h-1.5 w-full accent-sky-500"
        />
        <input
          type="number"
          min={min}
          max={max}
          step={step}
          value={safeValue.toFixed(3)}
          onChange={(event) => {
            const next = Number(event.target.value);
            if (!Number.isFinite(next)) {
              return;
            }
            onChange(clamp(next, min, max));
          }}
          className="w-20 rounded-sm border border-theme-outline bg-theme-secondary px-1.5 py-1 body-xxs-regular text-theme-primary"
        />
      </div>
    </label>
  );
}

export function PortfolioPolicyControlsCard({
  policy,
  backtest,
  promotedModel,
  walkforwardStatus,
  showPortfolioTimeline,
  onPolicyChange,
  onShowPortfolioTimelineChange,
}: PortfolioPolicyControlsCardProps) {
  return (
    <div className="rounded-sm border border-theme-outline bg-theme-secondary p-2">
      <p className="body-xs-medium text-theme-primary">
        Single-name cap {(policy.single_name_max_abs_weight * 100).toFixed(0)}% (Hard)
      </p>
      <p className="body-xxs-regular text-theme-muted">
        Template: {policy.template} | Small universe: {policy.small_universe_policy}
      </p>

      <div className="mt-2 space-y-2">
        <SliderField
          label="Single-name Max"
          value={policy.single_name_max_abs_weight}
          min={0.01}
          max={0.25}
          step={0.005}
          onChange={(value) => onPolicyChange({ single_name_max_abs_weight: value })}
        />
        <SliderField
          label="Sector Concentration"
          value={policy.sector_concentration_max}
          min={0.05}
          max={0.8}
          step={0.01}
          onChange={(value) => onPolicyChange({ sector_concentration_max: value })}
        />
        <SliderField
          label="Turnover Limit"
          value={policy.turnover_max}
          min={0.1}
          max={2.0}
          step={0.05}
          onChange={(value) => onPolicyChange({ turnover_max: value })}
        />
      </div>

      {backtest?.effective_constraints ? (
        <p className="mt-2 body-xxs-regular text-theme-muted">
          Applied cap:{" "}
          {(
            Number(backtest.effective_constraints.max_weight ?? policy.single_name_max_abs_weight) *
            100
          ).toFixed(1)}
          % | Cash buffer: {(Number(backtest.cash_weight ?? 0) * 100).toFixed(1)}%
        </p>
      ) : null}
      {promotedModel?.run_id ? (
        <p className="body-xxs-regular text-theme-muted">
          Promoted model: {promotedModel.run_id} ({promotedModel.ready ? "ready" : "not ready"})
        </p>
      ) : null}
      {walkforwardStatus ? (
        <p className="body-xxs-regular text-theme-muted">
          Walk-forward: {walkforwardStatus.status} ({walkforwardStatus.progress}%)
        </p>
      ) : null}
      <label className="mt-2 inline-flex items-center gap-2 body-xxs-regular text-theme-muted">
        <input
          type="checkbox"
          checked={showPortfolioTimeline}
          onChange={(event) => onShowPortfolioTimelineChange(event.target.checked)}
        />
        Portfolio Timeline
      </label>
    </div>
  );
}
