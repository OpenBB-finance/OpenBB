```
usage: load [-t S_TICKER] [-s S_START_DATE] [-i {1,5,15,30,60}] [--source {yf,av,iex}] [-p] [-h]
```
```
optional arguments:
  -t S_TICKER, --ticker S_TICKER
                        Stock ticker (default: None)
  -s S_START_DATE, --start S_START_DATE
                        The starting date (format YYYY-MM-DD) of the stock (default: 2020-09-14)
  -i {1,5,15,30,60}, --interval {1,5,15,30,60}
                        Intraday stock minutes (default: 1440)
  --source {yf,av,iex}  Source of historical data. (default: yf)
  -p, --prepost         Pre/After market hours. Only works for 'yf' source, and intraday data (default: False)
  -h, --help            show this help message (default: False)
```
Load a symbol to perform analysis using the string above as a template. Optional arguments and their descriptions are listed above. 

The default source is, yFinance (https://pypi.org/project/yfinance/). Alternatively, one may select either AlphaVantage (https://www.alphavantage.co/documentation/) or IEX Cloud (https://iexcloud.io/docs/api/) as the data source for the analysis. Please note that certain analytical features are exclusive to the source. 

To load a symbol from an exchange outside of the NYSE/NASDAQ default, use yFinance as the source and add the corresponding exchange to the end of the symbol. i.e. 'BNS.TO'. 

BNS is a dual-listed stock, there are separate options chains and order books for each listing. Opportunities for arbitrage may arise from momentary pricing discrepancies between listings with a dynamic exchange rate as a second order opportunity in ForEx spreads. 

Find the full list of supported exchanges here: https://help.yahoo.com/kb/exchanges-data-providers-yahoo-finance-sln2310.html

Certain analytical features, such as VWAP, require the ticker to be loaded as intraday using the '-i x' argument. When encountering this error, simply reload the symbol using the interval argument. i.e. 'load -t BNS -s YYYY-MM-DD -i 1 -p' loads one-minute intervals, including Pre/After Market data, using the default source, yFinance. 

Certain features, such as the Prediction menu, require the symbol to be loaded as daily and not intraday.

<img width="1390" alt="Feature Screenshot - Load" src="https://user-images.githubusercontent.com/85772166/139967994-82e42c75-3ff5-4a04-80a2-c9c9b870934c.png">


