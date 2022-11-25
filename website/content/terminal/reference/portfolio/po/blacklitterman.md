---
title: blacklitterman
description: OpenBB Terminal Function
---

# blacklitterman

Optimize portfolio using Black Litterman estimates

### Usage

```python
blacklitterman [-bm BENCHMARK] [-o {MinRisk,Utility,Sharpe,MaxRet}] [-pv P_VIEWS] [-qv Q_VIEWS] [-ra RISK_AVERSION] [-d DELTA] [-eq] [-op] [-vs SHORT_ALLOCATION] [--file FILE] [--download DOWNLOAD] [-mt METHOD] [-ct CATEGORIES] [-p PERIOD] [-s START_PERIOD] [-e END_PERIOD] [-lr] [--freq {d,w,m}] [-mn MAX_NAN] [-th THRESHOLD_VALUE] [-r RISK_FREE] [-v LONG_ALLOCATION] [--name NAME]
```

---

## Parameters

| Name | Description | Default | Optional | Choices |
| ---- | ----------- | ------- | -------- | ------- |
| benchmark | portfolio name from current portfolio list | None | True | None |
| objective | Objective function used to optimize the portfolio | Sharpe | True | MinRisk, Utility, Sharpe, MaxRet |
| p_views | matrix P of analyst views | None | True | None |
| q_views | matrix Q of analyst views | None | True | None |
| risk_aversion | Risk aversion parameter | 1 | True | None |
| delta | Risk aversion factor of Black Litterman model | None | True | None |
| equilibrium | If True excess returns are based on equilibrium market portfolio, if False excess returns are calculated as historical returns minus risk free rate. | True | True | None |
| optimize | If True Black Litterman estimates are used as inputs of mean variance model, if False returns equilibrium weights from Black Litterman model | True | True | None |
| short_allocation | Amount to allocate to portfolio in short positions | 0.0 | True | None |
| file | Upload an Excel file with views for Black Litterman model |  | True | None |
| download | Create a template to design Black Litterman model views |  | True | None |
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
| long_allocation | Amount to allocate to portfolio | 1 | True | None |
| name | Save portfolio with personalized or default name | BL_0 | True | None |


---

## Examples

```python
2022 Apr 26, 01:25 (🦋) /portfolio/po/ $ add AAPL,MSFT,JP,BA
2022 Apr 26, 01:26 (🦋) /portfolio/po/ $ maxsharpe

 [3 Years] Maximal return/risk ratio portfolio using volatility as risk measure

      Weights
┏━━━━━━┳━━━━━━━━━━┓
┃      ┃ Value    ┃
┡━━━━━━╇━━━━━━━━━━┩
│ AAPL │ 100.00 % │
├──────┼──────────┤
│ BA   │   0.00 % │
├──────┼──────────┤
│ JP   │   0.00 % │
├──────┼──────────┤
│ MSFT │   0.00 % │
└──────┴──────────┘
Annual (by 252) expected return: 45.46%
Annual (by √252) volatility: 34.16%
Sharpe ratio: 1.3209
```
---
