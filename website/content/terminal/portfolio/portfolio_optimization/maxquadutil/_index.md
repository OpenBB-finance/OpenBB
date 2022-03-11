```
usage: maxquadutil [-p {1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max}] [-v VALUE] [-n] [--pie] [-r RISK_AVERSION] [-h]
```
In financial economics, the utility function most frequently used to describe investor behaviour is the quadratic utility function. Its popularity stems from the fact that, under the assumption of quadratic utility, mean-variance analysis is optimal.

https://www.d42.com/portfolio/analysis/quadratic-utility

```
optional arguments:
  -p {1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max}, --period {1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max}
                        period to get yfinance data from (default: 1y)
  -v VALUE, --value VALUE
                        Amount to allocate to portfolio (default: 1.0)
  -n, --market-neutral  whether the portfolio should be market neutral (weights sum to zero), defaults to False. Requires negative lower weight bound. (default: False)
  --pie                 Display a pie chart for weights. Only if neutral flag is left False. (default: False)
  -r RISK_AVERSION, --risk-aversion RISK_AVERSION
                        risk aversion parameter (default: 1.0)
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 14, 11:16 (✨) /portfolio/po/ $ maxquadutil
[1 Year] Weights that maximise quadratic utility with risk aversion: 1.0
      Weights
┌────────┬─────────┐
│        │ Value   │
├────────┼─────────┤
│ BNS.TO │ -0.00 % │
├────────┼─────────┤
│ BMO.TO │ 100.0 % │
├────────┼─────────┤
│ TD.TO  │  0.0 %  │
├────────┼─────────┤
│ CM.TO  │ -0.0 %  │
├────────┼─────────┤
│ NA.TO  │  0.0 %  │
├────────┼─────────┤
│ RY.TO  │ -0.0 %  │
└────────┴─────────┘

Expected annual return: 57.5%
Annual volatility: 15.3%
Sharpe Ratio: 3.62
```
