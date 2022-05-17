```
usage: rsharpe [-p {3m,6m,1y,3y,5y,10y}] [-r RISK_FREE_RATE] [-h] [--export EXPORT]
```

Show rolling sharpe portfolio vs benchmark

```
optional arguments:
  -p {3m,6m,1y,3y,5y,10y}, --period {3m,6m,1y,3y,5y,10y}
                        Period to apply rolling window (default: 1y)
  -r RISK_FREE_RATE, --rfr RISK_FREE_RATE
                        Set risk free rate for calculations. (default: 0.0)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
```
