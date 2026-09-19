# OpenBB Fama-French Provider Extension

This package adds the `openbb-famafrench` provider and router extension to the Open Data Platform by OpenBB.

It implements the [Kenneth R. French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html),
maintained and hosted at Dartmouth College, exposing research factors, research portfolios, and
breakpoints as OpenBB Platform endpoints.

## Installation

Install from PyPI with:

```sh
pip install openbb-famafrench
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
The extension ships an `apps.json` describing a ready-made dashboard for exploring the
Fama-French datasets.

## Implementation Details

Kenneth French publishes returns and breakpoints as compressed CSV/DAT files. This extension
downloads the requested dataset on demand, parses the multi-table file layout, and maps each
table to the appropriate OpenBB standard model. Downloads are cached in-memory for the life of
the process, so repeated requests for the same dataset do not re-fetch.

Every response carries the source file's own description in the `extra["results_metadata"]`
field of the results object, including the dataset description, frequency, and the portfolio
or factor formations contained in the file:

```python
factors.extra["results_metadata"]

{
    "description": "### \n\nThis file was created using the 202504 CRSP database. ...",
    "frequency": "monthly",
    "formations": ["Mkt-RF", "SMB", "HML", "RF"],
}
```

### Datasets

- **Factors** — the 3-Factor and 5-Factor models, plus Momentum and short/long-term reversal
  factors, for eight regions (`america`, `north_america`, `europe`, `japan`,
  `asia_pacific_ex_japan`, `developed`, `developed_ex_us`, `emerging`). Availability of a
  factor, and of a frequency for that factor, varies by region.
- **US & Regional portfolios** — research portfolios formed on size, book-to-market, operating
  profitability, investment, and industry, retrievable by `value`, `equal`, `number_of_firms`,
  or `firm_size` measures.
- **Country & International index portfolios** — value/growth portfolios formed on four
  valuation ratios, available in USD, local currency, or as ratios.
- **Breakpoints** — the NYSE breakpoints (every fifth percentile) used to construct the
  research portfolios.

## Coverage

### Endpoints

```python
from openbb import obb

obb.famafrench
# /famafrench
#     breakpoints
#     country_portfolio_returns
#     factor_choices            <- utility endpoint serving choices to OpenBB Workspace widgets
#     factors
#     international_index_returns
#     regional_portfolio_returns
#     us_portfolio_returns
```

- `obb.famafrench.factors` — Fama-French research factors by region, factor, and frequency
- `obb.famafrench.us_portfolio_returns` — US research portfolio returns
- `obb.famafrench.regional_portfolio_returns` — regional research portfolio returns
- `obb.famafrench.country_portfolio_returns` — per-country value/growth portfolio returns
- `obb.famafrench.international_index_returns` — international index portfolio returns
- `obb.famafrench.breakpoints` — NYSE breakpoints used to form the research portfolios
- `obb.famafrench.factor_choices` — utility endpoint that populates OpenBB Workspace widget
  dropdowns (excluded from the OpenAPI schema)

## Example

```python
from openbb import obb

# The 3-Factor model for the US, monthly (defaults).
factors = obb.famafrench.factors()

# By region and factor.
momentum = obb.famafrench.factors(factor="momentum", region="europe")

# US research portfolios formed on size, equal-weighted, annual.
portfolios = obb.famafrench.us_portfolio_returns(
    portfolio="portfolios_formed_on_me",
    measure="equal",
    frequency="annual",
)

# Per-country value/growth portfolios.
japan = obb.famafrench.country_portfolio_returns(country="japan", measure="local")

# NYSE breakpoints.
breakpoints = obb.famafrench.breakpoints(breakpoint_type="op", start_date="1998-01-01")
```

Refer to each endpoint's docstring for detailed descriptions of the methodology.
