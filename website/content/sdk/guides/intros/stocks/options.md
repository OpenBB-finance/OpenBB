---
title: Options
---

The Options module wraps the Terminal commands for the SDK layer, providing programmatic access and greater flexibility for processing data.

## How to Use

The functions in the Options sub-module are listed below, along with a short description.

|Path |Description |
|:----|-----------:|
|openbb.stocks.options.chains |Options Chains |
|openbb.stocks.options.dte |Convert a Date in the Future to DTE |
|openbb.stocks.options.expirations |List of Expiration Dates for the Underlying |
|openbb.stocks.options.grhist |Historical Greeks for Individual Options |
|openbb.stocks.options.hist |Historical Data from Tradier |
|openbb.stocks.options.hist_ce |Historical Data from ChartExchange |
|openbb.stocks.options.info |Options Statistics for the Underling from BarChart |
|openbb.stocks.options.last_price |Last Price of the Underlying from Tradier |
|openbb.stocks.options.pcr |Historical Put/Call Ratio |
|openbb.stocks.options.screen |Options Screener |
|openbb.stocks.options.unu |Unusual Options |
|openbb.stocks.options.vsurf |Volatility Surface |

Alternatively, the contents of the menu or a function's docstrings can be printed using Python's built-in help.

```python
help(openbb.stocks.options)
```

## Examples

### Import Statements

The examples in this section will assume these statements are included at the top of the file:

```python
from openbb_terminal.sdk import openbb
import pandas as pd
```

### Unusual Options

`openbb.stocks.options.unu` returns a DataFrame with the current day's unusual options, those having a very high volume/open interest ratio. This function returns a Tuple containing the DataFrame and a string. Unpack it like this:

```python
unu_df,unu_ts = openbb.stocks.options.unu(limit = 500)
unu_df = unu_df.sort_values(by = 'Vol/OI', ascending = False)

unu_df
```

|    | Ticker   | Exp        |   Strike | Type   |   Vol/OI |    Vol |   OI |   Bid |   Ask |
|---:|:---------|:-----------|---------:|:-------|---------:|-------:|-----:|------:|------:|
|  0 | T        | 2023-01-06 |     21   | Call   |     61   |   8598 |  141 |  0.03 |  0.04 |
|  1 | T        | 2023-01-06 |     19   | Put    |     40.7 |  10173 |  250 |  0.39 |  0.42 |
|  2 | SCHW     | 2023-03-17 |     87.5 | Call   |     35.1 |   4317 |  123 |  3.2  |  3.35 |
|  3 | TSLA     | 2022-12-02 |    192.5 | Put    |     31.1 | 179688 | 5774 |  0.01 |  0.02 |
|  4 | FDX      | 2022-12-09 |    190   | Call   |     29.2 |   7098 |  243 |  0.67 |  0.69 |
| 403 | FCX      | 2022-12-09 |     36   | Put    |      2.1 |  1513 |  729 |  0.04 |  0.06 |
| 402 | CAT      | 2022-12-09 |    227.5 | Put    |      2.1 |   601 |  280 |  0.94 |  1.14 |
| 401 | NKE      | 2022-12-02 |    111   | Put    |      2.1 |   651 |  306 |  0    |  0.01 |
| 400 | NVDA     | 2022-12-09 |    160   | Put    |      2.1 |  8668 | 4059 |  1.06 |  1.08 |
| 425 | PG       | 2022-12-09 |    149   | Put    |      2.1 |   241 |  113 |  0.64 |  0.69 |

### PCR

Get up to ten years of historical Put-Call Ratios.

```python
openbb.stocks.options.pcr(start_date = '2012-01-01', window = 10, symbol = 'SPY')
```

| Date                |    PCR |
|:--------------------|-------:|
| 2012-12-05 00:00:00 | 1.1815 |
| 2012-12-06 00:00:00 | 1.7403 |
| 2012-12-07 00:00:00 | 1.7023 |
| 2012-12-10 00:00:00 | 1.8997 |
| 2012-12-11 00:00:00 | 1.5384 |
| 2022-11-28 00:00:00 | 1.2491 |
| 2022-11-29 00:00:00 | 2.135  |
| 2022-11-30 00:00:00 | 1.5901 |
| 2022-12-01 00:00:00 | 0.9842 |
| 2022-12-02 00:00:00 | 2.1346 |

### Hist_CE

The historical daily data of an individual option, from ChartExchange, includes open interest.

```python
openbb.stocks.options.hist_ce(symbol = 'SPY', price = '400', date = '2023-01-20', call = False)
```

|    | Date       |   Open |   High |   Low |   Close |   Change |   Volume |   Open Interest |   Change Since |
|---:|:-----------|-------:|-------:|------:|--------:|---------:|---------:|----------------:|---------------:|
|  0 | 2022-12-01 |   8.5  |  10.01 |  7.99 |    8.68 | -0.01251 |    11443 |           47690 |        0       |
|  1 | 2022-11-30 |  14.44 |  15.68 |  8.79 |    8.79 | -0.3866  |    19763 |           46218 |       -0.01251 |
|  2 | 2022-11-29 |  14.74 |  15.37 | 14.25 |   14.33 |  0.01415 |      666 |           45105 |       -0.39428 |
|  3 | 2022-11-28 |  12.49 |  14.86 | 11.94 |   14.13 |  0.27297 |    10643 |           45828 |       -0.3857  |
| 366 | 2021-05-21 |  37.72 |  37.72 | 37.59 |   37.59 | -0.01079 |        5 |               0 |       -0.76909 |
| 367 | 2021-05-20 |  38    |  38    | 38    |   38    | -0.07317 |        2 |               0 |       -0.77158 |
| 368 | 2021-05-19 |  41.67 |  41.67 | 41    |   41    |  0.07471 |       26 |               0 |       -0.78829 |
| 369 | 2021-05-17 |  37.43 |  38.15 | 37.43 |   38.15 | -0.0453  |        3 |               0 |       -0.77248 |
