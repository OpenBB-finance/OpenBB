# Quant ML Backend-Frontend Integration Analysis

## 1. Endpoint Mapping (quantApi.ts ↔ quant_ml_router.py)

| quantApi.ts Function | HTTP Method | Path | quant_ml_router.py Route | Status |
|---------------------|-------------|------|--------------------------|--------|
| `fetchUniverse` | GET | `/api/v1/quant_ml/universe` | `universe()` | ✅ |
| `fetchUniverseList` | GET | `/api/v1/quant_ml/universe/list` | `universe_list()` | ✅ |
| `resolveUniverse` | GET | `/api/v1/quant_ml/universe/resolve` | `universe_resolve()` | ✅ |
| `startTrain` | POST | `/api/v1/quant_ml/train` | `train()` | ✅ |
| `fetchRunStatus` | GET | `/api/v1/quant_ml/runs/{run_id}` | `run_status()` | ✅ |
| `createSignals` | POST | `/api/v1/quant_ml/signals` | `signals()` | ✅ |
| `runBacktest` | POST | `/api/v1/quant_ml/backtest` | `backtest()` | ✅ |
| `runBacktestWalkforward` | POST | `/api/v1/quant_ml/backtest/walkforward` | `backtest_walkforward()` | ✅ |
| `fetchWalkforwardBacktestStatus` | GET | `/api/v1/quant_ml/backtest/walkforward/{job_id}` | `backtest_walkforward_status()` | ✅ |
| `fetchPromotedModel` | GET | `/api/v1/quant_ml/model/promoted` | `model_promoted()` | ✅ |
| `fetchRunLatestMeta` | GET | `/api/v1/quant_ml/run/latest/meta` | `run_latest_meta()` | ✅ |
| `fetchRunLatestRisk` | GET | `/api/v1/quant_ml/run/latest/risk` | `run_latest_risk()` | ✅ |
| `fetchRunLatestExposures` | GET | `/api/v1/quant_ml/run/latest/exposures` | `run_latest_exposures()` | ✅ |
| `fetchRunLatestConstraints` | GET | `/api/v1/quant_ml/run/latest/constraints` | `run_latest_constraints()` | ✅ |
| `fetchRunSnapshot` | GET | `/api/v1/quant_ml/runs/{run_id}/snapshot` | `run_snapshot()` | ✅ |
| `fetchRunRisk` | GET | `/api/v1/quant_ml/runs/{run_id}/risk` | `run_risk()` | ✅ |
| `fetchRunExposures` | GET | `/api/v1/quant_ml/runs/{run_id}/exposures` | `run_exposures()` | ✅ |
| `fetchRunConstraints` | GET | `/api/v1/quant_ml/runs/{run_id}/constraints` | `run_constraints()` | ✅ |
| `fetchRunAudit` | GET | `/api/v1/quant_ml/runs/{run_id}/audit` | `run_audit()` | ✅ |
| `fetchArtifactSummary` | GET | `/api/v1/quant_ml/artifacts/{run_id}/summary` | `artifacts_summary()` | ✅ |
| `fetchModelPerformance` | GET | `/api/v1/quant_ml/model/performance` | `model_performance()` | ✅ |
| `fetchModelIc` | GET | `/api/v1/quant_ml/model/ic` | `model_ic()` | ✅ |
| `fetchModelRegime` | GET | `/api/v1/quant_ml/model/regime` | `model_regime()` | ✅ |
| `fetchPortfolioCurrent` | GET | `/api/v1/quant_ml/portfolio/current` | `portfolio_current()` | ✅ |
| `fetchRebalanceHistory` | GET | `/api/v1/quant_ml/portfolio/rebalance/history` | `portfolio_rebalance_history()` | ✅ |
| `fetchPortfolioPolicy` | GET | `/api/v1/quant_ml/portfolio/policy` | `portfolio_policy()` | ✅ |
| `fetchUniverseSnapshot` | GET | `/api/v1/quant_ml/universe/snapshot` | `universe_snapshot()` | ✅ |
| `fetchUniverseExclusions` | GET | `/api/v1/quant_ml/universe/exclusions` | `universe_exclusions()` | ✅ |
| `fetchFeatureImportance` | GET | `/api/v1/quant_ml/feature/importance` | `feature_importance()` | ✅ |
| `fetchPredictionsLatest` | GET | `/api/v1/quant_ml/predictions/latest` | `predictions_latest()` | ✅ |
| `fetchDashboardHealth` | GET | `/api/v1/quant_ml/health` | `health()` | ⚠️ mode not passed |
| `fetchPerformanceRolling` | GET | `/api/v1/quant_ml/performance/rolling` | `performance_rolling()` | ✅ |
| `fetchPerformanceRegime` | GET | `/api/v1/quant_ml/performance/regime` | `performance_regime()` | ✅ |
| `fetchPortfolioExposure` | GET | `/api/v1/quant_ml/portfolio/exposure` | `portfolio_exposure()` | ✅ |
| `fetchPortfolioRisk` | GET | `/api/v1/quant_ml/portfolio/risk` | `portfolio_risk()` | ✅ |
| `fetchModelIcDecay` | GET | `/api/v1/quant_ml/model/ic_decay` | `model_ic_decay()` | ✅ |
| `fetchPredictionDistribution` | GET | `/api/v1/quant_ml/model/prediction_distribution` | `prediction_distribution()` | ✅ |
| `fetchRegimeCurrent` | GET | `/api/v1/quant_ml/regime/current` | `regime_current()` | ✅ |
| `fetchRegimeHistory` | GET | `/api/v1/quant_ml/regime/history` | `regime_history()` | ✅ |
| `fetchAlertsCurrent` | GET | `/api/v1/quant_ml/alerts/current` | `alerts_current()` | ✅ |
| `fetchAlertsHistory` | GET | `/api/v1/quant_ml/alerts/history` | `alerts_history()` | ✅ |
| `fetchModelShap` | GET | `/api/v1/quant_ml/model/shap` | `model_shap()` | ✅ |
| `previewExecutionOrders` | POST | `/api/v1/quant_ml/execution/orders/preview` | `execution_orders_preview()` | ✅ |
| `submitExecutionOrders` | POST | `/api/v1/quant_ml/execution/orders/submit` | `execution_orders_submit()` | ✅ |
| `riskCheckPretrade` | POST | `/api/v1/quant_ml/risk/check/pretrade` | `risk_check_pretrade_route()` | ✅ |
| `fetchExecutionOrdersCurrent` | GET | `/api/v1/quant_ml/execution/orders/current` | `execution_orders_current()` | ✅ |
| `fetchExecutionFillsHistory` | GET | `/api/v1/quant_ml/execution/fills/history` | `execution_fills_history()` | ✅ |
| `fetchExecutionPositionsCurrent` | GET | `/api/v1/quant_ml/execution/positions/current` | `execution_positions_current()` | ✅ |
| `fetchExecutionPnl` | GET | `/api/v1/quant_ml/execution/pnl` | `execution_pnl()` | ✅ |
| `fetchRiskLimits` | GET | `/api/v1/quant_ml/risk/limits` | `risk_limits()` | ✅ |
| `fetchRiskEvents` | GET | `/api/v1/quant_ml/risk/events` | `risk_events()` | ✅ |
| `fetchOpsStatus` | GET | `/api/v1/quant_ml/ops/status` | `ops_status()` | ✅ |

**Backend-only endpoints (no quantApi.ts wrapper):**
- `GET /market/ratio` – used via `macroApi.ts` (fetchMarketRatio)
- `GET /market/rolling_corr` – used via `macroApi.ts` (fetchMarketRollingCorr)

---

## 2. Type Alignment (quant.ts vs models.py)

### 2.1 Aligned Types

| Type | Status | Notes |
|------|--------|-------|
| `ModelName` | ✅ | Both: `"xgb_lstm" \| "lgbm_ranker"` |
| `TrainRunStatus` | ✅ | `queued \| running \| completed \| failed` |
| `WalkForwardJobStatus` | ✅ | Includes `not_found` |
| `DashboardPayloadStatus` | ✅ | `ok \| insufficient_data \| not_found` |
| `UniverseResponse` | ✅ | version, assets |
| `UniverseListPayload` | ✅ | universes array |
| `UniverseResolvePayload` | ✅ | universe_id, mode, count, symbols, etc. |
| `TrainRequestPayload` | ✅ | date_range, model_config, feature_config, etc. |
| `TrainResponsePayload` | ✅ | run_id, status, artifact_root, created_at |
| `RunStatusPayload` | ✅ | run_id, status, progress, stage, logs_tail, etc. |
| `SignalsResponsePayload` | ✅ | run_id, model_name, as_of_date, signals |
| `BacktestRequestPayload` | ✅ | start/end aliases, constraints |
| `BacktestResponsePayload` | ✅ | metrics, equity_curve, benchmark_curve |
| `PortfolioCurrentPayload` | ✅ | symbol_weights, asset_class_weights |
| `DashboardHealthPayload` | ✅ | mode_supported, workflow_state |
| `ExecutionOrderPreviewRequestPayload` | ✅ | run_id, model_name, slippage_bps, cost_bps, nav |
| `RiskPretradeRequestPayload` | ✅ | run_id, model_name, turnover_limit |

### 2.2 Type Mismatches / Gaps

| Area | Frontend (quant.ts) | Backend (models.py) | Issue |
|------|--------------------|---------------------|-------|
| **SignalsRequestPayload** | No `balanced_long_short` | `SignalRequest.balanced_long_short: bool = False` | Frontend cannot send this flag |
| **DateRange** | `DateRangeInput { start, end }` (strings) | `DateRange { start_date, end_date }` with aliases | Backend accepts `start`/`end`; alignment OK |
| **BacktestRequest** | `start`, `end` (strings) | `start_date`, `end_date` aliased to `start`/`end` | ✅ Aligned |
| **RollingPerformancePayload** | `exposure_ts: ExposureTimeSeriesPoint[]` (`{date,cash,gross,net}`) | `exposure_ts: list[dict[str, float \| str]]` | Backend may return different keys; runtime validation may fail |
| **DashboardHealthPayload** | `mode_supported: DashboardMode[]` | `mode_supported: list[DashboardMode]` | ✅ Aligned |
| **RunLatestMetaPayload** | `run_id?: string \| null` | `run_id: str \| None` | ✅ Aligned |
| **PortfolioSymbolWeightItem** | `category_l2?: string \| null` | `category_l2: str = "other"` | ✅ Aligned |
| **OpsStatusPayload** | `jobs: OpsJobStatePayload[]` | `jobs: list[OpsJobStateResponse]` | ✅ Aligned |

### 2.3 Schema Validation (quantSchemas.ts)

Parsed endpoints with Zod schema validation:

- `parseRunLatestMeta` – RunLatestMetaPayload
- `parseRunLatestConstraints` – RunLatestConstraintsPayload
- `parseRunSnapshot` – DashboardSnapshotV2Payload
- `parseRunAudit` – RunAuditPayload
- `parseRunRisk` – RunRiskPayload
- `parseRunExposures` – RunExposuresPayload

`run_risk` schema requires `position_risk_contrib_top10`; backend may omit it in some cases. Schema allows it; backend `PortfolioRiskResponse` includes it.

---

## 3. Payload / Field Mismatches

### 3.1 SignalsRequestPayload

**Missing:** `balanced_long_short`

- **Backend:** `SignalRequest.balanced_long_short: bool = False`
- **Frontend:** `SignalsRequestPayload` does not include this field
- **Impact:** Frontend cannot request balanced long/short signal selection

### 3.2 Health Endpoint – mode Parameter

**Frontend:** `fetchDashboardHealth` uses `options.mode` for cache TTL only; does not pass `mode` to backend.

**Backend:** `health()` has no `mode` parameter.

**Impact:** Backend cannot return mode-specific health; frontend cache behavior is correct (live=no cache, backtest=60s).

### 3.3 DashboardHealthResponse – Extra Backend Fields

Backend `DashboardHealthResponse` includes:

- `latest_market_date`
- `staleness_days`
- `recommended_portfolio_mode`

Frontend `DashboardHealthPayload` does not include these. Not a breaking change; frontend simply ignores them.

---

## 4. Caching, Error Handling, and Retry

### 4.1 Caching (quantCache.ts)

| Mechanism | Implementation |
|-----------|-----------------|
| **Storage** | In-memory `Map<string, { expiresAt, value }>` |
| **TTL** | `DASHBOARD_CACHE_TTL_MS = 60_000` (60s) for dashboard |
| **Live mode** | `LIVE_CACHE_TTL_MS = 0` – no cache |

**Cached endpoints:**

- `fetchModelPerformance` – 60s
- `fetchModelIc` – 60s
- `fetchModelRegime` – 60s
- `fetchFeatureImportance` – 60s
- `fetchPredictionsLatest` – 60s
- `fetchPortfolioCurrent` – optional (useCache)
- `fetchRebalanceHistory` – optional (useCache)
- `fetchDashboardHealth` – mode-dependent (live=0, backtest=60s)
- `fetchPerformanceRolling`, `fetchPerformanceRegime`, etc. – mode-dependent

**Cache invalidation:** `invalidateQuantCaches(baseUrl, runId?, modelName?)` clears prefixes:

- `dashboard-`
- `portfolio-current:`
- `portfolio-rebalance-history:`
- `predictions-latest:`
- `model-performance:`

### 4.2 Error Handling

| Layer | Behavior |
|-------|----------|
| **quantApi.ts** | `requestJson` throws `Error(detail \|\| status)` on non-OK; `detail` from `payload.detail` |
| **Backend** | `HTTPException` with `detail` for 400/404/409 |
| **quantSchemas** | Zod parse throws on validation failure |

### 4.3 Retry Logic

None in `quantApi.ts` or `quantCache.ts`. No retries on failure or timeout.

---

## 5. run_id and model_name Propagation

### 5.1 Run-Scoped Endpoints (run_id required)

| Endpoint | run_id Source | model_name Default |
|----------|---------------|-------------------|
| `fetchRunStatus` | Path param | N/A |
| `fetchRunSnapshot` | Path param | `lgbm_ranker` |
| `fetchRunRisk` | Path param | `lgbm_ranker` |
| `fetchRunExposures` | Path param | `lgbm_ranker` |
| `fetchRunConstraints` | Path param | `lgbm_ranker` |
| `fetchRunAudit` | Path param | N/A |
| `fetchArtifactSummary` | Path param | Required |
| `fetchModelPerformance` | Query | N/A |
| `fetchModelIc` | Query | `lgbm_ranker` |
| `fetchModelRegime` | Query | `lgbm_ranker` |
| `fetchPortfolioCurrent` | Query | Required |
| `fetchRebalanceHistory` | Query | Required |
| `fetchUniverseSnapshot` | Query | N/A |
| `fetchUniverseExclusions` | Query | N/A |
| `fetchFeatureImportance` | Query | Required |
| `fetchPredictionsLatest` | Query | Required |

### 5.2 Run-Latest Endpoints (run_id optional)

| Endpoint | run_id | model_name |
|----------|--------|------------|
| `fetchRunLatestMeta` | Optional | `lgbm_ranker` |
| `fetchRunLatestRisk` | Optional | `lgbm_ranker` |
| `fetchRunLatestExposures` | Optional | `lgbm_ranker` |
| `fetchRunLatestConstraints` | Optional | `lgbm_ranker` |
| `fetchDashboardHealth` | Optional | `lgbm_ranker` |
| `fetchPromotedModel` | N/A | `lgbm_ranker` |

### 5.3 Propagation Flow

- **run_id:** From session/UI → `QuantSessionState` → API calls
- **model_name:** Default `lgbm_ranker`; optional override in UI
- **invalidateQuantCaches:** `runId` and `modelName` used to clear cache for specific run/model

---

## 6. Integration Gaps and Potential Bugs

### 6.1 Critical / High

| # | Issue | Location | Severity |
|---|-------|----------|----------|
| 1 | **SignalsRequestPayload missing `balanced_long_short`** | quant.ts | Medium – feature not exposed |
| 2 | **portfolio/rebalance/history 404** | Logs show repeated 404s | High – backend may return 404 when backtest not run |

### 6.2 Medium

| # | Issue | Location | Severity |
|---|-------|----------|----------|
| 3 | **No retry logic** | quantApi.ts | Medium – transient failures not retried |
| 4 | **Health mode not passed to backend** | quantApi.ts | Low – backend does not use mode |

### 6.3 Low / Informational

| # | Issue | Location | Severity |
|---|-------|----------|----------|
| 5 | **DashboardHealthResponse extra fields** | Frontend ignores `latest_market_date`, `staleness_days`, `recommended_portfolio_mode` | Low |
| 6 | **market/ratio, market/rolling_corr** | In macroApi.ts, not quantApi.ts | Informational |

### 6.4 Known Bug (from logs)

- **portfolio/rebalance/history 404:** Backend requires backtest artifact before rebalance history exists. `get_rebalance_history` raises `ValueError` when backtest not found. Frontend should handle 404 and show appropriate UI state.

---

## 7. Recommendations

1. **Add `balanced_long_short` to SignalsRequestPayload** in `quant.ts` and pass it through `createSignals`.
2. **Add retry logic** for transient failures (e.g., 503, network errors) in `quantApi.ts`.
3. **Add explicit handling for 404 on portfolio/rebalance/history** in the UI (e.g., “Run backtest first”).
4. **Optional:** Add `mode` to backend `/health` if mode-specific health responses are needed.
5. **Optional:** Add `latest_market_date`, `staleness_days`, `recommended_portfolio_mode` to `DashboardHealthPayload` if the UI will use them.
