# OpenBB Quant ML Extension

`openbb-quant-ml` adds a local-first ML/DL quant workflow to the OpenBB Platform API.

## Features

- Universe endpoint for predefined multi-asset universe
- Asynchronous model training (XGBoost + PyTorch LSTM)
- Signal generation using ensemble forecasts
- Portfolio backtesting with mean-variance optimization
- Local artifact and cache storage under `~/.openbb_platform/quant_ml`

## Endpoints

- `GET /api/v1/quant_ml/universe`
- `POST /api/v1/quant_ml/train`
- `GET /api/v1/quant_ml/runs/{run_id}`
- `POST /api/v1/quant_ml/signals`
- `POST /api/v1/quant_ml/backtest`
- `GET /api/v1/quant_ml/artifacts/{run_id}/summary`

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
python -m openbb_quant_ml.service.macro_update --all-default
```

### Macro endpoints

- `GET /api/v1/quant_ml/macro/catalog`
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
PYTHONPATH=openbb_platform/extensions/quant_ml python -m openbb_quant_ml.jobs.cli daily --config openbb_platform/extensions/quant_ml/openbb_quant_ml/config/job.yaml
PYTHONPATH=openbb_platform/extensions/quant_ml python -m openbb_quant_ml.jobs.cli weekly --config openbb_platform/extensions/quant_ml/openbb_quant_ml/config/job.yaml
PYTHONPATH=openbb_platform/extensions/quant_ml python -m openbb_quant_ml.jobs.cli monthly --config openbb_platform/extensions/quant_ml/openbb_quant_ml/config/job.yaml
```

### Windows Task Scheduler example

```powershell
schtasks /Create /F /TN "QuantML-Daily" /SC WEEKLY /D MON,TUE,WED,THU,FRI /ST 18:30 /TR "powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\Users\<user>\quant_ml_jobs\quantml_daily.ps1"
schtasks /Create /F /TN "QuantML-Weekly" /SC WEEKLY /D SAT /ST 08:00 /TR "powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\Users\<user>\quant_ml_jobs\quantml_weekly.ps1"
schtasks /Create /F /TN "QuantML-Monthly" /SC MONTHLY /D 1 /ST 09:00 /TR "powershell.exe -NoProfile -ExecutionPolicy Bypass -File C:\Users\<user>\quant_ml_jobs\quantml_monthly.ps1"
```

### cron appendix (Linux)

```bash
30 18 * * 1-5 cd <REPO_ROOT> && PYTHONPATH=openbb_platform/extensions/quant_ml python -m openbb_quant_ml.jobs.cli daily --config openbb_platform/extensions/quant_ml/openbb_quant_ml/config/job.yaml
0 8 * * 6 cd <REPO_ROOT> && PYTHONPATH=openbb_platform/extensions/quant_ml python -m openbb_quant_ml.jobs.cli weekly --config openbb_platform/extensions/quant_ml/openbb_quant_ml/config/job.yaml
0 9 1 * * cd <REPO_ROOT> && PYTHONPATH=openbb_platform/extensions/quant_ml python -m openbb_quant_ml.jobs.cli monthly --config openbb_platform/extensions/quant_ml/openbb_quant_ml/config/job.yaml
```
