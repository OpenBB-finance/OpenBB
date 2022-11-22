---
title: Stocks
---

The capabilities of the Stocks menu from the OpenBB Terminal are wrapped into a powerful SDK, enabling users to work with the data in a flexible environment that can be fully customized to meet the needs of any user. Code completion and contextual help makes it easy to use. Navigating is very similar to operating the CLI Terminal Application.

## How to use

The list below are the SDK functions within the Stocks module and a short description:

| Path                   |    Type    |                                       Description |
| :--------------------- | :--------: | ------------------------------------------------: |
| openbb.stocks.ba       | Sub-Module |                              Behavioural Analysis |
| openbb.stocks.ca       | Sub-Module |                               Comparison Analysis |
| openbb.stocks.candle   |  Function  |             OHLC + Volume + Moving Averages Chart |
| openbb.stocks.dd       | Sub-Module |                                     Due Diligence |
| openbb.stocks.disc     | Sub-Module |                                   Stock Discovery |
| openbb.stocks.dps      | Sub-Module |                               Dark Pools & Shorts |
| openbb.stocks.fa       | Sub-Module |                              Fundamental Analysis |
| openbb.stocks.gov      | Sub-Module | US Government, Lobbying & Representative Activity |
| openbb.stocks.ins      | Sub-Module |           Corporate Insider Activity (SEC Form 4) |
| openbb.stocks.load     |  Function  |                                         Load Data |
| openbb.stocks.options  | Sub-Module |                                           Options |
| openbb.stocks.qa       | Sub-Module |                 Stocks-Only Quantitative Analysis |
| openbb.stocks.quote    |  Function  |                             Last Price (yFinance) |
| openbb.stocks.screener | Sub-Module |                                    Stock Screener |
| openbb.stocks.search   |  Function  |                                       Find Stocks |
| openbb.stocks.sia      | Sub-Module |                        Sector & Industry Analysis |
| openbb.stocks.ta       | Sub-Module |                    Stocks-Only Technical Analysis |
| openbb.stocks.th       | Sub-Module |                     Trading Hours (Market Status) |
| openbb.stocks.tob      |  Function  |                                Top of Book (CBOE) |

Alternatively, contents of the menu is printed by running:

```python
help(openbb.stocks)
```

Most items in `openbb.stocks` are sub-modules. The objective of this guide is to introduce the functions at the top-level and to demonstrate a selection of functions from the sub-modules.

## Examples

The code snippets in the following section will assume that the import block contains:

```python
import pandas as pd
from datetime import datetime
from openbb_terminal.sdk import openbb
%matplotlib inline
```

### Load

The first step in a workflow might be to collect historical price data. The `load` function has the ability to request data from multiple sources. The choices for `source` are currently:

- YahooFinance (default)
- IEXCloud
- AlphaVantage
- Polygon
- EODHD

```python
spy_monthly = openbb.stocks.load(
    symbol = 'SPY',
    start_date = '1990-01-01',
    end_date = '',
    interval = 1440,
    prepost = False,
    source = 'YahooFinance',
    weekly = False,
    monthly = True,
)
spy_monthly.head(3)
```

| date                |    Open |    High |     Low |   Close | Adj Close |     Volume |
| :------------------ | ------: | ------: | ------: | ------: | --------: | ---------: |
| 1993-02-01 00:00:00 | 43.9688 |  45.125 | 42.8125 | 44.4062 |   25.6043 | 5.4176e+06 |
| 1993-03-01 00:00:00 | 44.5625 | 45.8438 | 44.2188 | 45.1875 |   26.0548 | 3.0192e+06 |
| 1993-04-01 00:00:00 |   45.25 |   45.25 | 43.2812 | 44.0312 |    25.508 | 2.6972e+06 |

There are source-dependent differences to the DataFrame returned. For example, compare the above with below:

```python
spy_monthly = openbb.stocks.load(
    symbol = 'SPY',
    start_date = '1990-01-01',
    end_date = '',
    interval = 1440,
    prepost = False,
    source = 'Polygon',
    weekly = False,
    monthly = True,
)
spy_monthly.head(3)
```

| date                |      Volume |      vw |   Open | Adj Close |   High |    Low | Transactions |  Close |
| :------------------ | ----------: | ------: | -----: | --------: | -----: | -----: | -----------: | -----: |
| 2022-09-01 04:00:00 | 1.99492e+09 | 382.507 | 392.89 |    357.18 | 411.73 | 357.04 |  1.35653e+07 | 357.18 |
| 2022-10-01 04:00:00 | 2.02389e+09 | 370.918 | 361.08 |    386.21 | 389.52 | 348.11 |  1.38047e+07 | 386.21 |
| 2022-11-01 04:00:00 | 1.17559e+09 | 386.119 | 390.14 |    394.28 | 402.31 | 368.79 |  8.34067e+06 | 394.28 |

### Candle

OHLC DataFrames can be passed through the `Candle` function to display a chart.

```python
openbb.stocks.candle(data = spy_monthly, symbol = 'SPY - Monthly Candles')
```

![openbb.stocks.candle](https://user-images.githubusercontent.com/85772166/201727311-e42f5ec3-bfdd-4d5d-ae4d-7e113f4b455d.png "openbb.stocks.candle")

The `candle` function is also aware if a ticker is being passed. This makes it unnecessary to create a DataFrame if the objective is only to display the chart.

```python
openbb.stocks.candle('SPY')
```

![openbb.stocks.candle](https://user-images.githubusercontent.com/85772166/202576993-08bfb90c-2254-423e-b599-8c86a1ea1e12.png "openbb.stocks.candle")

Add moving averages to the chart with:

```python
openbb.stocks.candle('SPY', ma = [50,150])
```

![openbb.stocks.candle](https://user-images.githubusercontent.com/85772166/202576848-27e86f9a-e9bd-49b4-9008-2ad374e07abb.png "openbb.stocks.candle")

### Search

Search for companies by name with the `search` function, with optional filters for sector, industry, and region:

```python
openbb.stocks.search(sector = 'Energy', country = 'United Kingdom', query = 'oil')
```

|     |        | long_name                       | country        | sector | industry      | exchange |
| --: | :----- | :------------------------------ | :------------- | :----- | :------------ | -------: |
|   0 | 3NO.F  | Nostrum Oil & Gas PLC           | United Kingdom | Energy | Oil & Gas E&P |      nan |
|   1 | BOIL.L | Baron Oil Plc                   | United Kingdom | Energy | Oil & Gas E&P |      nan |
|   2 | EGN.F  | Europa Oil & Gas (Holdings) plc | United Kingdom | Energy | Oil & Gas E&P |      nan |
|   3 | EOG.L  | Europa Oil & Gas (Holdings) plc | United Kingdom | Energy | Oil & Gas E&P |      nan |
|   4 | GHA.F  | Baron Oil Plc                   | United Kingdom | Energy | Oil & Gas E&P |      nan |

...continued

### Quote

Watchlists are easy to make. Get the last price and performance data for multiple tickers by looping the `quote` function:

```python
spdr_sectors = ['SPY', 'XLE', 'XLB', 'XLI', 'XLP', 'XLY', 'XLV', 'XLF', 'XLK', 'XLC', 'XLU', 'XLRE']

quotes: object = []
symbols = spdr_sectors
for symbols in spdr_sectors:
    quote = openbb.stocks.quote(symbols).transpose()
    quotes.append(quote)

quotes = pd.concat(quotes)

quotes
```

| Symbol | Name                            |  Price |   Open |   High |    Low | Previous Close | Volume     | 52 Week High | 52 Week Low | Change | Change % |
| :----- | :------------------------------ | -----: | -----: | -----: | -----: | -------------: | :--------- | -----------: | ----------: | -----: | :------- |
| SPY    | SPDR S&P 500                    | 399.62 | 396.66 | 400.18 | 395.92 |         398.51 | 42,786,020 |       479.98 |      348.11 |   1.11 | 0.28%    |
| XLE    | SPDR Select Sector Fund - Energ |     94 |  92.86 |   94.7 |  92.86 |          93.13 | 14,593,450 |         94.7 |       51.66 |   0.87 | 0.93%    |
| XLB    | Materials Select Sector SPDR    |  81.97 |  80.98 |  82.25 |   80.9 |          81.25 | 4,544,573  |        92.31 |       66.85 |   0.72 | 0.89%    |
| XLI    | SPDR Select Sector Fund - Indus | 100.07 |  99.24 | 100.26 |  99.16 |          99.53 | 6,186,242  |       107.88 |       82.75 |   0.54 | 0.54%    |
| XLP    | SPDR Select Sector Fund - Consu |  73.81 |  73.45 |  74.11 |  73.48 |          73.52 | 9,557,986  |        81.34 |       66.18 |   0.29 | 0.39%    |
| XLY    | SPDR Select Sector Fund - Consu | 144.43 | 143.83 | 145.08 | 142.68 |         145.09 | 3,614,077  |       215.06 |       131.9 |  -0.66 | -0.45%   |
| XLV    | SPDR Select Sector Fund - Healt | 134.67 | 133.53 | 134.84 | 133.53 |         133.13 | 7,913,382  |       143.42 |      118.75 |   1.54 | 1.16%    |
| XLF    | SPDR Select Sector Fund - Finan |  35.67 |  35.77 |   35.8 |  35.54 |          35.87 | 22,587,218 |         41.7 |       29.59 |   -0.2 | -0.56%   |
| XLK    | SPDR Select Sector Fund - Techn | 133.42 | 132.09 | 133.65 | 131.37 |         133.14 | 4,010,764  |       177.04 |      112.97 |   0.28 | 0.21%    |
| XLC    | The Communication Services Sele |  50.44 |  49.66 |  50.56 |  49.62 |          50.02 | 3,220,128  |        81.91 |       44.86 |   0.41 | 0.83%    |
| XLU    | SPDR Select Sector Fund - Utili |  67.91 |  68.12 |  68.49 |  67.75 |          68.08 | 6,871,930  |        78.22 |       60.35 |  -0.17 | -0.25%   |
| XLRE   | Real Estate Select Sector SPDR  |  38.09 |  38.52 |  38.55 |  38.03 |          38.74 | 4,769,207  |        52.17 |       33.12 |  -0.65 | -1.68%   |

### TOB

Top of Book gets the size and price at the top of the order book.

```python
bid,ask = openbb.stocks.tob('SPY')
quote_tob = bid.join(ask, lsuffix= ': Bid', rsuffix = ': Ask')

quote_tob
```

|     | Size: Bid | Price: Bid | Size: Ask | Price: Ask |
| --: | --------: | ---------: | --------: | ---------: |
|   0 |       100 |     394.85 |       100 |        395 |
|   1 |       100 |      394.8 |       300 |     395.05 |
|   2 |       100 |      394.7 |       100 |     395.07 |
|   3 |       100 |     394.68 |       200 |     395.25 |
|   4 |       100 |     394.65 |       100 |     395.29 |

### Upcoming Earnings

The upcoming earnings calendar is part of the `Discovery` sub-module. The results can be easily filtered to use as inputs for another function.

```python
earnings = openbb.stocks.disc.upcoming()
earnings.index = earnings.index.strftime('%Y-%m-%d')
earnings_today = earnings.filter(like = datetime.now().strftime('%Y-%m-%d'), axis = 0)

earnings_today.head(5)
```

| Date       | Ticker | Name                       |
| :--------- | :----- | :------------------------- |
| 2022-11-17 | DXLG   | Destination XL Group, Inc. |
| 2022-11-17 | CAMT   | Camtek Ltd.                |
| 2022-11-17 | CLBT   | Cellebrite DI Ltd.         |
| 2022-11-17 | HAYN   | Haynes International, Inc. |
| 2022-11-17 | ROST   | Ross Stores, Inc.          |

...continued

### Screener

Grab the list of filtered tickers and put them through the comparison analysis screener for valuation data:

```python
earnings_tickers = earnings_today['Ticker'].to_list()
screener_results = openbb.stocks.ca.screener(similar = earnings_tickers, data_type = 'valuation')
screener_results.sort_values(by = ['EPS next Y'], ascending = False, inplace = True)

screener_results.head(5)
```

|     | Ticker | Market Cap |   P/E | Fwd P/E |  PEG |  P/S |   P/B |   P/C | P/FCF | EPS this Y | EPS next Y | EPS past 5Y | EPS next 5Y | Sales past 5Y | Price |  Change |      Volume |
| --: | :----- | ---------: | ----: | ------: | ---: | ---: | ----: | ----: | ----: | ---------: | ---------: | ----------: | ----------: | ------------: | ----: | ------: | ----------: |
|   2 | CLBT   | 8.8396e+08 |  6.18 |   31.91 | 1.21 | 3.42 | 37.31 |  8.22 |   nan |     -0.708 |     1.1111 |         nan |       0.051 |           nan |  4.85 | -0.0122 |      105214 |
|   6 | GAMB   | 3.4528e+08 | 34.84 |   18.92 |  nan | 6.18 |  4.02 |  11.1 | 37.53 |     -0.177 |       1.04 |         nan |         nan |           nan |  9.65 |  0.0354 |       34618 |
|  13 | STNE   |   2.85e+09 |   nan |    3.57 |  nan | 1.69 |  1.31 |  2.43 |  5.05 |     -2.513 |     0.9624 |      -0.598 |      0.2815 |         0.694 |  9.87 | -0.0573 | 9.54896e+06 |
|   0 | AMSWA  |  5.415e+08 | 46.52 |    32.4 | 2.91 | 4.18 |  4.12 |  4.71 | 71.25 |      0.527 |     0.4318 |       -0.04 |        0.16 |         0.037 | 16.33 | -0.0337 |      126062 |
|  14 | WWD    |    5.9e+09 | 37.68 |   27.41 | 3.66 | 2.55 |  3.11 | 59.37 | 43.51 |      -0.15 |     0.3407 |       0.023 |       0.103 |         0.021 | 98.04 |  0.0007 |      455047 |

...continued

Along with the variety of screeners, the OpenBB SDK can create custom screeners. For example, the most popular tickers on Stocktwits:

```python
stocktwits = openbb.stocks.ba.trending()
stocktwits = pd.DataFrame(stocktwits).sort_values(by = 'Watchlist Count', ascending = False)
tickers = stocktwits['Ticker'].to_list()
stocktwits.head(10)
```

|     | Ticker | Watchlist Count | Name                           |
| --: | :----- | --------------: | :----------------------------- |
|  18 | NVDA   |          409301 | NVIDIA Corp                    |
|  12 | AMC    |          406952 | AMC Entertainment Holdings Inc |
|   5 | WMT    |          109864 | Walmart Inc                    |
|   6 | MRNA   |          100705 | Moderna Inc                    |
|  21 | PFE    |           87229 | Pfizer Inc.                    |
|   4 | DWAC   |           66122 | Digital World Acquisition Corp |
|  29 | CSCO   |           54458 | Cisco Systems, Inc.            |
|   0 | SAVA   |           49063 | Cassava Sciences Inc           |
|   8 | TDOC   |           38657 | Teladoc Health Inc             |
|  16 | PENN   |           38277 | Penn National Gaming, Inc.     |

Filter the results by market cap:

```python
screener_results = openbb.stocks.ca.screener(similar = tickers, data_type = 'overview')
screener_results = screener_results.sort_values(by = ['Market Cap'], ascending = False)

screener_results.head(5)
```

|     | Ticker | Company            | Sector             | Industry                     | Country | Market Cap |   P/E |  Price |  Change |      Volume |
| --: | :----- | :----------------- | :----------------- | :--------------------------- | :------ | ---------: | ----: | -----: | ------: | ----------: |
|  15 | NVDA   | NVIDIA Corporation | Technology         | Semiconductors               | USA     | 3.9217e+11 | 53.53 | 163.66 |  0.0024 | 3.16641e+07 |
|  26 | WMT    | Walmart Inc.       | Consumer Defensive | Discount Stores              | USA     |  3.864e+11 | 28.46 |  140.5 | -0.0146 | 5.33372e+06 |
|  18 | PFE    | Pfizer Inc.        | Healthcare         | Drug Manufacturers - General | USA     | 2.6591e+11 |  9.03 |  49.36 |   0.037 | 1.07892e+07 |
|   4 | BLK    | BlackRock, Inc.    | Financial          | Asset Management             | USA     | 1.1412e+11 | 21.34 | 747.95 | -0.0346 |      742602 |
|  25 | TGT    | Target Corporation | Consumer Defensive | Discount Stores              | USA     |  7.566e+10 | 19.68 | 175.67 |  0.0136 | 2.45293e+06 |

...continued

### SEC

Get the links for SEC filings belonging to a company:

```python
openbb.stocks.dd.sec(symbol = 'WMT')
```

| Filing Date | Document Date | Type     | Category          | Amended | Link                                                                                 |
| :---------- | :------------ | :------- | :---------------- | :------ | :----------------------------------------------------------------------------------- |
| 09/09/2022  | 09/06/2022    | 8-K      | Special Events    |         | https://www.marketwatch.com/investing/stock/wmt/financials/secfilings?docid=16074059 |
| 09/02/2022  | 07/31/2022    | 10-Q     | Quarterly Reports |         | https://www.marketwatch.com/investing/stock/wmt/financials/secfilings?docid=16064659 |
| 08/17/2022  | 08/17/2022    | 8-K      | Special Events    |         | https://www.marketwatch.com/investing/stock/wmt/financials/secfilings?docid=16026629 |
| 08/17/2022  | 08/17/2022    | 8-K      | Special Events    |         | https://www.marketwatch.com/investing/stock/wmt/financials/secfilings?docid=16025172 |
| 08/16/2022  | 08/16/2022    | 8-K      | Special Events    |         | https://www.marketwatch.com/investing/stock/wmt/financials/secfilings?docid=16021891 |
| 07/25/2022  | 07/25/2022    | 8-K      | Special Events    |         | https://www.marketwatch.com/investing/stock/wmt/financials/secfilings?docid=15964414 |
| 07/21/2022  | N/A           | SC 13D/A | N/A               | \*      | https://www.marketwatch.com/investing/stock/wmt/financials/secfilings?docid=15959675 |
| 06/28/2022  | 06/28/2022    | 8-K      | Special Events    |         | https://www.marketwatch.com/investing/stock/wmt/financials/secfilings?docid=15918852 |
| 06/21/2022  | N/A           | SC 13D   | N/A               |         | https://www.marketwatch.com/investing/stock/wmt/financials/secfilings?docid=15900809 |

...continued

### Insiders Trading

View insider activity on the stock:

```python
openbb.stocks.ins.lins(symbol = 'WMT')
```

| Date   | Relationship             | Transaction | #Shares |   Cost | Value ($)  | #Shares Total | Insider Trading    | SEC Form 4      |
| :----- | :----------------------- | :---------- | :------ | -----: | :--------- | :------------ | :----------------- | :-------------- |
| Oct 27 | President and CEO        | Sale        | 9,708   | 141.18 | 1,370,617  | 1,478,337     | McMillon C Douglas | Oct 28 06:14 PM |
| Oct 27 | Executive Vice President | Sale        | 4,375   | 140.94 | 616,612    | 263,809       | Furner John R.     | Oct 28 06:11 PM |
| Sep 22 | Executive Vice President | Sale        | 4,375   | 134.38 | 587,912    | 268,183       | Furner John R.     | Sep 23 05:21 PM |
| Sep 22 | President and CEO        | Sale        | 9,708   | 134.04 | 1,301,309  | 1,488,043     | McMillon C Douglas | Sep 23 05:18 PM |
| Aug 25 | Director                 | Sale        | 347,542 | 135.66 | 47,145,880 | 282,330,635   | WALTON S ROBSON    | Aug 26 06:36 PM |

...continued

### Income Statement Comparison

Income statements from multiple companies can be easily referenced:

```python
openbb.stocks.ca.income(similar = ['WMT', 'TGT', 'AMZN'], quarter = True)
```

| Item                                | 31-Jul-2022: WMT | 31-Jul-2022: TGT | 30-Sep-2022: AMZN |
| :---------------------------------- | :--------------- | :--------------- | :---------------- |
| Sales/Revenue                       | 152.86B          | 26.04B           | 127.1B            |
| Sales Growth                        | 7.97%            | 3.44%            | 4.84%             |
| Cost of Goods Sold (COGS) incl. D&A | 115.84B          | 20.71B           | 70.27B            |
| COGS Growth                         | 8.41%            | 8.67%            | 5.79%             |
| COGS excluding D&A                  | 113.14B          | 20.06B           | 60.06B            |
| Depreciation & Amortization Expense | 2.7B             | 650M             | 10.2B             |
| Depreciation                        | 2.7B             | -                | -                 |
| Amortization of Intangibles         | -                | -                | -                 |
| Gross Income                        | 37.02B           | 5.32B            | 56.83B            |
| Gross Income Growth                 | 6.62%            | -12.85%          | 3.69%             |
| Gross Profit Margin                 | 24.22%           | 20.44%           | 44.71%            |
| SG&A Expense                        | 30.17B           | 4.98B            | 54.14B            |
| SGA Growth                          | 3.30%            | 4.98%            | 5.33%             |
| Research & Development              | -                | -                | 19.49B            |
| Other SG&A                          | -                | -                | -                 |
| Other Operating Expense             | -                | -                | -                 |
| Unusual Expense                     | (238M)           | 27M              | (2.04B)           |
| EBIT after Unusual Expense          | 238M             | (27M)            | 2.04B             |
| Non Operating Income/Expense        | -                | 8M               | (1.45B)           |
| Non-Operating Interest Income       | 31M              | -                | 277M              |

...continued

### Ratios

Get historical fundamental ratios for a company:

```python
openbb.stocks.fa.ratios(symbol = 'WMT')
```

|                               | 2022   | 2021   | 2020   | 2019   | 2018   |
| :---------------------------- | :----- | :----- | :----- | :----- | :----- |
| Period                        | FY     | FY     | FY     | FY     | FY     |
| Current ratio                 | 0.928  | 0.972  | 0.795  | 0.799  | 0.760  |
| Quick ratio                   | 0.264  | 0.262  | 0.202  | 0.181  | 0.158  |
| Cash ratio                    | 0.169  | 0.191  | 0.122  | 0.100  | 0.086  |
| Days of sales outstanding     | 5.277  | 4.253  | 4.378  | 4.458  | 4.095  |
| Days of inventory outstanding | 48.080 | 39.034 | 41.101 | 41.937 | 42.799 |
| Operating cycle               | 53.357 | 43.287 | 45.479 | 46.395 | 46.894 |
| Days of payables outstanding  | 47.017 | 42.674 | 43.449 | 44.580 | 45.056 |
| Cash conversion cycle         | 6.340  | 0.613  | 2.030  | 1.814  | 1.838  |
| Gross profit margin           | 0.251  | 0.248  | 0.247  | 0.251  | 0.254  |
| Operating profit margin       | 0.045  | 0.040  | 0.039  | 0.043  | 0.041  |
| Pretax profit margin          | 0.033  | 0.037  | 0.038  | 0.022  | 0.030  |
| Net profit margin             | 0.024  | 0.024  | 0.028  | 0.013  | 0.020  |

...continued

Take just the ratio needed by filtering the index:

```python
ratios = openbb.stocks.fa.ratios(symbol = 'WMT', limit = 20)
ratios.filter(like = 'Price earnings to growth ratio', axis = 0)
```

|                                |   2022 |   2021 | 2020 |   2019 |   2018 |   2017 |   2016 |  2015 |   2014 |  2013 | 2012 |  2011 |  2010 |  2009 |  2008 |   2007 |  2006 |  2005 |  2004 |  2003 |
| :----------------------------- | -----: | -----: | ---: | -----: | -----: | -----: | -----: | ----: | -----: | ----: | ---: | ----: | ----: | ----: | ----: | -----: | ----: | ----: | ----: | ----: |
| Price earnings to growth ratio | 10.202 | -3.163 | 0.16 | -1.401 | -1.069 | -4.092 | -1.501 | 4.777 | -5.487 | 1.293 | 9.68 | 0.559 | 1.585 | 1.637 | 1.022 | 15.761 | 1.498 | 1.358 | 1.953 | 1.233 |

Be sure to check out the introduction guides for each sub-module as well.
