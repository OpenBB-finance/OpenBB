---
title: Discovery
keywords:
  [
    "stocks", "stock", "options", "option", "comparison", "analysis", "tickers", "stocks", "insight"
  ]
excerpt: "This guide introduces the Disc SDK in the context of the OpenBB SDK."
---

The Disc module provides programmatic access to the commands from within the OpenBB Terminal. Import the OpenBB SDK module, and then access the functions similarly to how the Terminal menus are navigated. The code completion will be activated upon entering `.`, after, `openbb.disc`
​

## How to Use

​
The examples provided below will assume that the following import block is included at the beginning of the Python script or Notebook file:
​

```python
from openbb_terminal.sdk import openbb
```

​
A brief description below highlights the main Functions and Modules available in the ETF SDK

| Path                       |    Type    |                                  Description |
| :------------------------- | :--------: | -------------------------------------------: |
| openbb.stocks.disc.pipo           |  Function  |                               Past IPO Dates |
| openbb.stocks.disc.active         |  Function  |            Stocks with Highest Trade Volumes |
| openbb.stocks.disc.gainers        |  Function  |                           Latest Top Gainers |
| openbb.stocks.disc.asc            |  Function  |    Small Caps with Earnings Growth Above 25% |
| openbb.stocks.disc.lowfloat       |  Function  |           Stocks with Under 10M Shares Float |
| openbb.stocks.disc.fipo           |  Function  |                             Future IPO Dates |
| openbb.stocks.disc.upcoming       |  Function  |              Upcoming Earnings Release Dates |
| openbb.stocks.disc.trending       |  Function  |                                Trending News |
| openbb.stocks.disc.ulc            |  Function  |     Potentially Undervalued Large Cap Stocks |
| openbb.stocks.disc.arkord         |  Function  |      Orders of ARK Investment Management LLC |
| openbb.stocks.disc.hotpenny       |  Function  |                             Hot Penny Stocks |
| openbb.stocks.disc.gtech          |  Function  |    Tech Stocks with Earnings Growth Over 25% |
| openbb.stocks.disc.losers         |  Function  |                              Show Top Losers |
| openbb.stocks.disc.ugs            |  Function  |   Undervalueds with Earnings Growth Over 25% |
| openbb.stocks.disc.rtat           |  Function  |                  Top 10 Retail Traded Stocks |
| openbb.stocks.disc.dividends      |  Function  |                            Screener Overview |

Alteratively you can print the contents of the Disc SDK with:

```python
help(openbb.stocks.disc)
```

## Examples

### pipo

Gives information on companies that recently had an IPO (Initial Public Offering)

```python
openbb.stocks.disc.pipo()
```

|    | Past       | Exchange       | Name                           | Number of Shares   | Price     | Status    | symbol   | Total Shares Value   |
|---:|:-----------|:---------------|:-------------------------------|:-------------------|:----------|:----------|:---------|:---------------------|
|  0 | 2022-11-22 | NASDAQ Capital | Adamas One Corp.               | 7165904.0          | 4.50-5.00 | expected  | JEWL     | 38192020.0           |
|  1 | 2022-11-21 |                | Solta Medical Corp             |                    |           | withdrawn |          |                      |
|  2 | 2022-11-18 |                | MGO Global Inc.                |                    |           | filed     | MGOL     | 8625000.0            |
|  3 | 2022-11-18 |                | CytoMed Therapeutics Pte. Ltd. |                    |           | filed     | GDTC     | 15000000.0           |
|  4 | 2022-11-18 |                | BKV Corp                       |                    |           | filed     | BKV      | 100000000.0          |
|  5 | 2022-11-18 |                | Coya Therapeutics, Inc.        |                    |           | filed     | COYA     | 17250000.0           |

### gainers

Shows stocks with the biggest percent change in daily growth

```python
openbb.stocks.disc.gainers()
```

|    | Symbol   | Name                                            |   Price (Intraday) |   Change | % Change   | Volume   | Avg Vol (3 month)   | Market Cap   | PE Ratio (TTM)   |
|---:|:---------|:------------------------------------------------|-------------------:|---------:|:-----------|:---------|:--------------------|:-------------|:-----------------|
|  0 | MPCFF    | Metro Pacific Investments Corporation           |             0.1021 |   0.0273 | +36.50%    | 20000    | 24674               | 2.963B       | 10.21            |
|  1 | JBARF    | Julius Bär Gruppe AG                            |            56.66   |  11.5    | +25.47%    | 47922    | 276                 | 14.48B       | 12.26            |
|  2 | BURL     | Burlington Stores, Inc.                         |           189.96   |  32.32   | +20.50%    | 5.369M   | 1.431M              | 12.451B      | 75.38            |
|  3 | PSNY     | Polestar Automotive Holding UK PLC              |             7.82   |   1.33   | +20.49%    | 8.878M   | 2.611M              | 16.495B      | 4.25             |
|  4 | AEO      | American Eagle Outfitters, Inc.                 |            15.36   |   2.36   | +18.15%    | 18.426M  | 6.448M              | 2.877B       | 16.52            |
|  5 | MMS      | Maximus, Inc.                                   |            70.34   |   9.8    | +16.19%    | 1.016M   | 380221              | 4.259B       | 23.45            |
|  6 | MRTX     | Mirati Therapeutics, Inc.                       |            86.11   |  11.57   | +15.52%    | 5.41M    | 857355              | 4.959B       |                  |
|  7 | WMG      | Warner Music Group Corp.                        |            31.09   |   4.11   | +15.23%    | 3.496M   | 1.209M              | 16.007B      | 37.91            |
|  8 | TIAOF    | Telecom Italia S.p.A.                           |             0.2477 |   0.0317 | +14.68%    | 20000    | 37835               | 5.578B       |                  |
|  9 | MANU     | Manchester United plc                           |            14.94   |   1.91   | +14.66%    | 5.253M   | 500920              | 2.436B       |                  |
| 10 | BBY      | Best Buy Co., Inc.                              |            79.88   |   9.05   | +12.78%    | 17.487M  | 3.047M              | 17.983B      | 10.69            |
| 11 | SGIOY    | Shionogi & Co., Ltd.                            |            13.8    |   1.55   | +12.65%    | 217546   | 253257              | 16.545B      | 20.0             |
| 12 | DKS      | DICK'S Sporting Goods, Inc.                     |           117.76   |  10.82   | +10.12%    | 6.403M   | 1.735M              | 9.326B       | 10.14            |
| 13 | BCDRF    | Banco Santander, S.A.                           |             2.85   |   0.25   | +9.62%     | 1.001M   | 230746              | 49.706B      | 5.09             |
| 14 | EE       | Excelerate Energy, Inc.                         |            30      |   2.63   | +9.61%     | 842088   | 466600              | 3.248B       | 16.39            |
| 15 | URBN     | Urban Outfitters, Inc.                          |            27.8    |   2.27   | +8.89%     | 7.168M   | 2.121M              | 2.562B       | 11.26            |
| 16 | WHITF    | Whitehaven Coal Limited                         |             6.2    |   0.5    | +8.77%     | 39639    | 62464               | 5.762B       | 4.37             |
| 17 | LINRF    | Liontown Resources Limited                      |             1.5    |   0.12   | +8.70%     | 36150    | 4637                | 3.295B       | 150.0            |
| 18 | MBLY     | Mobileye Global Inc.                            |            29.55   |   2.33   | +8.56%     | 1.327M   | 1.848M              | 23.837B      |                  |
| 19 | A        | Agilent Technologies, Inc.                      |           156.86   |  11.72   | +8.07%     | 3.468M   | 1.406M              | 46.437B      | 35.81            |
| 20 | FUTU     | Futu Holdings Limited                           |            54.39   |   3.99   | +7.92%     | 4.094M   | 2.489M              | 7.995B       | 27.61            |
| 21 | SYM      | Symbotic Inc.                                   |            10.77   |   0.79   | +7.92%     | 442139   | 215487              | 5.983B       |                  |
| 22 | KAEPF    | The Kansai Electric Power Company, Incorporated |             8.36   |   0.6    | +7.73%     | 21794    | 5106                | 7.93B        | 17.79            |
| 23 | HL       | Hecla Mining Company                            |             5.17   |   0.37   | +7.71%     | 11.242M  | 8.056M              | 3.134B       | 172.33           |
| 24 | RKLIF    | Rentokil Initial plc                            |             6.52   |   0.47   | +7.68%     | 29704    | 3911                | 16.434B      | 36.23            |

​

### rtat

Shows information on how retail investors are trading a particular ticker

```python
openbb.stocks.disc.rtat()
```

|      | Date       | Ticker   |   Activity |   Sentiment |
|-----:|:-----------|:---------|-----------:|------------:|
|    0 | 2022-11-22 | TSLA     |     0.0681 |           1 |
|    1 | 2022-11-22 | TQQQ     |     0.0159 |          -2 |
|    2 | 2022-11-22 | SQQQ     |     0.0219 |           0 |
|    3 | 2022-11-22 | SPY      |     0.0387 |           1 |
|    4 | 2022-11-22 | QQQ      |     0.019  |          -1 |
|    5 | 2022-11-22 | NVDA     |     0.0427 |          -3 |
|    6 | 2022-11-22 | META     |     0.0137 |          -1 |
|    7 | 2022-11-22 | AMZN     |     0.0333 |          -1 |
|    8 | 2022-11-22 | AMD      |     0.0317 |          -3 |
|    9 | 2022-11-22 | AAPL     |     0.0307 |          -5 |
|   10 | 2022-11-21 | TSLA     |     0.0763 |           0 |
|   11 | 2022-11-21 | TQQQ     |     0.0169 |           1 |
|   12 | 2022-11-21 | SQQQ     |     0.0249 |          -3 |
|   13 | 2022-11-21 | SPY      |     0.0354 |           2 |
|   14 | 2022-11-21 | QQQ      |     0.0203 |           2 |
|   15 | 2022-11-21 | NVDA     |     0.0312 |          -3 |
|   16 | 2022-11-21 | DIS      |     0.0367 |           1 |
|   17 | 2022-11-21 | AMZN     |     0.035  |           0 |
|   18 | 2022-11-21 | AMD      |     0.0275 |          -1 |
|   19 | 2022-11-21 | AAPL     |     0.0322 |          -3 |
|   20 | 2022-11-18 | TSLA     |     0.0621 |          -1 |
|   21 | 2022-11-18 | TQQQ     |     0.0246 |          -1 |
|   22 | 2022-11-18 | SQQQ     |     0.0274 |          -1 |
|   23 | 2022-11-18 | SPY      |     0.0456 |           1 |
|   24 | 2022-11-18 | QQQ      |     0.0235 |          -3 |
|   25 | 2022-11-18 | NVDA     |     0.0376 |          -5 |
|   26 | 2022-11-18 | META     |     0.0141 |           3 |
|   27 | 2022-11-18 | AMZN     |     0.0338 |           0 |
|   28 | 2022-11-18 | AMD      |     0.0379 |           0 |
|   29 | 2022-11-18 | AAPL     |     0.0403 |          -3 |
|   30 | 2022-11-17 | TSLA     |     0.0563 |          -1 |
