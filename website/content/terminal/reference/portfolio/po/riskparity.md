---
title: riskparity
description: OpenBB Terminal Function
---

# riskparity

Build a risk parity portfolio based on risk budgeting approach

### Usage

```python
riskparity [-rm RISK-MEASURE] [-rc RISK_CONTRIBUTION] [-tr TARGET_RETURN] [-de SMOOTHING_FACTOR_EWMA] [-mt METHOD] [-ct CATEGORIES] [-p PERIOD] [-s START_PERIOD] [-e END_PERIOD] [-lr] [--freq {d,w,m}] [-mn MAX_NAN] [-th THRESHOLD_VALUE] [-r RISK_FREE] [-a SIGNIFICANCE_LEVEL] [-v LONG_ALLOCATION] [--name NAME]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| risk_measure | Risk measure used to optimize the portfolio. Possible values are: 'MV' : Variance 'MAD' : Mean Absolute Deviation 'MSV' : Semi Variance (Variance of negative returns) 'FLPM' : First Lower Partial Moment 'SLPM' : Second Lower Partial Moment 'CVaR' : Conditional Value at Risk 'EVaR' : Entropic Value at Risk 'UCI' : Ulcer Index of uncompounded returns 'CDaR' : Conditional Drawdown at Risk of uncompounded returns 'EDaR' : Entropic Drawdown at Risk of uncompounded returns | MV | True | MV, MAD, MSV, FLPM, SLPM, CVaR, EVaR, CDaR, EDaR, UCI |
| risk_contribution | vector of risk contribution constraint | None | True | None |
| target_return | Constraint on minimum level of portfolio's return | -1 | True | None |
| smoothing_factor_ewma | Smoothing factor for ewma estimators | 0.94 | True | None |
| nan_fill_method | Method used to fill nan values in time series, by default time. Possible values are: 'linear': linear interpolation 'time': linear interpolation based on time index 'nearest': use nearest value to replace nan values 'zero': spline of zeroth order 'slinear': spline of first order 'quadratic': spline of second order 'cubic': spline of third order 'barycentric': builds a polynomial that pass for all points | time | True | linear, time, nearest, zero, slinear, quadratic, cubic, barycentric |
| categories | Show selected categories | ASSET_CLASS, COUNTRY, SECTOR, INDUSTRY | True | None |
| historic_period | Period to get yfinance data from. Possible frequency strings are: 'd': means days, for example '252d' means 252 days 'w': means weeks, for example '52w' means 52 weeks 'mo': means months, for example '12mo' means 12 months 'y': means years, for example '1y' means 1 year 'ytd': downloads data from beginning of year to today 'max': downloads all data available for each asset | 3y | True | 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max |
| start_period | Start date to get yfinance data from. Must be in 'YYYY-MM-DD' format |  | True | None |
| end_period | End date to get yfinance data from. Must be in 'YYYY-MM-DD' format |  | True | None |
| log_returns | If use logarithmic or arithmetic returns to calculate returns | False | True | None |
| return_frequency | Frequency used to calculate returns. Possible values are: 'd': for daily returns 'w': for weekly returns 'm': for monthly returns | d | True | d, w, m |
| max_nan | Max percentage of nan values accepted per asset to be considered in the optimization process | 0.05 | True | None |
| threshold_value | Value used to replace outliers that are higher to threshold in absolute value | 0.3 | True | None |
| risk_free | Risk-free rate of borrowing/lending. The period of the risk-free rate must be annual | 0.02924 | True | None |
| significance_level | Significance level of CVaR, EVaR, CDaR and EDaR | 0.05 | True | None |
| long_allocation | Amount to allocate to portfolio | 1 | True | None |
| name | Save portfolio with personalized or default name | RP_0 | True | None |


---

## Examples

```python
2022 Apr 05, 14:45 (🦋) /portfolio/po/ $ riskparity

 [3 Years] Risk parity portfolio based on risk budgeting approach
using volatility as risk measure

     Weights
┏━━━━━━┳━━━━━━━━━┓
┃      ┃ Value   ┃
┡━━━━━━╇━━━━━━━━━┩
│ AAPL │ 13.42 % │
├──────┼─────────┤
│ AMZN │ 16.51 % │
├──────┼─────────┤
│ BA   │ 10.18 % │
├──────┼─────────┤
│ FB   │ 12.83 % │
├──────┼─────────┤
│ MSFT │ 14.36 % │
├──────┼─────────┤
│ T    │ 24.00 % │
├──────┼─────────┤
│ TSLA │  8.68 % │
└──────┴─────────┘

Annual (by 252) expected return: 28.99%
Annual (by √252) volatility: 26.60%
Sharpe ratio: 1.0829
```
---
