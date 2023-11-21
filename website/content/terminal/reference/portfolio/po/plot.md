---
title: plot
description: The plot page allows users to select and plot charts for various portfolios,
  using a range of parameters and offering several optional features. It includes
  different types of charts such as pie, histogram, drawdown, and risk contribution
  charts. Different risk measures can be optimized, and users can control various
  other factors such as the calculation frequency, the max percentage of accepted
  NaN values, and the risk-free rate.
keywords:
- plot
- charts
- portfolios
- risk measures
- drawdown chart
- risk contribution chart
- correlation matrix
- heatmap
- CVaR
- EVaR
- Maximum Drawdown
- risk-free rate
- significance level
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="portfolio /po/plot - Reference | OpenBB Terminal Docs" />

Plot selected charts for portfolios

### Usage

```python wordwrap
plot [-pf PORTFOLIOS] [-pi] [-hi] [-dd] [-rc] [-he] [-rm {MV,MAD,MSV,FLPM,SLPM,CVaR,EVaR,WR,ADD,UCI,CDaR,EDaR,MDD}] [-mt METHOD] [-ct CATEGORIES] [-p PERIOD] [-s START_PERIOD] [-e END_PERIOD] [-lr] [--freq {d,w,m}] [-mn MAX_NAN] [-th THRESHOLD_VALUE] [-r RISK_FREE] [-a SIGNIFICANCE_LEVEL] [-v LONG_ALLOCATION]
```

---

## Parameters

| Name | Parameter | Description | Default | Optional | Choices |
| ---- | --------- | ----------- | ------- | -------- | ------- |
| portfolios | -pf  --portfolios | Selected portfolios that will be plotted |  | True | None |
| pie | -pi  --pie | Display a pie chart for weights | False | True | None |
| hist | -hi  --hist | Display a histogram with risk measures | False | True | None |
| dd | -dd  --drawdown | Display a drawdown chart with risk measures | False | True | None |
| rc_chart | -rc  --rc-chart | Display a risk contribution chart for assets | False | True | None |
| heat | -he  --heat | Display a heatmap of correlation matrix with dendrogram | False | True | None |
| risk_measure | -rm  --risk-measure | Risk measure used to optimize the portfolio. Possible values are: 'MV' : Variance 'MAD' : Mean Absolute Deviation 'MSV' : Semi Variance (Variance of negative returns) 'FLPM' : First Lower Partial Moment 'SLPM' : Second Lower Partial Moment 'CVaR' : Conditional Value at Risk 'EVaR' : Entropic Value at Risk 'WR' : Worst Realization 'ADD' : Average Drawdown of uncompounded returns 'UCI' : Ulcer Index of uncompounded returns 'CDaR' : Conditional Drawdown at Risk of uncompounded returns 'EDaR' : Entropic Drawdown at Risk of uncompounded returns 'MDD' : Maximum Drawdown of uncompounded returns | MV | True | MV, MAD, MSV, FLPM, SLPM, CVaR, EVaR, WR, ADD, UCI, CDaR, EDaR, MDD |
| nan_fill_method | -mt  --method | Method used to fill nan values in time series, by default time. Possible values are: 'linear': linear interpolation 'time': linear interpolation based on time index 'nearest': use nearest value to replace nan values 'zero': spline of zeroth order 'slinear': spline of first order 'quadratic': spline of second order 'cubic': spline of third order 'barycentric': builds a polynomial that pass for all points | time | True | linear, time, nearest, zero, slinear, quadratic, cubic, barycentric |
| categories | -ct  --categories | Show selected categories |  | True | None |
| historic_period | -p  --period | Period to get yfinance data from. Possible frequency strings are: 'd': means days, for example '252d' means 252 days 'w': means weeks, for example '52w' means 52 weeks 'mo': means months, for example '12mo' means 12 months 'y': means years, for example '1y' means 1 year 'ytd': downloads data from beginning of year to today 'max': downloads all data available for each asset | 3y | True | 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 3y, 5y, 10y, ytd, max |
| start_period | -s  --start | Start date to get yfinance data from. Must be in 'YYYY-MM-DD' format |  | True | None |
| end_period | -e  --end | End date to get yfinance data from. Must be in 'YYYY-MM-DD' format |  | True | None |
| log_returns | -lr  --log-returns | If use logarithmic or arithmetic returns to calculate returns | False | True | None |
| return_frequency | --freq | Frequency used to calculate returns. Possible values are: 'd': for daily returns 'w': for weekly returns 'm': for monthly returns | d | True | d, w, m |
| max_nan | -mn  --maxnan | Max percentage of nan values accepted per asset to be considered in the optimization process | 0.05 | True | None |
| threshold_value | -th  --threshold | Value used to replace outliers that are higher to threshold in absolute value | 0.3 | True | None |
| risk_free | -r  --risk-free-rate | Risk-free rate of borrowing/lending. The period of the risk-free rate must be annual | 0.05437 | True | None |
| significance_level | -a  --alpha | Significance level of CVaR, EVaR, CDaR and EDaR | 0.05 | True | None |
| long_allocation | -v  --value | Amount to allocate to portfolio | 1 | True | None |


---

## Examples

```python
2022 Apr 26, 02:19 (🦋) /portfolio/po/ $ plot -pf maxsharpe_0 -pi -hi -dd -rc -he
```
---
