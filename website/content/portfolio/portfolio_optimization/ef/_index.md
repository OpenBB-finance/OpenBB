```
usage: ef [-p {1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max}] [-n N_PORT] [-h] [-r]
```

This function plots random portfolios based on their risk and returns and shows the efficient frontier. 

https://pyportfolioopt.readthedocs.io/en/latest/GeneralEfficientFrontier.html

```
optional arguments:
  -p {1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max}, --period {1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max}
                        period to get yfinance data from (default: 3mo)
  -n N_PORT, --number-portfolios N_PORT
                        number of portfolios to simulate (default: 300)
  -h, --help            show this help message (default: False)
  -r, --risk-free       shows the risk free optimal line
```
<img width="1400" alt="Feature Screenshot - ef" src="https://user-images.githubusercontent.com/85772166/147480056-27682fb8-4087-44ff-acdc-4dcb931ea674.png">
