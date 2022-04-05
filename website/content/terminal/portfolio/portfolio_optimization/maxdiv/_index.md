```
usage: maxdiv [-p PERIOD] [-s START] [-e END] [-lr] [-f {d,w,m}] [-mn MAXNAN]
              [-th THRESHOLD] [-mt METHOD]
              [-cv {hist,ewma1,ewma2,ledoit,oas,shrunk,gl,jlogo,fixed,spectral,shrink}]
              [-de D_EWMA] [-v VALUE] [-vs VALUE_SHORT] [--pie] [--hist]
              [--dd] [--rc-chart] [--heat] [-h]
```

Maximizes diversification ratio of portfolio.

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
  -cv {hist,ewma1,ewma2,ledoit,oas,shrunk,gl,jlogo,fixed,spectral,shrink}, --covariance {hist,ewma1,ewma2,ledoit,oas,shrunk,gl,jlogo,fixed,spectral,shrink}
                        Method used to estimate covariance matrix (default:
                        hist)
  -de D_EWMA, --d-ewma D_EWMA
                        Smoothing factor for ewma estimators (default: 0.94)
  -v VALUE, --value VALUE
                        Amount to allocate to portfolio in long positions
                        (default: 1.0)
  -vs VALUE_SHORT, --value-short VALUE_SHORT
                        Amount to allocate to portfolio in short positions
                        (default: 0.0)
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