```
usage: maxquadutil [-p {1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max}] [-v VALUE] [-n] [--pie] [-r RISK_AVERSION] [-h]
```
In financial economics, the utility function most frequently used to describe investor behaviour is the quadratic utility function. Its popularity stems from the fact that, under the assumption of quadratic utility, mean-variance analysis is optimal.

https://www.d42.com/portfolio/analysis/quadratic-utility

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
<img width="1400" alt="Feature Screenshot - maxquadutil" src="https://user-images.githubusercontent.com/85772166/147484659-44fc1892-aa13-4e4e-8b5e-cab4686acc0f.png">
