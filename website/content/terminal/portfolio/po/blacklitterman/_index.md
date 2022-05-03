```
usage: blacklitterman [-p PERIOD] [-s START] [-e END] [-lr] [-f {d,w,m}]
                      [-mn MAXNAN] [-th THRESHOLD] [-mt METHOD]
                      [-bm BENCHMARK] [-o {MinRisk,Utility,Sharpe,MaxRet}]
                      [-pv P_VIEWS] [-qv Q_VIEWS] [-r RISK_FREE_RATE]
                      [-ra RISK_AVERSION] [-d DELTA] [-eq] [-op] [-v VALUE]
                      [-vs VALUE_SHORT] [--name NAME] [-h]
```

The Black-Litterman (BL) Model is an analytical tool used by portfolio managers to optimize asset allocation within an investor’s risk tolerance and market views. Global investors, such as pension funds and insurance companies, need to decide how to allocate their investments across different asset classes and countries. The BL model starts from a neutral position using modern portfolio theory (MPT), and then takes additional input from investors' views to determine how the ultimate asset allocation should deviate from the initial portfolio weights. It then undergoes a process of mean-variance optimization (MVO) to maximize expected return given one's objective risk tolerance.

```
optional arguments:
  -p PERIOD, --period PERIOD
                        Period to get yfinance data from. Possible frequency
                        strings are: 'd': means days, for example '252d' means
                        252 days 'w': means weeks, for example '52w' means 52
                        weeks 'mo': means months, for example '12mo' means 12
                        months 'y': means years, for example '1y' means 1 year
                        'ytd': downloads data from beginning of year to today
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

First we need to build a benchmark portfolio:

```
2022 Apr 26, 01:25 (🦋) /portfolio/po/ $ add AAPL,MSFT,JP,BA
2022 Apr 26, 01:26 (🦋) /portfolio/po/ $ maxsharpe

 [3 Years] Maximal return/risk ratio portfolio using volatility as risk measure

      Weights      
┏━━━━━━┳━━━━━━━━━━┓
┃      ┃ Value    ┃
┡━━━━━━╇━━━━━━━━━━┩
│ AAPL │ 100.00 % │
├──────┼──────────┤
│ BA   │   0.00 % │
├──────┼──────────┤
│ JP   │   0.00 % │
├──────┼──────────┤
│ MSFT │   0.00 % │
└──────┴──────────┘
Annual (by 252) expected return: 45.46%
Annual (by √252) volatility: 34.16%
Sharpe ratio: 1.3209
```

Then we add our views to the benchmark portfolio:

```
2022 Apr 26, 01:27 (🦋) /portfolio/po/ $ blacklitterman -bm maxsharpe_0 -pv 0,1,
0,0;1,0,0,0;0,0,0,1 -qv 0.1,0.1,0.05 -o Sharpe

 [3 Years] Black Litterman portfolio

      Weights      
┏━━━━━━┳━━━━━━━━━━┓
┃      ┃ Value    ┃
┡━━━━━━╇━━━━━━━━━━┩
│ AAPL │  70.30 % │
├──────┼──────────┤
│ BA   │  18.55 % │
├──────┼──────────┤
│ JP   │   0.01 % │
├──────┼──────────┤
│ MSFT │  11.14 % │
└──────┴──────────┘
Annual (by 252) expected return: 33.94%
Annual (by √252) volatility: 32.80%
Sharpe ratio: 1.0346
```