---
title: maxutil
description: OpenBB Terminal Function
---

# maxutil

Maximizes a risk averse utility function

### Usage

```python
maxutil [-ra RISK_AVERSION] [-tr TARGET_RETURN] [-tk TARGET_RISK] [-m {hist,ewma1,ewma2}] [-cv {hist,ewma1,ewma2,ledoit,oas,shrunk,gl,jlogo,fixed,spectral,shrink}] [-de SMOOTHING_FACTOR_EWMA] [-vs SHORT_ALLOCATION] [-rm {MV,MAD,MSV,FLPM,SLPM,CVaR,EVaR,WR,ADD,UCI,CDaR,EDaR,MDD}] [-mt METHOD] [-ct CATEGORIES] [-p PERIOD] [-s START_PERIOD] [-e END_PERIOD] [-lr] [--freq {d,w,m}] [-mn MAX_NAN] [-th THRESHOLD_VALUE] [-r RISK_FREE] [-a SIGNIFICANCE_LEVEL] [-v LONG_ALLOCATION] [--name NAME]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| risk_aversion | Risk aversion parameter | 1 | True | None |
| target_return | Constraint on minimum level of portfolio's return | -1 | True | None |
| target_risk | Constraint on maximum level of portfolio's risk | -1 | True | None |
| expected_return | Method used to estimate the expected return vector | hist | True | hist, ewma1, ewma2 |
| covariance | Method used to estimate covariance matrix. Possible values are 'hist': historical method 'ewma1': exponential weighted moving average with adjust=True 'ewma2': exponential weighted moving average with adjust=False 'ledoit': Ledoit and Wolf shrinkage method 'oas': oracle shrinkage method 'shrunk': scikit-learn shrunk method 'gl': graphical lasso method 'jlogo': j-logo covariance 'fixed': takes average of eigenvalues above max Marchenko Pastour limit 'spectral': makes zero eigenvalues above max Marchenko Pastour limit 'shrink': Lopez de Prado's book shrinkage method | hist | True | hist, ewma1, ewma2, ledoit, oas, shrunk, gl, jlogo, fixed, spectral, shrink |
| smoothing_factor_ewma | Smoothing factor for ewma estimators | 0.94 | True | None |
| short_allocation | Amount to allocate to portfolio in short positions | 0.0 | True | None |
| risk_measure | Risk measure used to optimize the portfolio. Possible values are: 'MV' : Variance 'MAD' : Mean Absolute Deviation 'MSV' : Semi Variance (Variance of negative returns) 'FLPM' : First Lower Partial Moment 'SLPM' : Second Lower Partial Moment 'CVaR' : Conditional Value at Risk 'EVaR' : Entropic Value at Risk 'WR' : Worst Realization 'ADD' : Average Drawdown of uncompounded returns 'UCI' : Ulcer Index of uncompounded returns 'CDaR' : Conditional Drawdown at Risk of uncompounded returns 'EDaR' : Entropic Drawdown at Risk of uncompounded returns 'MDD' : Maximum Drawdown of uncompounded returns | MV | True | MV, MAD, MSV, FLPM, SLPM, CVaR, EVaR, WR, ADD, UCI, CDaR, EDaR, MDD |
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
| name | Save portfolio with personalized or default name | MAXUTIL_0 | True | None |


---

## Examples

```python
2022 Apr 05, 13:21 (🦋) /portfolio/po/ $ maxutil

 [3 Years] Display a maximal risk averse utility function
 portfolio using volatility as risk measure

     Weights
┏━━━━━━┳━━━━━━━━━┓
┃      ┃ Value   ┃
┡━━━━━━╇━━━━━━━━━┩
│ AAPL │  0.0 %  │
├──────┼─────────┤
│ AMZN │  0.0 %  │
├──────┼─────────┤
│ BA   │  0.0 %  │
├──────┼─────────┤
│ FB   │  0.0 %  │
├──────┼─────────┤
│ MSFT │  0.0 %  │
├──────┼─────────┤
│ T    │  0.0 %  │
├──────┼─────────┤
│ TSLA │ 100.0 % │
└──────┴─────────┘

Annual (by 252) expected return: 124.85%
Annual (by √252) volatility: 68.44%
Sharpe ratio: 1.8215
```
---
