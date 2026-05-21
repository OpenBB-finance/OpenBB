# OpenBB Quantitative Extension

This package adds the `openbb-quantitative` extension to the Open Data Platform by OpenBB.

It provides a quantitative analysis toolkit — normality and unit root tests, CAPM risk
measures, descriptive statistics, rolling-window statistics, risk-adjusted performance
ratios, and multi-factor regression / attribution / risk-decomposition — that operate on
any tabular dataset passed in as `data`.

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

### Factor analysis

The factor endpoints take two payloads — a target series and a factor matrix —
plus an optional risk-free column name. Pair with any factor source; for
Fama-French data the [`openbb-famafrench`](../../providers/famafrench) provider
exposes the canonical research datasets.

```python
target = obb.equity.price.historical("SPY", provider="yfinance").results
factors = obb.famafrench.factors(provider="famafrench").results

# Multi-period regression: betas, p-values, CIs, R-squared per named window.
obb.quantitative.factors(
    data=target, factors_data=factors, target="close", risk_free_column="rf"
)

# Share of Var(target) attributable to each factor (residual sums to 1 - R^2).
obb.quantitative.risk_decomposition(
    data=target, factors_data=factors, target="close", risk_free_column="rf"
)

# Decompose the period's total return into factor contributions + alpha + residual.
obb.quantitative.attribution(
    data=target, factors_data=factors, target="close", risk_free_column="rf"
)

# Refit OLS on a sliding window to track time-varying factor exposures.
obb.quantitative.rolling.factors(
    data=target, factors_data=factors, target="close",
    window=252, step=21, risk_free_column="rf",
)
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

### Factor analysis

- `factors` — multi-period OLS regression of a target series on a factor matrix; returns coefficient, p-value, 95% CI, and R-squared per (period, factor)
- `risk_decomposition` — share of Var(target) attributable to each factor plus residual; per-period factor shares sum to R-squared and the residual share to 1 - R-squared
- `attribution` — additive decomposition of the period's total target return into factor contributions, alpha, and residual

### Rolling

- `rolling.skew` — rolling skew over a moving window
- `rolling.variance` — rolling variance over a moving window
- `rolling.stdev` — rolling standard deviation over a moving window
- `rolling.kurtosis` — rolling kurtosis over a moving window
- `rolling.mean` — rolling mean over a moving window
- `rolling.quantile` — rolling quantile over a moving window
- `rolling.factors` — rolling-window factor regression; emits per-factor betas and t-statistics at each window end

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

### Charts

The extension also ships chart views, auto-discovered by `openbb-charting`:

- `factors` — coefficient heatmap colored by p-value
- `risk_decomposition` — stacked horizontal bars of variance shares per period
- `attribution` — stacked horizontal bars of return contributions per period (signs preserved)
- `rolling.factors` — stacked area chart of rolling factor exposure over time.

See the full docs [here](https://docs.openbb.co/odp/python/extensions/data-processing/quantitative)
