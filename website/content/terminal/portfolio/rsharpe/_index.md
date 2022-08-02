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

<img width="1426" alt="Screenshot 2022-05-18 at 01 03 07" src="https://user-images.githubusercontent.com/25267873/168931347-7f20a9a9-971b-4bf3-94d4-bd33f83c082d.png">
