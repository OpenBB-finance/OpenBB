```
usage: minrisk [-p PERIOD] [-s START] [-e END] [-lr] [-f {d,w,m}] [-mn MAXNAN]
               [-th THRESHOLD] [-mt METHOD]
               [-rm {MV,MAD,MSV,FLPM,SLPM,CVaR,EVaR,WR,ADD,UCI,CDaR,EDaR,MDD}]
               [-r RISK_FREE_RATE] [-a ALPHA] [-tr TARGET_RETURN]
               [-tk TARGET_RISK] [-m {hist,ewma1,ewma2}]
               [-cv {hist,ewma1,ewma2,ledoit,oas,shrunk,gl,jlogo,fixed,spectral,shrink}]
               [-de D_EWMA] [-v VALUE] [-vs VALUE_SHORT] [--pie] [--hist]
               [--dd] [--rc-chart] [--heat] [-h]
```

Minimizes the selected risk measure of portfolio

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
  -tr TARGET_RETURN, --target-return TARGET_RETURN
                        Constraint on minimum level of portfolio's return
                        (default: -1)
  -tk TARGET_RISK, --target-risk TARGET_RISK
                        Constraint on maximum level of portfolio's risk
                        (default: -1)
  -m {hist,ewma1,ewma2}, --mean {hist,ewma1,ewma2}
                        Method used to estimate expected returns vector
                        (default: hist)
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
2022 Apr 05, 13:45 (🦋) /portfolio/po/ $ minrisk

 [3 Years] Display a minimum risk portfolio using
volatility as risk measure

     Weights      
┏━━━━━━┳━━━━━━━━━┓
┃      ┃ Value   ┃
┡━━━━━━╇━━━━━━━━━┩
│ AAPL │  0.0 %  │
├──────┼─────────┤
│ AMZN │ 35.21 % │
├──────┼─────────┤
│ BA   │  0.0 %  │
├──────┼─────────┤
│ FB   │  0.0 %  │
├──────┼─────────┤
│ MSFT │  5.86 % │
├──────┼─────────┤
│ T    │ 58.92 % │
├──────┼─────────┤
│ TSLA │  0.0 %  │
└──────┴─────────┘

Annual (by 252) expected return: 11.77%
Annual (by √252) volatility: 22.03%
Sharpe ratio: 0.5256
```