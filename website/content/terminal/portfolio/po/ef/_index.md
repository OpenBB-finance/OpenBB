```
usage: ef [-p PERIOD] [-s START] [-e END] [-lr] [-f {d,w,m}] [-mn MAXNAN]
          [-th THRESHOLD] [-mt METHOD]
          [-rm {MV,MAD,MSV,FLPM,SLPM,CVaR,EVaR,WR,ADD,UCI,CDaR,EDaR,MDD}]
          [-r RISK_FREE_RATE] [-a ALPHA] [-v VALUE] [-vs VALUE_SHORT]
          [-n N_PORTFOLIOS] [-se SEED] [-t] [-h]
```

This function plots random portfolios based on their risk and returns and
shows the efficient frontier of selected risk measure.

```
optional arguments:
  -p PERIOD, --period PERIOD
                        Period to get yfinance data from (default: 3y)
  -s START, --start START
                        Start date to get yfinance data from. Must be in
                        'YYYY-MM-DD' format (default: )
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
                        Amount to allocate to portfolio in long positions
                        (default: 1.0)
  -vs VALUE_SHORT, --value-short VALUE_SHORT
                        Amount to allocate to portfolio in short positions
                        (default: 0.0)
  -n N_PORTFOLIOS, --number-portfolios N_PORTFOLIOS
                        Number of portfolios to simulate (default: 100)
  -se SEED, --seed SEED
                        Seed used to generate random portfolios (default: 123)
  -t, --tangency        Adds the optimal line with the risk-free asset
                        (default: False)
  --no-plot  		Whether to plot the tickers (default: True)
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Apr 05, 15:03 (🦋) /portfolio/po/ $ ef
```
![Frontier](https://user-images.githubusercontent.com/61527316/161860003-e8b8ae93-ce8c-4e06-bad2-59c100f09325.png)

