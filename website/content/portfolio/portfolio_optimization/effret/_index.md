```
usage: effret [-p {1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max}] [-v VALUE] [-n] [--pie] [-t TARGET_RETURN] [-h]
```

Calculate the 'Markowitz portfolio', minimising volatility for a given target return. By combining assets with different expected returns and volatilities, one can decide on a mathematically optimal allocation.

```
optional arguments:
  -p {1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max}, --period {1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max}
                        period to get yfinance data from (default: 1y)
  -v VALUE, --value VALUE
                        Amount to allocate to portfolio (default: 1.0)
  -n, --market-neutral  whether the portfolio should be market neutral (weights sum to zero), defaults to False. Requires negative lower weight bound. (default: False)
  --pie                 Display a pie chart for weights. Only if neutral flag is left False. (default: False)
  -t TARGET_RETURN, --target-return TARGET_RETURN
                        the desired return of the resulting portfolio (default: 0.1)
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 14, 11:14 (✨) /portfolio/po/ $ effret --pie

Expected annual return: 42.9%
Annual volatility: 10.2%
Sharpe Ratio: 4.00
```
![effret](https://user-images.githubusercontent.com/46355364/153902203-c7a23b78-6211-4d2b-be06-6ed8f0b00143.png)
