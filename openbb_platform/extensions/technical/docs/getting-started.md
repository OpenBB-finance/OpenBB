# Getting Started

## Install

```bash
pip install openbb-technical
```

The extension depends on `openbb-core[pandas]`, `pandas-ta-openbb`, `scikit-learn`, `scipy`, and `statsmodels` — all installed transitively.

## Three ways to call an endpoint

Every endpoint is exposed identically through the Python SDK, the REST API, and the CLI. Pick whichever fits your workflow.

### 1. Python

```python
from openbb import obb

data = obb.equity.price.historical(
    symbol="SPY", start_date="2024-01-01", provider="yfinance"
).results

result = obb.technical.rsi(data=data, length=14)
print(result.results[0])         # first row of the RSI series
df = result.to_df()              # convert results to a DataFrame
```

### 2. REST API

Start the API server (defaults to `http://localhost:8000`):

```bash
openbb-api
```

POST to the endpoint. The `data` array is the request body; scalar args are query-string parameters:

```bash
curl -X POST 'http://localhost:8000/api/v1/technical/rsi?length=14' \
  -H 'Content-Type: application/json' \
  -d '[{"date":"2024-01-02","open":471.5,"high":473.7,"low":471.0,"close":472.6,"volume":78900},
       {"date":"2024-01-03","open":472.5,"high":473.1,"low":468.7,"close":468.8,"volume":111200},
       ...]'
```

Endpoints that take more than one body argument (`screen`, `multi`, `correlation`, `relative_rotation`, `realized_volatility_compare`, `signals/candlestick_patterns`) wrap the body as `{"data": [...], "<other>": [...]}`.

### 3. CLI

```bash
openbb -i
> /technical/rsi --data <path_or_json> --length 14
```

The CLI auto-generates an argparse interface from each endpoint's signature, so `--help` after any command lists every parameter with its type and default.

## Working with returns

Every endpoint returns an `OBBject`. The interesting bits:

```python
result = obb.technical.bbands(data=data, length=20)

result.results          # list[BbandsData] — one row per bar
result.to_df()          # pandas DataFrame keyed by date
result.to_dict()        # dict form
len(result.results)     # row count
result.results[-1]      # last row (most recent bar)
```

## Discovering what's available

The `indicators` endpoint introspects the router and returns a structured catalog:

```python
catalog = obb.technical.indicators(category="all").results
for entry in catalog.indicators:
    print(entry.name, entry.category, [p.name for p in entry.params])
```

Filter by category — `overlay`, `oscillator`, `volatility`, `volume`, `trend`, `signal`, `structure`, `stats`, `multi`, or `all`.

## Next steps

- [Single-symbol indicator workflows](./user-guides/01-indicators.md)
- [Signal endpoints](./user-guides/02-signals.md)
- [Multi-symbol analysis](./user-guides/03-multi-symbol.md)
- [Multi-indicator composition + catalog](./user-guides/04-composition-and-discovery.md)
- [Full API reference](./api-reference.md)
