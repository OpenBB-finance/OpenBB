---
title: Stocks
sidebar_position: 0
description: This documentation page describes all the modules that are within the stocks menu of OpenBB.
keywords:
- stocks
- behavioural analysis
- comparison analysis
- discovery
- dark pool
- short data
- government trading
- insider trading
- fundamental analysis
- technical analysis
---

The Stocks module provides the functionality of the Stocks menu from the OpenBB Terminal. The list below are the SDK functions within the Stocks module and a short description:

| Path                   |    Type    |                                             Description |
| :--------------------- | :--------: | ------------------------------------------------------: |
| openbb.stocks.ba       | Sub-Module |                                    Behavioural Analysis |
| openbb.stocks.ca       | Sub-Module |                                     Comparison Analysis |
| openbb.stocks.candle   |  Function  |                   OHLC + Volume + Moving Averages Chart |
| openbb.stocks.disc     | Sub-Module |                                         Stock Discovery |
| openbb.stocks.dps      | Sub-Module |                                     Dark Pools & Shorts |
| openbb.stocks.fa       | Sub-Module |               Fundamental Analysis & Future Estimations |
| openbb.stocks.gov      | Sub-Module |       US Government, Lobbying & Representative Activity |
| openbb.stocks.ins      | Sub-Module |                 Corporate Insider Activity (SEC Form 4) |
| openbb.stocks.load     |  Function  |                             Load Historical OHLC+V Data |
| openbb.stocks.options  | Sub-Module |                                                 Options |
| openbb.stocks.qa       | Sub-Module |                       Stocks-Only Quantitative Analysis |
| openbb.stocks.quote    |  Function  | Last Price and Performance Data (FinancialModelingPrep) |
| openbb.stocks.screener | Sub-Module |                                          Stock Screener |
| openbb.stocks.search   |  Function  |                                             Find Stocks |
| openbb.stocks.sia      | Sub-Module |                              Sector & Industry Analysis |
| openbb.stocks.ta       | Sub-Module |                          Stocks-Only Technical Analysis |
| openbb.stocks.th       | Sub-Module |                           Trading Hours (Market Status) |
| openbb.stocks.tob      |  Function  |                                      Top of Book (CBOE) |

## How to use

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

```

### Load

The first step in a workflow might be to collect historical price data. The `load` function has the ability to request data from multiple sources. The choices for `source` are currently:

- YahooFinance (default)
- AlphaVantage
- Polygon
- EODHD

```python
spy_monthly = openbb.stocks.load(
    symbol = 'SPY',
    start_date = '1990-01-01',
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

|   |        | long_name                       | country        | sector | industry      | exchange |
| -: | :----- | :------------------------------ | :------------- | :----- | :------------ | -------: |
| 0 | 3NO.F  | Nostrum Oil & Gas PLC           | United Kingdom | Energy | Oil & Gas E&P |      nan |
| 1 | BOIL.L | Baron Oil Plc                   | United Kingdom | Energy | Oil & Gas E&P |      nan |
| 2 | EGN.F  | Europa Oil & Gas (Holdings) plc | United Kingdom | Energy | Oil & Gas E&P |      nan |
| 3 | EOG.L  | Europa Oil & Gas (Holdings) plc | United Kingdom | Energy | Oil & Gas E&P |      nan |
| 4 | GHA.F  | Baron Oil Plc                   | United Kingdom | Energy | Oil & Gas E&P |      nan |

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

|    | Symbol   | Name                                           |   Price |   Changes percentage |   Change |   Day low |   Day high |   Year high |   Year low | Market cap   |   Price avg50 |   Price avg200 | Exchange   | Volume   |   Avg volume |   Open |   Previous close |      Eps |    Pe | Earnings announcement   | Shares outstanding   |   Timestamp |
|---:|:---------|:-----------------------------------------------|--------:|---------------------:|---------:|----------:|-----------:|------------:|-----------:|:-------------|--------------:|---------------:|:-----------|:---------|-------------:|-------:|-----------------:|---------:|------:|:------------------------|:---------------------|------------:|
|  0 | SPY      | SPDR S&P 500 ETF Trust                         |  393.74 |               0.9616 |   3.75   |   390.08  |   394.17   |      462.07 |    348.11  | 361.367 B    |      399.841  |       392.797  | AMEX       | 88.857 M |     89590689 | 390.8  |         389.99   | 19.9365  | 19.75 |                         | 917.782 M            |  1679342401 |
|  0 | XLE      | Energy Select Sector SPDR Fund                 |   77.7  |               2.0024 |   1.5253 |    76.1   |    78.2    |       94.71 |     65.48  | 14.485 B     |       86.6584 |        82.6697 | AMEX       | 25.791 M |     19906166 |  76.1  |          76.1747 | 10.86    |  7.15 |                         | 186.424 M            |  1679342400 |
|  0 | XLB      | Materials Select Sector SPDR Fund              |   76.73 |               2.0581 |   1.5473 |    75.77  |    76.77   |       91.49 |     66.85  | 5.519 B      |       81.7186 |        77.8203 | AMEX       | 7.327 M  |      5830645 |  75.77 |          75.1827 |  5.16256 | 14.86 |                         | 71.924 M             |  1679342400 |
|  0 | XLI      | Industrial Select Sector SPDR Fund             |   97.55 |               1.3242 |   1.2749 |    96.71  |    97.79   |      105.23 |     82.75  | 13.328 B     |      101.103  |        95.1877 | AMEX       | 14.078 M |     11957477 |  96.71 |          96.2751 |  4.6974  | 20.77 |                         | 136.626 M            |  1679342400 |
|  0 | XLP      | Consumer Staples Select Sector SPDR Fund       |   72.76 |               1.386  |   0.9947 |    72.01  |    72.83   |       81.34 |     66.18  | 15.292 B     |       73.092  |        72.9574 | AMEX       | 14.127 M |     10950449 |  72.04 |          71.7653 |  2.88675 | 25.2  |                         | 210.172 M            |  1679342400 |
|  0 | XLY      | Consumer Discretionary Select Sector SPDR Fund |  141.52 |               0.433  |   0.6102 |   139.75  |   142.39   |      192.19 |    126     | 17.018 B     |      143.901  |       146.454  | AMEX       | 5.863 M  |      5416313 | 140.74 |         140.91   |  6.27203 | 22.56 |                         | 120.253 M            |  1679342400 |
|  0 | XLV      | Health Care Select Sector SPDR Fund            |  126.96 |               1.2675 |   1.5891 |   125.58  |   127.145  |      143.42 |    118.75  | 25.064 B     |      131.092  |       130.376  | AMEX       | 10.584 M |      8826462 | 125.58 |         125.371  |  5.92017 | 21.45 |                         | 197.415 M            |  1679342400 |
|  0 | XLF      | Financial Select Sector SPDR Fund              |   31.17 |               1.1114 |   0.3426 |    31.025 |    31.44   |       40.01 |     29.59  | 27.537 B     |       35.4068 |        33.8593 | AMEX       | 74.917 M |     50017188 |  31.07 |          30.8274 |  2.57075 | 12.12 |                         | 883.445 M            |  1679342400 |
|  0 | XLK      | Technology Select Sector SPDR Fund             |  143.53 |               0.2693 |   0.3855 |   141.82  |   143.7    |      163.65 |    112.97  | 39.048 B     |      136.542  |       132.924  | AMEX       | 5.924 M  |      7283266 | 142.89 |         143.145  |  5.1111  | 28.08 |                         | 272.056 M            |  1679342400 |
|  0 | XLC      | Communication Services Select Sector SPDR Fund |   55.27 |               0.7474 |   0.41   |    54.71  |    55.41   |       71.57 |     44.86  | 0            |       54.1118 |        52.9782 | AMEX       | 7.189 M  |      6117298 |  54.91 |          54.86   |  2.87114 | 19.25 |                         | 0                    |  1679342400 |
|  0 | XLU      | Utilities Select Sector SPDR Fund              |   67    |               0.7818 |   0.5197 |    66.56  |    67.22   |       78.22 |     60.35  | 10.939 B     |       68.0158 |        69.9207 | AMEX       | 19.265 M |     12304022 |  66.58 |          66.4803 |  2.88295 | 23.24 |                         | 163.274 M            |  1679342400 |
|  0 | XLRE     | The Real Estate Select Sector SPDR Fund        |   36.36 |               1.0727 |   0.3859 |    35.87  |    36.4932 |       50.97 |     33.125 | 0            |       38.953  |        39.4885 | AMEX       | 4.963 M  |      6039455 |  36.06 |          35.9741 |  1.30938 | 27.77 |                         | 0                    |  1679342400 |

### TOB

Top of Book gets the size and price at the top of the order book.

```python
bid,ask = openbb.stocks.tob('SPY')
quote_tob = bid.join(ask, lsuffix= ': Bid', rsuffix = ': Ask')

quote_tob
```

|   | Size: Bid | Price: Bid | Size: Ask | Price: Ask |
| -: | --------: | ---------: | --------: | ---------: |
| 0 |       100 |     394.85 |       100 |        395 |
| 1 |       100 |      394.8 |       300 |     395.05 |
| 2 |       100 |      394.7 |       100 |     395.07 |
| 3 |       100 |     394.68 |       200 |     395.25 |
| 4 |       100 |     394.65 |       100 |     395.29 |

### Filings

Get the most-recent form submissions to the SEC.

```python
filings = openbb.stocks.disc.filings()
filings.head(3)
```

| Date                | Ticker   |     CIK | Form Type   | Title                                                 | URL                                                                                               |
|:--------------------|:---------|--------:|:------------|:------------------------------------------------------|:--------------------------------------------------------------------------------------------------|
| 2023-03-20 17:30:26 | TLGA     | 1827871 | 10-K        | 10-K - TLG Acquisition One Corp. (0001827871) (Filer) | https://www.sec.gov/Archives/edgar/data/1827871/000119312523074903/0001193125-23-074903-index.htm |
| 2023-03-20 17:30:26 | TLGA     | 1827871 | 10-K        | 10-K - TLG Acquisition One Corp. (0001827871) (Filer) | https://www.sec.gov/Archives/edgar/data/1827871/000119312523074903/0001193125-23-074903-index.htm |
| 2023-03-20 17:30:26 | TLGA-UN  | 1827871 | 10-K        | 10-K - TLG Acquisition One Corp. (0001827871) (Filer) | https://www.sec.gov/Archives/edgar/data/1827871/000119312523074903/0001193125-23-074903-index.htm |
| 2023-03-20 17:30:26 | TLGA-UN  | 1827871 | 10-K        | 10-K - TLG Acquisition One Corp. (0001827871) (Filer) | https://www.sec.gov/Archives/edgar/data/1827871/000119312523074903/0001193125-23-074903-index.htm |
| 2023-03-20 17:30:26 | TLGA-WT  | 1827871 | 10-K        | 10-K - TLG Acquisition One Corp. (0001827871) (Filer) | https://www.sec.gov/Archives/edgar/data/1827871/000119312523074903/0001193125-23-074903-index.htm |

Filter them to be from the current day only:

```python
today = filings.filter(like = datetime.now().strftime("%Y-%m-%d"), axis = 0)
```

### Screener

Grab the list of filtered tickers and put them through the comparison analysis screener and get an overview:

```python
tickers = today['Ticker'].to_list()
screener_results = openbb.stocks.ca.screener(similar = tickers, data_type = 'overview')
screener_results = screener_results.sort_values(by = ['Market Cap'], ascending = False).convert_dtypes()

screener_results.head(5)
```

|     | Ticker   | Company          | Sector                 | Industry                     | Country        |   Market Cap |   P/E |   Price |   Change |   Volume |
|----:|:---------|:-----------------|:-----------------------|:-----------------------------|:---------------|-------------:|------:|--------:|---------:|---------:|
|  72 | NVO      | Novo Nordisk A/S | Healthcare             | Biotechnology                | Denmark        |   2.4814e+11 | 41.42 |  143.59 |   0.0298 |  1242167 |
|  34 | EQNR     | Equinor ASA      | Energy                 | Oil & Gas Integrated         | Norway         |   8.591e+10  |  3.02 |   27.34 |   0.0096 |  4154740 |
|  46 | GSK      | GSK plc          | Healthcare             | Drug Manufacturers - General | United Kingdom |   7.026e+10  | 12.29 |   34.93 |   0.0252 |  2973805 |
| 105 | UBS      | UBS Group AG     | Financial              | Banks - Diversified          | Switzerland    |   6.783e+10  |  8.39 |   18.8  |   0.033  | 40598414 |
|  83 | RELX     | RELX PLC         | Communication Services | Publishing                   | United Kingdom |   5.97e+10   | 30.52 |   31.31 |   0.0205 |   620949 |

This type of framework can be used to create any type of custom screener. For example, the most popular tickers on Stocktwits:

```python
stocktwits = openbb.stocks.ba.trending()
stocktwits = pd.DataFrame(stocktwits).sort_values(by = 'Watchlist Count', ascending = False)
tickers = stocktwits['Ticker'].to_list()
stocktwits.head(10)
```

|    | Ticker | Watchlist Count | Name                           |
| -: | :----- | --------------: | :----------------------------- |
| 18 | NVDA   |          409301 | NVIDIA Corp                    |
| 12 | AMC    |          406952 | AMC Entertainment Holdings Inc |
|  5 | WMT    |          109864 | Walmart Inc                    |
|  6 | MRNA   |          100705 | Moderna Inc                    |
| 21 | PFE    |           87229 | Pfizer Inc.                    |
|  4 | DWAC   |           66122 | Digital World Acquisition Corp |
| 29 | CSCO   |           54458 | Cisco Systems, Inc.            |
|  0 | SAVA   |           49063 | Cassava Sciences Inc           |
|  8 | TDOC   |           38657 | Teladoc Health Inc             |
| 16 | PENN   |           38277 | Penn National Gaming, Inc.     |

Filter the results by market cap:

```python
screener_results = openbb.stocks.ca.screener(similar = tickers, data_type = 'overview')
screener_results = screener_results.sort_values(by = ['Market Cap'], ascending = False)

screener_results.head(5)
```

|    | Ticker | Company            | Sector             | Industry                     | Country | Market Cap |   P/E |  Price |  Change |      Volume |
| -: | :----- | :----------------- | :----------------- | :--------------------------- | :------ | ---------: | ----: | -----: | ------: | ----------: |
| 15 | NVDA   | NVIDIA Corporation | Technology         | Semiconductors               | USA     | 3.9217e+11 | 53.53 | 163.66 |  0.0024 | 3.16641e+07 |
| 26 | WMT    | Walmart Inc.       | Consumer Defensive | Discount Stores              | USA     |  3.864e+11 | 28.46 |  140.5 | -0.0146 | 5.33372e+06 |
| 18 | PFE    | Pfizer Inc.        | Healthcare         | Drug Manufacturers - General | USA     | 2.6591e+11 |  9.03 |  49.36 |   0.037 | 1.07892e+07 |
|  4 | BLK    | BlackRock, Inc.    | Financial          | Asset Management             | USA     | 1.1412e+11 | 21.34 | 747.95 | -0.0346 |      742602 |
| 25 | TGT    | Target Corporation | Consumer Defensive | Discount Stores              | USA     |  7.566e+10 | 19.68 | 175.67 |  0.0136 | 2.45293e+06 |

...continued

### SEC

Get the links for SEC filings belonging to a company:

```python
openbb.stocks.fa.sec(symbol = 'WMT')
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
