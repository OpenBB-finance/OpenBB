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
<img width="1400" alt="Feature Screenshot - minvol" src="https://user-images.githubusercontent.com/85772166/147485096-cac6c072-6bcc-4bbf-b0f6-85e899fe1ac9.png">
