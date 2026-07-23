# OpenBB CME Provider

CME Group equity index futures data for OpenBB. No API key required.

## Supported Symbols

| Symbol | Name | Exchange | Daily Volume (approx.) |
|--------|------|----------|------------------------|
| ES | E-mini S&P 500 | CME/Globex | ~1.5M |
| NQ | E-mini Nasdaq-100 | CME/Globex | ~800K |
| MES | Micro E-mini S&P 500 | CME/Globex | ~1.5M |
| MNQ | Micro E-mini Nasdaq-100 | CME/Globex | ~1M |
| YM | E-mini Dow ($5) | CBOT/Globex | ~100K |

## Installation

```bash
pip install openbb-cme
# or with uv
uv add openbb-cme
```

## Data Source

Public settlement data from CME Group:

```
https://www.cmegroup.com/CmeWS/mvc/Settlements/Futures/Settlements/{product_id}/FUT
```

Settlement data is published after the trading session. No authentication is
required.

### Authenticated CME APIs

CME also offers authenticated market-data products through its Data Services
Portal and DataMine APIs. An API ID can be created by an individual CME account,
but API responses are limited to datasets entitled through an order or
subscription. The real-time futures and options API, Reference Data API, and
DataMine historical files are therefore not treated as free data sources by
this provider.

- [CME Market Data APIs](https://www.cmegroup.com/market-data/market-data-api.html)
- [CME DataMine API](https://www.cmegroup.com/datamine/datamine-api.html)
- [CME DataMine List API](https://www.cmegroup.com/datamine/datamine-list-api.html)

The provider intentionally uses only the public settlement endpoint and does
not request CME credentials.

## Fetchers

### `FuturesHistorical`

Daily OHLCV + official settlement price and open interest.

```python
from openbb import obb

# Front-month ES settlement history (last 30 days by default)
df = obb.derivatives.futures.historical("ES", provider="cme").to_df()

# Specific contract month
df = obb.derivatives.futures.historical(
    "NQ", provider="cme",
    start_date="2025-01-01", end_date="2025-06-25",
    expiration="2025-06"
).to_df()
```

**Extra fields vs. standard model:**
- `settlement_price`: official CME end-of-day settlement (distinct from last trade)
- `open_interest`: daily outstanding contracts
- `expiration`: contract month in YYYY-MM format
- `symbol`: CME root symbol

### FuturesCurve

Term structure (all active contract months) for a given date.

```python
# Current term structure
df = obb.derivatives.futures.curve("ES", provider="cme").to_df()

# Historical term structure on a specific date
df = obb.derivatives.futures.curve(
    "ES", provider="cme", date="2025-03-21"
).to_df()
```

**Extra fields:** `open_interest`, `volume`, `symbol`

The `date` parameter accepts either one date or multiple comma-separated dates.

### `FuturesInfo`

Contract specifications + latest settlement summary. Accepts multiple symbols.

```python
# Single symbol
info = obb.derivatives.futures.info("ES", provider="cme").to_df()

# Multiple symbols
info = obb.derivatives.futures.info("ES,NQ,MES", provider="cme").to_df()
```

**Fields:** `tick_size`, `point_value`, `multiplier`, `exchange`, `currency`, `settlement_price`, `open_interest`, `volume`, `front_month`, `trade_date`

### `FuturesInstruments`

Listed contracts with expiration dates. Accepts multiple symbols.

```python
# All listed ES contracts
instruments = obb.derivatives.futures.instruments("ES", provider="cme").to_df()

# Multiple symbols
instruments = obb.derivatives.futures.instruments("ES,NQ", provider="cme").to_df()
```

## Standalone Router

When `openbb-derivatives` is installed, the fetchers register with the standard
`derivatives.futures` endpoints. Without that extension, `openbb-cme` exposes
the same four commands from the `cme` namespace:

- `cme.historical`
- `cme.curve`
- `cme.info`
- `cme.instruments`

## Running Tests

```bash
# Complete deterministic suite
uv run pytest

# Cassette replay tests only
uv run pytest tests/test_cme_fetchers.py -v -k record_http
```

Tests marked `@pytest.mark.record_http` replay recorded CME JSON responses.
Live endpoint checks are performed separately and are not part of the
deterministic unit suite.
