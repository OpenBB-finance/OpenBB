```
usage: load [-t TICKER] [-s START] [-e END] [-i {1,5,15,30,60}] [--source {yf,av,iex}] [-p] [-f {Test.csv}] [-m] [-w] [-r {ytd,1y,2y,5y,6m}] [-h]
```

Load a symbol to perform analysis using the string above as a template. Optional arguments and their descriptions are listed below. 

The default source is, yFinance (https://pypi.org/project/yfinance/). Alternatively, one may select either AlphaVantage (https://www.alphavantage.co/documentation/) or IEX Cloud (https://iexcloud.io/docs/api/) as the data source for the analysis. Please note that certain analytical features are exclusive to the source. 

To load a symbol from an exchange outside of the NYSE/NASDAQ default, use yFinance as the source and add the corresponding exchange to the end of the symbol. i.e. 'BNS.TO'. 

BNS is a dual-listed stock, there are separate options chains and order books for each listing. Opportunities for arbitrage may arise from momentary pricing discrepancies between listings with a dynamic exchange rate as a second order opportunity in ForEx spreads. 

Find the full list of supported exchanges here: https://help.yahoo.com/kb/exchanges-data-providers-yahoo-finance-sln2310.html

Certain analytical features, such as VWAP, require the ticker to be loaded as intraday using the '-i x' argument. When encountering this error, simply reload the symbol using the interval argument. i.e. 'load -t BNS -s YYYY-MM-DD -i 1 -p' loads one-minute intervals, including Pre/After Market data, using the default source, yFinance. 

Certain features, such as the Prediction menu, require the symbol to be loaded as daily and not intraday.

```
optional arguments:
optional arguments:
  -t TICKER, --ticker TICKER
                        Stock ticker (default: None)
  -s START, --start START
                        The starting date (format YYYY-MM-DD) of the stock (default: 2019-03-12)
  -e END, --end END     The ending date (format YYYY-MM-DD) of the stock (default: 2022-03-16)
  -i {1,5,15,30,60}, --interval {1,5,15,30,60}
                        Intraday stock minutes (default: 1440)
  --source {yf,av,iex}  Source of historical data. (default: yf)
  -p, --prepost         Pre/After market hours. Only works for 'yf' source, and intraday data (default: False)
  -f {Test.csv}, --file {Test.csv}
                        Path to load custom file. (default: None)
  -m, --monthly         Load monthly data (default: False)
  -w, --weekly          Load weekly data (default: False)
  -r {ytd,1y,2y,5y,6m}, --iexrange {ytd,1y,2y,5y,6m}
                        Range for using the iexcloud api. Note that longer range requires more tokens in account (default: ytd)
  -h, --help            show this help message (default: False)

```

Note that loading monthly and weekly data are limited to yahoo finance, and monthly data has displayed issues where 
older data just downloads as `nan`.

Loading a custom file looks in the folder `custom_imports/stocks` and is currently only designed for csv files.


Example:
```
2022 Feb 16, 08:29 (✨) /stocks/ $ load TSLA

Loading Daily TSLA stock with starting period 2019-02-11 for analysis.

Datetime: 2022 Feb 16 08:30
Timezone: America/New_York
Currency: USD
Market:   OPEN

2022 Feb 16, 08:30 (✨) /stocks/ $ load AAPL

Loading Daily AAPL stock with starting period 2019-02-11 for analysis.

Datetime: 2022 Feb 16 08:30
Timezone: America/New_York
Currency: USD
Market:   OPEN

2022 Feb 16, 08:30 (✨) /stocks/ $ load AMZN

Loading Daily AMZN stock with starting period 2019-02-11 for analysis.

Datetime: 2022 Feb 16 08:30
Timezone: America/New_York
Currency: USD
Market:   OPEN
```
