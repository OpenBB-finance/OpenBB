# OpenBB Econometrics Extension

This package adds the `openbb-econometrics` extension to the Open Data Platform by OpenBB.

It provides a toolkit of econometrics commands — regression, regression diagnostics,
stationarity and cointegration tests, Granger causality, GARCH volatility modelling, and
panel-data estimators — that operate on any tabular dataset passed in as `data`.

## Installation

Install from PyPI with:

```sh
pip install openbb-econometrics
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

# Coefficient table of an OLS regression.
obb.econometrics.ols_regression(
    data=prices, y_column="close", x_columns=["open", "high", "low"]
)

# Augmented Dickey-Fuller stationarity test.
obb.econometrics.unit_root(data=prices, column="close")

# GARCH(1, 1) conditional volatility.
obb.econometrics.garch(data=prices, column="close")
```

To use the extension over HTTP, start the API server with `openbb-api` and POST to
`/api/v1/econometrics/<command>`.

## Coverage

All commands are available under `obb.econometrics.*`.

### Tools

- `correlation_matrix` — correlation matrix of a dataset
- `summary_statistics` — per-column descriptive statistics

### Regression

- `ols_regression` — Ordinary Least Squares coefficient table
- `ols_regression_summary` — OLS goodness-of-fit summary

### Diagnostics

- `autocorrelation` — Durbin-Watson autocorrelation test
- `residual_autocorrelation` — Breusch-Godfrey residual autocorrelation test
- `heteroskedasticity` — Breusch-Pagan and White heteroskedasticity tests
- `normality` — Jarque-Bera normality test on residuals
- `variance_inflation_factor` — multicollinearity (VIF) test

### Time Series

- `unit_root` — Augmented Dickey-Fuller unit root test
- `kpss` — KPSS stationarity test
- `cointegration` — Engle-Granger pairwise cointegration test
- `cointegration_johansen` — Johansen multivariate cointegration test
- `causality` — Granger causality test
- `garch` — GARCH(p, q) conditional volatility model

### Panel

- `panel_random_effects` — one-way Random Effects model
- `panel_between` — Between estimator
- `panel_pooled` — Pooled OLS estimator
- `panel_fixed` — Fixed Effects estimator
- `panel_first_difference` — First-Difference estimator
- `panel_fmac` — Fama-MacBeth estimator

See the full docs [here](https://docs.openbb.co/odp/python/extensions/data-processing/econometrics)
