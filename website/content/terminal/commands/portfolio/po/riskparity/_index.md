```
usage: riskparity [-p HISTORIC_PERIOD] [-s START_PERIOD] [-e END_PERIOD] [-lr]
                  [-f {d,w,m}] [-mn MAX_NAN] [-th THRESHOLD_VALUE]
                  [-mt NAN_FILL_METHOD]
                  [-rm {MV,MAD,MSV,FLPM,SLPM,CVaR,EVaR,CDaR,EDaR,UCI}]
                  [-rc RISK_CONTRIBUTION] [-r RISK_FREE]
                  [-a SIGNIFICANCE_LEVEL] [-tr TARGET_RETURN]
                  [-de SMOOTHING_FACTOR_EWMA] [-v LONG_ALLOCATION]
                  [--name NAME] [-h]
```

Both the Minimum Variance and Maximum Diversification portfolios are mean-variance efficient under intuitive assumptions. Minimum Variance is efficient if assets have similar returns while Maximum Diversification is efficient if assets have similar Sharpe ratios. However, both methods have the drawback that they can be quite concentrated in a small number of assets. For example, the Minimum Variance portfolio will place disproportionate weight in the lowest volatility asset while the Maximum Diversification portfolio will concentrate in assets with high volatility and low covariance with the market. In fact, these optimizations may result in portfolios that hold just a small fraction of all available assets.

There are situations where this may not be preferable. Concentrated portfolios also may not accommodate large amounts of capital without high market impact costs. In addition, concentrated portfolios are more susceptible to mis-estimation of volatilities or correlations.

These issues prompted a search for heuristic optimizations that meet similar optimization objectives, but with less concentration. The equal weight and capitalization weighted portfolios are common examples of this, but there are other methods that are compelling under different assumptions.

**Risk parity was developed to remove the uncertainty of estimated returns and to protect against losses associated with portfolio concentration. In essence what this means is that you want to prevent allocation a significant portion to just a couple of assets because Minimum Variance and Maximum Diversification say this is the best allocation.**

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
                        considered in the optimization process. (default:
                        0.05)
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
  -rm {MV,MAD,MSV,FLPM,SLPM,CVaR,EVaR,CDaR,EDaR,UCI}, --risk-measure {MV,MAD,MSV,FLPM,SLPM,CVaR,EVaR,CDaR,EDaR,UCI}
                        Risk measure used to optimize the portfolio. Possible
                        values are: 'MV' : Variance 'MAD' : Mean Absolute
                        Deviation 'MSV' : Semi Variance (Variance of negative
                        returns) 'FLPM' : First Lower Partial Moment 'SLPM' :
                        Second Lower Partial Moment 'CVaR' : Conditional Value
                        at Risk 'EVaR' : Entropic Value at Risk 'UCI' : Ulcer
                        Index of uncompounded returns 'CDaR' : Conditional
                        Drawdown at Risk of uncompounded returns 'EDaR' :
                        Entropic Drawdown at Risk of uncompounded returns
                        (default: MV)
  -rc RISK_CONTRIBUTION, --risk-cont RISK_CONTRIBUTION
                        vector of risk contribution constraint (default: None)
  -r RISK_FREE, --risk-free-rate RISK_FREE
                        Risk-free rate of borrowing/lending. The period of the
                        risk-free rate must be annual (default: 0.00329)
  -a SIGNIFICANCE_LEVEL, --alpha SIGNIFICANCE_LEVEL
                        Significance level of CVaR, EVaR, CDaR and EDaR
                        (default: 0.05)
  -tr TARGET_RETURN, --target-return TARGET_RETURN
                        Constraint on minimum level of portfolio's return
                        (default: -1)
  -de SMOOTHING_FACTOR_EWMA, --d-ewma SMOOTHING_FACTOR_EWMA
                        Smoothing factor for ewma estimators (default: 0.94)
  -v LONG_ALLOCATION, --value LONG_ALLOCATION
                        Amount to allocate to portfolio (default: 1)
  --name NAME           Save portfolio with personalized or default name
                        (default: RP_8)
  -h, --help            show this help message (default: False)
  ```

Example:
```
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