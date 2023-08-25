---
title: maxdiv
description: OpenBB Terminal Function
---

# maxdiv

Maximizes the portfolio's diversification ratio

### Usage

```python
maxdiv [-cv {hist,ewma1,ewma2,ledoit,oas,shrunk,gl,jlogo,fixed,spectral,shrink}] [-de SMOOTHING_FACTOR_EWMA] [-vs SHORT_ALLOCATION] [-mt METHOD] [-ct CATEGORIES] [-p PERIOD] [-s START_PERIOD] [-e END_PERIOD] [-lr] [--freq {d,w,m}] [-mn MAX_NAN] [-th THRESHOLD_VALUE] [-v LONG_ALLOCATION] [--name NAME]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| covariance | Method used to estimate covariance matrix. Possible values are 'hist': historical method 'ewma1': exponential weighted moving average with adjust=True 'ewma2': exponential weighted moving average with adjust=False 'ledoit': Ledoit and Wolf shrinkage method 'oas': oracle shrinkage method 'shrunk': scikit-learn shrunk method 'gl': graphical lasso method 'jlogo': j-logo covariance 'fixed': takes average of eigenvalues above max Marchenko Pastour limit 'spectral': makes zero eigenvalues above max Marchenko Pastour limit 'shrink': Lopez de Prado's book shrinkage method | hist | True | hist, ewma1, ewma2, ledoit, oas, shrunk, gl, jlogo, fixed, spectral, shrink |
| smoothing_factor_ewma | Smoothing factor for ewma estimators | 0.94 | True | None |
| short_allocation | Amount to allocate to portfolio in short positions | 0.0 | True | None |
| nan_fill_method | Method used to fill nan values in time series, by default time. Possible values are: 'linear': linear interpolation 'time': linear interpolation based on time index 'nearest': use nearest value to replace nan values 'zero': spline of zeroth order 'slinear': spline of first order 'quadratic': spline of second order 'cubic': spline of third order 'barycentric': builds a polynomial that pass for all points | time | True | linear, time, nearest, zero, slinear, quadratic, cubic, barycentric |
| categories | Show selected categories | ASSET_CLASS, COUNTRY, SECTOR, INDUSTRY | True | None |
| historic_period | Period to get yfinance data from. Possible frequency strings are: 'd': means days, for example '252d' means 252 days 'w': means weeks, for example '52w' means 52 weeks 'mo': means months, for example '12mo' means 12 months 'y': means years, for example '1y' means 1 year 'ytd': downloads data from beginning of year to today 'max': downloads all data available for each asset | 3y | True | 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max |
| start_period | Start date to get yfinance data from. Must be in 'YYYY-MM-DD' format |  | True | None |
| end_period | End date to get yfinance data from. Must be in 'YYYY-MM-DD' format |  | True | None |
| log_returns | If use logarithmic or arithmetic returns to calculate returns | False | True | None |
| return_frequency | Frequency used to calculate returns. Possible values are: 'd': for daily returns 'w': for weekly returns 'm': for monthly returns | d | True | d, w, m |
| max_nan | Max percentage of nan values accepted per asset to be considered in the optimization process | 0.05 | True | None |
| threshold_value | Value used to replace outliers that are higher to threshold in absolute value | 0.3 | True | None |
| long_allocation | Amount to allocate to portfolio | 1 | True | None |
| name | Save portfolio with personalized or default name | MAXDIV_0 | True | None |


---

## Examples

```python
2022 Apr 05, 14:18 (🦋) /portfolio/po/ $ maxdiv

 [3 Years] Display a maximal diversification portfolio

     Weights
┏━━━━━━┳━━━━━━━━━┓
┃      ┃ Value   ┃
┡━━━━━━╇━━━━━━━━━┩
│ AAPL │  0.0 %  │
├──────┼─────────┤
│ AMZN │ 22.62 % │
├──────┼─────────┤
│ BA   │ 11.53 % │
├──────┼─────────┤
│ FB   │ 12.06 % │
├──────┼─────────┤
│ MSFT │  0.0 %  │
├──────┼─────────┤
│ T    │ 40.01 % │
├──────┼─────────┤
│ TSLA │ 13.75 % │
└──────┴─────────┘

Annual (by 252) expected return: 24.68%
Annual (by √252) volatility: 26.16%
Sharpe ratio: 0.9435
```
---
