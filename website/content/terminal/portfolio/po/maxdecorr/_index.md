```
usage: maxdecorr [-p HISTORIC_PERIOD] [-s START_PERIOD] [-e END_PERIOD] [-lr]
                 [-f {d,w,m}] [-mn MAX_NAN] [-th THRESHOLD_VALUE]
                 [-mt NAN_FILL_METHOD]
                 [-cv {hist,ewma1,ewma2,ledoit,oas,shrunk,gl,jlogo,fixed,spectral,shrink}]
                 [-de SMOOTHING_FACTOR_EWMA] [-v LONG_ALLOCATION]
                 [-vs SHORT_ALLOCATION] [--name NAME] [-h]
```

Maximum Decorrelation described by Christoffersen et al. ([source](https://investresolve.com/portfolio-optimization-simple-optimal-methods/#ref-Christoff2010)) is closely related to Minimum Variance and Maximum Diversification, but applies to the case where an investor believes all assets have similar returns and volatility, but heterogeneous correlations. It is a Minimum Variance optimization that is performed on the correlation matrix rather than the covariance matrix.

Interestingly, when the weights derived from the Maximum Decorrelation optimization are divided through by their respective volatilities and re-standardized so they sum to 1, we retrieve the Maximum Diversification weights. Thus, the portfolio weights that maximize decorrelation will also maximize the Diversification Ratio when all assets have equal volatility and maximize the Sharpe ratio when all assets have equal risks and returns.

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
  -f {d,w,m}, --freq {d,w,m}
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
                        (default: MAXDECORR_0)
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Apr 05, 14:15 (🦋) /portfolio/po/ $ maxdecorr

 [3 Years] Display a maximal decorrelation portfolio
     Weights      
┏━━━━━━┳━━━━━━━━━┓
┃      ┃ Value   ┃
┡━━━━━━╇━━━━━━━━━┩
│ AAPL │  0.0 %  │
├──────┼─────────┤
│ AMZN │ 18.49 % │
├──────┼─────────┤
│ BA   │ 17.29 % │
├──────┼─────────┤
│ FB   │ 12.33 % │
├──────┼─────────┤
│ MSFT │  0.0 %  │
├──────┼─────────┤
│ T    │ 27.37 % │
├──────┼─────────┤
│ TSLA │ 24.50 % │
└──────┴─────────┘

Annual (by 252) expected return: 36.58%
Annual (by √252) volatility: 31.17%
Sharpe ratio: 1.1735
```