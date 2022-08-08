```
usage: maxdiv [-p HISTORIC_PERIOD] [-s START_PERIOD] [-e END_PERIOD] [-lr]
              [--freq {d,w,m}] [-mn MAX_NAN] [-th THRESHOLD_VALUE]
              [-mt NAN_FILL_METHOD]
              [-cv {hist,ewma1,ewma2,ledoit,oas,shrunk,gl,jlogo,fixed,spectral,shrink}]
              [-de SMOOTHING_FACTOR_EWMA] [-v LONG_ALLOCATION]
              [-vs SHORT_ALLOCATION] [--name NAME] [-h]
```

Choueifaty and Coignard ([source](https://investresolve.com/portfolio-optimization-simple-optimal-methods/#ref-Choueifaty2008)) proposed that markets are risk-efficient, such that investments will produce returns in proportion to their total risk, as measured by volatility. This differs from CAPM, which assumes returns are proportional to non-diversifiable (i.e. systematic) risk. The Diversification Ratio, which is to be maximized, quantifies the degree to which the portfolio risk can be minimized through strategic placement of weights on diversifying (imperfectly correlated) assets.

```
optional arguments:
  -p HISTORIC_PERIOD, --period HISTORIC_PERIOD
                        Period to get yfinance data from. Possible frequency
                        strings are: 'd': means days, for example '252d' means
                        252 days 'w': means weeks, for example '52w' means 52
                        weeks 'mo': means months, for example '12mo' means 12
                        months 'y': means years, for example '1y' means 1 year
                        'ytd': downloads data from beginning of year to today
                        'max': downloads all data available for each asset
                        (default: 3y)
  -s START_PERIOD, --start START_PERIOD
                        Start date to get yfinance data from. Must be in
                        'YYYY-MM-DD' format (default: )
  -e END_PERIOD, --end END_PERIOD
                        End date to get yfinance data from. Must be in 'YYYY-
                        MM-DD' format (default: )
  -lr, --log-returns    If use logarithmic or arithmetic returns to calculate
                        returns (default: False)
  --freq {d,w,m}
                        Frequency used to calculate returns. Possible values
                        are: 'd': for daily returns 'w': for weekly returns
                        'm': for monthly returns (default: d)
  -mn MAX_NAN, --maxnan MAX_NAN
                        Max percentage of nan values accepted per asset to be
                        considered in the optimization process (default: 0.05)
  -th THRESHOLD_VALUE, --threshold THRESHOLD_VALUE
                        Value used to replace outliers that are higher to
                        threshold in absolute value (default: 0.3)
  -mt NAN_FILL_METHOD, --method NAN_FILL_METHOD
                        Method used to fill nan values in time series, by
                        default time. Possible values are: 'linear': linear
                        interpolation 'time': linear interpolation based on
                        time index 'nearest': use nearest value to replace nan
                        values 'zero': spline of zeroth order 'slinear':
                        spline of first order 'quadratic': spline of second
                        order 'cubic': spline of third order 'barycentric':
                        builds a polynomial that pass for all points (default:
                        time)
  -cv {hist,ewma1,ewma2,ledoit,oas,shrunk,gl,jlogo,fixed,spectral,shrink}, --covariance {hist,ewma1,ewma2,ledoit,oas,shrunk,gl,jlogo,fixed,spectral,shrink}
                        Method used to estimate covariance matrix. Possible
                        values are 'hist': historical method 'ewma1':
                        exponential weighted moving average with adjust=True
                        'ewma2': exponential weighted moving average with
                        adjust=False 'ledoit': Ledoit and Wolf shrinkage
                        method 'oas': oracle shrinkage method 'shrunk':
                        scikit-learn shrunk method 'gl': graphical lasso
                        method 'jlogo': j-logo covariance 'fixed': takes
                        average of eigenvalues above max Marchenko Pastour
                        limit 'spectral': makes zero eigenvalues above max
                        Marchenko Pastour limit 'shrink': Lopez de Prado's
                        book shrinkage method (default: hist)
  -de SMOOTHING_FACTOR_EWMA, --d-ewma SMOOTHING_FACTOR_EWMA
                        Smoothing factor for ewma estimators (default: 0.94)
  -v LONG_ALLOCATION, --value LONG_ALLOCATION
                        Amount to allocate to portfolio in long positions
                        (default: 1)
  -vs SHORT_ALLOCATION, --value-short SHORT_ALLOCATION
                        Amount to allocate to portfolio in short positions
                        (default: 0.0)
  --name NAME           Save portfolio with personalized or default name
                        (default: MAXDIV_0)
  -h, --help            show this help message (default: False)
```

Example:
```
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
