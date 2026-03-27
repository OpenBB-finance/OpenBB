/// <reference types="vitest/globals" />
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";
import { vi } from "vitest";
import { invoke } from "@tauri-apps/api/core";
import { clearCachePrefix } from "../../lib/quantCache";
import { Route as DashboardRoute } from "../../routes/dashboard";

vi.mock("@tanstack/react-router", () => ({
  createFileRoute: vi.fn(() => (options: { component: React.ComponentType }) => ({
    options: {
      component: options.component,
    },
  })),
  useNavigate: vi.fn(() => vi.fn()),
}));

vi.mock("@tauri-apps/api/core", () => ({
  invoke: vi.fn(),
}));

function mockJsonResponse(payload: unknown, ok = true, status = 200): Response {
  return {
    ok,
    status,
    json: async () => payload,
  } as Response;
}

describe("Dashboard Route v3", () => {
  const DashboardComponent = DashboardRoute.options.component as React.ComponentType;
  let endpointHits: Record<string, number>;

  const hit = (key: string) => {
    endpointHits[key] = (endpointHits[key] ?? 0) + 1;
  };

  beforeEach(() => {
    vi.clearAllMocks();
    clearCachePrefix("");
    endpointHits = {};
    localStorage.setItem("quant_latest_run_id", "run-1");

    vi.mocked(invoke).mockResolvedValue([
      {
        id: "openbb-api",
        name: "OpenBB API",
        command: "openbb-api --host 127.0.0.1 --port 6900",
        status: "running",
        url: "http://127.0.0.1:6900",
      },
    ]);

    global.fetch = vi.fn(async (input: string | URL) => {
      const url = String(input);
    if (url.endsWith("/api/v1/coverage/providers") || url.endsWith("/api/v1/system")) {
        return mockJsonResponse({ results: {} });
      }
      if (url.endsWith("/api/v1/quant_ml/portfolio/policy")) {
        return mockJsonResponse({
          template: "diversified_long_only",
          single_name_max_abs_weight: 0.1,
          small_universe_policy: "cash_buffer",
          sector_concentration_max: 0.35,
          turnover_max: 0.8,
          gross_exposure_max: 1.0,
          net_exposure_abs_max: 1.0,
          cash_symbol: "CASH",
          cash_category: "cash_proxy",
        });
      }
      if (url.includes("/api/v1/quant_ml/dashboard/bootstrap")) {
        hit("dashboard_bootstrap");
        return mockJsonResponse({
          health: {
            run_id: "run-1",
            model_name: "lgbm_ranker",
            status: "ok",
            backend_connected: true,
            backend_source: "quant_ml_api",
            backend_detail: "quant_ml_api_connected",
            latest_run_id: "run-1",
            resolved_run_id: "run-1",
            mode_supported: ["live", "backtest"],
            data_timestamp: "2026-02-01",
            universe_size: 50,
            cost_bps: 10,
            cash_exposure: 0.0,
            gross_exposure: 1.0,
            net_exposure: 1.0,
            strategy_health: {
              signal_dispersion: 1.02,
              crowding_risk_proxy: 0.28,
              market_correlation: 0.44,
              regime_mismatch_risk: 0.12,
              prediction_confidence: 0.78,
            },
          },
          snapshot: {
            run_id: "run-1",
            run_uid: "uid-1",
            model_name: "lgbm_ranker",
            snapshot_profile: "core",
            as_of_utc: "2026-02-01T00:00:00Z",
            total_return: 0.03,
            cagr: 0.04,
            sharpe: 1.1,
            sortino: 1.3,
            max_drawdown: -0.1,
            volatility: 0.12,
            turnover: 0.4,
            win_rate: 0.55,
            exposure: { us_sector_etf: 0.6 },
            risk_contrib_top10: [{ symbol: "XLK", contribution: 0.03 }],
            constraint_bindings: [],
            ic_rolling: [{ date: "2026-02-01", value: 0.08 }],
            regime_current: { trend_regime: "bull", vol_regime: "mid", liquidity_regime: "mid" },
            alerts_current_count: 1,
            constraint_summary: { binding_rows: 1 },
            artifact_summary: {
              run_id: "run-1",
              model_name: "lgbm_ranker",
              model_meta: {},
              latest_validation_error: null,
              feature_importance: [],
              params: {
                request: {
                  walk_forward_config: {
                    train_months: 36,
                    val_months: 1,
                  },
                },
              },
              available_artifacts: [],
            },
            model_performance: {
              run_id: "run-1",
              models: [
                {
                  model_name: "lgbm_ranker",
                  train_ic: 0.11,
                  val_ic: 0.08,
                  ndcg: 0.62,
                  sharpe: 1.12,
                  max_dd: -0.13,
                  turnover: 0.41,
                  hit_rate: 0.58,
                },
              ],
            },
            run_latest_meta: {
              run_id: "run-1",
              run_uid: "uid-1",
              model_name: "lgbm_ranker",
              as_of_date: "2026-02-01",
              status: "ok",
              artifact_contract_version: "v1",
              required_artifacts_ready: true,
              universe_stage_counts: { u0: 50 },
              artifact_completeness: [],
              message: null,
            },
            currency: "USD",
          },
        });
      }
      if (url.includes("/api/v1/quant_ml/health")) {
        hit("health");
        return mockJsonResponse({
          run_id: "run-1",
          model_name: "lgbm_ranker",
          status: "ok",
          backend_connected: true,
          backend_source: "quant_ml_api",
          backend_detail: "quant_ml_api_connected",
          latest_run_id: "run-1",
          resolved_run_id: "run-1",
          mode_supported: ["live", "backtest"],
          data_timestamp: "2026-02-01",
          universe_size: 50,
          cost_bps: 10,
          cash_exposure: 0.0,
          gross_exposure: 1.0,
          net_exposure: 1.0,
          strategy_health: {
            signal_dispersion: 1.02,
            crowding_risk_proxy: 0.28,
            market_correlation: 0.44,
            regime_mismatch_risk: 0.12,
            prediction_confidence: 0.78,
          },
        });
      }
      if (url.includes("/api/v1/quant_ml/runs/run-1/snapshot")) {
        hit("run_snapshot");
        return mockJsonResponse({
          run_id: "run-1",
          run_uid: "uid-1",
          model_name: "lgbm_ranker",
          snapshot_profile: "full",
          as_of_utc: "2026-02-01T00:00:00Z",
          total_return: 0.03,
          cagr: 0.04,
          sharpe: 1.1,
          sortino: 1.3,
          max_drawdown: -0.1,
          volatility: 0.12,
          turnover: 0.4,
          win_rate: 0.55,
          exposure: { us_sector_etf: 0.6 },
          risk_contrib_top10: [{ symbol: "XLK", contribution: 0.03 }],
          constraint_bindings: [],
          ic_rolling: [{ date: "2026-02-01", value: 0.08 }],
          regime_current: { trend_regime: "bull", vol_regime: "mid", liquidity_regime: "mid" },
          alerts_current_count: 1,
          constraint_summary: { binding_rows: 1 },
          artifact_summary: {
            run_id: "run-1",
            model_name: "lgbm_ranker",
            model_meta: {},
            latest_validation_error: null,
            feature_importance: [],
            params: {
              request: {
                walk_forward_config: {
                  train_months: 36,
                  val_months: 1,
                },
              },
            },
            available_artifacts: [],
          },
          model_performance: {
            run_id: "run-1",
            models: [
              {
                model_name: "lgbm_ranker",
                train_ic: 0.11,
                val_ic: 0.08,
                ndcg: 0.62,
                sharpe: 1.12,
                max_dd: -0.13,
                turnover: 0.41,
                hit_rate: 0.58,
              },
            ],
          },
          run_latest_meta: {
            run_id: "run-1",
            run_uid: "uid-1",
            model_name: "lgbm_ranker",
            as_of_date: "2026-02-01",
            status: "ok",
            artifact_contract_version: "v1",
            required_artifacts_ready: true,
            universe_stage_counts: { u0: 50 },
            artifact_completeness: [],
            message: null,
          },
          currency: "USD",
        });
      }
      if (url.includes("/api/v1/quant_ml/artifacts/run-1/summary")) {
        hit("summary");
        return mockJsonResponse({
          run_id: "run-1",
          model_name: "lgbm_ranker",
          model_meta: {},
          feature_importance: [],
          params: {
            request: {
              walk_forward_config: {
                train_months: 36,
                val_months: 1,
              },
            },
          },
          available_artifacts: [],
        });
      }
      if (url.includes("/api/v1/quant_ml/model/performance")) {
        hit("model_performance");
        return mockJsonResponse({
          run_id: "run-1",
          models: [
            {
              model_name: "lgbm_ranker",
              train_ic: 0.11,
              val_ic: 0.08,
              ndcg: 0.62,
              sharpe: 1.12,
              max_dd: -0.13,
              turnover: 0.41,
              hit_rate: 0.58,
            },
          ],
        });
      }
      if (url.includes("/api/v1/quant_ml/performance/rolling")) {
        hit("performance_rolling");
        return mockJsonResponse({
          run_id: "run-1",
          model_name: "lgbm_ranker",
          status: "ok",
          window_short: 63,
          window_long: 126,
          cumulative_return: [
            { date: "2026-01-01", value: 0.01 },
            { date: "2026-02-01", value: 0.03 },
          ],
          rolling_sharpe_3m: [{ date: "2026-02-01", value: 1.1 }],
          rolling_sharpe_6m: [{ date: "2026-02-01", value: 0.9 }],
          rolling_ic_3m: [{ date: "2026-02-01", value: 0.08 }],
          rolling_ic_6m: [{ date: "2026-02-01", value: 0.05 }],
          rolling_maxdd: [{ date: "2026-02-01", value: -0.1 }],
          turnover_ts: [{ date: "2026-02-01", value: 0.4 }],
          exposure_ts: [{ date: "2026-02-01", cash: 0, gross: 1, net: 1 }],
        });
      }
      if (url.includes("/api/v1/quant_ml/performance/regime")) {
        return mockJsonResponse({
          run_id: "run-1",
          model_name: "lgbm_ranker",
          status: "ok",
          trend_regime_perf: { bull: { count: 10, mean_return: 0.001, sharpe: 1.3, ic: 0.07, turnover: 0.3 } },
          vol_regime_perf: {},
          liquidity_regime_perf: {},
          matrix_2d: [{ trend_regime: "bull", vol_regime: "mid", count: 10, sharpe: 1.3, mean_return: 0.001, ic: 0.07 }],
        });
      }
      if (url.includes("/api/v1/quant_ml/regime/current")) {
        return mockJsonResponse({
          run_id: "run-1",
          model_name: "lgbm_ranker",
          status: "ok",
          trend_regime: "bull",
          vol_regime: "mid",
          liquidity_regime: "mid",
          vix_level: 16.2,
          breadth: 0.61,
          spx_distance_200ma: 0.04,
        });
      }
      if (url.includes("/api/v1/quant_ml/regime/history")) {
        return mockJsonResponse({
          run_id: "run-1",
          model_name: "lgbm_ranker",
          status: "ok",
          history: [{ date: "2026-02-01", trend_regime: "bull", vol_regime: "mid", liquidity_regime: "mid", vix_level: 16, breadth: 0.6, spx_distance_200ma: 0.03 }],
          regime_transition_stats: { total_points: 1, transitions: 0, transition_rate: 0 },
        });
      }
      if (url.includes("/api/v1/quant_ml/portfolio/exposure")) {
        return mockJsonResponse({
          run_id: "run-1",
          model_name: "lgbm_ranker",
          status: "ok",
          sector_exposure: [{ category: "us_sector_etf", weight: 0.6 }],
          factor_exposure: { momentum: 0.2, value: 0.1, size: 0.05, volatility: -0.1 },
          beta_spy: 0.9,
          beta_qqq: 1.1,
          duration_estimate: 2.2,
          top10_long: [{ symbol: "XLK", weight: 0.2 }],
          top10_short: [],
        });
      }
      if (url.includes("/api/v1/quant_ml/portfolio/risk")) {
        return mockJsonResponse({
          run_id: "run-1",
          model_name: "lgbm_ranker",
          status: "ok",
          vol_ex_ante: 0.15,
          cvar_95: -0.022,
          position_risk_contrib_top5: [{ symbol: "XLK", contribution: 0.03 }],
          position_return_contrib_top5: [{ symbol: "XLK", contribution: 0.02 }],
          worst5_positions: [{ symbol: "XLF", contribution: -0.01 }],
        });
      }
      if (url.includes("/api/v1/quant_ml/feature/importance")) {
        return mockJsonResponse({
          run_id: "run-1",
          model_name: "lgbm_ranker",
          items: [{ feature: "ret_lag_1", importance: 0.2 }],
        });
      }
      if (url.includes("/api/v1/quant_ml/model/prediction_distribution")) {
        return mockJsonResponse({
          run_id: "run-1",
          model_name: "lgbm_ranker",
          status: "ok",
          bins: 10,
          histogram: [{ bin_left: -0.01, bin_right: -0.005, count: 2 }],
          top_decile_mean: 0.011,
          bottom_decile_mean: -0.008,
          decile_spread_ts: [{ date: "2026-02-01", spread: 0.019 }],
        });
      }
      if (url.includes("/api/v1/quant_ml/model/ic_decay")) {
        hit("model_ic_decay");
        return mockJsonResponse({
          run_id: "run-1",
          model_name: "lgbm_ranker",
          status: "ok",
          max_horizon: 20,
          ic_decay: [{ horizon: 1, ic: 0.1 }],
          ic_t_stat: 1.9,
        });
      }
      if (url.includes("/api/v1/quant_ml/predictions/latest")) {
        return mockJsonResponse({
          run_id: "run-1",
          model_name: "lgbm_ranker",
          as_of_date: "2026-02-01",
          predictions: [{ symbol: "XLK", predicted_return: 0.01, z_score: 1.2 }],
        });
      }
      if (url.includes("/api/v1/quant_ml/alerts/current")) {
        return mockJsonResponse({
          run_id: "run-1",
          model_name: "lgbm_ranker",
          status: "ok",
          alerts: [{ rule_id: "maxdd_over_15pct", severity: "critical", triggered_at: "2026-02-01T00:00:00Z", message: "Max drawdown exceeded 15%.", value: -0.2 }],
        });
      }
      if (url.includes("/api/v1/quant_ml/alerts/history")) {
        return mockJsonResponse({
          run_id: "run-1",
          model_name: "lgbm_ranker",
          status: "ok",
          alerts: [{ rule_id: "maxdd_over_15pct", severity: "critical", triggered_at: "2026-02-01T00:00:00Z", message: "Max drawdown exceeded 15%.", value: -0.2 }],
        });
      }
      return mockJsonResponse({ detail: "not-found" }, false, 404);
    }) as unknown as typeof fetch;
  });

  test("renders dashboard v3 widgets", async () => {
    await act(async () => {
      render(<DashboardComponent />);
    });

    await waitFor(() => {
      expect(screen.getByText("Quant Dashboard v3")).toBeInTheDocument();
      expect(screen.getByText(/Run Action Center/i)).toBeInTheDocument();
      expect(screen.getByText(/Single-name 10% \(Hard\)/i)).toBeInTheDocument();
    });

    await act(async () => {
      fireEvent.click(screen.getAllByRole("tab")[2]);
    });
    await waitFor(() => {
      expect(screen.getByText(/Strategy Health/i)).toBeInTheDocument();
      expect(screen.getByText(/Strategy Alerts/i)).toBeInTheDocument();
    });

    await act(async () => {
      fireEvent.click(screen.getAllByRole("tab")[1]);
    });
    await waitFor(() => {
      expect(screen.getByText(/Regime Matrix/i)).toBeInTheDocument();
    });

    await act(async () => {
      fireEvent.click(screen.getAllByRole("tab")[4]);
    });
    await waitFor(() => {
      expect(screen.getByText(/TradingView Heatmap/i)).toBeInTheDocument();
    });
  });

  test("loads core first and lazy-loads tab endpoints", async () => {
    await act(async () => {
      render(<DashboardComponent />);
    });

    await waitFor(() => {
      expect(screen.getByText("Quant Dashboard v3")).toBeInTheDocument();
    });
    expect(endpointHits.dashboard_bootstrap ?? 0).toBeGreaterThanOrEqual(1);
    expect(endpointHits.run_snapshot ?? 0).toBe(0);
    expect(endpointHits.summary ?? 0).toBe(0);
    expect(endpointHits.model_performance ?? 0).toBe(0);
    expect(endpointHits.performance_rolling ?? 0).toBe(0);
    expect(endpointHits.model_ic_decay ?? 0).toBe(0);

    await act(async () => {
      fireEvent.click(screen.getByRole("tab", { name: "Performance" }));
    });

    await waitFor(() => {
      expect(endpointHits.performance_rolling ?? 0).toBeGreaterThanOrEqual(1);
    });
  });
});
