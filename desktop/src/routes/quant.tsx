import { createFileRoute, useRouter } from "@tanstack/react-router";
import { useCallback, useEffect, useMemo, useState } from "react";
import { ConnectionStatusCard } from "../components/quant/ConnectionStatusCard";
import { EquityCurveChart } from "../components/quant/EquityCurveChart";
import { ExplainabilityCard } from "../components/quant/ExplainabilityCard";
import { MetricsCards } from "../components/quant/MetricsCards";
import { PanelCard } from "../components/quant/PanelCard";
import { PortfolioRationaleCard } from "../components/quant/PortfolioRationaleCard";
import { RunStatusCard } from "../components/quant/RunStatusCard";
import { SignalsTable } from "../components/quant/SignalsTable";
import {
  createSignals,
  fetchArtifactSummary,
  fetchPortfolioCurrent,
  fetchRunStatus,
  fetchUniverse,
  invalidateQuantCaches,
  runBacktest,
  startTrain,
} from "../lib/quantApi";
import { resolveOpenBBBackend } from "../lib/openbbBackend";
import { useQuantSession } from "../contexts/QuantSessionContext";
import type {
  ArtifactSummaryPayload,
  BacktestResponsePayload,
  ModelName,
  ModelConfigInput,
  RankerConfigInput,
  PortfolioCurrentPayload,
  RunStatusPayload,
  SignalsResponsePayload,
  UniverseAsset,
  UniverseResponse,
} from "../types/quant";

type UniverseProfileId = "all" | "aggressive" | "defensive" | "custom";

interface UniverseProfile {
  id: Exclude<UniverseProfileId, "custom">;
  label: string;
  description: string;
}

const PROFILE_LIST: UniverseProfile[] = [
  { id: "all", label: "All", description: "Use every symbol in universe." },
  {
    id: "aggressive",
    label: "Aggressive",
    description: "Equity/sector/factor-focused basket.",
  },
  {
    id: "defensive",
    label: "Defensive",
    description: "Bonds, commodities, and defensive assets.",
  },
];

const AGGRESSIVE_CATEGORIES = new Set([
  "korea_index",
  "korea_etf",
  "us_index",
  "us_equity_etf",
  "us_tech_index",
  "us_tech_etf",
  "us_sector_etf",
  "semiconductor_etf",
  "software_etf",
  "global_equity_etf",
  "developed_market_etf",
  "emerging_market_etf",
  "factor_etf",
  "us_large_cap_equity",
  "ai_semiconductor_equity",
  "kospi200_constituent",
]);

const DEFENSIVE_CATEGORIES = new Set([
  "bond_etf",
  "cash_proxy",
  "commodity_etf",
  "reit_etf",
  "currency_etf",
]);

const todayIso = new Date().toISOString().slice(0, 10);
const fiveYearsAgoIso = (() => {
  const base = new Date();
  base.setFullYear(base.getFullYear() - 5);
  return base.toISOString().slice(0, 10);
})();

const defaultModelConfig: ModelConfigInput = {
  seq_len: 60,
  xgb_n_estimators: 400,
  xgb_max_depth: 4,
  xgb_learning_rate: 0.03,
  xgb_subsample: 0.9,
  xgb_colsample_bytree: 0.9,
  lstm_hidden_size: 64,
  lstm_num_layers: 2,
  lstm_dropout: 0.1,
  lstm_epochs: 30,
  lstm_batch_size: 128,
  lstm_learning_rate: 0.001,
  train_val_split: 0.8,
};

const defaultWalkForwardConfig = {
  train_months: 36,
  embargo_months: 1,
  val_months: 1,
  step_months: 1,
};

const defaultRankerConfig: RankerConfigInput = {
  objective: "rank_xendcg",
  metric: "ndcg",
  ndcg_eval_at: [5, 10, 20],
  learning_rate: 0.03,
  n_estimators: 6000,
  num_leaves: 63,
  min_data_in_leaf: 300,
  subsample: 0.8,
  colsample_bytree: 0.8,
  reg_lambda: 10.0,
  random_state: 42,
  early_stopping_rounds: 200,
};

const defaultThetaGrid = [0.8, 1.0, 1.2, 1.5];

function parseSymbolsText(text: string): string[] {
  const seen = new Set<string>();
  const parsed: string[] = [];
  const items = text
    .split(/[\s,;]+/)
    .map((item) => item.trim())
    .filter(Boolean);

  for (const item of items) {
    const normalized = item.toUpperCase();
    if (!seen.has(normalized)) {
      seen.add(normalized);
      parsed.push(normalized);
    }
  }

  return parsed;
}

function formatSymbolsForTextarea(symbols: string[], perLine = 6): string {
  if (symbols.length === 0) {
    return "";
  }
  const lines: string[] = [];
  for (let idx = 0; idx < symbols.length; idx += perLine) {
    lines.push(symbols.slice(idx, idx + perLine).join(", "));
  }
  return lines.join("\n");
}

function symbolsByProfile(assets: UniverseAsset[], profileId: UniverseProfileId): string[] {
  if (profileId === "all" || profileId === "custom") {
    return assets.map((asset) => asset.symbol);
  }

  if (profileId === "aggressive") {
    return assets
      .filter((asset) => AGGRESSIVE_CATEGORIES.has(asset.category))
      .map((asset) => asset.symbol);
  }

  return assets
    .filter((asset) => DEFENSIVE_CATEGORIES.has(asset.category))
    .map((asset) => asset.symbol);
}

function profileLabel(profileId: UniverseProfileId): string {
  if (profileId === "custom") {
    return "Custom";
  }
  return PROFILE_LIST.find((profile) => profile.id === profileId)?.label ?? "Custom";
}

export default function QuantPage() {
  const router = useRouter();
  const { session, setRunId, setModelName, patchSession, markArtifactReady } = useQuantSession();

  const [isResolvingBackend, setIsResolvingBackend] = useState(false);
  const [backend, setBackend] = useState<Awaited<ReturnType<typeof resolveOpenBBBackend>> | null>(null);
  const [universe, setUniverse] = useState<UniverseResponse | null>(null);

  const [selectedProfile, setSelectedProfile] = useState<UniverseProfileId>("all");
  const [symbolsInput, setSymbolsInput] = useState("");

  const [dateStart, setDateStart] = useState(fiveYearsAgoIso);
  const [dateEnd, setDateEnd] = useState(todayIso);
  const [modelConfig, setModelConfig] = useState<ModelConfigInput>(defaultModelConfig);
  const [selectedModel, setSelectedModel] = useState<ModelName>(() => session.model_name);

  const [runStatus, setRunStatus] = useState<RunStatusPayload | null>(null);
  const [runIdInput, setRunIdInput] = useState(() => session.run_id);
  const [activeTrainingRunId, setActiveTrainingRunId] = useState<string | null>(null);
  const [signals, setSignals] = useState<SignalsResponsePayload | null>(null);
  const [backtest, setBacktest] = useState<BacktestResponsePayload | null>(null);
  const [summary, setSummary] = useState<ArtifactSummaryPayload | null>(null);
  const [portfolioCurrent, setPortfolioCurrent] = useState<PortfolioCurrentPayload | null>(null);

  const [topK, setTopK] = useState(20);
  const [scoreThreshold, setScoreThreshold] = useState(0.5);

  const [isSubmittingTrain, setIsSubmittingTrain] = useState(false);
  const [isSubmittingSignals, setIsSubmittingSignals] = useState(false);
  const [isSubmittingBacktest, setIsSubmittingBacktest] = useState(false);
  const [isLoadingPortfolio, setIsLoadingPortfolio] = useState(false);
  const [portfolioError, setPortfolioError] = useState<string | null>(null);

  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const applyProfile = useCallback(
    (profileId: Exclude<UniverseProfileId, "custom">, sourceUniverse: UniverseResponse | null) => {
      if (!sourceUniverse) {
        return;
      }

      const symbols = symbolsByProfile(sourceUniverse.assets, profileId);
      setSelectedProfile(profileId);
      setSymbolsInput(formatSymbolsForTextarea(symbols));
    },
    [],
  );

  const resolveBackendAndUniverse = useCallback(async () => {
    setIsResolvingBackend(true);
    setErrorMessage(null);

    try {
      const resolved = await resolveOpenBBBackend();
      setBackend(resolved);

      if (!resolved.connected) {
        setUniverse(null);
        return;
      }

      const fetchedUniverse = await fetchUniverse(resolved.baseUrl);
      setUniverse(fetchedUniverse);

      setSymbolsInput((prev) => {
        if (prev.trim()) {
          return prev;
        }
        return formatSymbolsForTextarea(symbolsByProfile(fetchedUniverse.assets, "all"));
      });
      setSelectedProfile((prev) => (prev === "custom" ? prev : "all"));
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to resolve backend connection.");
    } finally {
      setIsResolvingBackend(false);
    }
  }, []);

  useEffect(() => {
    void resolveBackendAndUniverse();
  }, [resolveBackendAndUniverse]);

  useEffect(() => {
    setSelectedModel(session.model_name);
  }, [session.model_name]);

  useEffect(() => {
    setRunIdInput(session.run_id);
  }, [session.run_id]);

  useEffect(() => {
    const search = new URLSearchParams(window.location.search);
    const queryRunId = search.get("run_id")?.trim();
    const queryModel = search.get("model") || search.get("model_name");
    if (queryRunId) {
      setRunId(queryRunId);
      setRunIdInput(queryRunId);
    }
    if (queryModel === "lgbm_ranker" || queryModel === "xgb_lstm") {
      setSelectedModel(queryModel);
      setModelName(queryModel);
    }
  }, [setModelName, setRunId]);

  const runId = (runStatus?.run_id ?? "").trim() || null;

  useEffect(() => {
    if (runId) {
      setRunId(runId);
      patchSession({
        run_id: runId,
        model_name: selectedModel,
      });
      setRunIdInput(runId);
    }
  }, [patchSession, runId, selectedModel, setRunId]);

  const loadExistingRun = useCallback(
    async (candidateRunId?: string) => {
      if (!backend?.connected) {
        return;
      }

      const targetRunId = (candidateRunId ?? runIdInput).trim();
      if (!targetRunId) {
        setErrorMessage("Enter a run ID to load artifacts.");
        return;
      }

      setErrorMessage(null);
      setPortfolioError(null);
      try {
        const latest = await fetchRunStatus(backend.baseUrl, targetRunId);
        setRunStatus(latest);
        setActiveTrainingRunId(latest.status === "queued" || latest.status === "running" ? latest.run_id : null);
        setRunIdInput(targetRunId);
        setRunId(targetRunId);
        patchSession({
          run_id: targetRunId,
          model_name: selectedModel,
          run_status: latest.status,
          run_stage: latest.stage,
          run_progress: latest.progress,
          updated_at: latest.updated_at,
        });
      } catch (error) {
        setRunStatus(null);
        setActiveTrainingRunId(null);
        setSignals(null);
        setBacktest(null);
        setSummary(null);
        setPortfolioCurrent(null);
        setErrorMessage(error instanceof Error ? error.message : "Failed to load run by ID.");
      }
    },
    [backend, patchSession, runIdInput, selectedModel, setRunId],
  );

  useEffect(() => {
    if (!backend?.connected || runStatus) {
      return;
    }
    const existingRunId = session.run_id.trim();
    if (!existingRunId) {
      return;
    }
    setRunIdInput(existingRunId);
    void loadExistingRun(existingRunId);
  }, [backend, runStatus, loadExistingRun, session.run_id]);

  useEffect(() => {
    if (!backend?.connected || !runId || !runStatus) {
      return;
    }

    if (runStatus.status !== "queued" && runStatus.status !== "running") {
      return;
    }

    const timer = window.setInterval(async () => {
      try {
        const latest = await fetchRunStatus(backend.baseUrl, runId);
        setRunStatus(latest);
        patchSession({
          run_id: latest.run_id,
          model_name: selectedModel,
          run_status: latest.status,
          run_stage: latest.stage,
          run_progress: latest.progress,
          updated_at: latest.updated_at,
        });
        if (latest.status === "queued" || latest.status === "running") {
          setActiveTrainingRunId(latest.run_id);
        } else if (latest.status === "completed" || latest.status === "failed") {
          setActiveTrainingRunId((prev) => (prev === latest.run_id ? null : prev));
        }

        if (latest.status === "completed") {
          const latestSummary = await fetchArtifactSummary(backend.baseUrl, runId, selectedModel);
          setSummary(latestSummary);
          markArtifactReady("predictions", true);
        }
      } catch (error) {
        setErrorMessage(error instanceof Error ? error.message : "Failed to refresh run status.");
      }
    }, 3000);

    return () => window.clearInterval(timer);
  }, [backend, markArtifactReady, patchSession, runId, runStatus, selectedModel]);

  const parsedSymbols = useMemo(() => {
    const explicit = parseSymbolsText(symbolsInput);

    if (explicit.length > 0) {
      return explicit;
    }

    return universe?.assets.map((asset) => asset.symbol) ?? [];
  }, [symbolsInput, universe]);

  const canUseApi = backend?.connected === true;
  const canGenerateSignals = canUseApi && runStatus?.status === "completed";
  const dashboardLink = runId
    ? `/dashboard?run_id=${encodeURIComponent(runId)}&model=${encodeURIComponent(selectedModel)}&mode=backtest&focus=portfolio`
    : "/dashboard";

  const loadPortfolioCurrent = useCallback(
    async (options?: { suppressNotReady?: boolean; useCache?: boolean }) => {
      if (!backend?.connected || !runId) {
        return;
      }

      const suppressNotReady = options?.suppressNotReady ?? false;
      const useCache = options?.useCache ?? false;
      setIsLoadingPortfolio(true);
      setPortfolioError(null);
      try {
        const response = await fetchPortfolioCurrent(backend.baseUrl, runId, selectedModel, useCache);
        setPortfolioCurrent(response);
        const hasPortfolio = response.asset_class_weights.length > 0;
        markArtifactReady("portfolio_current", hasPortfolio);
        patchSession({
          data_timestamp: response.as_of_date ?? null,
          artifacts_ready: {
            portfolio_current: hasPortfolio,
          },
        });
      } catch (error) {
        const message =
          error instanceof Error ? error.message : "Failed to load portfolio rationale.";
        if (suppressNotReady && /Run backtest first/i.test(message)) {
          setPortfolioCurrent(null);
          setPortfolioError(null);
        } else {
          setPortfolioError(message);
        }
      } finally {
        setIsLoadingPortfolio(false);
      }
    },
    [backend, markArtifactReady, patchSession, runId, selectedModel],
  );

  useEffect(() => {
    if (!backend?.connected || !runId) {
      return;
    }
    void (async () => {
      try {
        const latestSummary = await fetchArtifactSummary(backend.baseUrl, runId, selectedModel);
        setSummary(latestSummary);
        const hasPredictions = latestSummary.available_artifacts.some((name) => name.startsWith("predictions"));
        markArtifactReady("predictions", hasPredictions);
      } catch {
        // summary is optional for model-switching UX.
      }
      await loadPortfolioCurrent({ suppressNotReady: true, useCache: true });
    })();
  }, [backend, loadPortfolioCurrent, markArtifactReady, runId, selectedModel]);

  const handleTrain = useCallback(async () => {
    if (!backend?.connected) {
      setErrorMessage("OpenBB API is not connected.");
      return;
    }

    setIsSubmittingTrain(true);
    setErrorMessage(null);
    setRunStatus(null);
    setSignals(null);
    setBacktest(null);
    setSummary(null);
    setPortfolioCurrent(null);
    setPortfolioError(null);
    setActiveTrainingRunId(null);

    try {
      const response = await startTrain(backend.baseUrl, {
        symbols: parsedSymbols,
        date_range: { start: dateStart, end: dateEnd },
        horizon_days: 1,
        model_config: modelConfig,
        feature_config: {
          lags: [1, 2, 3, 5, 10, 20],
          vol_windows: [5, 20],
          momentum_windows: [5, 20],
          include_rsi: true,
          include_macd: true,
          include_regime_features: true,
        },
        training_mode: "dual_compare",
        model_set: ["xgb_lstm", "lgbm_ranker"],
        walk_forward_config: defaultWalkForwardConfig,
        ranker_config: defaultRankerConfig,
        signal_config: {
          theta_grid: defaultThetaGrid,
          selection_metric: "val_sharpe",
        },
        portfolio_mode: "long_only",
        mu_mapping: "quantile_mean_return",
      });

      setRunStatus({
        run_id: response.run_id,
        status: "queued",
        progress: 0,
        stage: "queued",
        created_at: response.created_at,
        updated_at: response.created_at,
        logs_tail: ["Training job queued."],
        error: null,
      });
      setActiveTrainingRunId(response.run_id);
      patchSession({
        run_id: response.run_id,
        model_name: selectedModel,
        run_status: "queued",
        run_stage: "queued",
        run_progress: 0,
        updated_at: response.created_at,
        artifacts_ready: {
          predictions: false,
          signals: false,
          backtest: false,
          portfolio_current: false,
        },
      });
      const latest = await fetchRunStatus(backend.baseUrl, response.run_id);
      setRunStatus(latest);
      if (latest.status === "queued" || latest.status === "running") {
        setActiveTrainingRunId(latest.run_id);
      } else if (latest.status === "completed" || latest.status === "failed") {
        setActiveTrainingRunId(null);
      }
      setRunIdInput(response.run_id);
      setRunId(response.run_id);
      invalidateQuantCaches(backend.baseUrl, response.run_id, selectedModel);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to start training.");
    } finally {
      setIsSubmittingTrain(false);
    }
  }, [backend, dateEnd, dateStart, modelConfig, parsedSymbols, patchSession, selectedModel, setRunId]);

  const handleSignals = useCallback(async () => {
    if (!backend?.connected || !runId) {
      return;
    }

    setIsSubmittingSignals(true);
    setErrorMessage(null);

    try {
      const response = await createSignals(backend.baseUrl, {
        run_id: runId,
        model_name: selectedModel,
        top_k: topK,
        score_threshold: scoreThreshold,
      });
      setSignals(response);
      markArtifactReady("signals", true);
      markArtifactReady("predictions", true);
      patchSession({
        data_timestamp: response.as_of_date,
      });
      invalidateQuantCaches(backend.baseUrl, runId, selectedModel);

      const latestSummary = await fetchArtifactSummary(backend.baseUrl, runId, selectedModel);
      setSummary(latestSummary);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to generate signals.");
    } finally {
      setIsSubmittingSignals(false);
    }
  }, [backend, markArtifactReady, patchSession, runId, scoreThreshold, selectedModel, topK]);

  const handleBacktest = useCallback(async () => {
    if (!backend?.connected || !runId) {
      return;
    }

    setIsSubmittingBacktest(true);
    setErrorMessage(null);

    try {
      const response = await runBacktest(backend.baseUrl, {
        run_id: runId,
        model_name: selectedModel,
        start: dateStart,
        end: dateEnd,
        rebalance: "monthly",
        constraints: {
          max_weight: 0.2,
          long_only: true,
          risk_aversion: 3.0,
          lookback_days: 126,
        },
        cost_bps: 10,
        portfolio_mode: "long_only",
        mu_mapping: "quantile_mean_return",
      });
      setBacktest(response);
      markArtifactReady("backtest", true);
      patchSession({
        data_timestamp: response.end_date,
        artifacts_ready: {
          backtest: true,
        },
      });
      invalidateQuantCaches(backend.baseUrl, runId, selectedModel);

      const latestSummary = await fetchArtifactSummary(backend.baseUrl, runId, selectedModel);
      setSummary(latestSummary);
      await loadPortfolioCurrent({ suppressNotReady: false, useCache: false });
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to run backtest.");
    } finally {
      setIsSubmittingBacktest(false);
    }
  }, [backend, dateEnd, dateStart, loadPortfolioCurrent, markArtifactReady, patchSession, runId, selectedModel]);

  return (
    <div className="h-full min-h-0 overflow-auto py-4">
      <div className="mb-4">
        <h1 className="body-lg-medium text-theme-primary">Quant Lab</h1>
        <p className="body-sm-regular text-theme-muted">
          Local ML/DL quant workflow: train, signal generation, backtest, and SPY benchmark comparison.
        </p>
      </div>

      {errorMessage ? (
        <div className="mb-3 rounded-sm border border-red-500/60 bg-red-500/10 p-2">
          <p className="body-xs-medium text-red-400">{errorMessage}</p>
        </div>
      ) : null}

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-[360px_minmax(0,1fr)]">
        <div className="space-y-4">
          <PanelCard title="Controls" description="Universe, period, model, and run actions">
            <div className="space-y-3">
              <div>
                <p className="body-xs-medium text-theme-muted">Universe Profile</p>
                <div className="mt-1 flex flex-wrap gap-2">
                  {PROFILE_LIST.map((profile) => (
                    <button
                      key={profile.id}
                      type="button"
                      className={`rounded-sm px-2 py-1 body-xs-medium ${
                        selectedProfile === profile.id ? "button-neutral" : "button-secondary"
                      }`}
                      onClick={() => applyProfile(profile.id, universe)}
                      disabled={!universe}
                      title={profile.description}
                    >
                      {profile.id === "all" && universe ? `All (${universe.assets.length})` : profile.label}
                    </button>
                  ))}
                  <span className="rounded-sm bg-theme-secondary px-2 py-1 body-xs-regular text-theme-muted">
                    Current: {profileLabel(selectedProfile)}
                  </span>
                </div>
              </div>

              <div>
                <label htmlFor="quant-symbols" className="body-xs-medium text-theme-muted">
                  Symbols (comma/newline separated)
                </label>
                <textarea
                  id="quant-symbols"
                  className="mt-1 h-28 w-full resize-y rounded-sm border border-theme-outline bg-theme-secondary p-2 font-mono text-[13px] !leading-6 tracking-normal text-theme-primary"
                  value={symbolsInput}
                  spellCheck={false}
                  placeholder="SPY, QQQ, TLT ..."
                  onChange={(event) => {
                    setSelectedProfile("custom");
                    setSymbolsInput(event.target.value);
                  }}
                />
                <div className="mt-2 flex gap-2">
                  <button
                    type="button"
                    className="button-secondary rounded-sm px-2 py-1 body-xs-medium"
                    onClick={() => {
                      setSelectedProfile("custom");
                      setSymbolsInput(formatSymbolsForTextarea(parsedSymbols));
                    }}
                  >
                    Format
                  </button>
                  <button
                    type="button"
                    className="button-secondary rounded-sm px-2 py-1 body-xs-medium"
                    onClick={() => {
                      setSelectedProfile("custom");
                      setSymbolsInput("");
                    }}
                  >
                    Clear
                  </button>
                </div>
                <p className="mt-1 body-xs-regular text-theme-muted">
                  Parsed symbols: {parsedSymbols.length}
                  {universe ? ` / Universe version: ${universe.version}` : ""}
                </p>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <label className="body-xs-medium text-theme-muted">
                  Start
                  <input
                    type="date"
                    className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary p-2 body-xs-regular text-theme-primary"
                    value={dateStart}
                    onChange={(event) => setDateStart(event.target.value)}
                  />
                </label>
                <label className="body-xs-medium text-theme-muted">
                  End
                  <input
                    type="date"
                    className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary p-2 body-xs-regular text-theme-primary"
                    value={dateEnd}
                    onChange={(event) => setDateEnd(event.target.value)}
                  />
                </label>
              </div>

              <div className="grid grid-cols-[minmax(0,1fr)_auto] gap-2">
                <label className="body-xs-medium text-theme-muted">
                  Run ID
                  <input
                    type="text"
                    className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary p-2 body-xs-regular text-theme-primary"
                    value={runIdInput}
                    onChange={(event) => setRunIdInput(event.target.value)}
                    placeholder="Paste existing run_id"
                  />
                </label>
                <button
                  type="button"
                  className="button-secondary mb-0.5 self-end rounded-sm px-3 py-2 body-xs-medium"
                  onClick={() => {
                    void loadExistingRun();
                  }}
                  disabled={!canUseApi || !runIdInput.trim()}
                >
                  Load Run
                </button>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <label className="body-xs-medium text-theme-muted">
                  LSTM Seq Len
                  <input
                    type="number"
                    min={20}
                    max={240}
                    className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary p-2 body-xs-regular text-theme-primary"
                    value={modelConfig.seq_len}
                    onChange={(event) =>
                      setModelConfig((prev) => ({ ...prev, seq_len: Number(event.target.value) }))
                    }
                  />
                </label>
                <label className="body-xs-medium text-theme-muted">
                  LSTM Epochs
                  <input
                    type="number"
                    min={5}
                    max={300}
                    className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary p-2 body-xs-regular text-theme-primary"
                    value={modelConfig.lstm_epochs}
                    onChange={(event) =>
                      setModelConfig((prev) => ({ ...prev, lstm_epochs: Number(event.target.value) }))
                    }
                  />
                </label>
              </div>

              <div className="grid grid-cols-2 gap-2">
                <label className="body-xs-medium text-theme-muted">
                  Model
                  <select
                    className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary p-2 body-xs-regular text-theme-primary"
                    value={selectedModel}
                    onChange={(event) => {
                      const next = event.target.value as ModelName;
                      setSelectedModel(next);
                      setModelName(next);
                    }}
                  >
                    <option value="lgbm_ranker">LGBM Ranker</option>
                    <option value="xgb_lstm">XGB + LSTM</option>
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
                    onChange={(event) => setTopK(Number(event.target.value))}
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
                    onChange={(event) => setScoreThreshold(Number(event.target.value))}
                  />
                </label>
              </div>

              <div className="grid grid-cols-1 gap-2">
                <button
                  type="button"
                  className="button-neutral rounded-sm px-3 py-2 body-xs-medium"
                  onClick={handleTrain}
                  disabled={!canUseApi || isSubmittingTrain}
                >
                  {isSubmittingTrain ? "Submitting..." : "Start Training"}
                </button>
                <button
                  type="button"
                  className="button-secondary rounded-sm px-3 py-2 body-xs-medium"
                  onClick={handleSignals}
                  disabled={!canGenerateSignals || isSubmittingSignals}
                >
                  {isSubmittingSignals ? "Generating..." : "Generate Signals"}
                </button>
                <button
                  type="button"
                  className="button-secondary rounded-sm px-3 py-2 body-xs-medium"
                  onClick={handleBacktest}
                  disabled={!canGenerateSignals || isSubmittingBacktest}
                >
                  {isSubmittingBacktest ? "Running..." : "Run Backtest"}
                </button>
              </div>
            </div>
          </PanelCard>
        </div>

        <div className="space-y-4">
          <ConnectionStatusCard
            resolution={backend}
            isLoading={isResolvingBackend}
            onRetry={() => void resolveBackendAndUniverse()}
            onGoBackends={() => router.navigate({ to: "/backends" })}
          />
          <PanelCard title="Workflow Sync" description="Shared run/model session with Dashboard">
            <div className="space-y-2">
              <div className="rounded-sm bg-theme-secondary p-2">
                <p className="body-xs-regular text-theme-muted">
                  Run: <span className="text-theme-primary">{session.run_id || "-"}</span>
                </p>
                <p className="body-xs-regular text-theme-muted">
                  Model: <span className="text-theme-primary">{session.model_name}</span>
                </p>
                <p className="body-xs-regular text-theme-muted">
                  Dashboard timestamp: <span className="text-theme-primary">{session.data_timestamp || "-"}</span>
                </p>
              </div>
              <div className="grid grid-cols-2 gap-2">
                <div className="rounded-sm bg-theme-secondary p-2">
                  <p className="body-xxs-regular text-theme-muted">Predictions</p>
                  <p className="body-xs-medium text-theme-primary">{session.artifacts_ready.predictions ? "Ready" : "Not Ready"}</p>
                </div>
                <div className="rounded-sm bg-theme-secondary p-2">
                  <p className="body-xxs-regular text-theme-muted">Backtest</p>
                  <p className="body-xs-medium text-theme-primary">{session.artifacts_ready.backtest ? "Ready" : "Not Ready"}</p>
                </div>
                <div className="rounded-sm bg-theme-secondary p-2">
                  <p className="body-xxs-regular text-theme-muted">Signals</p>
                  <p className="body-xs-medium text-theme-primary">{session.artifacts_ready.signals ? "Ready" : "Not Ready"}</p>
                </div>
                <div className="rounded-sm bg-theme-secondary p-2">
                  <p className="body-xxs-regular text-theme-muted">Portfolio Rationale</p>
                  <p className="body-xs-medium text-theme-primary">{session.artifacts_ready.portfolio_current ? "Ready" : "Not Ready"}</p>
                </div>
              </div>
              <a className="button-secondary inline-flex rounded-sm px-3 py-2 body-xs-medium" href={dashboardLink}>
                Dashboard에서 리스크 구조 보기
              </a>
            </div>
          </PanelCard>
          <RunStatusCard run={runStatus} isLiveRun={runStatus?.run_id === activeTrainingRunId} />
          <SignalsTable asOfDate={signals?.as_of_date} signals={signals?.signals ?? []} />
          <MetricsCards metrics={backtest?.metrics ?? null} />
          <PortfolioRationaleCard
            portfolio={portfolioCurrent}
            isLoading={isLoadingPortfolio}
            errorMessage={portfolioError}
            onRetry={() => {
              void loadPortfolioCurrent({ suppressNotReady: false, useCache: false });
            }}
          />
          <EquityCurveChart
            points={backtest?.equity_curve ?? []}
            benchmarkPoints={backtest?.benchmark_curve ?? []}
            benchmarkSymbol={backtest?.benchmark_symbol ?? "SPY"}
            baseIndex={backtest?.base_index ?? 100}
          />
          <ExplainabilityCard summary={summary} />
        </div>
      </div>
    </div>
  );
}

export const Route = createFileRoute("/quant")({
  component: QuantPage,
});
