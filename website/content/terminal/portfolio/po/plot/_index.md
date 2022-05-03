```
usage: plot [-pf PORTFOLIOS] [-ct CATEGORIES] [-p HISTORIC_PERIOD]
            [-s START_PERIOD] [-e END_PERIOD] [-lr] [-f {d,w,m}] [-mn MAX_NAN]
            [-th THRESHOLD_VALUE] [-mt NAN_FILL_METHOD]
            [-rm {MV,MAD,MSV,FLPM,SLPM,CVaR,EVaR,WR,ADD,UCI,CDaR,EDaR,MDD}]
            [-r RISK_FREE] [-a SIGNIFICANCE_LEVEL] [-pi] [-hi] [-dd] [-rc]
            [-he] [-h]
```

Plot selected charts for portfolios

```
optional arguments:
  -pf PORTFOLIOS, --portfolios PORTFOLIOS
                        Selected portfolios that will be plotted (default: [])
  -ct CATEGORIES, --categories CATEGORIES
                        Show selected categories (default: [])
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
  -rm {MV,MAD,MSV,FLPM,SLPM,CVaR,EVaR,WR,ADD,UCI,CDaR,EDaR,MDD}, --risk-measure {MV,MAD,MSV,FLPM,SLPM,CVaR,EVaR,WR,ADD,UCI,CDaR,EDaR,MDD}
                        Risk measure used to optimize the portfolio. Possible
                        values are: 'MV' : Variance 'MAD' : Mean Absolute
                        Deviation 'MSV' : Semi Variance (Variance of negative
                        returns) 'FLPM' : First Lower Partial Moment 'SLPM' :
                        Second Lower Partial Moment 'CVaR' : Conditional Value
                        at Risk 'EVaR' : Entropic Value at Risk 'WR' : Worst
                        Realization 'ADD' : Average Drawdown of uncompounded
                        returns 'UCI' : Ulcer Index of uncompounded returns
                        'CDaR' : Conditional Drawdown at Risk of uncompounded
                        returns 'EDaR' : Entropic Drawdown at Risk of
                        uncompounded returns 'MDD' : Maximum Drawdown of
                        uncompounded returns (default: MV)
  -r RISK_FREE, --risk-free-rate RISK_FREE
                        Risk-free rate of borrowing/lending. The period of the
                        risk-free rate must be annual (default: 0.00329)
  -a SIGNIFICANCE_LEVEL, --alpha SIGNIFICANCE_LEVEL
                        Significance level of CVaR, EVaR, CDaR and EDaR
                        (default: 0.05)
  -pi, --pie            Display a pie chart for weights (default: False)
  -hi, --hist           Display a histogram with risk measures (default:
                        False)
  -dd, --drawdown       Display a drawdown chart with risk measures (default:
                        False)
  -rc, --rc-chart       Display a risk contribution chart for assets (default:
                        False)
  -he, --heat           Display a heatmap of correlation matrix with
                        dendrogram (default: False)
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Apr 26, 02:19 (🦋) /portfolio/po/ $ plot -pf maxsharpe_0 -pi -hi -dd -rc -he
```