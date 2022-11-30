---
title: Comparison Analysis
---

The CA module provides programmatic access to the commands from within the OpenBB Terminal menu. Import the OpenBB SDK module, and then access the functions similarly to how the Terminal menus are navigated. The code completion will be activated upon entering `.`, after, `openbb.ca`

## How to Use

The examples provided below will assume that the following import block is included at the beginning of the Python script or Notebook file:

```python
from openbb_terminal.sdk import openbb
```

A brief description below highlights the functions available within the module:

| Path                              |    Type    |                                  Description |
| :-------------------------------- | :--------: | -------------------------------------------: |
| openbb.stocks.ca.balance          |  Function  |                Balance Financials Comparison |
| openbb.stocks.ca.cashflow         |  Function  |               Cashflow Financials Comparison |
| openbb.stocks.ca.hcorr            |  Function  |                 Historical Price Correlation |
| openbb.stocks.ca.hist             |  Function  |             Historical Price Data Comparison |
| openbb.stocks.ca.income           |  Function  |                 Income Financials Comparison |
| openbb.stocks.ca.scorr            |  Function  |                        Sentiment Correlation | 
| openbb.stocks.ca.screener         |  Function  |                            Screener Overview |
| openbb.stocks.ca.sentiment        |  Function  |                Sentiment Analysis Comparison |
| openbb.stocks.ca.similar          |  Function  |              Get a List of Similar Companies |
| openbb.stocks.ca.volume           |  Function  |            Historical Volume Data Comparison |

Alteratively, the contents of the menu is printed with:

```python
help(openbb.stocks.ca)
```

## Examples

### Balance

`openbb.stocks.ca.balance` compares the balance sheets for a list of companies.

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

### Sentiment

Social sentiment over time, for a list of tickers:

```python
openbb.stocks.ca.sentiment(["tsla", "f", "ge"])
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

### Screener

Show a high-level overview of company information for tickers in a given list

```python
openbb.stocks.ca.screener(["f", "ge", "tsla"])
```

|    | Ticker   | Company                  | Sector            | Industry                       | Country   |   Market Cap |    P/E |   Price |   Change |      Volume |
|---:|:---------|:-------------------------|:------------------|:-------------------------------|:----------|-------------:|-------:|--------:|---------:|------------:|
|  0 | F        | Ford Motor Company       | Consumer Cyclical | Auto Manufacturers             | USA       |   5.577e+10  |   6.31 |   13.95 |  -0.0029 | 3.40871e+07 |
|  1 | GE       | General Electric Company | Industrials       | Specialty Industrial Machinery | USA       |   9.375e+10  | nan    |   85.89 |   0.0048 | 3.26976e+06 |
|  2 | TSLA     | Tesla, Inc.              | Consumer Cyclical | Auto Manufacturers             | USA       |   5.3886e+11 |  51.72 |  167.87 |  -0.0684 | 9.28827e+07 |


### HCorr

Calculates the historical price (or returns) correlation for a list of tickers, over a specified window.

```python
correlation,historical = openbb.stocks.ca.hcorr(similar = openbb.stocks.ca.similar('TSLA', source = 'Polygon'), candle_type = 'R', start_date = '2018-11-01')

correlation
```

|     |      HMC |       TM |        F |       GM |
|:----|---------:|---------:|---------:|---------:|
| HMC | 1        | 0.74425  | 0.596182 | 0.62178  |
| TM  | 0.74425  | 1        | 0.532589 | 0.539333 |
| F   | 0.596182 | 0.532589 | 1        | 0.787406 |
| GM  | 0.62178  | 0.539333 | 0.787406 | 1        |
