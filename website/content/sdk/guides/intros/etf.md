---
title: ETF
keywords:
  [
    "stocks, stock, options, option, call, put, earnings, calendar, how-to, guide, scripts, fundamental, analysis, technical, behavioural, analyst, equity, research, api, sdk, application, python, notebook, jupyter",
  ]
excerpt: "This guide introduces the ETF SDK in the context of the OpenBB SDK."
---

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

|Path |Type |Description |
|:---------|:---------:|------------------------------:|
|openbb.etf.candle |Function |Chart OHLC + Volume + Moving Averages |
|openbb.etf.disc |Sub-Module |Best/Worst/Highest Volume ETFs Today |
|openbb.etf.etf_by_category |Function |Lookup by Category |
|openbb.etf.etf_by_name |Function |Lookup by Name |
|openbb.etf.holdings |Function |Holdings and Weights |
|openbb.etf.ld |Function |Lookup by Description |
|openbb.etf.load |Function |Get Historical Price Data |
|openbb.etf.ln |Function |Lookup by Name (More Details Than `by_name`) |
|openbb.etf.news |Function |News Headlines for a Ticker |
|openbb.etf.overview |Function |Basic Statistics for an ETF |
|openbb.etf.scr |Sub-Module |ETF Screener |
|openbb.etf.summary |Function |Text Description and Summary of an ETF |
|openbb.etf.symbols |Dictionary |Dictionary of {Ticker:Name} |
|openbb.etf.weights |Function |Table or Pie Graph of Sector Weightings |

Alteratively you can print the contents of the ETF SDK with:
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
etf_list = pd.DataFrame.from_dict(openbb.etf.etf_by_category('')).transpose()
categories = list(etf_list['category'].drop_duplicates())
categories = pd.DataFrame(categories[1::], columns = ['Type'])

categories.head(6)
```

|     | Type                      |
| --: | :------------------------ |
|   0 | Pacific/Asia ex-Japan Stk |
|   1 | Large Value               |
|   2 | Equity Energy             |
|   3 | Foreign Large Blend       |
|   4 | Large Blend               |
|   5 | Multisector Bond          |

​Replacing the empty category in the syntax above will return the ETFs within that category:
​

```python
etf_category = pd.DataFrame.from_dict(openbb.etf.etf_by_category('Foreign Large Blend')).transpose()
etf_category = etf_category.sort_values(by=['total_assets'], ascending = False)

etf_category.head(2)
```

|      | short_name                      | long_name                                                | currency | summary                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           | category            | family   | exchange | market    | total_assets |
| :--- | :------------------------------ | :------------------------------------------------------- | :------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------ | :------- | :------- | :-------- | -----------: |
| VXUS | Vanguard Total International St | Vanguard Total International Stock Index Fund ETF Shares | USD      | The investment seeks to track the performance of a benchmark index that measures the investment return of stocks issued by companies located in developed and emerging markets, excluding the United States.                                                                                                                                                                                                                                                                                                                                                                      | Foreign Large Blend | Vanguard | NGM      | us_market | 379067924480 |
|      |                                 |                                                          |          | The fund employs an indexing investment approach designed to track the performance of the FTSE Global All Cap ex US Index, a float-adjusted market-capitalization-weighted index designed to measure equity market performance of companies located in developed and emerging markets, excluding the United States. It invests all, or substantially all, of its assets in the common stocks included in its target index.                                                                                                                                                        |                     |          |          |           |              |
| VEA  | Vanguard FTSE Developed Markets | Vanguard FTSE Developed Markets Index Fund ETF Shares    | USD      | The investment seeks to track the performance of the FTSE Developed All Cap ex US Index.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          | Foreign Large Blend | Vanguard | PCX      | us_market | 150540566528 |
|      |                                 |                                                          |          | The fund employs an indexing investment approach designed to track the performance of the FTSE Developed All Cap ex US Index, a market-capitalization-weighted index that is made up of approximately 3865 common stocks of large-, mid-, and small-cap companies located in Canada and the major markets of Europe and the Pacific region. The adviser attempts to replicate the target index by investing all, or substantially all, of its assets in the stocks that make up the index, holding each stock in approximately the same proportion as its weighting in the index. |                     |          |          |           |              |

​
### ETF Tickers

A list of all tickers in the specific category can be generated from the index of the above DataFrame, `etf_category`:

```python
symbols = etf_category.index.to_list()
```

### Performance Metrics

This list of tickers can then be used for comparison analysis, or portfolio optimization. For example, comparing the performance metrics of the Foreign Large Blend category:

```python
performance = openbb.stocks.ca.screener(similar = symbols, data_type = 'performance')
performance = performance.sort_values(by=['Perf Quart'])
performance.head(5)
```

|    | Ticker   |   Perf Week |   Perf Month |   Perf Quart |   Perf Half |   Perf Year |   Perf YTD |   Volatility W |   Volatility M | Recom   |   Avg Volume |   Rel Volume |   Price |   Change |   Volume |
|---:|:---------|------------:|-------------:|-------------:|------------:|------------:|-----------:|---------------:|---------------:|:--------|-------------:|-------------:|--------:|---------:|---------:|
| 22 | IFV      |      0.0057 |       0.0531 |      -0.0873 |     -0.122  |     -0.2817 |    -0.2657 |         0.0188 |         0.0194 |         |        26410 |         1.44 |   16.78 |  -0.0158 |    13090 |
| 20 | IDLV     |      0.0326 |       0.0814 |      -0.0836 |     -0.1162 |     -0.1756 |    -0.1758 |         0.0113 |         0.0121 |         |       152070 |         0.57 |   26.39 |   0.003  |    29698 |
| 18 | HDMV     |      0.0456 |       0.0873 |      -0.0728 |     -0.1071 |     -0.1709 |    -0.1683 |         0.0087 |         0.0081 |         |         4330 |         1.35 |   26.44 |   0.0006 |     2011 |
|  7 | DEEF     |      0.0457 |       0.1061 |      -0.0612 |     -0.0997 |     -0.2099 |    -0.2071 |         0.0067 |         0.0122 |         |         8350 |         0.08 |   25    |  -0.0031 |      244 |
| 38 | RODM     |      0.0424 |       0.1106 |      -0.0428 |     -0.1012 |     -0.2015 |    -0.1827 |         0.0141 |         0.0139 |         |       345640 |         1.05 |   24.64 |   0.0011 |   125217 |

### Holdings

To peer into the holdings of a specific ETF:

```python
holdings = openbb.etf.holdings('DIA').reset_index()
holdings.head(5)
```

|    | Symbol   | Name                            | % Of Etf   |   Shares |
|---:|:---------|:--------------------------------|:-----------|---------:|
|  0 | UNH      | UnitedHealth Group Incorporated | 10.09%     |  5985297 |
|  1 | GS       | The Goldman Sachs Group, Inc.   | 7.51%      |  5985297 |
|  2 | HD       | The Home Depot, Inc.            | 6.03%      |  5985297 |
|  3 | AMGN     | Amgen Inc.                      | 5.61%      |  5985297 |
|  4 | MCD      | McDonald's Corporation          | 5.35%      |  5985297 |

### ETF Screener

The ETF screener is also accessible through the SDK. Variables for the screener are set in preset files. The path to their location will depend on the type of installation and operating system; it will be similar to:

- For a pip/PyPi installation: `~/path_to/miniconda3/envs/obb/Lib/site-packages/openbb_terminal/etf/screener/presets/etf_config.ini`
- For a Git Clone & Conda installation: `~/path_to/cloned_folder/OpenBBTerminal/openbb_terminal/etf/screener/presets/etf_config.ini`
- For a the EXE/DMG installer bundles: `~/path_to_installation/OpenBB Terminal/.OpenBB/openbb_terminal/etf/screener/etf_config.ini`

This file can be copied to the user data folder, `~/OpenBBUserData/presets/etf/screener/`, along with any other user-generated screener presets.

```python
results = openbb.etf.scr.screen(preset='etf_config.ini')
results.head(5)
```

In this example, the configuration file is set to return results with a maximum Beta value of -2.

|    | index   |   Assets |   NAV |   Expense |   PE | SharesOut   |    Div |   DivYield |         Volume |   Open |   PrevClose |   YrLow |   YrHigh |   Beta |   N_Hold |
|---:|:--------|---------:|------:|----------:|-----:|:------------|-------:|-----------:|---------------:|-------:|------------:|--------:|---------:|-------:|---------:|
|  0 | CLDS    |    14.15 | 28.3  |      0.99 |  N/A | 500,000     | N/A    |     N/A    | 7815           |  28.58 |       28.05 |   14.79 |    46.43 |  -2.12 |        6 |
|  1 | CTEX    |     3.95 | 39.52 |      0.58 |  N/A | 100,000     | N/A    |     N/A    | 1161           |  39.56 |       39.48 |   24.48 |    51.3  |  -2.07 |       31 |
|  2 | KLNE    |     5.7  | 22.81 |      1.29 |  N/A | 250,000     |   0.08 |       0.37 | 5580           |  21.55 |       21.7  |   12    |    31.38 |  -2.79 |        5 |
|  3 | LABD    |    97.16 | 18.61 |      1    |  N/A | 5.22        | N/A    |     N/A    |    8.12293e+06 |  22.26 |       21.35 |   15.7  |    85.28 |  -2.67 |       17 |
|  4 | MJIN    |     2.79 | 17.45 |      0.95 |  N/A | 160,000     |   0.88 |       4.45 |  282           |  19.81 |       19.07 |    7.87 |    26.73 |  -3.23 |        2 |

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

|    |                                                          |   Price |    Chg |   %Chg | Vol    |
|---:|:---------------------------------------------------------|--------:|-------:|-------:|:-------|
|  0 | Direxion Daily Semiconductor Bear 3X Shares              | 35.3101 | 3.3101 |  10.34 | 24.5M  |
|  1 | ProShares UltraShort Bloomberg Natural Gas               | 18.09   | 1.19   |   7.04 | 4.4M   |
|  2 | MicroSectors FANG & Innovation -3x Inverse Leveraged ETN | 28.98   | 1.83   |   6.74 | 160.1K |
|  3 | Direxion Daily Dow Jones Internet Bear 3X Shares         | 32.14   | 1.91   |   6.32 | 554.2K |
|  4 | Direxion Daily S&P 500 High Beta Bear 3X Shares          |  6.4652 | 0.3752 |   6.16 | 1.2M   |
