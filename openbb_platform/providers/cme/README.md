# OpenBB CME Provider

CME Group futures and options-on-futures reference and settlement data for
OpenBB. No API key is required.

## Coverage

The provider builds its product universe from CME Group's public product slate
instead of maintaining a hard-coded symbol list. It covers futures and options
on futures listed by CME, CBOT, NYMEX, and COMEX across:

- Agriculture
- Cryptocurrencies
- Energy
- Equities
- FX
- Interest rates
- Metals
- Real estate
- Weather

The catalog includes every published product-code variant, asset class,
exchange, venue, previous-day volume and open interest, and the official
contract-specification URL. Product metadata is cached in memory for six hours.
The same validated catalog is written atomically to the OpenBB user cache. If
CME is temporarily unavailable, the provider can use a cache no more than seven
days old instead of losing symbol resolution entirely.

## Installation

```bash
pip install openbb-cme
# or with uv
uv add openbb-cme
```

## Public Data Sources

The provider uses the same public resources that power CME Group's website:

```
https://www.cmegroup.com/services/product-slate
https://www.cmegroup.com/CmeWS/mvc/ContractSpecs/List/productId/{product_id}
https://www.cmegroup.com/CmeWS/mvc/ProductCalendar/{Future|Options}/{product_id}
https://www.cmegroup.com/CmeWS/mvc/Settlements/Futures/Settlements/{product_id}/FUT
https://www.cmegroup.com/CmeWS/mvc/Settlements/Options/...
```

Settlement data is end-of-day reference data published after the trading
session. No authentication is required.

These resources are public CME website services rather than a versioned,
contractual API. The provider validates their response shape and fails
explicitly if it changes; CME does not publish an availability SLA for them.

## Reliability

- One pooled browser-compatible TLS session is reused per fetch operation.
- Requests are paced globally and limited to eight concurrent calls by default.
- Timeouts, network failures, malformed JSON, HTTP 408/425/429, and transient
  5xx responses are retried up to four attempts with exponential backoff and
  jitter. `Retry-After` is honored when CME supplies it.
- Catalog refreshes are de-duplicated so concurrent cold-cache requests perform
  one upstream refresh.
- Catalog responses are schema-checked before replacing either the memory or
  disk cache. Cache writes use atomic replacement.
- Multi-date history and multi-expiration option requests fail as a unit when
  any upstream request fails. The provider never presents a silently truncated
  dataset as complete.

The defaults can be tuned with `OPENBB_CME_TIMEOUT`,
`OPENBB_CME_MAX_ATTEMPTS`, `OPENBB_CME_BACKOFF`,
`OPENBB_CME_MAX_BACKOFF`, `OPENBB_CME_MIN_INTERVAL`,
`OPENBB_CME_MAX_CONCURRENCY`, `OPENBB_CME_CATALOG_TTL`, and
`OPENBB_CME_CATALOG_STALE_TTL`.

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

The provider intentionally uses only public website resources and does not
request CME credentials.

## Fetchers

### `CmeProducts`

Search the complete futures and options product catalog.

```python
# All CME Energy futures
products = obb.cme.products(
    product_type="Futures", asset_class="Energy", provider="cme"
).to_df()

# Resolve every published code for a product
gold = obb.cme.products(symbol="GC", provider="cme").to_df()
```

### `CmeContractSpecs`

Complete exchange-published contract specifications, including contract unit,
tick rules, product codes, listing cycle, trading hours, settlement method,
termination rules, option exercise details, and underlying contracts.

```python
specs = obb.cme.contract_specs(
    symbol="GC", product_type="Futures", provider="cme"
).to_df()

# Product IDs disambiguate weekly, daily, and serial option families.
option_specs = obb.cme.contract_specs(product_id=192, provider="cme").to_df()
```

### `FuturesHistorical`

Daily OHLCV, official settlement price, and open interest for any futures
product code in the generated catalog.

```python
from openbb import obb

# Front-month ES settlement history
df = obb.derivatives.futures.historical("ES", provider="cme").to_df()

# A different asset class and specific contract month
df = obb.derivatives.futures.historical(
    "GC", provider="cme",
    start_date="2025-01-01", end_date="2025-06-25",
    expiration="2025-06"
).to_df()
```

One request is limited to 252 weekdays to bound load on the public settlement
service. Larger ranges can be retrieved in multiple calls.

**Extra fields vs. standard model:**
- `settlement_price`: official CME end-of-day settlement (distinct from last trade)
- `open_interest`: daily outstanding contracts
- `expiration`: contract month in YYYY-MM format
- `symbol`: CME root symbol

### FuturesCurve

Term structure for any futures product and one or more dates.

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

Contract specifications plus the latest settlement summary. Specifications are
loaded from CME by product ID rather than from local constants.

```python
# Single symbol
info = obb.derivatives.futures.info("ES", provider="cme").to_df()

# Multiple symbols
info = obb.derivatives.futures.info("ES,NQ,MES", provider="cme").to_df()
```

The output retains both parsed convenience fields and the exchange-published
contract unit, price quotation, tick rules, listing cycle, trading hours,
settlement method, and termination rules.

### `FuturesInstruments`

Official listed-contract calendars with first trade, last trade, expiration,
and settlement dates. Accepts multiple product codes.

```python
# All listed ES contracts
instruments = obb.derivatives.futures.instruments("ES", provider="cme").to_df()

# Multiple asset classes
instruments = obb.derivatives.futures.instruments(
    "ES,GC,CL", provider="cme"
).to_df()
```

### `OptionsChains`

End-of-day call and put chains for options on futures. The fetcher discovers
available expirations, retrieves them concurrently, and normalizes strikes,
settlements, OHLC, volume, and open interest to OpenBB's standard options model.

```python
chain = obb.derivatives.options.chains(
    "OG",
    provider="cme",
    product_id=192,
    expiration="2026-07-28",
).to_df()
```

Use `cme.products(product_type="Options")` to discover exact option product IDs.
The public options settlement service advertises a rolling set of recent trade
dates for each expiration; it is not a replacement for licensed deep-history
datasets from CME DataMine.

## Routing

`cme.products` and `cme.contract_specs` are always registered in the CME
namespace.

When `openbb-derivatives` is installed, the fetchers register with the standard
`derivatives.futures` and `derivatives.options` endpoints. Without that
extension, `openbb-cme` exposes provider-local commands:

- `cme.historical`
- `cme.curve`
- `cme.info`
- `cme.instruments`
- `cme.options_chains`

## Running Tests

```bash
# Complete deterministic suite (45 tests)
uv run pytest

# Cassette replay tests only
uv run pytest tests/test_cme_fetchers.py -v -k record_http
```

Tests cover catalog pagination and normalization, contract specifications,
dynamic symbol resolution, futures history and curves, official calendars,
options-chain normalization, routing, fractional price formats,
market-closure fallback behavior, retries, throttling responses, schema drift,
cache corruption, single-flight refresh, stale fallback, and atomic failure
semantics. Tests marked `@pytest.mark.record_http` replay recorded responses;
live endpoint checks are performed separately.
