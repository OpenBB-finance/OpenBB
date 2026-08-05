# OilPriceAPI Provider Extension for OpenBB

This extension integrates [OilPriceAPI](https://www.oilpriceapi.com) into the OpenBB Platform.

OilPriceAPI serves source-timestamped energy and commodity prices through one normalized
REST API — crude benchmarks, natural gas, refined products, coal, carbon, marine fuels and
drilling activity. The public catalogue (`GET /v1/commodities`) currently exposes **463
series**, each carrying its own source timestamp and freshness metadata.

## Installation

```bash
pip install openbb-oilpriceapi
```

## Credentials

Sign up at <https://www.oilpriceapi.com/auth/signup> for a free tier — 200 requests/month,
no card required — then set `oilpriceapi_api_key`.

A **keyless** demo endpoint is available for evaluation without signing up:

```bash
curl https://api.oilpriceapi.com/v1/demo/prices
```

## Coverage

| Standard model        | OpenBB command             |
| --------------------- | -------------------------- |
| `CommoditySpotPrices` | `obb.commodity.price.spot` |

Omit `start_date`/`end_date` for the latest observation; supply either for a daily series.

```python
from openbb import obb

obb.commodity.price.spot(provider="oilpriceapi", commodity="brent")

obb.commodity.price.spot(
    provider="oilpriceapi",
    commodity="wti",
    start_date="2026-01-01",
    end_date="2026-06-30",
)
```

`commodity` accepts the friendly aliases listed in the command signature (`brent`, `wti`,
`dutch_ttf`, `eu_carbon`, …) **or** any raw code from `/v1/commodities`, forwarded
unchanged.

## Documentation

- API reference: <https://docs.oilpriceapi.com>
- OpenAPI spec: <https://api.oilpriceapi.com/.well-known/openapi.json>

## Data rights

OilPriceAPI is a data access and packaging service. It conveys no rights in the underlying
data, which remains subject to its original sources' terms.
