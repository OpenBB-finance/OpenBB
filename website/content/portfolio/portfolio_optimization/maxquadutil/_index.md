```
usage: maxquadutil [-p {1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max}] [-v VALUE] [-n] [--pie] [-r RISK_AVERSION] [-h]
```

Maximises the quadratic utility, given some risk aversion

```
optional arguments:
  -p {1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max}, --period {1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max}
                        period to get yfinance data from (default: 3mo)
  -v VALUE, --value VALUE
                        Amount to allocate to portfolio (default: 1.0)
  -n, --market-neutral  whether the portfolio should be market neutral (weights sum to zero), defaults to False. Requires negative lower weight
                        bound. (default: False)
  --pie                 Display a pie chart for weights. Only if neutral flag is left False. (default: False)
  -r RISK_AVERSION, --risk-aversion RISK_AVERSION
                        risk aversion parameter (default: 1)
  -h, --help            show this help message (default: False)
```
