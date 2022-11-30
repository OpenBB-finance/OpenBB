```
usage: rsort [-p {3m,6m,1y,3y,5y,10y}] [-r RISK_FREE_RATE] [-h] [--export EXPORT]
```

Show rolling sortino portfolio vs benchmark

```
optional arguments:
  -p {3m,6m,1y,3y,5y,10y}, --period {3m,6m,1y,3y,5y,10y}
                        Period to apply rolling window (default: 1y)
  -r RISK_FREE_RATE, --rfr RISK_FREE_RATE
                        Set risk free rate for calculations. (default: 0.0)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
```

<img width="1428" alt="Screenshot 2022-05-18 at 01 03 39" src="https://user-images.githubusercontent.com/25267873/168931383-f9a61791-7a14-48fb-b538-0177657d50ed.png">
