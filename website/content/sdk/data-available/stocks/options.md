---
title: Options
description: This documentation page explains how to use the Options module in the
  OpenBB SDK that allows programmatic access to trading data. It covers a range of
  functions that correspond to many aspects of stock option data, from Unusual Options
  Activity to Put-Call Ratios.
keywords:
- Options Module
- OpenBB SDK
- Trading Data
- Stock Option Data
- Unusual Options Activity
- Put-Call Ratios
- Programmatic Access
- Terminal Commands
- Data Processing
- Documentation
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Options - Stocks - Intros - Usage | OpenBB SDK Docs" />

The Options module wraps the Terminal commands for the SDK layer, providing programmatic access and greater flexibility for processing data.

## How to Use

The functions in the Options sub-module are listed below, along with a short description.

|Path |Description |
|:----|-----------:|
|stocks.options.pcr| Put-Call Ratio |
|stocks.options.info| Option Information |
|stocks.options.unu| Unusual Options Activity|
|stocks.options.hist|Historical Option Data|
|stocks.options.chains | Option Chain Data|
||stocks.options.eodchain | Get End of Day Option Chain Data|
|stocks.options.vol| Display Volume plot|
|stocks.options.oi| Display open interest plot|
|stocks.options.voi| Display plot of volume and open interest|
|stocks.options.expirations| Get Option Expirations|
|stocks.options.vsurf|Show volatility surface|

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

### Chains

Get the current option chain for a selected ticker.  We support the following sources: YahooFinance, Nasdaq,
Tradier (Sandbox) and Intrinio.  Note that each API returns slightly different data fields.

```python
openbb.stocks.options.chains(symbol = 'SPY')
```

|    | contractSymbol      | optionType   | expiration   |   strike |   lastPrice |    bid |    ask |   openInterest |   volume |   impliedVolatility |
|---:|:--------------------|:-------------|:-------------|---------:|------------:|-------:|-------:|---------------:|---------:|--------------------:|
|  0 | AAPL230210C00050000 | call         | 2023-02-10   |       50 |      101.95 | 101.15 | 102.8  |            153 |       44 |             4.73438 |
|  1 | AAPL230210C00055000 | call         | 2023-02-10   |       55 |       96.6  |  96.15 |  97.85 |             81 |        3 |             4.53125 |
|  2 | AAPL230210C00070000 | call         | 2023-02-10   |       70 |       76.39 |  81.1  |  82.95 |              0 |        1 |             3.63281 |
|  3 | AAPL230210C00075000 | call         | 2023-02-10   |       75 |       79.45 |  76.1  |  78.05 |              2 |        1 |             3.50781 |
|  4 | AAPL230210C00080000 | call         | 2023-02-10   |       80 |       72.55 |  71.1  |  73.05 |              2 |        2 |             3.21094 |
