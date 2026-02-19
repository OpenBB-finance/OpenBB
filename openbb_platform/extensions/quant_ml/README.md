# OpenBB Quant ML Extension

`openbb-quant-ml` adds a local-first ML/DL quant workflow to the OpenBB Platform API.

## Features

- Universe endpoint for predefined multi-asset universe
- Asynchronous model training (XGBoost + PyTorch LSTM)
- Signal generation using ensemble forecasts
- Portfolio backtesting with mean-variance optimization
- Local artifact and cache storage under `~/.openbb_platform/quant_ml`

## Universe Files

Local universe files are discovered from:

- `openbb_platform/extensions/quant_ml/openbb_quant_ml/universe/<universe_id>.csv`
- `openbb_platform/extensions/quant_ml/openbb_quant_ml/universe/<universe_id>.txt`

CSV format:

- UTF-8
- header: `symbol`
- one symbol per row

Bundled universe ids:

- `kospi200`, `kosdaq100`, `sp500`, `nasdaq100`, `sox`, `dow30`

Training policy:

- `symbols` wins when provided
- if `symbols` is empty and `universe_id` is provided, strict resolve is used
- unknown or empty `universe_id` returns HTTP 400
- undersized universe CSV also returns HTTP 400 (`actual_count`, `minimum_required` in message)
- if neither is provided, default symbols from `config/universe.yaml` are used

Minimum size guardrails:

- `sp500 >= 450`
- `nasdaq100 >= 95`
- `dow30 >= 25`
- `sox >= 25`
- `kospi200 >= 180`
- `kosdaq100 >= 90`

## Refresh Universes

Refresh local CSVs with atomic writes:

```bash
PYTHONPATH=openbb_platform/extensions/quant_ml python -m openbb_quant_ml.tools.refresh_universes --all
PYTHONPATH=openbb_platform/extensions/quant_ml python -m openbb_quant_ml.tools.refresh_universes --only sp500 nasdaq100
PYTHONPATH=openbb_platform/extensions/quant_ml python -m openbb_quant_ml.tools.refresh_universes --all --dry-run
PYTHONPATH=openbb_platform/extensions/quant_ml python -m openbb_quant_ml.tools.refresh_universes --all --validate
```

Behavior:

- KR universes use `pykrx` when available
- US universes use Wikipedia table parsing
- default refresh mode is `--no-validate` (faster, stable bulk updates)
- optional fast validation uses `yfinance` only when `--validate` is passed
- failed refreshes do not overwrite existing CSV files
- undersized refresh output does not overwrite existing CSV files
- invalid symbols (when validation is on) are written to `_invalid_<universe_id>.csv`
- network/package failures are logged per-universe and do not crash unrelated universe refresh jobs

Optional dependency for KR refresh:

```bash
pip install pykrx
# or poetry install -E kr
```

## Endpoints

- `GET /api/v1/quant_ml/universe`
- `POST /api/v1/quant_ml/train`
- `GET /api/v1/quant_ml/runs/{run_id}`
- `POST /api/v1/quant_ml/signals`
- `POST /api/v1/quant_ml/backtest`
- `POST /api/v1/quant_ml/backtest/walkforward`
- `GET /api/v1/quant_ml/backtest/walkforward/{job_id}`
- `GET /api/v1/quant_ml/artifacts/{run_id}/summary`
- `GET /api/v1/quant_ml/portfolio/policy`
- `GET /api/v1/quant_ml/model/promoted`

## Portfolio Policy (Hard Constraints)

The extension enforces a centralized policy from:

- `openbb_platform/extensions/quant_ml/openbb_quant_ml/config/portfolio_policy.yaml`

Default live policy:

- single-name absolute weight cap: `10%` (hard)
- small-universe behavior: `cash_buffer`
- template: `diversified_long_only`
- risk defaults: `max_weight=0.10`, `sector_concentration=0.35`, `gross_exposure=1.0`, `net_exposure_abs=1.0`, `turnover=0.8`

Backtest responses include:

- `effective_constraints` (requested vs applied constraints)
- `cash_weight` (remaining capital not allocated to risky assets)

Quick verification:

```bash
pytest openbb_platform/extensions/quant_ml/tests/test_backtest.py -q
pytest openbb_platform/extensions/quant_ml/tests/test_execution_risk.py -q
pytest openbb_platform/extensions/quant_ml/tests/test_portfolio_policy.py -q
```

## Macro Tab API

Macro endpoints are available under:

- canonical: `/api/v1/quant_ml/macro/*`
- alias: `/api/v1/macro/*`

### Required environment variables

- `FRED_API_KEY=<your_key>`
- `OPENBB_API_BASE_URL=http://127.0.0.1:6900` (optional, for market fallback)

### Local data storage

- SQLite path: `~/.openbb_platform/quant_ml/macro/macro.db`
- Config path: `openbb_quant_ml/config/macro.yaml`

### Update commands

```bash
python -m openbb_quant_ml.service.macro_update --series UNRATE CPIAUCSL --start 1990-01-01 --end today
python -m openbb_quant_ml.service.macro_update --all-default --also-features --features-lookback-days 365
```

### Macro endpoints

- `GET /api/v1/quant_ml/macro/catalog`
- `GET /api/v1/quant_ml/macro/health`
- `POST /api/v1/quant_ml/macro/catalog/search`
- `POST /api/v1/quant_ml/macro/catalog/register`
- `GET /api/v1/quant_ml/macro/series?key=FRED:UNRATE&start=2015-01-01&end=2026-01-01&transform=yoy&freq=M&fill=ffill`
- `POST /api/v1/quant_ml/macro/expression`
- `GET /api/v1/quant_ml/macro/regime`
- `GET /api/v1/quant_ml/macro/alerts`
- `POST /api/v1/quant_ml/macro/derived/save`
- `GET /api/v1/quant_ml/macro/derived`
- `POST /api/v1/quant_ml/macro/update`
- `GET /api/v1/quant_ml/macro/presets/copper_gold`

If `/api/v1/macro/*` alias returns `404`, use canonical `/api/v1/quant_ml/macro/*` paths. The frontend macro client already falls back to canonical first.

### Copper/Gold preset examples

```bash
# canonical route
curl "http://127.0.0.1:6900/api/v1/quant_ml/macro/presets/copper_gold?start=2000-01-01&end=2024-08-19&freq=W&adjust_units=true&scale=1000"

# alias route
curl "http://127.0.0.1:6900/api/v1/macro/presets/copper_gold?start=2000-01-01&end=2024-08-19&freq=W&adjust_units=false&scale=1000"
```

### Manual expression examples

```bash
# simple ratio
curl -X POST "http://127.0.0.1:6900/api/v1/macro/expression" \
  -H "Content-Type: application/json" \
  -d "{\"expr\":\"(HG/GC)*1000\",\"freq\":\"W\",\"fill\":\"ffill\"}"

# per-ounce adjusted ratio
curl -X POST "http://127.0.0.1:6900/api/v1/macro/expression" \
  -H "Content-Type: application/json" \
  -d "{\"expr\":\"((HG/16)/(GC*0.911458))*1000\",\"freq\":\"W\",\"fill\":\"ffill\"}"
```

## Jobs CLI Scheduling

The operational jobs entrypoint:

```bash
PYTHONPATH=openbb_platform/extensions/quant_ml python -m openbb_quant_ml.jobs.cli daily --config openbb_platform/extensions/quant_ml/openbb_quant_ml/config/ops_jobs.yaml
PYTHONPATH=openbb_platform/extensions/quant_ml python -m openbb_quant_ml.jobs.cli weekly --config openbb_platform/extensions/quant_ml/openbb_quant_ml/config/ops_jobs.yaml
PYTHONPATH=openbb_platform/extensions/quant_ml python -m openbb_quant_ml.jobs.cli monthly --config openbb_platform/extensions/quant_ml/openbb_quant_ml/config/ops_jobs.yaml
PYTHONPATH=openbb_platform/extensions/quant_ml python -m openbb_quant_ml.jobs.cli bootstrap --config openbb_platform/extensions/quant_ml/openbb_quant_ml/config/ops_jobs.yaml
```

Run id scheme and incremental defaults (`ops_jobs.yaml`):

- `defaults.run_id_scheme: compact_v1`
- `defaults.training_run_id_scheme: compact_v1`
- `defaults.pretrain_bootstrap_enabled: true`
- `daily.predict_mode: infer_only`
- `daily.predict_fallback_legacy: true`
- `daily.market_delta_days: 45`
- `daily.feature_delta_days: 120`
- `daily.max_infer_workers: 4`
- `weekly.promote_on_success: true`
- `retention.policy: keep_all`
- `retention.index_compaction: true`

Compact run id examples:

- daily: `dly-260219-01`
- weekly: `wkl-260219-01`
- monthly: `mth-260301-01`
- training: `trn-260219-001`

Operational policy:

- Daily: infer-only refresh (no model retraining)
- Weekly/Monthly: full model training + promotion workflow
- Bootstrap (one-time): cache warmup + feature precompute + weekly-style train/promote
- Backtest dual mode:
  - fast: existing `/backtest`
  - walk-forward: `/backtest/walkforward` async job

Rollback switches:

- `run_id_scheme: legacy`
- `training_run_id_scheme: legacy`
- `daily.predict_mode: legacy`

Ops status endpoint:

- `GET /api/v1/quant_ml/ops/status`

Cache warmup helper:

```bash
python -m openbb_quant_ml.service.data_cache_warmup --symbols-file universe/sp500.txt --start 2010-01-01 --end today
```

Baseline snapshot helper:

```bash
python -m openbb_quant_ml.service.baseline_snapshot --run-id <run_id> --period 1y --symbols-count 20 --target-mode next_open_to_close --entry-price next_open --exit-price close
```

### Windows Task Scheduler example

```powershell
schtasks /Create /F /TN "QuantML-Daily" /SC WEEKLY /D MON,TUE,WED,THU,FRI /ST 18:30 /TR "powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\Users\<user>\quant_ml_jobs\quantml_daily.ps1"
schtasks /Create /F /TN "QuantML-Weekly" /SC WEEKLY /D SAT /ST 08:00 /TR "powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\Users\<user>\quant_ml_jobs\quantml_weekly.ps1"
schtasks /Create /F /TN "QuantML-Monthly" /SC MONTHLY /D 1 /ST 09:00 /TR "powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\Users\<user>\quant_ml_jobs\quantml_monthly.ps1"
```

### cron appendix (Linux)

```bash
30 18 * * 1-5 cd <REPO_ROOT> && PYTHONPATH=openbb_platform/extensions/quant_ml python -m openbb_quant_ml.jobs.cli daily --config openbb_platform/extensions/quant_ml/openbb_quant_ml/config/ops_jobs.yaml
0 8 * * 6 cd <REPO_ROOT> && PYTHONPATH=openbb_platform/extensions/quant_ml python -m openbb_quant_ml.jobs.cli weekly --config openbb_platform/extensions/quant_ml/openbb_quant_ml/config/ops_jobs.yaml
0 9 1 * * cd <REPO_ROOT> && PYTHONPATH=openbb_platform/extensions/quant_ml python -m openbb_quant_ml.jobs.cli monthly --config openbb_platform/extensions/quant_ml/openbb_quant_ml/config/ops_jobs.yaml
```
