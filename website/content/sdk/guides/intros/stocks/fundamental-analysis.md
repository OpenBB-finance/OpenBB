---
title: Fundamental Analysis
keywords:
  [
    "stocks", "stock", "options", "option", "call", "put", "earnings", "calendar", "how-to", "guide", "scripts", "fundamental", "analysis", "technical", "behavioural", "analyst", "equity", "research", "api", "sdk", "application", "python", "notebook", "jupyter",
  ]
excerpt: "This guide introduces the FA menu in the context of the OpenBB SDK."
---

The FA module provides programmatic access to the commands from within the OpenBB Terminal. Import the OpenBB SDK module, and then access the functions similarly to how the Terminal menus are navigated. The code completion will be activated upon entering `.`, after, `openbb.fa`
​

## How to Use

​
The examples provided below will assume that the following import block is included at the beginning of the Python script or Notebook file:
​

```python
from openbb_terminal.sdk import openbb
```

​
A brief description below highlights the main Functions and Modules available in the FA SDK

| Path                       |    Type    |                                  Description |
| :------------------------- | :--------: | -------------------------------------------: |
| openbb.stocks.fa.mgmt             |  Function  |                      Company Management Team |
| openbb.stocks.fa.score            |  Function  |           Investing Score from Warren Buffet |
| openbb.stocks.fa.sust             |  Function  |                        Sustianability Values |
| openbb.stocks.fa.divs             |  Function  |           Historical Dividends for a Company |
| openbb.stocks.fa.shrs             |  Function  | Shareholders (Insiders, Institutions, Funds) |
| openbb.stocks.fa.earnings         |  Function  |                        Earnings Data and EPS |
| openbb.stocks.fa.info             |  Function  |                  Information About a Company |
| openbb.stocks.fa.dcf              |  Function  |                Shows DCF Values for a Ticker |
| openbb.stocks.fa.overview         |  Function  |                      Overview of the Company |
| openbb.stocks.fa.data             |  Function  |               Fundamental and Technical Data |
| openbb.stocks.fa.ratios           |  Function  |                    In-Depth Ratios over Time |
| openbb.stocks.fa.growth           |  Function  |          Growth of Financial Statement Items |
| openbb.stocks.fa.enterprise       |  Function  |                     Company Enterprise Value |
| openbb.stocks.fa.analysis         |  Function  |  Analysis SEC Fillings with Machine Learning |
| openbb.stocks.fa.balance          |  Function  |                        Company Balance Sheet |
| openbb.stocks.fa.dupont           |  Function  |                       Detailed ROE Breakdown |
| openbb.stocks.fa.profile          |  Function  |                              Company Profile |
| openbb.stocks.fa.fraud            |  Function  |                             Key Fraud Ratios |
| openbb.stocks.fa.income           |  Function  |                     Company Income Statement |
| openbb.stocks.fa.key              |  Function  |                          Company Key Metrics |
| openbb.stocks.fa.splits           |  Function  |    Stock Splits and Reverse Splits Since IPO |
| openbb.stocks.fa.hq               |  Function  |                      HQ Location for Company |
| openbb.stocks.fa.cal              |  Function  |              Calendar Earnings and Estimates |
| openbb.stocks.fa.mktcap           |  Function  |                         Estimated Market Cap |
| openbb.stocks.fa.metrics          |  Function  |                        Key Metrics Over Time |
| openbb.stocks.fa.cash             |  Function  |                           Company Cash Flows |

Alteratively you can print the contents of the FA SDK with:

```python
help(openbb.stocks.fa)
```

## Examples

### shrs

The shrs command give a breakdown of the top shareholders for a given ticker

```python
openbb.stocks.fa.shrs("TSLA")
```

|    | Holder                        | Shares    | Date Reported       | Stake   | Value    |
|---:|:------------------------------|:----------|:--------------------|:--------|:---------|
|  0 | Vanguard Group, Inc. (The)    | 213.025 M | 2022-09-29 00:00:00 | 6.75 %  | 36.195 B |
|  1 | Blackrock Inc.                | 171.861 M | 2022-09-29 00:00:00 | 5.44 %  | 29.201 B |
|  2 | State Street Corporation      | 99.647 M  | 2022-09-29 00:00:00 | 3.16 %  | 16.931 B |
|  3 | Capital World Investors       | 90.162 M  | 2022-09-29 00:00:00 | 2.86 %  | 15.319 B |
|  4 | Geode Capital Management, LLC | 47.496 M  | 2022-09-29 00:00:00 | 1.50 %  | 8.070 B  |
|  5 | Price (T.Rowe) Associates Inc | 46.957 M  | 2022-09-29 00:00:00 | 1.49 %  | 7.978 B  |
|  6 | FMR, LLC                      | 38.429 M  | 2022-09-29 00:00:00 | 1.22 %  | 6.529 B  |
|  7 | Jennison Associates LLC       | 29.558 M  | 2022-09-29 00:00:00 | 0.94 %  | 5.022 B  |
|  8 | Baillie Gifford and Company   | 27.877 M  | 2022-09-29 00:00:00 | 0.88 %  | 4.737 B  |
|  9 | Northern Trust Corporation    | 26.602 M  | 2022-09-29 00:00:00 | 0.84 %  | 4.520 B  |

### enterprise

Creates a table showing enterprise value over time for a ticker

```python
openbb.stocks.fa.enterprise("TSLA")
```

|                                 | 2021      | 2020      | 2019      | 2018     | 2017     |
|:--------------------------------|:----------|:----------|:----------|:---------|:---------|
| Symbol                          | TSLA      | TSLA      | TSLA      | TSLA     | TSLA     |
| Stock price                     | 282.117   | 264.510   | 42.721    | 20.585   | 23.055   |
| Number of shares                | 2.958 B   | 2.880 B   | 2.655 B   | 2.558 B  | 2.486 B  |
| Market capitalization           | 834.501 B | 761.789 B | 113.423 B | 52.653 B | 57.322 B |
| Minus cash and cash equivalents | 17.576 B  | 19.384 B  | 6.268 B   | 3.686 B  | 3.368 B  |
| Add total debt                  | 6.834 B   | 11.688 B  | 13.704 B  | 12.115 B | 10.382 B |
| Enterprise value                | 823.759 B | 754.093 B | 120.859 B | 61.082 B | 64.337 B |

​

### income

Income statements over time for a ticker

```python
openbb.stocks.fa.income(["tsla", "aapl"])
```

| Breakdown                                   |           ttm |      2021-12-31 |       2020-12-31 |   2019-12-31 |
|:--------------------------------------------|--------------:|----------------:|-----------------:|-------------:|
| Total revenue                               |   2.5508e+09  |     1.60937e+09 |      8.31576e+08 |  3.61384e+08 |
| Cost of revenue                             |   2.16586e+09 |     1.4104e+09  |      6.66345e+08 |  2.84672e+08 |
| Gross profit                                |   3.84936e+08 |     1.98969e+08 |      1.65231e+08 |  7.6712e+07  |
| Selling general and administrative          |   4.07964e+08 |     2.52133e+08 |      1.03962e+08 |  5.9148e+07  |
| Total operating expenses                    |   4.90874e+08 |     3.01574e+08 |      1.22461e+08 |  6.597e+07   |
| Operating income or loss                    |  -1.05938e+08 |    -1.02605e+08 |      4.277e+07   |  1.0742e+07  |
| Interest expense                            |   5.7796e+07  |     5.1291e+07  |      3.4002e+07  |  1.0163e+07  |
| Total other income/expenses net             |   3.8987e+07  |     3.7169e+07  |     -7.9501e+07  | -2.0678e+07  |
| Income before tax                           |  -1.2474e+08  |    -1.16723e+08 |     -7.0413e+07  | -1.978e+07   |
| Income tax expense                          |   1.417e+06   | 14000           | 651000           |  0           |
| Income from continuing operations           |  -1.26157e+08 |    -1.16737e+08 |     -7.1064e+07  | -1.978e+07   |
| Net income                                  |  -5.824e+07   |    -1.802e+07   |     -7.1064e+07  | -1.978e+07   |
| Net income available to common shareholders |  -5.824e+07   |    -1.802e+07   |     -7.1064e+07  | -1.978e+07   |
| Basic EPS                                   | nan           |    -0.11        |     -0.43        | -0.12        |
| Diluted EPS                                 | nan           |    -0.28        |     -0.43        | -0.12        |
| Basic average shares                        | nan           |     1.70507e+08 |      1.66243e+08 |  1.66243e+08 |
| Diluted average shares                      | nan           |     4.75697e+08 |      1.66243e+08 |  1.66243e+08 |
| EBITDA                                      | nan           |    -1.5991e+07  |     -1.7912e+07  | -2.795e+06   |
