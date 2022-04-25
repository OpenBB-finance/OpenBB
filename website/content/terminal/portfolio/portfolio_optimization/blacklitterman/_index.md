```
usage: blacklitterman [-p PERIOD] [-s START] [-e END] [-lr] [-f {d,w,m}]
                      [-mn MAXNAN] [-th THRESHOLD] [-mt METHOD]
                      [-bm BENCHMARK] [-o {MinRisk,Utility,Sharpe,MaxRet}]
                      [-pv P_VIEWS] [-qv Q_VIEWS] [-r RISK_FREE_RATE]
                      [-ra RISK_AVERSION] [-d DELTA] [-eq] [-op] [-v VALUE]
                      [-vs VALUE_SHORT] [--name NAME] [-h]
```

Minimizes the selected risk measure of portfolio

```
optional arguments:
  -p PERIOD, --period PERIOD
                        Period to get yfinance data from. Possible frequency
                        strings are: 'd': means days, for example '252d' means
                        252 days 'w': means weeks, for example '52w' means 52
                        weeks 'mo': means months, for example '12mo' means 12
                        months 'y': means years, for example '1y' means 1 year
                        'ytd': downloads data from begining of year to today
                        'max': downloads all data available for each asset
                        (default: 3y)
  -s START, --start START
                        Start date to get yfinance data from. Must be in
                        'YYYY-MM-DD' format (default: )
  -e END, --end END     End date to get yfinance data from. Must be in 'YYYY-
                        MM-DD' format (default: )
  -lr, --log-returns    If use logarithmic or arithmetic returns to calculate
                        returns (default: False)
  -f {d,w,m}, --freq {d,w,m}
                        Frequency used to calculate returns. Possible values
                        are: 'd': for daily returns 'w': for weekly returns
                        'm': for monthly returns (default: d)
  -mn MAXNAN, --maxnan MAXNAN
                        Max percentage of nan values accepted per asset to be
                        considered in the optimization process (default: 0.05)
  -th THRESHOLD, --threshold THRESHOLD
                        Value used to replace outliers that are higher to
                        threshold in absolute value (default: 0.3)
  -mt METHOD, --method METHOD
                        Method used to fill nan values in time series, by
                        default time. Possible values are: linear: linear
                        interpolation time: linear interpolation based on time
                        index nearest: use nearest value to replace nan values
                        zero: spline of zeroth order slinear: spline of first
                        order quadratic: spline of second order cubic: spline
                        of third order barycentric: builds a polynomial that
                        pass for all points (default: time)
  -bm BENCHMARK, --benchmark BENCHMARK
                        portfolio name from current portfolio list (default:
                        None)
  -o {MinRisk,Utility,Sharpe,MaxRet}, --objective {MinRisk,Utility,Sharpe,MaxRet}
                        Objective function used to optimize the portfolio
                        (default: MinRisk)
  -pv P_VIEWS, --p-views P_VIEWS
                        matrix P of views (default: None)
  -qv Q_VIEWS, --q-views Q_VIEWS
                        matrix Q of views (default: None)
  -r RISK_FREE_RATE, --risk-free-rate RISK_FREE_RATE
                        Risk-free rate of borrowing/lending. The period of the
                        risk-free rate must be annual (default: 0.00329)
  -ra RISK_AVERSION, --risk-aversion RISK_AVERSION
                        Risk aversion parameter (default: 1.0)
  -d DELTA, --delta DELTA
                        Risk aversion factor of Black Litterman model
                        (default: None)
  -eq, --equilibrium    If True excess returns are based on equilibrium market
                        portfolio, if False excess returns are calculated as
                        historical returns minus risk free rate. (default:
                        True)
  -op, --optimize       If True Black Litterman estimates are used as inputs
                        of mean variance model, if False returns equilibrium
                        weights from Black Litterman model (default: True)
  -v VALUE, --value VALUE
                        Amount to allocate to portfolio in long positions
                        (default: 1.0)
  -vs VALUE_SHORT, --value-short VALUE_SHORT
                        Amount to allocate to portfolio in short positions
                        (default: 0.0)
  --name NAME           Save portfolio with personalized or default name
                        (default: BL_3)
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Apr 25, 01:22 (🦋) /portfolio/po/ $ add AAPL,MSFT,JP
2022 Apr 25, 01:25 (🦋) /portfolio/po/ $ minrisk

 [3 Years] Minimum risk portfolio using
volatility as risk measure

      Weights      
┏━━━━━━┳━━━━━━━━━━┓
┃      ┃ Value    ┃
┡━━━━━━╇━━━━━━━━━━┩
│ AAPL │  26.29 % │
├──────┼──────────┤
│ JP   │   8.82 % │
├──────┼──────────┤
│ MSFT │  64.89 % │
└──────┴──────────┘
Annual (by 252) expected return: 28.10%
Annual (by √252) volatility: 29.70%
Sharpe ratio: 0.9351

2022 Apr 25, 01:26 (🦋) /portfolio/po/ $ blacklitterman -bm minrisk_0 -pv 0,1,0;
1,0,0;1,0,0 -qv 0.1,0.1,0.05 -o MinRisk

 [3 Years] Black Litterman portfolio

      Weights      
┏━━━━━━┳━━━━━━━━━━┓
┃      ┃ Value    ┃
┡━━━━━━╇━━━━━━━━━━┩
│ AAPL │  26.29 % │
├──────┼──────────┤
│ JP   │   8.82 % │
├──────┼──────────┤
│ MSFT │  64.89 % │
└──────┴──────────┘
Annual (by 252) expected return: 28.10%
Annual (by √252) volatility: 29.70%
Sharpe ratio: 0.9462
```