# OpenBB Quant ML Extension

`openbb-quant-ml` adds a local-first ML/DL quant workflow to the OpenBB Platform API.

## Features

- Universe endpoint for predefined multi-asset universe
- Asynchronous model training (XGBoost + PyTorch LSTM)
- Signal generation using ensemble forecasts
- Portfolio backtesting with mean-variance optimization
- Local artifact and cache storage under `~/.openbb_platform/quant_ml`

## Quick Start

Use this as the canonical local dev path for the Quant ML stack:

```powershell
uv venv .venv --python 3.11
.\.venv\Scripts\python.exe openbb_platform/dev_install.py -e --bootstrap-installer uv
.\start_all.ps1 -ApiNoBuild $true -ApiAuthMode enabled -QuantMlTrainingBackend process
.\qa\scripts\quant_ml_startup_smoke.ps1 -RepoRoot .
npm.cmd test -- --run src/tests/routes/__root.test.tsx src/tests/routes/finance.test.tsx src/tests/routes/trading.test.tsx src/tests/lib/openbbBackend.test.ts src/tests/lib/openbbSse.test.ts src/tests/routes/backends.test.tsx src/tests/routes/quant.test.tsx src/tests/routes/macro.test.tsx
```

Defaults chosen for this repo:

- Poetry remains the dependency resolver and `openbb_platform/poetry.lock` remains the source of truth.
- `uv` is used for bootstrap and runner setup, not for replacing Poetry metadata.
- `start_all.ps1` defaults to auth-enabled local startup.
- `Finance Lab` is the canonical desktop label for the `/finance` route.

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
- `russell1000 >= 900`
- `kospi200 >= 180`
- `kosdaq100 >= 90`
- `all_in_one >= 1200`

## Refresh Universes

Refresh local CSVs with atomic writes:

```bash
PYTHONPATH=openbb_platform/extensions/quant_ml python -m openbb_quant_ml.tools.refresh_universes --all
PYTHONPATH=openbb_platform/extensions/quant_ml python -m openbb_quant_ml.tools.refresh_universes --only sp500 nasdaq100
PYTHONPATH=openbb_platform/extensions/quant_ml python -m openbb_quant_ml.tools.refresh_universes --only russell1000 all_in_one --no-validate
PYTHONPATH=openbb_platform/extensions/quant_ml python -m openbb_quant_ml.tools.refresh_universes --all --dry-run
PYTHONPATH=openbb_platform/extensions/quant_ml python -m openbb_quant_ml.tools.refresh_universes --all --validate
```

Behavior:

- KR universes use `pykrx` when available
- US universes use Wikipedia table parsing
- `russell1000` uses iShares IWB holdings CSV parsing
- `all_in_one` merges KR/US stock universes and only keeps ETF categories:
  `bond_etf`, `commodity_etf`, `currency_etf`
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

## Optional Runtime Features

Install optional dependencies only for the features you need:

```bash
python -m pip install "./openbb_platform/extensions/quant_ml[cache,tracking]"
# or, from openbb_platform/: poetry install --extras quant_ml --no-interaction --no-ansi && python -m pip install "./extensions/quant_ml[cache,tracking]"
```

Supported extras:

- `kr`: `pykrx` universe refresh
- `catboost`: CatBoost ranker
- `hpo`: Optuna-based tuning
- `cvar`: CVXPY-based CVaR optimization
- `hmm`: HMM regime modeling
- `cache`: Redis-backed shared runtime cache
- `tracking`: MLflow run mirroring

Dependency and lockfile policy:

- `openbb_platform/poetry.lock` is the repository-level source of truth.
- `openbb_platform/extensions/quant_ml/uv.lock` is intentionally not used.
- `cache` and `tracking` stay as extension-level extras and are installed explicitly where needed.

Environment template:

- copy `openbb_platform/extensions/quant_ml/.env.example` into your local secret management flow or CI environment
- package installation alone does not activate Redis or MLflow; the corresponding env vars must also be present

Runtime environment variables:

- `OPENBB_API_AUTH=true`: enable OpenBB core HTTP Basic auth
- `OPENBB_API_USERNAME` / `OPENBB_API_PASSWORD`: credentials used by `OPENBB_API_AUTH`
- `OPENBB_QUANT_ML_CACHE_REDIS_URL` or `OPENBB_QUANT_ML_REDIS_URL`: enable shared Redis cache for router read caches
- `OPENBB_QUANT_ML_CACHE_PREFIX`: Redis key prefix, default `openbb:quant-ml:cache`
- `OPENBB_QUANT_ML_TRAINING_BACKEND=thread|process`: choose in-process thread dispatch or isolated spawn process dispatch for training jobs
- `OPENBB_QUANT_ML_MLFLOW_ENABLED=true`: opt in to MLflow mirror writes
- `OPENBB_QUANT_ML_MLFLOW_TRACKING_URI` or `MLFLOW_TRACKING_URI`: MLflow server location
- `OPENBB_QUANT_ML_MLFLOW_EXPERIMENT_NAME` or `MLFLOW_EXPERIMENT_NAME`: target MLflow experiment name

Launcher examples:

```powershell
$env:OPENBB_API_AUTH = "true"
$env:OPENBB_API_USERNAME = "openbb"
$env:OPENBB_API_PASSWORD = "change-me"
$env:OPENBB_QUANT_ML_CACHE_REDIS_URL = "redis://127.0.0.1:6379/0"
$env:OPENBB_QUANT_ML_MLFLOW_ENABLED = "true"
$env:OPENBB_QUANT_ML_MLFLOW_TRACKING_URI = "http://127.0.0.1:5000"
.\start_all.ps1 -ApiNoBuild $true -ApiAuthMode enabled -QuantMlTrainingBackend process
```

`start_all.ps1` now defaults to `-ApiAuthMode enabled`. When it launches the API itself and no password is already configured, it generates a temporary dev-session Basic password, uses it for API readiness probes, and injects the same credentials into the frontend dev server through `VITE_OPENBB_API_USERNAME` / `VITE_OPENBB_API_PASSWORD`.

That generated password is a local development convenience only. Staging and production should always provide explicit credentials through environment variables or an external secret manager.

Without `start_all.ps1`, the API can be started directly:

```powershell
$env:OPENBB_API_AUTH = "true"
$env:OPENBB_API_USERNAME = "openbb"
$env:OPENBB_API_PASSWORD = "change-me"
$env:OPENBB_QUANT_ML_TRAINING_BACKEND = "process"
$env:OPENBB_QUANT_ML_CACHE_REDIS_URL = "redis://127.0.0.1:6379/0"
$env:OPENBB_QUANT_ML_MLFLOW_ENABLED = "true"
$env:OPENBB_QUANT_ML_MLFLOW_TRACKING_URI = "http://127.0.0.1:5000"
openbb-api --host 127.0.0.1 --port 6900 --workers 1 --no-build
```

Desktop note:

- The Backends page supports both Basic credentials and Bearer tokens for OpenBB API requests.
- When both are stored, Basic credentials take precedence because current OpenBB core auth uses HTTP Basic.
- For dev runs launched by `start_all.ps1`, the frontend can authenticate automatically from injected Vite env vars even before anything is stored locally.

## Docker and Staging

The staging image is built from local repository source, not from PyPI packages. `build/docker/platformAPI.Dockerfile` installs the checked-out `openbb_platform` tree and then explicitly installs the quant optional runtime extras:

```bash
docker build -f build/docker/platformAPI.Dockerfile -t openbb-platform-api:local .
```

Authenticated local container smoke example:

```bash
docker run --rm -d \
  --name openbb-platform-api-local \
  -p 6900:6900 \
  -e OPENBB_API_AUTH=true \
  -e OPENBB_API_USERNAME=openbb \
  -e OPENBB_API_PASSWORD=change-me \
  -e OPENBB_QUANT_ML_TRAINING_BACKEND=process \
  -e OPENBB_QUANT_ML_CACHE_REDIS_URL=redis://host.docker.internal:6379/0 \
  -e OPENBB_QUANT_ML_MLFLOW_ENABLED=false \
  openbb-platform-api:local

curl -u openbb:change-me http://127.0.0.1:6900/api/v1/coverage/providers
curl -u openbb:change-me http://127.0.0.1:6900/api/v1/quant_ml/health
```

The staging workflow expects these GitHub environment variables and secrets:

- `vars.QUANT_STAGING_API_AUTH`
- `secrets.QUANT_STAGING_API_USERNAME`
- `secrets.QUANT_STAGING_API_PASSWORD`
- `vars.QUANT_STAGING_TRAINING_BACKEND`
- `secrets.QUANT_STAGING_CACHE_REDIS_URL`
- `vars.QUANT_STAGING_MLFLOW_ENABLED`
- `secrets.QUANT_STAGING_MLFLOW_TRACKING_URI`
- `vars.QUANT_STAGING_MLFLOW_EXPERIMENT_NAME`

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
- `GET /api/v1/quant_ml/run/latest/meta`
- `GET /api/v1/quant_ml/run/latest/risk`
- `GET /api/v1/quant_ml/run/latest/exposures`
- `GET /api/v1/quant_ml/run/latest/constraints`
- `GET /api/v1/quant_ml/runs/{run_id}/snapshot`
- `GET /api/v1/quant_ml/runs/{run_id}/risk`
- `GET /api/v1/quant_ml/runs/{run_id}/exposures`
- `GET /api/v1/quant_ml/runs/{run_id}/constraints`
- `GET /api/v1/quant_ml/runs/{run_id}/audit`

Compatibility note:

- `run/latest/*` endpoints stay available for one release cycle.
- New automation and dashboards should prefer explicit `runs/{run_id}/*`.

## Institutional Artifact Contract

Backtest now writes a standardized artifact bundle under:

- `~/.openbb_platform/quant_ml/runs/<run_id>/artifacts/`

Required outputs:

- `universe.parquet`, `exclusions.parquet`, `signals.parquet`
- `weights_target.parquet`, `weights_final.parquet`, `constraints_log.parquet`
- `trades.parquet`, `costs.parquet`, `returns_daily.parquet`
- `risk_summary.parquet`, `exposures_sector.parquet`, `report.html`

Run metadata now includes:

- `run_uid` (`YYYY-MM-DD_HHMMSSZ_<8hex>`)
- `artifact_contract_version`
- `required_artifacts_ready`

Run registry storage:

- legacy JSON: `~/.openbb_platform/quant_ml/registry.json` (dual-write compatibility)
- canonical DB: `~/.openbb_platform/quant_ml/run_registry.sqlite3`
- audit events are queryable through `GET /runs/{run_id}/audit`

Contract inventory generators:

```bash
PYTHONPATH=openbb_platform/extensions/quant_ml python qa/scripts/quant_ml_contract_inventory.py
python qa/scripts/quant_ml_frontend_contract_inventory.py
PYTHONPATH=openbb_platform/extensions/quant_ml python qa/scripts/generate_quant_ts_types.py
```

## Portfolio Policy (Hard Constraints)

The extension enforces a centralized policy from:

- `openbb_platform/extensions/quant_ml/openbb_quant_ml/config/portfolio_policy.yaml`

Default live policy:

- single-name absolute weight cap: `10%` (hard)
- small-universe behavior: `cash_buffer`
- template: `diversified_long_only`
- risk defaults: `max_weight=0.10`, `sector_concentration=0.35`, `gross_exposure=1.0`, `net_exposure_abs=1.0`, `turnover=0.8`

Defensive two-bucket policy (long-only backtest):

- `universe_policy.backtest.defensive_bucket` enables defensive/risk 2-stage optimization.
- defensive minimum weight uses regime floor (`low/mid/high/risk_off`) and defaults to `25/35/45/55%`.
- postcheck runs global ex-ante `CVaR/vol` guard and applies:
  1) defensive floor raise, then
  2) risk bucket de-lever, when needed.
- legacy single-bucket optimizer remains as fallback when no defensive symbols are available.

Backtest request constraint keys:

- `defensive_bucket_enabled`
- `defensive_floor_mode` (`regime` or `fixed`)
- `defensive_floor_fixed|low|mid|high|risk_off`
- `defensive_risk_off_drawdown`
- `defensive_postcheck_enabled`
- `defensive_postcheck_cvar_limit`
- `defensive_postcheck_vol_limit`

Example payload (excerpt):

```json
{
  "constraints": {
    "optimizer_mode": "cvar",
    "defensive_bucket_enabled": true,
    "defensive_floor_mode": "regime",
    "defensive_floor_low": 0.25,
    "defensive_floor_mid": 0.35,
    "defensive_floor_high": 0.45,
    "defensive_floor_risk_off": 0.55,
    "defensive_postcheck_enabled": true,
    "defensive_postcheck_cvar_limit": -0.02,
    "defensive_postcheck_vol_limit": 0.20
  }
}
```

Backtest responses include:

- `effective_constraints` (requested vs applied constraints)
- `cash_weight` (remaining capital not allocated to risky assets)

Quick verification:

```bash
pytest openbb_platform/extensions/quant_ml/tests/test_backtest.py -q
pytest openbb_platform/extensions/quant_ml/tests/test_execution_risk.py -q
pytest openbb_platform/extensions/quant_ml/tests/test_portfolio_policy.py -q
pytest openbb_platform/extensions/quant_ml/tests/test_runtime_cache.py -q
pytest openbb_platform/extensions/quant_ml/tests/test_experiment_tracking_mlflow.py -q
pytest openbb_platform/extensions/quant_ml/tests/test_pipeline_training_backend.py -q
```

Merge-ready baseline verification:

```powershell
.\.venv\Scripts\python.exe -m pytest openbb_platform/tests/test_dev_install.py openbb_platform/tests/test_pyproject_toml.py openbb_platform/tests/test_resolve_python.py -q
.\.venv\Scripts\python.exe -m pytest openbb_platform/extensions/platform_api/tests/test_api.py openbb_platform/extensions/quant_ml/tests/test_runtime_cache.py openbb_platform/extensions/quant_ml/tests/test_experiment_tracking_mlflow.py openbb_platform/extensions/quant_ml/tests/test_pipeline_training_backend.py openbb_platform/extensions/quant_ml/tests/test_quant_router_extra.py -q
.\qa\scripts\quant_ml_startup_smoke.ps1 -RepoRoot .
npm.cmd test -- --run src/tests/routes/__root.test.tsx src/tests/routes/finance.test.tsx src/tests/routes/trading.test.tsx src/tests/lib/openbbBackend.test.ts src/tests/lib/openbbSse.test.ts src/tests/routes/backends.test.tsx src/tests/routes/quant.test.tsx src/tests/routes/macro.test.tsx
```

Repo-consistency verification after bootstrap:

```powershell
.\.venv\Scripts\python.exe openbb_platform/dev_install.py -e --bootstrap-installer uv
.\.venv\Scripts\python.exe openbb_platform/dev_install.py -e --cli --bootstrap-installer uv
git diff --exit-code -- openbb_platform/pyproject.toml openbb_platform/poetry.lock cli/pyproject.toml cli/poetry.lock
git ls-files --others --exclude-standard | Select-String -Pattern '(^|/|\\)uv\.lock$'
```

Startup smoke verification:

```powershell
.\qa\scripts\quant_ml_startup_smoke.ps1
```

Gate policy:

- manual `quant_ml_verify_full.ps1` keeps startup smoke opt-in through `-IncludeStartupSmoke`
- `quant_ml_overnight_runner.ps1` always includes startup smoke in phase 7
- GitHub Actions `quant-ml-platform.yml` runs a dedicated Windows startup smoke gate

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
- `defaults.stale_timeout_minutes: 90`
- `defaults.heartbeat_interval_sec: 30`
- `defaults.market_data_timeout_sec: 20`
- `defaults.market_data_retry: 2`
- `defaults.market_data_workers: 6`
- `daily.predict_mode: infer_only`
- `daily.predict_fallback_legacy: true`
- `daily.market_delta_days: 45`
- `daily.feature_delta_days: 120`
- `daily.max_infer_workers: 4`
- `daily/weekly/monthly.universe_id: all_in_one`
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

## Overnight Unattended Runner

Nightly unattended automation scripts:

- `qa/scripts/quant_ml_recover_state.ps1`
- `qa/scripts/quant_ml_verify_full.ps1`
- `qa/scripts/quant_ml_overnight_runner.ps1`
- `qa/scripts/quant_ml_collect_report.py`
- config: `openbb_platform/extensions/quant_ml/openbb_quant_ml/config/ops_jobs_overnight.yaml`

Artifacts:

- `logs/overnight/<session_id>/timeline.log`
- `logs/overnight/<session_id>/checks.json`
- `logs/overnight/<session_id>/final_report.md`

Long-running step monitoring:

- `update_market_data` writes heartbeat logs every `30s` or `50 symbols` (whichever comes first)
- stale-fail policy uses combined signals (`updated_at`, `last_heartbeat_at`, artifact mtime), timeout `90m`
- recovery gate passes only when `active_runs_after == 0` and lock health is `ok` or `missing`

Example (run overnight pipeline):

```powershell
cd <REPO_ROOT>
$env:PYTHONPATH='openbb_platform/extensions/quant_ml'
powershell -ExecutionPolicy Bypass -File qa/scripts/quant_ml_overnight_runner.ps1 `
  -ConfigPath openbb_platform/extensions/quant_ml/openbb_quant_ml/config/ops_jobs_overnight.yaml `
  -ApiBaseUrl http://127.0.0.1:6900
```

Optional push after all gates pass:

```powershell
powershell -ExecutionPolicy Bypass -File qa/scripts/quant_ml_overnight_runner.ps1 `
  -ConfigPath openbb_platform/extensions/quant_ml/openbb_quant_ml/config/ops_jobs_overnight.yaml `
  -EnablePush
```

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
