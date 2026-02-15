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
