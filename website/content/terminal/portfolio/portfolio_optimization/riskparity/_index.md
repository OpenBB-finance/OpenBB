```
usage: riskparity [-p PERIOD] [-s START] [-e END] [-lr] [-f {d,w,m}]
                  [-mn MAXNAN] [-th THRESHOLD] [-mt METHOD]
                  [-rm {MV,MAD,MSV,FLPM,SLPM,CVaR,EVaR,CDaR,EDaR,UCI}]
                  [-rc RISK_CONT] [-r RISK_FREE_RATE] [-a ALPHA]
                  [-tr TARGET_RETURN] [-de D_EWMA] [-v VALUE] [--pie] [--hist]
                  [--dd] [--rc-chart] [--heat] [-h]
```

Builds a risk parity portfolio based on risk budgeting approach

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
  -rm {MV,MAD,MSV,FLPM,SLPM,CVaR,EVaR,CDaR,EDaR,UCI}, --risk-measure {MV,MAD,MSV,FLPM,SLPM,CVaR,EVaR,CDaR,EDaR,UCI}
                        Risk measure used to optimize the portfolio (default:
                        MV)
  -rc RISK_CONT, --risk-cont RISK_CONT
                        vector of risk contribution constraint (default: None)
  -r RISK_FREE_RATE, --risk-free-rate RISK_FREE_RATE
                        Risk-free rate of borrowing/lending. The period of the
                        risk-free rate must be annual (default: 0.00185)
  -a ALPHA, --alpha ALPHA
                        Significance level of CVaR, EVaR, CDaR and EDaR
                        (default: 0.05)
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
  -h, --help            show this help message (default: False)```

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