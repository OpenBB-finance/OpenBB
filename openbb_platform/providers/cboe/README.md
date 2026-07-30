# OpenBB Cboe Provider Extension

This package adds the `openbb-cboe` provider and router extension to the Open Data Platform by OpenBB.

It implements the public market data published by [Cboe Global Markets](https://www.cboe.com/) across
its operating jurisdictions — US options, equities and futures, Cboe Europe indices, and the
Cboe Australia (CXA) index series — as OpenBB Platform endpoints. No API key is required.

## Installation

Install from PyPI with:

```sh
pip install openbb-cboe
```

To enable the Plotly options-analysis charts, install with the `charting` extra:

```sh
pip install "openbb-cboe[charting]"
```

Then build the Python static assets by running:

```sh
openbb-build
```

## Quick Start

The fastest way to get started is by connecting to the OpenBB Workspace as a custom backend.

### Start Server

```sh
openbb-api
```

This starts the FastAPI server over localhost on port 6900.

### Add to Workspace

See the documentation [here](https://docs.openbb.co/python/quickstart/workspace) for more details.
The extension ships an `apps.json` describing a ready-made dashboard with Indices, Equities,
Volatility, and Options tabs.

## Conditional Registration

The Cboe models implement OpenBB standard models — `EquityQuote`, `IndexSnapshots`, `OptionsChains`,
and so on — which are normally served by the `openbb-equity`, `openbb-index`, `openbb-etf`, and
`openbb-derivatives` extensions. When those are installed, Cboe registers as a provider under their
existing commands and no Cboe-specific routes are added.

When they are absent, the same data is served from this extension's own router under `/cboe/...`, so
installing `openbb-cboe` on its own still exposes every dataset. Each namespace resolves
independently: installing only `openbb-index` moves the index models under `obb.index.*` while the
equity, options, and futures commands stay under `obb.cboe.*`.

The bundled `apps.json` resolves its widget IDs the same way, and drops the Plotly options charts when
`openbb-charting` is not installed.

## Coverage

### Endpoints

```python
from openbb import obb

obb.cboe
# /cboe
#     equity
#         historical
#         quote
#         search
#         symbol_choices        <- utility endpoint serving choices to Workspace widgets
#     futures
#         curve
#         roots
#         settlement_prices
#     index
#         available
#         constituents
#         constituent_choices   <- utility endpoint
#         documents
#         historical
#         search
#         snapshots
#         symbol_choices        <- utility endpoint
#     options
#         chains
#         get_tickers           <- utility endpoint
#         smile                 <- Plotly chart widget, requires openbb-charting
#         spreads
#         stats                 <- Plotly chart widget, requires openbb-charting
#         straddle
#         strangle
#         surface               <- Plotly chart widget, requires openbb-charting
#         term_structure        <- Plotly chart widget, requires openbb-charting
```

### Jurisdictions

Cboe operates markets in the US, UK/Europe, Canada, and Australia. This extension covers every
jurisdiction that publishes a free market data feed:

- **United States** — the delayed options chain with greeks, delayed equity and index quotes, the
  VIX futures term structure, futures settlement prices, and the complete daily history of all
  941 Cboe-calculated indices.
- **Europe** — the 178 Cboe Europe proprietary indices, their current levels, and current-day
  constituent quotes for the 57 indices that publish them.
- **Australia** — the Cboe Australia (CXA) 200 index series, its current levels, and the full
  index composition with weights.

### Datasets

- **Options chains** — the delayed US options chain, carrying implied volatility, all five greeks,
  and DEX/GEX. Underlying quote data is returned in `extra["results_metadata"]`.
- **Options analysis** — long straddles, strangles, and all four vertical spreads priced at every
  expiration, plus IV smile/skew, a 3-D surface over DTE and strike (choose IV or any greek), open
  interest and volume statistics, and the price/IV term structure.
- **Index levels** — daily history from each index's inception, sourced from Cboe's published
  per-symbol files. One-minute levels are available for
  the most recent session.
- **Index constituents** — European indices return current-day constituent quotes; the Australian
  CXA indices return the index composition with weights, ISIN, SEDOL, GICS, float ratio, and
  free-float adjusted market capitalization.
- **Index reference** — the full directory across all three jurisdictions, annotated with the Cboe
  Global Indices feed channel (`CGI`, `MSTAR`, `FTSE`, `MSCI`, `CCCY`, `INAV`, `MAIN`), plus a
  catalog of every published factsheet, methodology, governance, and constituents document.
- **Equities** — delayed quotes with 30/60/90-day implied and realized volatility, daily and
  one-minute historical prices, and the Cboe US company directory.
- **Futures** — the VIX (VX) term structure at mid-morning TWAP or end-of-day levels, the futures
  roots directory, and current or final settlement prices.

## Example

```python
from openbb import obb

# The full VIX history, from 1990.
vix = obb.cboe.index.historical(symbol="VIX", provider="cboe")

# Current levels for every Cboe Australia index.
au = obb.cboe.index.snapshots(region="au", provider="cboe")

# CXA 200 composition, with weights.
cxa = obb.cboe.index.constituents(symbol="X2C", provider="cboe")

# The delayed options chain, with greeks.
chains = obb.cboe.options.chains(symbol="SPY", provider="cboe")

# Long straddle pricing at every expiration.
straddle = obb.cboe.options.straddle(symbol="SPY")

# The VIX futures term structure as of two past sessions.
curve = obb.cboe.futures.curve(symbol="VX_EOD", date="2024-06-25,2024-06-26", provider="cboe")

# The methodology documents from the Cboe index documents catalog.
docs = obb.cboe.index.documents(category="Methodology", provider="cboe")

# Every document that applies to one index, factsheet first.
cxa_docs = obb.cboe.index.documents(symbol="X2C", provider="cboe")
```

When `openbb-index` and `openbb-derivatives` are installed, the same data is reached through the
standard namespaces instead — `obb.index.snapshots(provider="cboe")`,
`obb.derivatives.options.chains(provider="cboe")`, and so on.

## Notes

Symbol directories are cached on disk for 24 hours. Pass `use_cache=False` to bypass the cache; the
results of the endpoints themselves are never cached.

Cboe publishes index constituents only for its European and Australian series. The US indices are
strategy, settlement, and box-rate indices rather than baskets, and Cboe publishes no component
files for them beyond a handful of PDFs surfaced by `obb.cboe.index.documents`.
