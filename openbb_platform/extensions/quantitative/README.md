# OpenBB Quantitative Extension

This package adds the `openbb-quantitative` extension to the Open Data Platform by OpenBB.

It provides a quantitative analysis toolkit — normality and unit root tests, CAPM risk
measures, descriptive statistics, rolling-window statistics, and risk-adjusted
performance ratios — that operate on any tabular dataset passed in as `data`.

## Installation

Install from PyPI with:

```sh
pip install openbb-quantitative
```

Then build the Python static assets by running:

```sh
openbb-build
```

## Quick Start

Every command is a `POST` endpoint that takes a `data` payload (a list of records, e.g.
the `.results` of another OpenBB command) plus typed parameters, and returns an `OBBject`.

```python
from openbb import obb

prices = obb.equity.price.historical(
    symbol="AAPL", start_date="2023-01-01", provider="yfinance"
).results

# Descriptive summary statistics of a series.
obb.quantitative.summary(data=prices, target="close")

# Augmented Dickey-Fuller and KPSS unit root tests.
obb.quantitative.unitroot_test(data=prices, target="close")

# Rolling standard deviation over a moving window.
obb.quantitative.rolling.stdev(data=prices, target="close", window=21)

# Rolling Sharpe ratio.
obb.quantitative.performance.sharpe_ratio(data=prices, target="close")
```

To use the extension over HTTP, start the API server with `openbb-api` and POST to
`/api/v1/quantitative/<command>`.

## Coverage

All commands are available under `obb.quantitative.*`.

### Metrics

- `normality` — kurtosis, skewness, Jarque-Bera, Shapiro-Wilk, and Kolmogorov-Smirnov normality tests
- `capm` — Capital Asset Pricing Model risk measures
- `unitroot_test` — Augmented Dickey-Fuller and KPSS unit root tests
- `summary` — descriptive summary statistics of a series

### Rolling

- `rolling.skew` — rolling skew over a moving window
- `rolling.variance` — rolling variance over a moving window
- `rolling.stdev` — rolling standard deviation over a moving window
- `rolling.kurtosis` — rolling kurtosis over a moving window
- `rolling.mean` — rolling mean over a moving window
- `rolling.quantile` — rolling quantile over a moving window

### Stats

- `stats.skew` — skewness of a series
- `stats.variance` — variance of a series
- `stats.stdev` — standard deviation of a series
- `stats.kurtosis` — kurtosis of a series
- `stats.mean` — arithmetic mean of a series
- `stats.quantile` — quantile of a series

### Performance

- `performance.omega_ratio` — Omega ratio across a range of return thresholds
- `performance.sharpe_ratio` — rolling Sharpe ratio
- `performance.sortino_ratio` — rolling Sortino ratio

See the full docs [here](https://docs.openbb.co/odp/python/extensions/data-processing/quantitative)
