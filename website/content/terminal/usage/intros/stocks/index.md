---
title: Stocks
keywords: [stocks, fundamental analysis, analysis, Behavioural, strategy, comparison, due diligence, discovery, dark pool, short, data, forecasting, fundamental, quantitative, government, forecasting, ml, ai, machine learning, artificial intelligence, insider, trading, research, sector, industry, technical, trading hours, quote, market data, close, adjusted close, download, export, tools, openbb terminal]
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
usage: news [-t TICKER] [-d N_START_DATE] [-o] [-s SOURCES] [-h] [--export EXPORT] [--sheet-name SHEET_NAME [SHEET_NAME ...]] [-l LIMIT]
            [--source {Feedparser,NewsApi}]

latest news of the company

optional arguments:
  -t TICKER, --ticker TICKER
                        Ticker to get data for
  -d N_START_DATE, --date N_START_DATE
                        The starting date (format YYYY-MM-DD) to search articles from
  -o, --oldest          Show oldest articles first
  -s SOURCES, --sources SOURCES
                        Show news only from the sources specified (e.g bloomberg,reuters)
  -h, --help            show this help message
  --export EXPORT       Export raw data into csv, json, xlsx
  --sheet-name SHEET_NAME [SHEET_NAME ...]
                        Name of excel sheet to save data to. Only valid for .xlsx files.
  -l LIMIT, --limit LIMIT
                        Number of entries to show in data.
  --source {Feedparser,NewsApi}
                        Data source to select from

For more information and examples, use 'about news' to access the related guide.
```

The first step in many workflows will be to load a stock symbol with historical data. The amount, granularity, and market coverage will vary by source. Users can elect to subscribe to any of the data sources accordingly. While no API keys are required to get started using the Terminal, acquiring these credentials at the free level will enhance the user experience with additional functionality. Refer to the [API keys guide](https://docs.openbb.co/terminal/quickstart/api-keys) for links to obtain each.

<img width="800" alt="image" src="https://user-images.githubusercontent.com/46355364/218974442-563cb216-623f-4f98-b2e1-9f1bb0e1a199.png"></img>

Attaching the source argument to a command enables users to select their preferred source. The default sources can be changed from the [`/sources` menu](https://docs.openbb.co/terminal/usage/guides/changing-sources). To select the `source` as `NewsApi`, use the block below.

```console
news --source NewsApi
```

## Examples

The `load` function is a starting point for most functions, and parameters can be adjusted for intraday and resolution. It has many optional arguments which can be displayed for reference by attaching, `-h`, or, `--help`, to any function. Entering:

```console
load -h
```

Prints the dialogue on the screen:

```console
usage: load [-t TICKER] [-s START] [-e END] [-i {1,5,15,30,60}] [-p] [-f FILEPATH] [-m] [-w] [--exchange] [--performance] [-h] [--export EXPORT]
            [--sheet-name SHEET_NAME [SHEET_NAME ...]] [--source {YahooFinance,AlphaVantage,Polygon,EODHD,Intrinio}]

Load stock ticker to perform analysis on. When the data source is yf, an Indian ticker can be loaded by using '.NS' at the end, e.g. 'SBIN.NS'. See available market
in https://help.yahoo.com/kb/exchanges-data-providers-yahoo-finance-sln2310.html.

optional arguments:
  -t TICKER, --ticker TICKER
                        Stock ticker (default: None)
  -s START, --start START
                        The starting date (format YYYY-MM-DD) of the stock (default: 2020-02-11)
  -e END, --end END     The ending date (format YYYY-MM-DD) of the stock (default: 2023-02-15)
  -i {1,5,15,30,60}, --interval {1,5,15,30,60}
                        Intraday stock minutes (default: 1440)
  -p, --prepost         Pre/After market hours. Only reflected in 'YahooFinance' intraday data. (default: False)
  -f FILEPATH, --file FILEPATH
                        Path to load custom file. (default: None)
  -m, --monthly         Load monthly data (default: False)
  -w, --weekly          Load weekly data (default: False)
  --exchange            Show exchange information. (default: False)
  --performance         Show performance information. (default: False)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx (default: )
  --sheet-name SHEET_NAME [SHEET_NAME ...]
                        Name of excel sheet to save data to. Only valid for .xlsx files. (default: None)
  --source {YahooFinance,AlphaVantage,Polygon,EODHD,Intrinio}
                        Data source to select from (default: YahooFinance)

For more information and examples, use 'about load' to access the related guide.
```

By default, a daily period, with three-years of OHLC+V data, from YahooFinance, is loaded to memory. Use the default settings like this:

```console
load MSFT
```

A message will print indicating the starting date from which the data begins.

```console
Loading Daily data for MSFT with starting period 2019-11-27.
```

A simple way to get the entire history available from a source is to use an arbitrary starting date from a long time ago, like `1900-01-01`.

```console
load MSFT -s 1990-01-01
```

The console print indicates the first date of history, provided by this source, is January 29, 1993.

```console
Loading Daily data for MSFT with starting period 1993-01-29.
```

A range-bound window can also be loaded; for example, the dot-com era:

```console
load MSFT -s 1997-01-01 -e 2003-01-01
```

The interval of the data can also be set as weekly or monthly; `-w` for weekly, and `-m` for monthly candles. The data will now start on a Monday or at the beginning of a month.

```console
load MSFT -s 1997-01-01 -e 2003-01-01 -w
```

Intraday data is also requested this way, only using the `-i` or `--interval` argument. One-minute data can be loaded like this:

```console
load MSFT -i 1
```

The performance table will not be displayed with intraday data, and we can see that five-days of one-minute candles are available from YahooFinance.

```console
Loading Intraday 1min data for MSFT with starting period 2022-11-25.
```

This can be augmented further by adding pre/post market price candles. The `-p` flag is only applicable to YahooFinance, Polygon will automatically include the candles from 4AM-8PM US/Eastern when intraday is selected.

```console
load MSFT -i 1 -p
```

Data can also be exported directly from the `load` function as a CSV, JSON, or XLSX file. The file is created in the OpenBBUserData folder.

```console
load MSFT -s 1990-01-01 -m --export msft_monthly.csv
```

```console
Loading Daily data for MSFT with starting period 1993-02-01.

Saved file: /Users/{username}/OpenBBUserData/exports/msft_monthly.csv
```

Exported files can also be loaded by declaring the `--file` argument. Place the file to import in the folder: `OpenBBUserData/custom_imports/stocks`

### Candle

The `candle` command displays a chart of the loaded symbol. It needs no arguments to display, but modifiers can enhance the content of the chart. Commands can also be sequenced together with a `/` separating each individual command.

```console
(🦋) /stocks/ $ load MSFT

cLoading Daily data for MSFT with starting period 2020-02-11.

(🦋) /stocks/ $ candle
```

![candle](https://user-images.githubusercontent.com/46355364/218981911-90d38930-a621-43cc-873a-1c55db842e95.png)

The help dialogue for the `candle` command shows how this chart can be supplemented with additional data; specifically, `-t` for trend, `--ma` for moving averages, and `--log` for a log scale.

```console
candle -h
```

Which prints to screen:

```console
usage: candle [-t TICKER] [-p] [--sort {adjclose,open,close,high,low,volume,returns,logret}] [-r] [--raw] [--trend] [--ma MOV_AVG] [--log] [-h] [--export EXPORT] [--sheet-name SHEET_NAME [SHEET_NAME ...]] [-l LIMIT]

Shows historic data for a stock

optional arguments:
  -t TICKER, --ticker TICKER
                        Ticker to analyze (default: None)
  -p, --plotly          Flag to show interactive plotly chart (default: True)
  --sort {adjclose,open,close,high,low,volume,returns,logret}
                        Choose a column to sort by. Only works when raw data is displayed. (default: )
  -r, --reverse         Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed.
                        (default: False)
  --raw                 Shows raw data instead of chart. (default: False)
  --trend               Flag to add high and low trends to candle (default: False)
  --ma MOV_AVG          Add moving average in number of days to plot and separate by a comma. Value for ma (moving average) keyword needs to be greater than 1.
                        (default: None)
  --log                 Plot with y axis on log scale (default: False)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
  --sheet-name SHEET_NAME [SHEET_NAME ...]
                        Name of excel sheet to save data to. Only valid for .xlsx files. (default: None)
  -l LIMIT, --limit LIMIT
                        Number of entries to show in data. (default: 20)

For more information and examples, use 'about candle' to access the related guide.
```

Be sure to adjust the values for moving averages to correspond with the interval of the data loaded. Below adds movings averages for one and four year periods (because data loaded is monthly), and changes the y-axis to a log-scale.

```console
candle --ma 20,30 --log
```

![candle moving average log](https://user-images.githubusercontent.com/46355364/218982220-411e780a-aa8d-436e-b2db-3c95a981b6eb.png)

Get ticker-related news headlines by entering `news` after loading a ticker.

```console
news --source NewsApi
```

The output will look like:

```console
(🦋) /stocks/ $ news --source NewsApi

346 news articles for Tesla,+Inc. were found since 2023-02-08

                                         Elon Musk says he may lead Twitter for almost another year
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Content                                                                                                                                   ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 2023-02-15 07:57:55                                                                                                                       │
├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ The billionaire executive embarked on a search for a new CEO for Twitter in December, a person familiar with the search said at the time. │
├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ https://www.moneycontrol.com/news/world/elon-musk-says-he-may-lead-twitter-for-almost-another-year-10088481.html                          │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                                                   Elon Musk Gave $1.9 Billion of Tesla Shares to Charity Last Year
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Content                                                                                                                                                            ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 2023-02-15 06:46:08                                                                                                                                                │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Tesla CEO Elon Musk now owns around 13% of the company. Elon Musk donated roughly $1.9 billion of Tesla Inc. stock to charity last year, according to a regulatory │
│ filing made Tuesday. Mr. Musk, Tesla’s chief executive, reported having donated roughly 11.6 mil…                                                                  │
├────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ https://biztoc.com/x/99aa746544171bae                                                                                                                              │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
                           Elon Musk Aims to Find Twitter CEO Successor Toward End of 2023
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Content                                                                                                           ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ 2023-02-15 06:14:49                                                                                               │
├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ Elon Musk is aiming to find his successor to lead Twitter Inc. as chief executive officer toward the end of 2023. │
├───────────────────────────────────────────────────────────────────────────────────────────────────────────────────┤
│ https://www.bloomberg.com/news/articles/2023-02-15/musk-aims-to-replace-himself-as-twitter-ceo-toward-end-of-2023 │
└───────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

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

Get the current market price, during exchange hours.

```console
quote
```

Displays a table:

```console
(🦋) /stocks/ $ quote

                  TSLA Quote
┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃                       ┃                     ┃
┡━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ Symbol                │ TSLA                │
├───────────────────────┼─────────────────────┤
│ Name                  │ Tesla, Inc.         │
├───────────────────────┼─────────────────────┤
│ Price                 │ 209.25              │
├───────────────────────┼─────────────────────┤
│ Changes percentage    │ 7.51                │
├───────────────────────┼─────────────────────┤
│ Change                │ 14.61               │
├───────────────────────┼─────────────────────┤
│ Day low               │ 189.45              │
├───────────────────────┼─────────────────────┤
│ Day high              │ 209.82              │
├───────────────────────┼─────────────────────┤
│ Year high             │ 384.29              │
├───────────────────────┼─────────────────────┤
│ Year low              │ 101.81              │
├───────────────────────┼─────────────────────┤
│ Market cap            │ 662.088 B           │
├───────────────────────┼─────────────────────┤
│ Price avg50           │ 152.95              │
├───────────────────────┼─────────────────────┤
│ Price avg200          │ 225.47              │
├───────────────────────┼─────────────────────┤
│ Exchange              │ NASDAQ              │
├───────────────────────┼─────────────────────┤
│ Volume                │ 214.769 M           │
├───────────────────────┼─────────────────────┤
│ Avg volume            │ 156755621           │
├───────────────────────┼─────────────────────┤
│ Open                  │ 191.94              │
├───────────────────────┼─────────────────────┤
│ Previous close        │ 194.64              │
├───────────────────────┼─────────────────────┤
│ Eps                   │ 3.44                │
├───────────────────────┼─────────────────────┤
│ Pe                    │ 60.83               │
├───────────────────────┼─────────────────────┤
│ Earnings announcement │ 2023-04-18 10:59:00 │
├───────────────────────┼─────────────────────┤
│ Shares outstanding    │ 3.164 B             │
├───────────────────────┼─────────────────────┤
│ Timestamp             │ 1676408405          │
└───────────────────────┴─────────────────────┘
```

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

The `search` function provides a way to find stocks by name, region, sector, industry and exchange location. The results can be easily exported as a CSV, JSON, or XLSX file.

```console
search -h
```

Prints the help dialogue for the command:

```console
usage: search [-q QUERY [QUERY ...]] [-c country] [-s sector] [-i industry] [-e exchange] [-a] [-h] [--export EXPORT] [--sheet-name SHEET_NAME [SHEET_NAME ...]] [-l LIMIT]

Show companies matching the search query, country, sector, industry and/or exchange. Note that by default only the United States exchanges are searched which tend
to contain the most extensive data for each company. To search all exchanges use the --all-exchanges flag.

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
