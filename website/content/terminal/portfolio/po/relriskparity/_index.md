```
usage: relriskparity [-p HISTORIC_PERIOD] [-s START_PERIOD] [-e END_PERIOD]
                     [-lr] [--freq {d,w,m}] [-mn MAX_NAN] [-th THRESHOLD_VALUE]
                     [-mt NAN_FILL_METHOD] [-ve {A,B,C}]
                     [-rc RISK_CONTRIBUTION] [-pf PENAL_FACTOR]
                     [-tr TARGET_RETURN] [-de SMOOTHING_FACTOR_EWMA]
                     [-v LONG_ALLOCATION] [--name NAME] [-h]
```

A relaxed risk parity optimization model controls the balance of risk parity violation against the total portfolio performance. Risk parity has been criticized as being overly conservative and it is improved by re-introducing the asset expected returns into the model and permitting the portfolio to violate the risk parity condition. The paper by Gambeta & Kwon ([source](https://www.mdpi.com/1911-8074/13/10/237/htm)) proposes the incorporation of an explicit target return goal with an intuitive target return approach into a second-order-cone model of a risk parity optimization. When the target return is greater than risk parity return, a violation to risk parity allocations occurs that is controlled using a computational construct to obtain near-risk parity portfolios to retain as much risk parity-like traits as possible. This model is used to demonstrate empirically that higher returns can be achieved than risk parity without the risk contributions deviating dramatically from the risk parity allocations. Furthermore, this study reveals that the relaxed risk parity model exhibits advantageous traits of robustness to expected returns, which should not deter the use of expected returns in risk parity model.

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
  -ve {A,B,C}, --version {A,B,C}
                        version of relaxed risk parity model: Possible values
                        are: 'A': risk parity without regularization and
                        penalization constraints 'B': with regularization
                        constraint but without penalization constraint 'C':
                        with regularization and penalization constraints
                        (default: A)
  -rc RISK_CONTRIBUTION, --risk-cont RISK_CONTRIBUTION
                        Vector of risk contribution constraints (default:
                        None)
  -pf PENAL_FACTOR, --penal-factor PENAL_FACTOR
                        The penalization factor of penalization constraints.
                        Only used with version 'C'. (default: 1)
  -tr TARGET_RETURN, --target-return TARGET_RETURN
                        Constraint on minimum level of portfolio's return
                        (default: -1)
  -de SMOOTHING_FACTOR_EWMA, --d-ewma SMOOTHING_FACTOR_EWMA
                        Smoothing factor for ewma estimators (default: 0.94)
  -v LONG_ALLOCATION, --value LONG_ALLOCATION
                        Amount to allocate to portfolio (default: 1)
  --name NAME           Save portfolio with personalized or default name
                        (default: RRP_0)
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Apr 05, 14:08 (🦋) /portfolio/po/ $ relriskparity

 [3 Years] Relaxed risk parity portfolio based on least squares approach

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
│ T    │ 24.0 %  │
├──────┼─────────┤
│ TSLA │  8.68 % │
└──────┴─────────┘

Annual (by 252) expected return: 28.99%
Annual (by √252) volatility: 26.60%
Sharpe ratio: 1.0899
```
