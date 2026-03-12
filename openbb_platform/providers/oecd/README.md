# OpenBB OECD Provider Extension

This package adds the `openbb-oecd` provider extension to the Open Data Platform by OpenBB.

It provides everything you need — endpoints, tools, and metadata — to access and explore the entirety of
https://data-explorer.oecd.org, without any previous experience working with it.

## Installation

Install from PyPI with:

```sh
pip install openbb-oecd
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

### Click to Open App

Once added, click on the app to open the dashboard.

The dashboard contains widgets with metadata and information, as well as ones for exploring and retrieving the data.

## Implementation Details

OECD publishes data through a SDMX v2 REST API, and organizes everything into "dataflows". You can think of
these as databases, each with its own dimension definitions, codelists, and observation attributes.
Some definitions are shared across dataflows, others are domain-specific.

The extension ships with a bundled metadata cache that covers all OECD dataflows. It contains dimension
definitions, codelist mappings, content constraints, and the full topic taxonomy. When anything is missing
from the bundled cache, it is fetched on first use and added to a user-writable cache file that persists
across sessions.

Input is validated against the dataflow's content constraints. Codes are resolved to human-readable labels
in the output, and dataset and series metadata are returned alongside the observations.

### Indicators

In this library, we use the term "indicator" to refer to indicator-like dimensions within individual dataflows.
These are dimensions that represent what is being measured, such as `MEASURE`, `SUBJECT`, `TRANSACTION`, or
`ACTIVITY`. The specific dimension varies by dataflow.

The OECD codes for these values — `B1GQ`, `CPI`, `LI`, etc. — are used to construct ticker-like symbols.

### Symbology

The Open Data Platform refers to all time series IDs as a `symbol`.
Requesting data requires a symbol constructed from the dataflow's short ID and the indicator code, joined with `::`.

```
DF_PRICES_ALL::CPI         — Consumer Price Index, all items
DF_QNA::B1GQ               — GDP, expenditure approach (Quarterly National Accounts)
DF_CLI::LI                 — Composite Leading Indicator
DF_EO::GDPV_USD            — GDP forecast, volume (Economic Outlook)
DF_BOP::B6_USD             — Current account balance
```

Multiple indicators from the same dataflow can be comma-separated:

```
DF_PRICES_ALL::CPI,DF_PRICES_ALL::HICP
```

Use `obb.economy.available_indicators(provider='oecd')` to search for or list all available symbols.

Use `obb.oecd_utils.get_dataflow_parameters()` to see all dimensions and valid codes for any dataflow.

### Metadata Cache

The library ships with a bundled base cache (`oecd_cache.pkl.xz`) containing:

- All dataflow IDs, names, and version metadata
- DSD dimension definitions and codelist references for every dataflow
- All codelist code-to-label mappings
- Content constraints (valid value sets per dimension)
- The full OECD topic taxonomy (category scheme and categorisations)

When a structure is missing, it is fetched on demand and merged into a user-level cache stored under
`~/OpenBBUserData/cache/oecd_cache.pkl.xz` (configurable via `~/.openbb_platform/user_settings.json`).

## Coverage

All data available from https://data-explorer.oecd.org can be retrieved via `obb.economy.indicators(provider='oecd', **kwargs)`.

The extension also exposes specialized fetchers for the most commonly used OECD datasets.

The extension creates a router path, `oecd_utils`, that exposes utility functions for UI integrations
and metadata lookup.

### Endpoints

**Economy**

- `obb.economy.available_indicators` — search all OECD indicator symbols
- `obb.economy.indicators` — fetch data for any OECD indicator symbol
- `obb.economy.balance_of_payments` — Balance of Payments
- `obb.economy.composite_leading_indicator` — Composite Leading Indicators
- `obb.economy.cpi` — Consumer Price Indices
- `obb.economy.country_interest_rates` — Short and long-term interest rates
- `obb.economy.gdp.nominal` — Nominal GDP
- `obb.economy.gdp.real` — Real GDP
- `obb.economy.gdp.forecast` — GDP forecasts (Economic Outlook)
- `obb.economy.house_price_index` — Residential property price indices
- `obb.economy.share_price_index` — Share price indices
- `obb.economy.unemployment` — Unemployment rates

**Utilities**

- `obb.oecd_utils.list_dataflows` — list all OECD dataflows with topic breadcrumbs
- `obb.oecd_utils.list_dataflow_choices` — dropdown choices for UI widgets
- `obb.oecd_utils.get_dataflow_parameters` — dimensions and valid codes for a dataflow

"Choices" endpoints are used by OpenBB Workspace to populate widget dropdown menus.

### Example

```python
from openbb import obb

# List all available OECD indicators to find what you need
indicators = obb.economy.available_indicators(provider="oecd", query="GDP")
print(indicators.to_df())

# Fetch real GDP growth for the US, UK, and Germany
data = obb.economy.indicators(
    provider="oecd",
    symbol="DF_QNA::B1GQ",
    country="USA,GBR,DEU",
    frequency="quarterly",
)
print(data.to_df())

# Inspect all dimensions and valid values for a dataflow
params = obb.oecd_utils.get_dataflow_parameters("DF_PRICES_ALL", output_format="json")
print(params.results)
```
