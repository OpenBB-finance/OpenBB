```
usage: minvol [-p {1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max}] [-v VALUE] [--pie] [-h]
```

Optimizes for minimum volatility

```
optional arguments:
  -p {1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max}, --period {1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max}
                        period to get yfinance data from (default: 3mo)
  -v VALUE, --value VALUE
                        Amount to allocate to portfolio (default: 1.0)
  --pie                 Display a pie chart for weights (default: False)
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 14, 11:19 (✨) /portfolio/po/ $ minvol --pie

Expected annual return: 43.1%
Annual volatility: 10.2%
Sharpe Ratio: 4.03
```

![minvol](https://user-images.githubusercontent.com/46355364/153903170-177a82b7-81d6-4c86-a43b-72ac238de62b.png)
