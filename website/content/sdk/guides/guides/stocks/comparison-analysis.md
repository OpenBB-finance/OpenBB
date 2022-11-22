---
title: Comparison Analysis
keywords:
  [
    "stocks, stock, options, option, comparison, analysis, tickers, stocks, insight"
  ]
excerpt: "This guide introduces the CA SDK in the context of the OpenBB SDK."
---

The CA module provides programmatic access to the commands from within the OpenBB Terminal. Import the OpenBB SDK module, and then access the functions similarly to how the Terminal menus are navigated. The code completion will be activated upon entering `.`, after, `openbb.ca`
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
| openbb.ca.balance          |  Function  |                Balance Financials Comparison |
| openbb.ca.hcorr            |  Function  |                 Historical Price Correlation |
| openbb.ca.volume           |  Function  |            Historical Volume Data Comparison |
| openbb.ca.scorr            |  Function  |                        Sentiment Correlation | 
| openbb.ca.hist             |  Function  |             Historical Price Data Comparison |
| openbb.ca.sentiment        |  Function  |                Sentiment Analysis Comparison |
| openbb.ca.polygon_peers    |  Function  |                 Similar Tickers from Polygon |
| openbb.ca.finviz_peers     |  Function  |                  Similar Tickers from Finvix |
| openbb.ca.income           |  Function  |                 Income Financials Comparison |
| openbb.ca.cashflow         |  Function  |               Cashflow Financials Comparison |
| openbb.ca.screener         |  Function  |                            Screener Overview |

Alteratively you can print the contents of the ETF SDK with:

```python
help(openbb.ca)
```

## Examples

### balance

The balance commands allows use to compare the balance sheets for various companies

```python
openbb.stocks.ca.balance(["TSLA","F", "GE"])
```

| Item                                 | TSLA   | F       | GE      |
|:-------------------------------------|:-------|:--------|:--------|
| Cash & Short Term Investments        | 18.05B | 49.59B  | 28.07B  |
| Cash & Short Term Investments Growth | -8.00% | -0.74%  | -35.99% |
| Cash Only                            | 17.92B | 20.54B  | 15.77B  |
| Short-Term Investments               | -      | -       | -       |
| Cash & ST Investments / Total Assets | 29.05% | 19.29%  | 14.11%  |
| Total Accounts Receivable            | 1.91B  | 44.04B  | 20.5B   |
| Total Accounts Receivable Growth     | 1.43%  | -16.24% | -8.70%  |
| Accounts Receivables, Net            | 1.91B  | 43.91B  | 20.5B   |
| Accounts Receivables, Gross          | 1.91B  | 44.28B  | 21.58B  |
| Bad Debt/Doubtful Accounts           | -      | (366M)  | (1.07B) |
| Other Receivable                     | -      | -       | -       |
| Accounts Receivable Turnover         | 28.14  | 3.10    | 3.62    |
| Inventories                          | 5.76B  | 12.07B  | 15.85B  |
| Finished Goods                       | 1.28B  | 6.28B   | 4.93B   |
| Work in Progress                     | 1.09B  | -       | -       |
| Raw Materials                        | 3.39B  | 5.79B   | 8.71B   |
| Progress Payments & Other            | -      | -       | 2.21B   |
| Other Current Assets                 | 1.38B  | 3.3B    | 1.93B   |
| Miscellaneous Current Assets         | 1.38B  | 3.3B    | 1.93B   |
| Total Current Assets                 | 27.1B  | 109B    | 66.35B  |
| Net Property, Plant & Equipment      | 31.18B | 64.84B  | 15.61B  |
| Property, Plant & Equipment - Gross  | 39.87B | 101.99B | 31.9B   |
| Buildings                            | 4.68B  | 12.44B  | 8.31B   |
| Land & Improvements                  | -      | 450M    | 585M    |
| Computer Software and Equipment      | 1.41B  | 4.6B    | -       |
| Other Property, Plant & Equipment    | 18.73B | 11.4B   | -       |
| Accumulated Depreciation             | 8.69B  | 37.16B  | 16.3B   |
| Total Investments and Advances       | 223M   | 5.64B   | 42.21B  |
| Other Long-Term Investments          | 223M   | 197M    | 42.21B  |
| Long-Term Note Receivables           | 299M   | 51.26B  | -       |
| Intangible Assets                    | 1.72B  | 619M    | 35.51B  |
| Net Goodwill                         | 200M   | 619M    | 26.18B  |
| Net Other Intangibles                | -      | -       | -       |
| Other Assets                         | 1.62B  | 11.89B  | 28.34B  |
| Total Assets                         | 62.13B | 257.04B | 198.87B |
| Total Assets Growth                  | 19.14% | -3.83%  | -22.38% |

### sentiment

Produces a table with sentiment over time for a given list of tickers

```python
openbb.stocks.ca.sentiment(["tsla", "aapl"])
```

|            |   TSLA |     F |    GE |
|:-----------|-------:|------:|------:|
| 2022-11-08 | -0.028 | 0.382 | 0.328 |
| 2022-11-09 |  0.209 | 0.199 | 0.242 |
| 2022-11-10 | -0.025 | 0.178 | 0.112 |
| 2022-11-11 |  0.027 | 0.086 | 0.056 |
| 2022-11-14 | -0.402 | 0.105 | 0.104 |
| 2022-11-15 | -0.122 | 0.081 | 0.075 |
| 2022-11-16 | -0.35  | 0.179 | 0.086 |
| 2022-11-17 |  0.156 | 0.387 | 0.025 |
| 2022-11-18 |  0.216 | 0.093 | 0.019 |
| 2022-11-21 | -0.071 | 0.069 | 0.01  |

​

### scr

Show a high-level overview of company information for tickers in a given list

```python
openbb.stocks.ca.screener(["tsla", "aapl"])
```

|    | Ticker   | Company                  | Sector            | Industry                       | Country   |   Market Cap |    P/E |   Price |   Change |      Volume |
|---:|:---------|:-------------------------|:------------------|:-------------------------------|:----------|-------------:|-------:|--------:|---------:|------------:|
|  0 | F        | Ford Motor Company       | Consumer Cyclical | Auto Manufacturers             | USA       |   5.577e+10  |   6.31 |   13.95 |  -0.0029 | 3.40871e+07 |
|  1 | GE       | General Electric Company | Industrials       | Specialty Industrial Machinery | USA       |   9.375e+10  | nan    |   85.89 |   0.0048 | 3.26976e+06 |
|  2 | TSLA     | Tesla, Inc.              | Consumer Cyclical | Auto Manufacturers             | USA       |   5.3886e+11 |  51.72 |  167.87 |  -0.0684 | 9.28827e+07 |
