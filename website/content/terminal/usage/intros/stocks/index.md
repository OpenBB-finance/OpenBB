---
title: Stocks
keywords: [stocks, fundamental analysis, analysis, Behavioural, strategy, comparison, due diligence, discovery, dark pool, short, data, forecasting, fundamental, quantitative, government, forecasting, ml, ai, machine learning, artificial intelligence, insider, trading, research, sector, industry, technical, trading hours, quote, market data, close, adjusted close, download, export, tools, openbb terminal, how to, example]
description: Introduction to the Stocks menu. It is the high-level menu for the Public Equity asset class. It contains functions for searching and loading company market data, showing candle charts, quotes and company specifics via a large selection of sub-menus.
---
The Stocks menu is the high-level menu for the Public Equity asset class. It contains functions for searching and loading company market data, showing candle charts, quotes and company specifics via a large selection of sub-menus. The sub-menus break the functions down into groups based on the type of data they return. The items in the stocks menu are listed below with a short description. Refer to each sub-menu's introductory guide for a more detailed explanation of the functions within.

## Menu Contents

| Command  | Type     |                     Name |                                                                  Description |
| :------- | -------- | -----------------------: | ---------------------------------------------------------------------------: |
| ba       | Sub-Menu |     Behavioural Analysis |                                              Social Media, Sentiment, Trends |
| bt       | Sub-Menu |      Strategy Backtester |                                   Simple EMA, EMA Crossover & RSI Strategies |
| ca       | Sub-Menu |      Comparison Analysis |                          Compare Historical Prices, Correlations, Financials |
| candle   | Function |                   Candle |                                         Candlestick Chart of the Loaded Data |
| codes    | Function |                    Codes |                                   Cross-Reference FIGI, CIK, and SIC Numbers |
| disc     | Sub-Menu |                Discovery |            Upcoming Earnings and Dividends Calendar, Heatmaps, Trending News |
| dps      | Sub-Menu | Dark Pool and Short Data |                      Short Interest, Borrow Rates, Off-Exchange Short Volume |
| fa       | Sub-Menu |     Fundamental Analysis |     Financial Statements, Company Overviews, Analyst Coverage, Price Targets |
| forecast | Sub-Menu |       Forecasting and ML |                               Enter the Forecast Menu With the Loaded Ticker |
| gov      | Sub-Menu |               Government | House and Senate Trading Disclosures, Lobbying Efforts, US Treasury Spending |
| ins      | Sub-Menu |          Insider Trading |                                            SEC Form 4 Disclosures & Screener |
| load     | Function |                     Load |                                                         Load a Ticker Symbol |
| news     | Function |                     News |                                               Ticker-Specific News Headlines |
| options  | Sub-Menu |           Equity Options |               Options Analysis, Quotes, Historical Prices, Greeks & Screener |
| qa       | Sub-Menu |    Quantitative Analysis |                                                        Mathematical Analysis |
| quote    | Function |                    Quote |                            Current Price and Performance Data for the Ticker |
| res      | Sub-Menu |        Research Websites |                          Shortcuts to Online Resources for the Loaded Ticker |
| scr      | Sub-Menu |          Stocks Screener |                                                       Custom Stocks Screener |
| search   | Function |            Stocks Search |                                                    Find a company and ticker |
| ta       | Sub-Menu |       Technical Analysis |                                              Technical Indicators and Charts |
| th       | Sub-Menu |            Trading Hours |                                    Lists of World Markets and Current Status |
| tob      | Function |              Top of Book |                Top of Book Bid/Ask from CBOE (US-only when markets are open) |

## How to Use

Navigate to the menu by entering, `stocks`, from the Main Menu. From another menu, `/stocks`, will jump directly there.

The current screen can always be re-printed with any of: `?`, `h`, `help`. The help dialogue, containing all parameters for each function, is printed when `-h` is attached to any command. The help dialogue will also provide the list of sources available to each command, the `news` function is shown below.

```console
news -h
```

Which prints the reference information on the screen:

```console
usage: news [-t TICKER] [-d N_START_DATE] [-o] [-s SOURCES] [-h] [--export EXPORT] [--sheet-name SHEET_NAME [SHEET_NAME ...]] [-l LIMIT] [--source {Feedparser,NewsApi,Ultima}]

latest news of the company

options:
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
  --source {Feedparser,NewsApi,Ultima}
                        Data source to select from

For more information and examples, use 'about news' to access the related guide.
```

Attaching the source argument to a command selects a source other than the default, which can also be set permanently from the [`/sources` menu](https://docs.openbb.co/terminal/usage/guides/changing-sources). To select the `source` as `Ultima`, use the syntax below.

```console
news -t WMT --source Ultima

------------------------
> 2023-04-10 15:44:56 - The Federal Trade Commission and Justice Department should stop the acquisition of Albertsons by Kroger. The usual false claims are being made such as...

Relevancy score: 4.87/5 Stars

Competition Risk (Walmart Inc. faces competition risk due to the presence of other large retailers in the market, as well as physical, eCommerce and omni-channel retailers, social commerce platforms, wholesale club operators and retail intermediaries. 
These competitors have the ability to leverage their economies of scale to offer lower prices than Walmart, which can put pressure on Walmart’s margins. 
Additionally, these competitors have the ability to quickly respond to changes in the market, which can put Walmart at a disadvantage.
Furthermore, Walmart is subject to laws and regulations related to competition and antitrust matters, which could require extensive system and operational changes, increase operating costs, and require significant capital expenditures.)

Read more: https://www.cincinnati.com/story/opinion/letters/2023/04/10/letters-kroger-acquiring-albertsons-will-reduce-competition-not-prices/70080423007/
```

The first step in many workflows will be to load a stock symbol with historical data. The amount, granularity, and market coverage will vary by source. Users can elect to subscribe to any of the data sources accordingly. While no API keys are required to get started using the Terminal, acquiring these credentials at the free level significantly enhances the user experience with additional functionality and available data. Refer to the [API keys guide](https://docs.openbb.co/terminal/usage/guides/api-keys) for links to obtain each.

## Examples

### Load

The `load` function is a starting point for most functions, and parameters can be adjusted for intraday and resolution. It has many optional arguments which can be displayed for reference by attaching, `-h`, or, `--help`, to any function. Entering:

```console
load -h
```

Reveals the choices:

```console
usage: load [-t TICKER] [-s START] [-e END] [-i {1,5,15,30,60}] [-p] [-f FILEPATH] [-m] [-w] [--exchange] [--performance] [-h] [--export EXPORT]
            [--sheet-name SHEET_NAME [SHEET_NAME ...]] [--source {YahooFinance,AlphaVantage,Polygon,EODHD,Intrinio}]

optional arguments:
  -t TICKER, --ticker TICKER
                        Stock ticker (default: None)
  -s START, --start START
                        The starting date (format YYYY-MM-DD) of the stock (default: 2020-02-11)
  -e END, --end END     The ending date (format YYYY-MM-DD) of the stock (default: 2023-02-15)
  -i {1,5,15,30,60}, --interval {1,5,15,30,60}
                        Intraday stock minutes (default: 1440)
  -p, --prepost         Pre/After market hours. Only reflected in intraday data. (default: False)
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
  --source {YahooFinance,AlphaVantage,Polygon,EODHD,Intrinio,DataBento}
                        Data source to select from (default: YahooFinance)


```

By default, a daily period of OHLC+V data over three years, from YahooFinance, is loaded to memory. Use the default settings like this:

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

From YahooFinance, five days of one-minute data is available.  The amount of historical price data will vary by source.

```console
Loading Intraday 1min data for MSFT with starting period 2022-11-25.
```

This can be augmented further by adding pre/post market price candles.

```console
load MSFT -i 1 -p
```

Data can also be exported, as a CSV, JSON, or XLSX file, directly from the `load` function. The file is created in the OpenBBUserData folder.

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

Loading Daily data for MSFT with starting period 2020-04-08.

(🦋) /stocks/ $ candle
```

![stocks/candle](https://user-images.githubusercontent.com/85772166/231903835-a0157626-1329-4d5a-80a1-8d21b71adcb1.png)

The help dialogue for the `candle` command shows how this chart can be supplemented with additional data; specifically, `-t` for trend, `--ma` for moving averages, `--log` for a log scale, and `--ha` to convert the candles to a Heikin Ashi pattern.

```console
candle -h
```

Which prints to screen:

```console
usage: candle [-t TICKER] [-p] [--sort {open,high,low,close,adjclose,volume,dividends,stock_splits}] [-r] [--raw] [--trend] [--ma MOV_AVG] [--ha] [--log] [-h] [--export EXPORT]
              [--sheet-name SHEET_NAME [SHEET_NAME ...]] [-l LIMIT]

Shows historic price and volume for the asset.

options:
  -t TICKER, --ticker TICKER
                        Ticker to analyze. (default: None)
  -p, --prepost         Pre/After market hours. Only works for intraday data. (default: False)
  --sort {open,high,low,close,adjclose,volume,dividends,stock_splits}
                        Choose a column to sort by. Only works when raw data is displayed. (default: )
  -r, --reverse         Data is sorted in descending order by default. Reverse flag will sort it in an ascending way. Only works when raw data is displayed. (default: False)
  --raw                 Shows raw data instead of a chart. (default: False)
  --trend               Flag to add high and low trends to candle. (default: False)
  --ma MOV_AVG          Add moving average in number of days to plot and separate by a comma. Value for ma (moving average) keyword needs to be greater than 1. (default: None)
  --ha                  Flag to show Heikin Ashi candles. (default: False)
  --log                 Plot with y axis on log scale (default: False)
  -h, --help            show this help message (default: False)
  --export EXPORT       Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg (default: )
  --sheet-name SHEET_NAME [SHEET_NAME ...]
                        Name of excel sheet to save data to. Only valid for .xlsx files. (default: None)
  -l LIMIT, --limit LIMIT
                        Number of entries to show in data. (default: 20)

For more information and examples, use 'about candle' to access the related guide.
```

Be sure to adjust the values for moving averages to correspond with the interval of the data loaded. Below adds movings averages for three and twelve month periods (because data loaded is monthly), and changes the y-axis to a log-scale.

```console
load msft --start 1980-01-01 --monthly
candle --ma 3,12 --log
```

![candle moving average log](https://user-images.githubusercontent.com/85772166/231904022-7da40eae-2389-4dfa-a619-f950fa8f2929.png)

### News

Get ticker-related news headlines by entering `news` after loading a ticker.

```console
news --source NewsApi
```

![stocks/news](https://user-images.githubusercontent.com/85772166/231904057-235b93e2-12e6-45db-a4eb-f6c7c93e02ff.png)

### TOB

The `tob` function is the "Top of Book", and it returns data during market hours.

```console
tob
```

![stocks/tob](https://user-images.githubusercontent.com/85772166/231904101-0df25e0e-631c-4a58-a449-e851df6fd4d8.png)

### Quote

Get the current market price and general performance metrics of the loaded ticker.

```console
quote
```

![stocks/quote](https://user-images.githubusercontent.com/85772166/231904179-1908801d-ac8d-4bc2-aa08-e93507df1630.png)

### Codes

`codes` prints the CIK, Composite FIGI, Share Class FIGI, and SIC codes - when available - for a US-listed stock. This function requires a free API key from Polygon.

```console
codes
```

![stocks/codes](https://user-images.githubusercontent.com/85772166/231904217-b477d719-389c-4678-ac04-266641ec7652.png)

### Search

The `search` function provides a way to find stocks by name, region, sector, industry and exchange location. The results can be exported as a CSV, JSON, or XLSX file from the command line or within the table.

Return all Canadian banks with US listings with:

```console
search --country canada --industrygroup banks
```

![stocks/search](https://user-images.githubusercontent.com/85772166/231904274-cc3ba608-280a-47f7-834a-98ba2f3de6c3.png)
