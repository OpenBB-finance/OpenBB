```
usage: equal [-p PERIOD] [-s START] [-e END] [-lr] [-f {d,w,m}] [-mn MAXNAN]
             [-th THRESHOLD] [-mt METHOD]
             [-rm {MV,MAD,MSV,FLPM,SLPM,CVaR,EVaR,WR,ADD,UCI,CDaR,EDaR,MDD}]
             [-r RISK_FREE_RATE] [-a ALPHA] [-v VALUE] [--pie] [--hist] [--dd]
             [--rc-chart] [--heat] [-h]
```

Returns an equally weighted portfolio.

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
  -rm {MV,MAD,MSV,FLPM,SLPM,CVaR,EVaR,WR,ADD,UCI,CDaR,EDaR,MDD}, --risk-measure {MV,MAD,MSV,FLPM,SLPM,CVaR,EVaR,WR,ADD,UCI,CDaR,EDaR,MDD}
                        Risk measure used to optimize the portfolio (default:
                        MV)
  -r RISK_FREE_RATE, --risk-free-rate RISK_FREE_RATE
                        Risk-free rate of borrowing/lending. The period of the
                        risk-free rate must be annual (default: 0.00185)
  -a ALPHA, --alpha ALPHA
                        Significance level of CVaR, EVaR, CDaR and EDaR
                        (default: 0.05)
  -v VALUE, --value VALUE
                        Amount to allocate to portfolio (default: 1)
  --pie                 Display a pie chart for weights (default: False)
  --hist                Display a histogram with risk measures (default:
                        False)
  --dd                  Display a drawdown chart with risk measures (default:
                        False)
  --rc-chart            Display a risk contribution chart for assets (default:
                        False)
  --heat                Display a heatmap of correlation matrix with
                        dendrogram (default: False)
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Apr 05, 14:52 (🦋) /portfolio/po/ $ equal

 [3 Years] Equally Weighted Portfolio

     Weights      
┏━━━━━━┳━━━━━━━━━┓
┃      ┃ Value   ┃
┡━━━━━━╇━━━━━━━━━┩
│ AAPL │ 14.28 % │
├──────┼─────────┤
│ AMZN │ 14.28 % │
├──────┼─────────┤
│ BA   │ 14.28 % │
├──────┼─────────┤
│ FB   │ 14.28 % │
├──────┼─────────┤
│ MSFT │ 14.28 % │
├──────┼─────────┤
│ T    │ 14.28 % │
├──────┼─────────┤
│ TSLA │ 14.28 % │
└──────┴─────────┘

Annual (by 252) expected return: 35.70%
Annual (by √252) volatility: 29.50%
Sharpe ratio: 1.2041
```