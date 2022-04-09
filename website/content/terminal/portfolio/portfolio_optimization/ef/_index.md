```
usage: ef [-p {1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max}] [-n N_PORT] [-r] [-h]
```

This function plots random portfolios based on their risk and returns and shows the efficient frontier.

See: https://pyportfolioopt.readthedocs.io/en/latest/GeneralEfficientFrontier.html

```
optional arguments:
  -p {1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max}, --period {1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max}
                        period to get yfinance data from (default: 1y)
  -n N_PORT, --number-portfolios N_PORT
                        number of portfolios to simulate (default: 300)
  -r, --risk-free       Adds the optimal line with the risk-free asset (default: False)
  -h, --help            show this help message (default: False)
```

Example:
```
2022 Feb 14, 11:12 (✨) /portfolio/po/ $ ef
Expected annual return: 46.7%
Annual volatility: 10.7%
Sharpe Ratio: 4.36
```
![ef](https://user-images.githubusercontent.com/46355364/153901823-bca43498-43f8-40ae-8933-b6deb9d1086c.png)
