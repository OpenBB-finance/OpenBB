```
usage: metric [-m {volatility,sharpe,sortino,maxdrawdown,rsquare,skew,kurtosis}] [-r RISK_FREE_RATE] [-h] [--export EXPORT]
```

Display metric of choice for different periods

```
optional arguments:
  -m {volatility,sharpe,sortino,maxdrawdown,rsquare,skew,kurtosis}, --metric {volatility,sharpe,sortino,maxdrawdown,rsquare,skew,kurtosis}
                        Period to apply rolling window (default: False)
  -r RISK_FREE_RATE, --rfr RISK_FREE_RATE
                        Set risk free rate for calculations. (default: 0.0)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx (default: )
```
