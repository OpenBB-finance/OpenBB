import type {
  AlphaMappingMode,
  CovarianceMethod,
  MVOptimizerEngine,
  ModelConfigInput,
  ModelName,
  PurgingMode,
  RunListItemPayload,
  WalkForwardConfigInput,
} from "../../types/quant";
import { RunSelectorCard } from "./RunSelectorCard";

export interface SpeedPresetOption {
  id: string;
  label: string;
  description: string;
  estimatedTime: string;
  quickMode: boolean;
  featurePruning: boolean;
}

interface BacktestAdvancedInput {
  mv_optimizer_engine: MVOptimizerEngine;
  optimizer_strict: boolean;
  cov_method: CovarianceMethod;
  cov_pca_components: number;
  cov_pca_idio_floor: number;
  alpha_mapping_mode: AlphaMappingMode;
  ic_lookback_days: number;
  ic_ewma_halflife: number;
  ic_clip_min: number;
  ic_clip_max: number;
  ic_fallback: number;
  alpha_ema_halflife_days: number;
  trigger_rebalance_enabled: boolean;
  trigger_threshold_bps: number;
  trigger_cost_multiplier: number;
}

interface TrainingConfigSectionProps {
  runIdInput: string;
  recentRuns: RunListItemPayload[];
  canUseApi: boolean;
  onRunIdInputChange: (value: string) => void;
  onLoadRun: () => void;
  speedPreset: string;
  speedPresetOptions: SpeedPresetOption[];
  onApplySpeedPreset: (presetId: string) => void;
  selectedModel: ModelName;
  onSelectedModelChange: (model: ModelName) => void;
  dataProvider: string;
  onDataProviderChange: (provider: string) => void;
  includeFundamentals: boolean;
  onIncludeFundamentalsChange: (checked: boolean) => void;
  fundamentalProvider: string;
  onFundamentalProviderChange: (provider: string) => void;
  includeSentiment: boolean;
  onIncludeSentimentChange: (checked: boolean) => void;
  topK: number;
  onTopKChange: (value: number) => void;
  scoreThreshold: number;
  onScoreThresholdChange: (value: number) => void;
  balancedLongShort: boolean;
  onBalancedLongShortChange: (checked: boolean) => void;
  showAdvancedConfig: boolean;
  onToggleAdvancedConfig: () => void;
  modelConfig: ModelConfigInput;
  onModelConfigChange: (patch: Partial<ModelConfigInput>) => void;
  walkForwardConfig: WalkForwardConfigInput;
  onWalkForwardConfigChange: (patch: Partial<WalkForwardConfigInput>) => void;
  backtestAdvanced: BacktestAdvancedInput;
  onBacktestAdvancedChange: (patch: Partial<BacktestAdvancedInput>) => void;
  isSubmittingTrain: boolean;
  isTrainBlockedByUniverse: boolean;
  onTrain: () => void;
  canGenerateSignals: boolean;
  isSubmittingSignals: boolean;
  onSignals: () => void;
  canRunBacktest: boolean;
  isSubmittingBacktest: boolean;
  onBacktest: () => void;
  isSubmittingWalkforward: boolean;
  walkforwardElapsed: number;
  onWalkforwardBacktest: () => void;
}

export function TrainingConfigSection({
  runIdInput,
  recentRuns,
  canUseApi,
  onRunIdInputChange,
  onLoadRun,
  speedPreset,
  speedPresetOptions,
  onApplySpeedPreset,
  selectedModel,
  onSelectedModelChange,
  dataProvider,
  onDataProviderChange,
  includeFundamentals,
  onIncludeFundamentalsChange,
  fundamentalProvider,
  onFundamentalProviderChange,
  includeSentiment,
  onIncludeSentimentChange,
  topK,
  onTopKChange,
  scoreThreshold,
  onScoreThresholdChange,
  balancedLongShort,
  onBalancedLongShortChange,
  showAdvancedConfig,
  onToggleAdvancedConfig,
  modelConfig,
  onModelConfigChange,
  walkForwardConfig,
  onWalkForwardConfigChange,
  backtestAdvanced,
  onBacktestAdvancedChange,
  isSubmittingTrain,
  isTrainBlockedByUniverse,
  onTrain,
  canGenerateSignals,
  isSubmittingSignals,
  onSignals,
  canRunBacktest,
  isSubmittingBacktest,
  onBacktest,
  isSubmittingWalkforward,
  walkforwardElapsed,
  onWalkforwardBacktest,
}: TrainingConfigSectionProps) {
  return (
    <>
      <RunSelectorCard
        runIdInput={runIdInput}
        recentRuns={recentRuns}
        canUseApi={canUseApi}
        onRunIdInputChange={onRunIdInputChange}
        onLoadRun={onLoadRun}
      />

      <div>
        <p className="body-xs-medium text-theme-muted mb-1.5">Training Speed</p>
        <div className="grid grid-cols-4 gap-1.5">
          {speedPresetOptions.map((preset) => (
            <button
              key={preset.id}
              type="button"
              onClick={() => onApplySpeedPreset(preset.id)}
              className={`rounded-sm border p-2 text-center transition-all ${
                speedPreset === preset.id
                  ? "border-sky-500/60 bg-sky-500/15 text-sky-300"
                  : "border-theme-outline bg-theme-secondary text-theme-muted hover:bg-theme-tertiary"
              }`}
            >
              <p className="body-xs-medium">{preset.label}</p>
              <p className="body-xxs-regular mt-0.5">{preset.estimatedTime}</p>
            </button>
          ))}
        </div>
        <p className="mt-1.5 body-xxs-regular text-theme-muted">
          {speedPresetOptions.find((preset) => preset.id === speedPreset)?.description ?? ""}
        </p>
        <div className="mt-1.5 grid grid-cols-3 gap-1">
          <div className="rounded-sm bg-theme-tertiary p-1.5 text-center">
            <p className="body-xxs-regular text-theme-muted">Quick</p>
            <p
              className={`body-xxs-medium ${
                speedPresetOptions.find((preset) => preset.id === speedPreset)?.quickMode
                  ? "text-emerald-400"
                  : "text-theme-muted"
              }`}
            >
              {speedPresetOptions.find((preset) => preset.id === speedPreset)?.quickMode ? "ON" : "OFF"}
            </p>
          </div>
          <div className="rounded-sm bg-theme-tertiary p-1.5 text-center">
            <p className="body-xxs-regular text-theme-muted">Pruning</p>
            <p
              className={`body-xxs-medium ${
                speedPresetOptions.find((preset) => preset.id === speedPreset)?.featurePruning
                  ? "text-emerald-400"
                  : "text-theme-muted"
              }`}
            >
              {speedPresetOptions.find((preset) => preset.id === speedPreset)?.featurePruning
                ? "ON"
                : "OFF"}
            </p>
          </div>
          <div className="rounded-sm bg-theme-tertiary p-1.5 text-center">
            <p className="body-xxs-regular text-theme-muted">HPO</p>
            <p className={`body-xxs-medium ${speedPreset === "thorough" ? "text-emerald-400" : "text-theme-muted"}`}>
              {speedPreset === "thorough" ? "ON" : "OFF"}
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <label className="body-xs-medium text-theme-muted">
          Model
          <select
            className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary p-2 body-xs-regular text-theme-primary"
            value={selectedModel}
            onChange={(event) => onSelectedModelChange(event.target.value as ModelName)}
          >
            <option value="lgbm_ranker">LGBM Ranker</option>
            <option value="xgb_lstm">XGB + LSTM</option>
            <option value="catboost_ranker" disabled>
              CatBoost Ranker (temporarily disabled)
            </option>
          </select>
        </label>
        <label className="body-xs-medium text-theme-muted">
          Data Provider
          <select
            className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary p-2 body-xs-regular text-theme-primary"
            value={dataProvider}
            onChange={(event) => onDataProviderChange(event.target.value)}
          >
            <option value="yfinance">YFinance</option>
            <option value="fmp">FMP</option>
            <option value="polygon">Polygon</option>
          </select>
        </label>
        <label className="body-xs-medium text-theme-muted">
          Top K
          <input
            type="number"
            min={1}
            max={200}
            className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary p-2 body-xs-regular text-theme-primary"
            value={topK}
            onChange={(event) => onTopKChange(Number(event.target.value))}
          />
        </label>
        <label className="body-xs-medium text-theme-muted">
          Score Threshold
          <input
            type="number"
            step={0.1}
            min={0}
            max={5}
            className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary p-2 body-xs-regular text-theme-primary"
            value={scoreThreshold}
            onChange={(event) => onScoreThresholdChange(Number(event.target.value))}
          />
        </label>
        <label className="flex items-center gap-2 body-xs-medium text-theme-muted pt-6">
          <input
            type="checkbox"
            checked={balancedLongShort}
            onChange={(event) => onBalancedLongShortChange(event.target.checked)}
            aria-label="Balanced long/short"
          />
          Balanced long/short
        </label>
        <label className="flex items-center gap-2 body-xs-medium text-theme-muted pt-6">
          <input
            type="checkbox"
            checked={includeFundamentals}
            onChange={(event) => onIncludeFundamentalsChange(event.target.checked)}
            aria-label="Include fundamentals"
          />
          Fundamental Momentum
        </label>
        <label className="body-xs-medium text-theme-muted">
          Fundamental Provider
          <select
            className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary p-2 body-xs-regular text-theme-primary"
            value={fundamentalProvider}
            onChange={(event) => onFundamentalProviderChange(event.target.value)}
            disabled={!includeFundamentals}
          >
            <option value="">Auto (same as data)</option>
            <option value="yfinance">YFinance</option>
            <option value="fmp">FMP</option>
            <option value="polygon">Polygon</option>
          </select>
        </label>
        <label className="flex items-center gap-2 body-xs-medium text-theme-muted pt-6">
          <input
            type="checkbox"
            checked={includeSentiment}
            onChange={(event) => onIncludeSentimentChange(event.target.checked)}
            aria-label="Include sentiment"
          />
          Market Sentiment (preview)
        </label>
      </div>

      <button
        type="button"
        className="w-full text-left body-xxs-regular text-theme-muted hover:text-theme-primary transition-colors"
        onClick={onToggleAdvancedConfig}
      >
        {showAdvancedConfig
          ? "Hide Advanced Model Config"
          : "Show Advanced Model Config (LSTM, XGB, WF params)"}
      </button>

      {showAdvancedConfig ? (
        <div className="space-y-2 rounded-sm border border-theme-outline bg-theme-tertiary p-2">
          <div className="grid grid-cols-3 gap-2">
            <label className="body-xxs-medium text-theme-muted">
              Purging Mode
              <select
                className="mt-0.5 w-full rounded-sm border border-theme-outline bg-theme-secondary p-1.5 body-xxs-regular text-theme-primary"
                value={walkForwardConfig.purging_mode ?? "legacy_month_cutoff"}
                onChange={(event) =>
                  onWalkForwardConfigChange({
                    purging_mode: event.target.value as PurgingMode,
                  })
                }
              >
                <option value="legacy_month_cutoff">Legacy Month Cutoff</option>
                <option value="strict_label_overlap">Strict Label Overlap</option>
                <option value="purged_group_kfold">Purged Group K-Fold</option>
              </select>
            </label>
            <label className="body-xxs-medium text-theme-muted">
              Purged Splits
              <input
                type="number"
                min={2}
                max={24}
                className="mt-0.5 w-full rounded-sm border border-theme-outline bg-theme-secondary p-1.5 body-xxs-regular text-theme-primary"
                value={walkForwardConfig.purged_n_splits ?? 5}
                onChange={(event) =>
                  onWalkForwardConfigChange({
                    purged_n_splits: Number(event.target.value),
                  })
                }
                disabled={(walkForwardConfig.purging_mode ?? "legacy_month_cutoff") !== "purged_group_kfold"}
              />
            </label>
            <label className="body-xxs-medium text-theme-muted">
              Embargo %
              <input
                type="number"
                step={0.005}
                min={0}
                max={0.5}
                className="mt-0.5 w-full rounded-sm border border-theme-outline bg-theme-secondary p-1.5 body-xxs-regular text-theme-primary"
                value={walkForwardConfig.purged_embargo_pct ?? 0.01}
                onChange={(event) =>
                  onWalkForwardConfigChange({
                    purged_embargo_pct: Number(event.target.value),
                  })
                }
                disabled={(walkForwardConfig.purging_mode ?? "legacy_month_cutoff") !== "purged_group_kfold"}
              />
            </label>
          </div>

          <div className="grid grid-cols-3 gap-2">
            <label className="body-xxs-medium text-theme-muted">
              Seq Len
              <input
                type="number"
                min={10}
                max={240}
                className="mt-0.5 w-full rounded-sm border border-theme-outline bg-theme-secondary p-1.5 body-xxs-regular text-theme-primary"
                value={modelConfig.seq_len}
                onChange={(event) => onModelConfigChange({ seq_len: Number(event.target.value) })}
              />
            </label>
            <label className="body-xxs-medium text-theme-muted">
              LSTM Epochs
              <input
                type="number"
                min={3}
                max={300}
                className="mt-0.5 w-full rounded-sm border border-theme-outline bg-theme-secondary p-1.5 body-xxs-regular text-theme-primary"
                value={modelConfig.lstm_epochs}
                onChange={(event) => onModelConfigChange({ lstm_epochs: Number(event.target.value) })}
              />
            </label>
            <label className="body-xxs-medium text-theme-muted">
              LSTM Hidden
              <input
                type="number"
                min={16}
                max={512}
                className="mt-0.5 w-full rounded-sm border border-theme-outline bg-theme-secondary p-1.5 body-xxs-regular text-theme-primary"
                value={modelConfig.lstm_hidden_size}
                onChange={(event) => onModelConfigChange({ lstm_hidden_size: Number(event.target.value) })}
              />
            </label>
            <label className="body-xxs-medium text-theme-muted">
              XGB Trees
              <input
                type="number"
                min={50}
                max={2000}
                className="mt-0.5 w-full rounded-sm border border-theme-outline bg-theme-secondary p-1.5 body-xxs-regular text-theme-primary"
                value={modelConfig.xgb_n_estimators}
                onChange={(event) => onModelConfigChange({ xgb_n_estimators: Number(event.target.value) })}
              />
            </label>
            <label className="body-xxs-medium text-theme-muted">
              XGB Depth
              <input
                type="number"
                min={2}
                max={10}
                className="mt-0.5 w-full rounded-sm border border-theme-outline bg-theme-secondary p-1.5 body-xxs-regular text-theme-primary"
                value={modelConfig.xgb_max_depth}
                onChange={(event) => onModelConfigChange({ xgb_max_depth: Number(event.target.value) })}
              />
            </label>
            <label className="body-xxs-medium text-theme-muted">
              Batch Size
              <input
                type="number"
                min={32}
                max={512}
                className="mt-0.5 w-full rounded-sm border border-theme-outline bg-theme-secondary p-1.5 body-xxs-regular text-theme-primary"
                value={modelConfig.lstm_batch_size}
                onChange={(event) => onModelConfigChange({ lstm_batch_size: Number(event.target.value) })}
              />
            </label>
          </div>

          <div className="grid grid-cols-3 gap-2">
            <label className="body-xxs-medium text-theme-muted">
              MV Engine
              <select
                className="mt-0.5 w-full rounded-sm border border-theme-outline bg-theme-secondary p-1.5 body-xxs-regular text-theme-primary"
                value={backtestAdvanced.mv_optimizer_engine}
                onChange={(event) =>
                  onBacktestAdvancedChange({
                    mv_optimizer_engine: event.target.value as MVOptimizerEngine,
                  })
                }
              >
                <option value="legacy_slsqp">Legacy SLSQP</option>
                <option value="auto">Auto (CVXPY -&gt; SLSQP)</option>
                <option value="cvxpy">CVXPY</option>
              </select>
            </label>
            <label className="body-xxs-medium text-theme-muted">
              Covariance
              <select
                className="mt-0.5 w-full rounded-sm border border-theme-outline bg-theme-secondary p-1.5 body-xxs-regular text-theme-primary"
                value={backtestAdvanced.cov_method}
                onChange={(event) =>
                  onBacktestAdvancedChange({
                    cov_method: event.target.value as CovarianceMethod,
                  })
                }
              >
                <option value="ewma_shrink">EWMA + Shrink</option>
                <option value="ewma">EWMA</option>
                <option value="ledoit_wolf">Ledoit-Wolf</option>
                <option value="sample">Sample</option>
                <option value="stat_factor_pca">Stat Factor PCA</option>
              </select>
            </label>
            <label className="body-xxs-medium text-theme-muted">
              Alpha Mapping
              <select
                className="mt-0.5 w-full rounded-sm border border-theme-outline bg-theme-secondary p-1.5 body-xxs-regular text-theme-primary"
                value={backtestAdvanced.alpha_mapping_mode}
                onChange={(event) =>
                  onBacktestAdvancedChange({
                    alpha_mapping_mode: event.target.value as AlphaMappingMode,
                  })
                }
              >
                <option value="legacy_score">Legacy Score</option>
                <option value="ic_vol_scaled">IC x Vol x Z</option>
              </select>
            </label>
          </div>

          <div className="grid grid-cols-3 gap-2">
            <label className="body-xxs-medium text-theme-muted">
              IC Lookback
              <input
                type="number"
                min={20}
                max={2520}
                className="mt-0.5 w-full rounded-sm border border-theme-outline bg-theme-secondary p-1.5 body-xxs-regular text-theme-primary"
                value={backtestAdvanced.ic_lookback_days}
                onChange={(event) =>
                  onBacktestAdvancedChange({
                    ic_lookback_days: Number(event.target.value),
                  })
                }
              />
            </label>
            <label className="body-xxs-medium text-theme-muted">
              IC Halflife
              <input
                type="number"
                min={2}
                max={2520}
                className="mt-0.5 w-full rounded-sm border border-theme-outline bg-theme-secondary p-1.5 body-xxs-regular text-theme-primary"
                value={backtestAdvanced.ic_ewma_halflife}
                onChange={(event) =>
                  onBacktestAdvancedChange({
                    ic_ewma_halflife: Number(event.target.value),
                  })
                }
              />
            </label>
            <label className="body-xxs-medium text-theme-muted">
              Alpha EMA
              <input
                type="number"
                min={0}
                max={2520}
                className="mt-0.5 w-full rounded-sm border border-theme-outline bg-theme-secondary p-1.5 body-xxs-regular text-theme-primary"
                value={backtestAdvanced.alpha_ema_halflife_days}
                onChange={(event) =>
                  onBacktestAdvancedChange({
                    alpha_ema_halflife_days: Number(event.target.value),
                  })
                }
              />
            </label>
          </div>

          <div className="grid grid-cols-3 gap-2">
            <label className="flex items-center gap-2 body-xxs-medium text-theme-muted pt-4">
              <input
                type="checkbox"
                checked={backtestAdvanced.trigger_rebalance_enabled}
                onChange={(event) =>
                  onBacktestAdvancedChange({
                    trigger_rebalance_enabled: event.target.checked,
                  })
                }
              />
              Trigger Rebalance
            </label>
            <label className="body-xxs-medium text-theme-muted">
              Trigger bps
              <input
                type="number"
                min={0}
                max={5000}
                step={1}
                className="mt-0.5 w-full rounded-sm border border-theme-outline bg-theme-secondary p-1.5 body-xxs-regular text-theme-primary"
                value={backtestAdvanced.trigger_threshold_bps}
                onChange={(event) =>
                  onBacktestAdvancedChange({
                    trigger_threshold_bps: Number(event.target.value),
                  })
                }
              />
            </label>
            <label className="body-xxs-medium text-theme-muted">
              Trigger Cost Mult
              <input
                type="number"
                min={0}
                max={100}
                step={0.1}
                className="mt-0.5 w-full rounded-sm border border-theme-outline bg-theme-secondary p-1.5 body-xxs-regular text-theme-primary"
                value={backtestAdvanced.trigger_cost_multiplier}
                onChange={(event) =>
                  onBacktestAdvancedChange({
                    trigger_cost_multiplier: Number(event.target.value),
                  })
                }
              />
            </label>
          </div>
        </div>
      ) : null}

      <div className="grid grid-cols-1 gap-2">
        <button
          id="quant-action-train"
          type="button"
          className="button-neutral rounded-sm px-3 py-2 body-xs-medium"
          onClick={onTrain}
          disabled={!canUseApi || isSubmittingTrain || isTrainBlockedByUniverse}
        >
          {isSubmittingTrain ? "Submitting..." : "Start Training"}
        </button>
        <button
          id="quant-action-signals"
          type="button"
          className="button-secondary rounded-sm px-3 py-2 body-xs-medium"
          onClick={onSignals}
          disabled={!canGenerateSignals || isSubmittingSignals}
        >
          {isSubmittingSignals ? "Generating..." : "Generate Signals"}
        </button>
        <button
          id="quant-action-backtest"
          type="button"
          className="button-secondary rounded-sm px-3 py-2 body-xs-medium"
          onClick={onBacktest}
          disabled={!canRunBacktest || isSubmittingBacktest}
        >
          {isSubmittingBacktest ? "Running..." : "Run Backtest"}
        </button>
        <button
          type="button"
          className="button-secondary rounded-sm px-3 py-2 body-xs-medium"
          onClick={onWalkforwardBacktest}
          disabled={!canRunBacktest || isSubmittingWalkforward}
        >
          {isSubmittingWalkforward
            ? `Walk-forward... ${walkforwardElapsed > 0 ? `(${walkforwardElapsed}s)` : ""}`
            : "Run Walk-forward Backtest"}
        </button>
      </div>
    </>
  );
}
