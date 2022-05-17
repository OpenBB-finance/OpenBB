```
usage: summary [-p {mtd,qtd,ytd,3m,6m,1y,3y,5y,10y,all}] [-r RISK_FREE_RATE] [-h] [--export EXPORT]
```

Display summary of portfolio vs benchmark

```
optional arguments:
  -p {mtd,qtd,ytd,3m,6m,1y,3y,5y,10y,all}, --period {mtd,qtd,ytd,3m,6m,1y,3y,5y,10y,all}
                        The file to be loaded (default: all)
  -r RISK_FREE_RATE, --rfr RISK_FREE_RATE
                        Set risk free rate for calculations. (default: 0.0)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx (default: )
```
