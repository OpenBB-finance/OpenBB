---
title: ETF
description:
  This documentation page provides a comprehensive guide on how to use
  the ETF module of the OpenBB Terminal SDK for programmatic access. It covers a list
  of functions within the ETF module, how to import the SDK, how to print contents
  of the SDK, how to use the ETF module in various situations such as getting list
  of ETF categories, getting ETF tickers, comparing performance metrics, getting the
  holdings of a specific ETF, performing ETF screening, and retrieving current top
  gainers, losers, and volume for ETFs.
keywords:
  - OpenBB Terminal SDK
  - ETF module
  - programmatic access
  - import SDK
  - perform ETF screening
  - get ETF holdings
  - compare performance metrics
  - retrieve top gainers and losers
  - retrieve top volume for ETFs
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="ETF - Intros - Usage | OpenBB SDK Docs" />

The ETF module provides programmatic access to the commands from within the OpenBB Terminal. Import the OpenBB SDK module, and then access the functions similarly to how the Terminal menus are navigated. The code completion will be activated upon entering `.`, after, `openbb.etf`
​

## How to Use

​The examples provided below will assume that the following import block is included at the beginning of the Python script or Notebook file:
​

```python
from openbb_terminal.sdk import openbb
import pandas as pd
```

​Below is a brief description of each function within the ETF module:

| Path                       |    Type    |                                  Description |
| :------------------------- | :--------: | -------------------------------------------: |
| openbb.etf.candle          |  Function  |        Chart OHLC + Volume + Moving Averages |
| openbb.etf.disc            | Sub-Module |         Best/Worst/Highest Volume ETFs Today |
| openbb.etf.etf_by_category |  Function  |                           Lookup by Category |
| openbb.etf.etf_by_name     |  Function  |                               Lookup by Name |
| openbb.etf.holdings        |  Function  |                         Holdings and Weights |
| openbb.etf.ld              |  Function  |                        Lookup by Description |
| openbb.etf.load            |  Function  |                    Get Historical Price Data |
| openbb.etf.ln              |  Function  | Lookup by Name (More Details Than `by_name`) |
| openbb.etf.news            |  Function  |                  News Headlines for a Ticker |
| openbb.etf.overview        |  Function  |                  Basic Statistics for an ETF |
| openbb.etf.scr             | Sub-Module |                                 ETF Screener |
| openbb.etf.summary         |  Function  |       Text Description and Summary of an ETF |
| openbb.etf.symbols         | Dictionary |                Dictionary of `{Ticker:Name}` |
| openbb.etf.weights         |  Function  |      Table or Pie Graph of Sector Weightings |

Alternatively you can print the contents of the ETF SDK with:
​

```python
help(openbb.etf)
```

## Examples

### etf_by_category

​
ETFs are categorized into different buckets. Use the code block below as a way to generate a list of all categories:
​

```python
etf_list = pd.DataFrame.from_dict(openbb.etf.etf_by_category(''))
categories = list(etf_list['category'].drop_duplicates())
categories = pd.DataFrame(categories[1::], columns = ['Type'])

categories.head(6)
```

|       Type       |
| :--------------: |
|    Financials    |
| Emerging Markets |
|   Industrials    |
|     Factors      |
|    Utilities     |
|      Bonds       |

​Replacing the empty category in the syntax above will return the ETFs within that category:
​

```python
etf_category = pd.DataFrame.from_dict(openbb.etf.etf_by_category('Emerging Markets'))
etf_category.head(2)
```

| symbol | name                                          | currency | summary                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | category_group | category         | family                     | exchange | market    |
| :----- | :-------------------------------------------- | :------- | :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------- | :--------------- | :------------------------- | :------- | :-------- |
| AAXJ   | iShares MSCI All Country Asia ex Japan ETF    | USD      | The investment seeks to track the investment results of the MSCI AC Asia ex Japan Index.                                                                                                                                                                                                                                                                                                                                                                                                                                                             | Equities       | Emerging Markets | BlackRock Asset Management | NMS      | us_market |
|        |                                               |          | The fund will invest at least 90% of its assets in the component securities of the index and in investments that have economic characteristics that are substantially identical to the component securities of the index. The index is a free float-adjusted market capitalization index designed to measure equity market performance of securities from the following 11 developed and emerging market countries or regions: China, Hong Kong, India, Indonesia, Malaysia, Pakistan, the Philippines, Singapore, South Korea, Taiwan and Thailand. |                |                  |                            |          |           |
| JHEM   | John Hancock Multifactor Emerging Markets ETF | USD      | The investment seeks to provide investment results that closely correspond, before fees and expenses, to the performance of the John Hancock Dimensional Emerging Markets Index (the index).                                                                                                                                                                                                                                                                                                                                                         | Equities       | Emerging Markets | John Hancock               | PCX      | us_market |
|        |                                               |          | The fund normally invests at least 80% of its net assets (plus any borrowings for investment purposes) in securities included in the index, in depositary receipts representing securities included in the index, and in underlying stocks in respect of depositary receipts included in the index. The index is designed to comprise a subset of securities associated with emerging markets, which may include frontier markets (emerging markets in an earlier stage of development).                                                             |                |                  |                            |          |           |

### ETF Tickers

A list of all tickers in the specific category can be generated from the index of the above DataFrame, `etf_category`:

```python
symbols = etf_category.index.to_list()
```

### Performance Metrics

This list of tickers can then be used for comparison analysis, or portfolio optimization. For example, comparing the performance metrics of the Emerging Market category:

```python
performance = openbb.stocks.ca.screener(similar = symbols, data_type = 'performance')
performance = performance.sort_values(by=['3M'], ascending=False)
performance.head(5)
```

| Ticker |     1W |     1M |     3M |     6M |     1Y |     YTD | 1W Volatility | 1M Volatility | Recom | Avg Volume | Rel Volume | Price | Change |  Volume |
| :----- | -----: | -----: | -----: | -----: | -----: | ------: | ------------: | ------------: | :---- | ---------: | ---------: | ----: | -----: | ------: |
| CHB    | 0.0301 | -0.015 | 0.1123 | 0.0086 | -0.132 | -0.1277 |        0.0105 |        0.0048 |       |       1130 |       0.04 |  8.22 | 0.0123 |      21 |
| INCO   | 0.0193 | 0.0716 | 0.1092 | 0.1543 | 0.2706 |  0.3171 |        0.0066 |        0.0049 |       |      17810 |       1.62 | 59.77 | 0.0073 |   14060 |
| GLIN   | 0.0251 | 0.0733 | 0.1083 |  0.221 | 0.2704 |  0.3319 |        0.0105 |        0.0079 |       |      20360 |       0.89 |  43.5 | 0.0133 |    8833 |
| ILF    | 0.0497 | 0.0631 | 0.1032 |  0.062 | 0.3082 |  0.2768 |        0.0141 |        0.0135 |       |   1.18e+06 |       2.16 | 29.23 | 0.0215 | 1237337 |
| SMIN   | 0.0174 | 0.0573 | 0.0914 | 0.2128 | 0.2848 |  0.3447 |        0.0078 |        0.0074 |       |      99980 |       5.61 |  69.6 | 0.0053 |  272774 |

### Holdings

To peer into the holdings of a specific ETF:

```python
holdings = openbb.etf.holdings('DIA').reset_index()
holdings.head(5)
```

|     | Symbol | Name                            | % Of Etf |  Shares |
| --: | :----- | :------------------------------ | :------- | ------: |
|   0 | UNH    | UnitedHealth Group Incorporated | 10.09%   | 5985297 |
|   1 | GS     | The Goldman Sachs Group, Inc.   | 7.51%    | 5985297 |
|   2 | HD     | The Home Depot, Inc.            | 6.03%    | 5985297 |
|   3 | AMGN   | Amgen Inc.                      | 5.61%    | 5985297 |
|   4 | MCD    | McDonald's Corporation          | 5.35%    | 5985297 |

### Disc

The current top gainers, losers, and volume for ETFs is returned with:

```python
openbb.etf.disc.mover(sort_type = 'decliners')

openbb.etf.disc.mover(sort_type = 'gainers')

openbb.etf.disc.mover(sort_type = 'active')
```

With no `sort_type` chosen, it will default to `gainers`:

```python
movers = openbb.etf.disc.mover()
movers.head(5)
```

|     |                                                          |   Price |    Chg |  %Chg | Vol    |
| --: | :------------------------------------------------------- | ------: | -----: | ----: | :----- |
|   0 | Direxion Daily Semiconductor Bear 3X Shares              | 35.3101 | 3.3101 | 10.34 | 24.5M  |
|   1 | ProShares UltraShort Bloomberg Natural Gas               |   18.09 |   1.19 |  7.04 | 4.4M   |
|   2 | MicroSectors FANG & Innovation -3x Inverse Leveraged ETN |   28.98 |   1.83 |  6.74 | 160.1K |
|   3 | Direxion Daily Dow Jones Internet Bear 3X Shares         |   32.14 |   1.91 |  6.32 | 554.2K |
|   4 | Direxion Daily S&P 500 High Beta Bear 3X Shares          |  6.4652 | 0.3752 |  6.16 | 1.2M   |
