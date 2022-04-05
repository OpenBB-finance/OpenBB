```
usage: relriskparity [-p PERIOD] [-s START] [-e END] [-lr] [-f {d,w,m}]
                     [-mn MAXNAN] [-th THRESHOLD] [-mt METHOD] [-ve {A,B,C}]
                     [-rc RISK_CONT] [-pf PENAL_FACTOR] [-tr TARGET_RETURN]
                     [-de D_EWMA] [-v VALUE] [--pie] [--hist] [--dd]
                     [--rc-chart] [--heat] [-h]
```

Builds a relaxed risk parity based on least squares approach.

```
optional arguments:
  -p PERIOD, --period PERIOD
                        Period to get yfinance data from (default: 3y)
  -s START, --start START
                        Start date to get yfinance data from (default: )
  -e END, --end END     End date to get yfinance data from (default: )
  -lr, --log-returns    If use logarithmic or arithmetic returns to calculate
                        returns (default: False)
  -f {d,w,m}, --freq {d,w,m}
                        Frequency used to calculate returns (default: d)
  -mn MAXNAN, --maxnan MAXNAN
                        Max percentage of nan values accepted per asset to be
                        considered in the optimization process (default: 0.05)
  -th THRESHOLD, --threshold THRESHOLD
                        Value used to replace outliers that are higher to
                        threshold in absolute value (default: 0.3)
  -mt METHOD, --method METHOD
                        Method used to fill nan values (default: time)
  -ve {A,B,C}, --version {A,B,C}
                        version of relaxed risk parity model (default: A)
  -rc RISK_CONT, --risk-cont RISK_CONT
                        Vector of risk contribution constraints (default:
                        None)
  -pf PENAL_FACTOR, --penal-factor PENAL_FACTOR
                        The penalization factor of penalization constraints.
                        Only used with version 'C'. (default: 1)
  -tr TARGET_RETURN, --target-return TARGET_RETURN
                        Constraint on minimum level of portfolio's return
                        (default: -1)
  -de D_EWMA, --d-ewma D_EWMA
                        Smoothing factor for ewma estimators (default: 0.94)
  -v VALUE, --value VALUE
                        Amount to allocate to portfolio (default: 1.0)
  --pie                 Display a pie chart for weights (default: False)
  --hist                Display a histogram with risk measures (default:
                        False)
  --dd                  Display a drawdown chart with risk measures (default:
                        False)
  --rc-chart            Display a risck contribution chart for assets
                        (default: False)
  --heat                Display a heatmap of correlation matrix with
                        dendrogram (default: False)
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