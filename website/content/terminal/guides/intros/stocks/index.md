---
title: Stocks
---

The Stocks menu is the high-level menu for the public equities asset class. It is divided into two sections:

- Functions for searching, loading, and displaying candles, quotes, and news.
- Sub-menus

The sub-menus break the functions down into groups based on the type of data they return. They are listed below with a short description. Refer to each sub-menu's introductory guide for a more detailed explanation of the functions within.

|Command  |Sub-Menu |Description |
|:---------|------------:|----------------------:|
|ba |Behavioural Analysis |Social Media, Sentiment, Trends |
|bt |Strategy Backtester | Simple EMA, EMA Crossover & RSI Strategies |
|ca |Comparison Analysis |Compare Historical Prices, Correlations, Financials |
|dd |Due Diligence |Analyst Coverage, Price Targets, SEC Filings, Customers and Suppliers |
|disc |Discovery |Upcoming Earnings and Dividends Calendar, Heatmaps, Trending News |
|dps |Dark Pool and Short Data |Short Interest, Borrow Rates, Off-Exchange Short Volume |
|fa |Fundamental Analysis |Financial Statements and Analysis |
|forecast |Forecasting and ML |Enter the Forecast Menu With the Loaded Ticker |
|gov |Government |House and Senate Trading Disclosures, Lobbying Efforts, US Treasury Spending |
|ins |Insider Trading |SEC Form 4 Disclosures & Screener |
|options |Equity Options |Options Analysis, Quotes, Historical Prices, Greeks & Screener |
|qa |Quantitative Analysis |Mathematical Analysis |
|res |Research Websites |Shortcuts to Online Resources for the Loaded Ticker |
|scr |Stocks Screener |Custom Stocks Screener |
|sia |Sector & Industry Analysis |Find and Compare by Region, Sector, Industry & Market Cap |
|ta |Technical Analysis |Technical Indicators and Charts |
|th |Trading Hours |Lists of World Markets and Current Status |

## How to Use

The current screen can always be re-printed with any of: `?`, `h`, `help`.

### Data Sources

The first step in many workflows will be to load a stock symbol with historical data. The amount, granularity, and market coverage will vary by source. Users can elect to subscribe to any of the data sources accordingly. While no API keys are required to get started using the Terminal, acquiring these credentials at the free level will enhance the user experience with additional functionality. Refer to the [API keys guide](https://docs.openbb.co/terminal/guides/advanced/api-keys) for links to obtain each. The data sources used in the Stocks menu that require API credentials are:

- AlphaVantage
- EODHD
- Financial Modeling Prep
- News
- Polygon
- Quandl
- Tradier

The data source for each function is located on the right-side of the menu. For example:

|    |                          |                     |
|:---|:------------------------:|--------------------:|
|news|latest news of the company|[Feedparser, NewsApi]|

Attaching the source argument to a command, `news --source NewsApi`, enables users to select their preferred source. The default sources can be changed from the [`/sources` menu](https://docs.openbb.co/terminal/guides/advanced/changing-sources).

Let's get started using the Stocks menu with some examples.

## Examples

### Load

The `load` function is a starting point for most functions, and parameters can be adjusted for intraday and resolution. A daily period, with three-years of OHLC+V data, from YahooFinance, is loaded to memory as the default. Use the default settings like this:

```console
load SPY
```

A message will print indicating the starting date from which the data begins along with a table summarizing its recent performance.

```console
Loading Daily data for SPY with starting period 2019-11-27.

Company:  SPDR S&P 500
Exchange: PCX
Currency: USD

                                          SPY Performance                                           
┏━━━━━━━━┳━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ 1 Day  ┃ 1 Week ┃ 1 Month ┃ 1 Year  ┃ YTD      ┃ Volatility (1Y) ┃ Volume (10D avg) ┃ Last Price ┃
┡━━━━━━━━╇━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 2.97 % │ 1.95 % │ 5.56 %  │ -9.16 % │ -13.67 % │ 24.19 %         │ 67.92 M          │ 407.68     │
└────────┴────────┴─────────┴─────────┴──────────┴─────────────────┴──────────────────┴────────────┘
```

The load function has many optional arguments. Attach `-h` or `--help` to any function to print the list of specific arguments and their syntax.

```console
options:
  -t TICKER, --ticker TICKER
                        Stock ticker (default: None)
  -s START, --start START
                        The starting date (format YYYY-MM-DD) of the stock (default: 2019-11-27)
  -e END, --end END     The ending date (format YYYY-MM-DD) of the stock (default: 2022-12-01)
  -i {1,5,15,30,60}, --interval {1,5,15,30,60}
                        Intraday stock minutes (default: 1440)
  -p, --prepost         Pre/After market hours. Only works for 'yf' source, and intraday data (default: False)
  -f FILEPATH, --file FILEPATH
                        Path to load custom file. (default: None)
  -m, --monthly         Load monthly data (default: False)
  -w, --weekly          Load weekly data (default: False)
  -r {ytd,1y,2y,5y,6m}, --iexrange {ytd,1y,2y,5y,6m}
                        Range for using the iexcloud api. Longer range requires more tokens in account (default: ytd)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx (default: )
  --source {YahooFinance,IEXCloud,AlphaVantage,Polygon,EODHD}
                        Data source to select from (default: YahooFinance)
```

A simple way to get the entire history available from a source is to use an arbitrary starting date from a long time ago, like `1900-01-01`.

```console
load SPY -s 1990-01-01
```

The console print indicates the first date of history, provided by this source, is January 29, 1993.

```console
Loading Daily data for SPY with starting period 1993-01-29.
```

A range-bound window can also be loaded; for example, the dot-com era:

```console
load SPY -s 1997-01-01 -e 2003-01-01
```

The interval of the data can also be set as weekly or monthly; `-w` for weekly, and `-m` for monthly candles. The data will now start on a Monday or at the beginning of a month.

```console
load SPY -s 1997-01-01 -e 2003-01-01 -w
```

Intraday data is also requested this way, only using the `-i` or `--interval` argument. One-minute data can be loaded like this:

```console
load SPY -i 1
```

The performance table will not be displayed with intraday data, and we can see that five-days of one-minute candles are available from YahooFinance.

```console
Loading Intraday 1min data for SPY with starting period 2022-11-25.

Company:  SPDR S&P 500
Exchange: PCX
Currency: USD
```

This can be augmented further by adding pre/post market price candles. The `-p` flag is only applicable to YahooFinance, Polygon will automatically include the candles from 4AM-8PM US/Eastern when intraday is selected.

```console
load spy -i 1 -p
```

Data can also be exported directly from the `load` function as a CSV, JSON, or XLSX file. The file is created in the OpenBBUserData folder.

```console
load spy -s 1990-01-01 -m --export spy_monthly.csv

Loading Daily data for SPY with starting period 1993-02-01.

Company:  SPDR S&P 500
Exchange: PCX
Currency: USD

Saved file: /Users/{username}/OpenBBUserData/exports/spy_monthly.csv
```

Exported files can also be loaded by declaring the `--file` argument. Place a file for importing in the folder: `OpenBBUserData/custom_imports/stocks`

### Candle

The `candle` command displays a chart of the loaded symbol. It needs no arguments to display, but modifiers can enhance the content of the chart. Commands can also be sequenced together with a `/` separating each individual command.

```console
/stocks/load SPY -s 1990-01-01 -m/candle
```

![candle](https://user-images.githubusercontent.com/85772166/205148777-cd7379f1-b7ef-41b8-890a-d0cf24e725d3.png "candle")

The help dialgoe for the `candle` command shows how this chart can be supplemented with additional data; specifically, these arguments:

```console
-t, --trend           Flag to add high and low trends to candle (default: False)
  --ma MOV_AVG          Add moving average in number of days to plot and separate by a comma. Value for ma (moving average) keyword needs to be greater
                        than 1. (default: None)
  --log                 Plot with y axis on log scale (default: False)
```

Be sure to adjust the values for moving averages to correspond with the interval of the data loaded. Below adds movings averages for one and four year periods (because data loaded is monthly), and changes the y-axis to a log-scale.

```console
candle --ma 12,48 --log
```

!![candle](https://user-images.githubusercontent.com/85772166/205148707-f1f2172f-8dee-4f31-b020-4f8043ccccd7.png "candle")

The look and feel of the `candle` chart can be altered with [custom style sheets](https://matplotlib.org/stable/tutorials/introductory/customizing.html#the-default-matplotlibrc-file) placed in `OpenBBUserData/styles/user`.

### News

Get ticker-related news headlines by entering `news` after loading a ticker.

```console
news --source NewsApi

135 news articles for  SPDR+S&P+500 were found since 2022-11-24

              Earnings Results: Big Lots to address weak results with even lower prices: ‘We will own bargains and treasures’               
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Content                                                                                                                                  ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 2022-12-01 18:41:00                                                                                                                      │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Big Lots says it will address weak results by leaning into bargains and treasures in a much bigger way.                                  │
├──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ https://www.marketwatch.com/story/big-lots-to-address-weak-results-with-even-lower-prices-we-will-own-bargains-and-treasures-11669920117 │
└──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

                                     Costco's Sales Update Slams the Stock. Strong Grocery Sales Weren't Enough.                                      
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Content                                                                                                                                            ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 2022-12-01 17:48:00                                                                                                                                │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Sales of food and sundries climbed by double digits, while, non-food categories were largely lower, hurt by products like electronics and jewelry. │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ https://www.barrons.com/articles/costco-november-sales-51669916824                                                                                 │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘

                                                      Investors Pull $8 Billion From Major Stock ETFs                                                      
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Content                                                                                                                                                 ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 2022-12-01 17:34:05                                                                                                                                     │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ (Bloomberg) -- Exchange-traded fund investors took Wednesday’s stock-market surge as an opportunity to offload $8 billion of holdings in two of the     │
│ biggest equity funds. Most Read from Bloomberg Investors pulled $5.8 billion from the $380 billion SPDR S&P 500…                                        │
├─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ https://biztoc.com/x/b81c9c421015a955                                                                                                                   │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### TOB

The `tob` function gets bid/ask prices and lot sizes from order books on CBOE exchanges.

```console
tob

                SPY Top of Book                
┏━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━┓
┃ Bid Size ┃ Bid Price ┃ Ask Price ┃ Ask Size ┃
┡━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━┩
│ 223.00   │ 407.60    │ 407.62    │ 536.00   │
├──────────┼───────────┼───────────┼──────────┤
│ 823.00   │ 407.59    │ 407.63    │ 436.00   │
├──────────┼───────────┼───────────┼──────────┤
│ 923.00   │ 407.58    │ 407.64    │ 836.00   │
├──────────┼───────────┼───────────┼──────────┤
│ 316.00   │ 407.57    │ 407.65    │ 936.00   │
├──────────┼───────────┼───────────┼──────────┤
│ 823.00   │ 407.56    │ 407.66    │ 636.00   │
└──────────┴───────────┴───────────┴──────────┘
```

### Quote

`quote` displays a table with the current price (during market hours) and some general statistics.

```console
quote

          Ticker Quote           
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃                ┃ SPY          ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ Name           │ SPDR S&P 500 │
├────────────────┼──────────────┤
│ Price          │ 407.69       │
├────────────────┼──────────────┤
│ Open           │ 408.77       │
├────────────────┼──────────────┤
│ High           │ 410.00       │
├────────────────┼──────────────┤
│ Low            │ 404.75       │
├────────────────┼──────────────┤
│ Previous Close │ 407.68       │
├────────────────┼──────────────┤
│ Volume         │ 52,458,993   │
├────────────────┼──────────────┤
│ 52 Week High   │ 479.98       │
├────────────────┼──────────────┤
│ 52 Week Low    │ 348.11       │
├────────────────┼──────────────┤
│ Change         │ 0.01         │
├────────────────┼──────────────┤
│ Change %       │ 0.00%        │
└────────────────┴──────────────┘
```

### Codes

`codes` prints the CIK, Composite FIGI, Share Class FIGI, and SIC codes - when available - for a US-listed stock. This function requires a free API key from Polygon.

```console
load aapl/codes

            AAPL Codes             
┏━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃                  ┃              ┃
┡━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ CIK              │ 0000320193   │
├──────────────────┼──────────────┤
│ COMPOSITE FIGI   │ BBG000B9XRY4 │
├──────────────────┼──────────────┤
│ SHARE CLASS FIGI │ BBG001S5N8V8 │
├──────────────────┼──────────────┤
│ SIC CODE         │ 3571         │
└──────────────────┴──────────────┘
```

### Search

The `search` function provides a way to find stocks by name, region, sector, industry and exchange location. The results can be easily exported as a CSV, JSON, or XLSX file.


```console
search -s technology --country india -e india --export csv

                          Companies found on an exchange in India in India within Technology                           
┏━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃               ┃ Name                            ┃ Country ┃ Sector     ┃ Industry                        ┃ Exchange ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ 3IINFOTECH.NS │ 3i Infotech Limited             │ India   │ Technology │ Information Technology Services │ None     │
├───────────────┼─────────────────────────────────┼─────────┼────────────┼─────────────────────────────────┼──────────┤
│ 543282.BO     │ Niks Technology Limited         │ India   │ Technology │ Information Technology Services │ None     │
├───────────────┼─────────────────────────────────┼─────────┼────────────┼─────────────────────────────────┼──────────┤
│ ACCELYA.NS    │ Accelya Solutions India Limited │ India   │ Technology │ Information Technology Services │ None     │
├───────────────┼─────────────────────────────────┼─────────┼────────────┼─────────────────────────────────┼──────────┤
│ ADROITINFO.NS │ Adroit Infotech Limited         │ India   │ Technology │ Information Technology Services │ None     │
├───────────────┼─────────────────────────────────┼─────────┼────────────┼─────────────────────────────────┼──────────┤
│ ADSL.NS       │ Allied Digital Services Limited │ India   │ Technology │ Information Technology Services │ None     │
├───────────────┼─────────────────────────────────┼─────────┼────────────┼─────────────────────────────────┼──────────┤
│ AGCNET.NS     │ AGC Networks Limited            │ India   │ Technology │ Software - Application          │ None     │
├───────────────┼─────────────────────────────────┼─────────┼────────────┼─────────────────────────────────┼──────────┤
│ AIRAN.NS      │ Airan Limited                   │ India   │ Technology │ Information Technology Services │ None     │
├───────────────┼─────────────────────────────────┼─────────┼────────────┼─────────────────────────────────┼──────────┤
│ AKSHOPTFBR.NS │ Aksh Optifibre Limited          │ India   │ Technology │ Communication Equipment         │ None     │
├───────────────┼─────────────────────────────────┼─────────┼────────────┼─────────────────────────────────┼──────────┤
│ ALANKIT.NS    │ Alankit Limited                 │ India   │ Technology │ Information Technology Services │ None     │
├───────────────┼─────────────────────────────────┼─────────┼────────────┼─────────────────────────────────┼──────────┤
│ AMBER.NS      │ Amber Enterprises India Limited │ India   │ Technology │ Consumer Electronics            │ None     │
└───────────────┴─────────────────────────────────┴─────────┴────────────┴─────────────────────────────────┴──────────┘

Saved file: /Users/{username}/OpenBBUserData/exports/20221201_115807_stocks_search.csv

```

The exported file will contain all results despite not being shown. To view more results, add the `--limit` argument.

```console
search -s technology --country india -e india --limit 1000
```
