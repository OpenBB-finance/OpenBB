---
title: Stocks
keywords: [stocks, fundamental analysis, analysis, Behavioural, strategy, comparison, due diligence, discovery, dark pool, short, data, forecasting, fundamental, quantitative, government, forecating, ml, ai, machine learning, artificial intelligence, insider, trading, research, sector, industry, technical, trading hours, quote, market data, close, adjusted close, download, export, tools, openbb terminal]
description: The Stocks menu is the high-level menu for the Public Equity asset class. It contains functions for searching and loading company market data, showing candle charts, quotes and company specifics via a large selection of sub-menus. The sub-menus break the functions down into groups based on the type of data they return. They are listed below with a short description. Refer to each sub-menu's introductory guide for a more detailed explanation of the functions within.
---

The Stocks menu is the high-level menu for the Public Equity asset class. It contains functions for searching and loading company market data, showing candle charts, quotes and company specifics via a large selection of sub-menus. The sub-menus break the functions down into groups based on the type of data they return. They are listed below with a short description. Refer to each sub-menu's introductory guide for a more detailed explanation of the functions within.

|Command  |Sub-Menu |Description |
|:---------|------------:|----------------------:|
|ba |Behavioural Analysis |Social Media, Sentiment, Trends |
|bt |Strategy Backtester | Simple EMA, EMA Crossover & RSI Strategies |
|ca |Comparison Analysis |Compare Historical Prices, Correlations, Financials |
|disc |Discovery |Upcoming Earnings and Dividends Calendar, Heatmaps, Trending News |
|dps |Dark Pool and Short Data |Short Interest, Borrow Rates, Off-Exchange Short Volume |
|fa |Fundamental Analysis |Financial Statements, Company Overviews, Analyst Coverage, Price Targets |
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

The current screen can always be re-printed with any of: `?`, `h`, `help`. The help dialogue, containing all parameters for each function, is printed when `-h` is attached to any command. The help dialogue will also provide the list of sources available to each command, the `news` function is shown below.

```console
news -h
```

Which prints the reference information on the screen:

```console
usage: news [-d N_START_DATE] [-o] [-s SOURCES] [-h] [--export {csv,json,xlsx}] [-l LIMIT] [--source {Feedparser,NewsApi}]

latest news of the company

optional arguments:
  -d N_START_DATE, --date N_START_DATE
                        The starting date (format YYYY-MM-DD) to search articles from
  -o, --oldest          Show oldest articles first
  -s SOURCES, --sources SOURCES
                        Show news only from the sources specified (e.g bloomberg,reuters)
  -h, --help            show this help message
  --export {csv,json,xlsx}
                        Export raw data into csv, json, xlsx
  -l LIMIT, --limit LIMIT
                        Number of entries to show in data.
  --source {Feedparser,NewsApi}
                        Data source to select from

For more information and examples, use 'about news' to access the related guide.
```

### Data Sources

The first step in many workflows will be to load a stock symbol with historical data. The amount, granularity, and market coverage will vary by source. Users can elect to subscribe to any of the data sources accordingly. While no API keys are required to get started using the Terminal, acquiring these credentials at the free level will enhance the user experience with additional functionality. Refer to the [API keys guide](https://docs.openbb.co/terminal/guides/advanced/api-keys) for links to obtain each. The data sources used in the Stocks menu that require API credentials are:

- AlphaVantage
- EODHD
- Financial Modeling Prep
- News
- Polygon
- Quandl
- Tradier

The data source for each function is located on the right-side of the menu. In the image below, this is depicted by the text in [blue].

![Stocks Menu](https://user-images.githubusercontent.com/85772166/205688600-afaf4663-37f7-492e-aa9b-7d5263abe27b.png "Stocks Menu")

Attaching the source argument to a command enables users to select their preferred source. The default sources can be changed from the [`/sources` menu](https://docs.openbb.co/terminal/guides/advanced/changing-sources). To select the `source` as `NewsApi`, use the block below.

```console
news --source NewsApi
```

### Sub-Menus

Access the sub-menus, like `Fundamental Analysis` and `Technical Analysis`, by entering the abbreviation on the left-side of the screen, beside `>`, and pressing return. Alternatively, navigation can take the form of absolute paths. This makes it possible to quickly jump between all menus, from anywhere.

[Fundamental Analysis](https://docs.openbb.co/terminal/guides/intros/stocks/fa)

```console
/stocks/fa
```

[Technical Analysis](https://docs.openbb.co/terminal/guides/intros/common/ta)

```console
/stocks/ta
```

Let's get started using the Stocks menu with some examples.

## Examples

### Load

The `load` function is a starting point for most functions, and parameters can be adjusted for intraday and resolution. It has many optional arguments which can be displayed for reference by attaching, `-h`, or, `--help`, to any function. Entering:

```console
load -h
```

Prints the dialogue on the screen:

```console
optional arguments:
  -t TICKER, --ticker TICKER
                        Stock ticker (default: None)
  -s START, --start START
                        The starting date (format YYYY-MM-DD) of the stock (default: 2020-01-09)
  -e END, --end END     The ending date (format YYYY-MM-DD) of the stock (default: 2023-01-13)
  -i {1,5,15,30,60}, --interval {1,5,15,30,60}
                        Intraday stock minutes (default: 1440)
  -p, --prepost         Pre/After market hours. Only works for 'yf' source, and intraday data (default: False)
  -f FILEPATH, --file FILEPATH
                        Path to load custom file. (default: None)
  -m, --monthly         Load monthly data (default: False)
  -w, --weekly          Load weekly data (default: False)
  -r {ytd,1y,2y,5y,6m}, --iexrange {ytd,1y,2y,5y,6m}
                        Range for using the iexcloud api. Longer range requires more tokens in account (default: ytd)
  --exchange            Show exchange information. (default: False)
  --performance         Show performance information. (default: False)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx (default: )
  --source {YahooFinance,IEXCloud,AlphaVantage,Polygon,EODHD}
                        Data source to select from (default: YahooFinance)
```

By default, a daily period, with three-years of OHLC+V data, from YahooFinance, is loaded to memory. Use the default settings like this:

```console
load SPY
```

A message will print indicating the starting date from which the data begins.

```console
Loading Daily data for SPY with starting period 2019-11-27.
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
```

This can be augmented further by adding pre/post market price candles. The `-p` flag is only applicable to YahooFinance, Polygon will automatically include the candles from 4AM-8PM US/Eastern when intraday is selected.

```console
load spy -i 1 -p
```

Data can also be exported directly from the `load` function as a CSV, JSON, or XLSX file. The file is created in the OpenBBUserData folder.

```console
load spy -s 1990-01-01 -m --export spy_monthly.csv
```

```console
Loading Daily data for SPY with starting period 1993-02-01.

Saved file: /Users/{username}/OpenBBUserData/exports/spy_monthly.csv
```

Exported files can also be loaded by declaring the `--file` argument. Place the file to import in the folder: `OpenBBUserData/custom_imports/stocks`

### Candle

The `candle` command displays a chart of the loaded symbol. It needs no arguments to display, but modifiers can enhance the content of the chart. Commands can also be sequenced together with a `/` separating each individual command.

```console
/stocks/load SPY -s 1990-01-01 -m/candle
```

![candle](https://user-images.githubusercontent.com/85772166/205693156-18328092-f423-4a9b-a3c3-47319b3d27b3.png "candle")

The help dialogue for the `candle` command shows how this chart can be supplemented with additional data; specifically, `-t` for trend, `--ma` for moving averages, and `--log` for a log scale.

```console
candle -h
```

Which prints to screen:

```console
usage: candle [-p] [--sort {adjclose,open,close,high,low,volume,returns,logret}] [-r] [--raw] [-t] [--ma MOV_AVG] [--log] [-h] [--export {csv,json,xlsx,png,jpg,pdf,svg}] [-l LIMIT]

Shows historic data for a stock

optional arguments:
  -p, --plotly          Flag to show interactive plotly chart (default: True)
  --sort {adjclose,open,close,high,low,volume,returns,logret}
                        Choose a column to sort by. Only works when raw data is displayed. (default: )
  -r, --reverse         Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. (default: False)
  --raw                 Shows raw data instead of chart. (default: False)
  -t, --trend           Flag to add high and low trends to candle (default: False)
  --ma MOV_AVG          Add moving average in number of days to plot and separate by a comma. Value for ma (moving average) keyword needs to be greater than 1. (default: None)
  --log                 Plot with y axis on log scale (default: False)
  -h, --help            show this help message (default: False)
  --export {csv,json,xlsx,png,jpg,pdf,svg}
                        Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
  -l LIMIT, --limit LIMIT
                        Number of entries to show in data. (default: 20)

For more information and examples, use 'about candle' to access the related guide.
```

Be sure to adjust the values for moving averages to correspond with the interval of the data loaded. Below adds movings averages for one and four year periods (because data loaded is monthly), and changes the y-axis to a log-scale.

```console
candle --ma 12,48 --log
```

![candle](https://user-images.githubusercontent.com/85772166/205697995-f4032ab5-143b-461b-a016-5b8e91a40374.png "candle")

The look and feel of the `candle` chart can be altered with [custom style sheets](https://matplotlib.org/stable/tutorials/introductory/customizing.html#the-default-matplotlibrc-file) placed in `OpenBBUserData/styles/user`.

### News

Get ticker-related news headlines by entering `news` after loading a ticker.

```console
news --source NewsApi
```

The output will look like:

```console
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

The `tob` function is the "Top of Book", and it returns data during market hours.

```console
tob
```

Which displays an output like:

```console
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

Get the current market price, during exchange hours.

```console
quote
```

Displays a table:

```console
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
```

Prints the output:

```console
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
search -h
```

Prints the help dialogue for the command:

```console
usage: search [-q QUERY [QUERY ...]] [-c country] [-s sector] [-i industry] [-e exchange] [-a] [-h] [--export EXPORT] [--sheet-name SHEET_NAME [SHEET_NAME ...]] [-l LIMIT]

Show companies matching the search query, country, sector, industry and/or exchange. Note that by default only the United States exchanges are searched which tend to contain the most extensive
data for each company. To search all exchanges use the --all-exchanges flag.

optional arguments:
  -q QUERY [QUERY ...], --query QUERY [QUERY ...]
                        The search term used to find company tickers (default: )
  -c country, --country country
                        Search by country to find stocks matching the criteria (default: )
  -s sector, --sector sector
                        Search by sector to find stocks matching the criteria (default: )
  -i industry, --industry industry
                        Search by industry to find stocks matching the criteria (default: )
  -e exchange, --exchange exchange
                        Search by a specific exchange country to find stocks matching the criteria (default: )
  -a, --all-exchanges   Whether to search all exchanges, without this option only the United States market is searched. (default: False)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx (default: )
  --sheet-name SHEET_NAME [SHEET_NAME ...]
                        Name of excel sheet to save data to. Only valid for .xlsx files. (default: None)
  -l LIMIT, --limit LIMIT
                        Number of entries to show in data. (default: 10)

For more information and examples, use 'about search' to access the related guide.
```

As an example, if you wish to obtain the ticker for Apple, you can do so with the following:

```
(🦋) /stocks/ $ search -q apple

                                              Companies found on term apple                                               
┏━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃      ┃ Name                                ┃ Country       ┃ Sector             ┃ Industry                  ┃ Exchange ┃
┡━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ AAPL │ Apple Inc.                          │ United States │ Technology         │ Consumer Electronics      │ NMS      │
├──────┼─────────────────────────────────────┼───────────────┼────────────────────┼───────────────────────────┼──────────┤
│ AGPL │ Apple Green Holding, Inc.           │ Canada        │ Technology         │ Software - Application    │ PNK      │
├──────┼─────────────────────────────────────┼───────────────┼────────────────────┼───────────────────────────┼──────────┤
│ APLE │ Apple Hospitality REIT, Inc.        │ United States │ Real Estate        │ REIT - Hotel & Motel      │ NYQ      │
├──────┼─────────────────────────────────────┼───────────────┼────────────────────┼───────────────────────────┼──────────┤
│ APRU │ Apple Rush Company, Inc.            │ United States │ Consumer Defensive │ Beverages - Non-Alcoholic │ PNK      │
├──────┼─────────────────────────────────────┼───────────────┼────────────────────┼───────────────────────────┼──────────┤
│ GAPJ │ Golden Apple Oil & Gas Inc.         │ United States │                    │                           │ PNK      │
├──────┼─────────────────────────────────────┼───────────────┼────────────────────┼───────────────────────────┼──────────┤
│ MLP  │ Maui Land & Pineapple Company, Inc. │ United States │ Real Estate        │ Real Estate Services      │ NYQ      │
├──────┼─────────────────────────────────────┼───────────────┼────────────────────┼───────────────────────────┼──────────┤
│ PNPL │ Pineapple, Inc.                     │ United States │ Healthcare         │ Pharmaceutical Retailers  │ PNK      │
└──────┴─────────────────────────────────────┴───────────────┴────────────────────┴───────────────────────────┴──────────┘
```

With a variety of options to also discover country-specific and sector-specific companies:

```
(🦋) /stocks/ $ search --sector technology --country united_kingdom -l 20

                                  Companies found in United Kingdom within Technology                                   
┏━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━┓
┃       ┃ Name                          ┃ Country        ┃ Sector     ┃ Industry                            ┃ Exchange ┃
┡━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━┩
│ ATC   │ Atotech Limited               │ United Kingdom │ Technology │ Electronic Components               │ NYQ      │
├───────┼───────────────────────────────┼────────────────┼────────────┼─────────────────────────────────────┼──────────┤
│ MIME  │ Mimecast Limited              │ United Kingdom │ Technology │ Software - Infrastructure           │ NMS      │
├───────┼───────────────────────────────┼────────────────┼────────────┼─────────────────────────────────────┼──────────┤
│ NNOCF │ Nanoco Group plc              │ United Kingdom │ Technology │ Semiconductor Equipment & Materials │ PNK      │
├───────┼───────────────────────────────┼────────────────┼────────────┼─────────────────────────────────────┼──────────┤
│ OXINF │ Oxford Instruments plc        │ United Kingdom │ Technology │ Semiconductor Equipment & Materials │ PNK      │
├───────┼───────────────────────────────┼────────────────┼────────────┼─────────────────────────────────────┼──────────┤
│ PSFE  │ Paysafe Limited               │ United Kingdom │ Technology │ Information Technology Services     │ NYQ      │
├───────┼───────────────────────────────┼────────────────┼────────────┼─────────────────────────────────────┼──────────┤
│ PXAMF │ Location Sciences Group PLC   │ United Kingdom │ Technology │ Software - Application              │ PNK      │
├───────┼───────────────────────────────┼────────────────┼────────────┼─────────────────────────────────────┼──────────┤
│ RNSHF │ Renishaw plc                  │ United Kingdom │ Technology │ Scientific & Technical Instruments  │ PNK      │
├───────┼───────────────────────────────┼────────────────┼────────────┼─────────────────────────────────────┼──────────┤
│ MFGP  │ Micro Focus International plc │ United Kingdom │ Technology │ Software - Infrastructure           │ NYQ      │
├───────┼───────────────────────────────┼────────────────┼────────────┼─────────────────────────────────────┼──────────┤
│ SEPJF │ Spectris plc                  │ United Kingdom │ Technology │ Scientific & Technical Instruments  │ PNK      │
├───────┼───────────────────────────────┼────────────────┼────────────┼─────────────────────────────────────┼──────────┤
│ SLLN  │ Searchlight Solutions Ltd.    │ United Kingdom │ Technology │ Information Technology Services     │ PNK      │
├───────┼───────────────────────────────┼────────────────┼────────────┼─────────────────────────────────────┼──────────┤
│ SPMYY │ Spirent Communications plc    │ United Kingdom │ Technology │ Software - Infrastructure           │ PNK      │
├───────┼───────────────────────────────┼────────────────┼────────────┼─────────────────────────────────────┼──────────┤
│ SPNUF │ Spirent Communications plc    │ United Kingdom │ Technology │ Software - Infrastructure           │ PNK      │
├───────┼───────────────────────────────┼────────────────┼────────────┼─────────────────────────────────────┼──────────┤
│ TEKCF │ Tekcapital plc                │ United Kingdom │ Technology │ Software - Application              │ PNK      │
├───────┼───────────────────────────────┼────────────────┼────────────┼─────────────────────────────────────┼──────────┤
│ TTCNF │ Telit Communications PLC      │ United Kingdom │ Technology │ Communication Equipment             │ PNK      │
├───────┼───────────────────────────────┼────────────────┼────────────┼─────────────────────────────────────┼──────────┤
│ TTGPF │ TT Electronics plc            │ United Kingdom │ Technology │ Electronic Components               │ PNK      │
├───────┼───────────────────────────────┼────────────────┼────────────┼─────────────────────────────────────┼──────────┤
│ SGPYY │ The Sage Group plc            │ United Kingdom │ Technology │ Software - Application              │ PNK      │
├───────┼───────────────────────────────┼────────────────┼────────────┼─────────────────────────────────────┼──────────┤
│ VVPR  │ VivoPower International PLC   │ United Kingdom │ Technology │ Solar                               │ NMS      │
├───────┼───────────────────────────────┼────────────────┼────────────┼─────────────────────────────────────┼──────────┤
│ MCFUF │ Micro Focus International plc │ United Kingdom │ Technology │ Software - Infrastructure           │ PNK      │
├───────┼───────────────────────────────┼────────────────┼────────────┼─────────────────────────────────────┼──────────┤
│ KNNNF │ Kainos Group plc              │ United Kingdom │ Technology │ Software - Application              │ PNK      │
├───────┼───────────────────────────────┼────────────────┼────────────┼─────────────────────────────────────┼──────────┤
│ AVEVF │ AVEVA Group plc               │ United Kingdom │ Technology │ Software - Application              │ PNK      │
└───────┴───────────────────────────────┴────────────────┴────────────┴─────────────────────────────────────┴──────────┘
```
