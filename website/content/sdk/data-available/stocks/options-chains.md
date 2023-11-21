---
title: Options Chains
description: A technical guide detailing how to load options chains data from six
  different sources into memory using openbb. Reviews how to properly filter, sort,
  and analyze this kind of data, and outlines the process for implementing various
  options strategies. This document is heavily focused on technical processes within
  a financial context.
keywords:
- Options Chains Data
- Option Strategies
- Financial Data
- Data Filtering
- Data Sorting
- Data Visualization
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Options Chains - Stocks - Intros - Usage | OpenBB SDK Docs" />

## Overview

### Options Data Object

Options chains data is loaded to memory by using the function, `openbb.stocks.options.load_options_chains()`, and is available from six sources:

- CBOE
- Intrinio (no free data)
- Nasdaq
- TMX
- Tradier (requires Sandbox developer key)
- YahooFinance

Every source will return the same object which has data and additional callable functions bound to the class.  They are methods for filtering, sorting, and analyzing the data contained within.

```python
from openbb_terminal.sdk import openbb
openbb.stocks.options.load_options_chains?
```

```python
Parameters
----------
symbol: str
    The ticker symbol to load the data for.
source: str
    The source for the data. Defaults to "CBOE". ["CBOE", "Intrinio", "Nasdaq", "TMX", "Tradier", "YahooFinance"]
date: str
    The date for EOD chains data.  Only available for "Intrinio" and "TMX".
pydantic: bool
    Whether to return as a Pydantic Model or as a Pandas object.  Defaults to False.

Returns
------
OptionsChains
    chains: pd.DataFrame
        The complete options chain for the ticker. Returns as a dictionary if pydantic is True.
    expirations: list[str]
        List of unique expiration dates. (YYYY-MM-DD)
    strikes: list[float]
        List of unique strike prices.
    last_price: float
        The last price of the underlying asset.
    underlying_name: str
        The name of the underlying asset.
    underlying_price: pd.Series
        The price and recent performance of the underlying asset. Returns as a dictionary if pydantic is True.
    hasIV: bool
        Returns implied volatility.
    hasGreeks: bool
        Returns greeks data.
    symbol: str
        The symbol entered by the user.
    source: str
        The source of the data.
    date: str
        The date, when the chains data is historical EOD.
    SYMBOLS: pd.DataFrame
        The symbol directory for the source, when available. Returns as a dictionary if pydantic is True.

    Methods
    ------
    chart_skew: Callable
        Function to chart the implied volatility skew.
    chart_stats: Callable
        Function to chart a variety of volume and open interest statistics.
    chart_surface: Callable
        Function to chart the volatility as a 3-D surface.
    chart_volatility: Callable
        Function to chart the implied volatility smile.
    get_skew: Callable
        Function to calculate horizontal and vertical skewness.
    get_stats: Callable
        Function to return a table of summary statistics, by strike or by expiration.
    get_straddle: Callable
        Function to calculate straddles and the payoff profile.
    get_strangle: Callable
        Function to calculate strangles and the payoff profile.
    get_synthetic_long: Callable
        Function to calculate a synthetic long position.
    get_synthetic_short: Callable
        Function to calculate a synthetic short position.
    get_vertical_call_spread: Callable
        Function to calculate vertical call spreads.
    get_vertical_put_spreads: Callable
        Function to calculate vertical put spreads.
    get_strategies: Callable
        Function for calculating multiple straddles and strangles at different expirations and moneyness.
```

## Loading Data

### `load_options_chains()`

The default source to load data from is, `CBOE`.  Use the command below to get started.

```python
from openbb_terminal.sdk import openbb
spy = openbb.stocks.options.load_options_chains("SPY")
```

The result is returned as the object described in the previous section.

![Options Data Object](https://github.com/deeleeramone/OpenBBTerminal/assets/85772166/704e6d60-b148-442d-b4b2-689ceca6f55c)

The object is still returned if an unsupported symbol is requested and a message will be printed.

```python
In [4]: data = openbb.stocks.options.load_options_chains("spyyy")
The symbol, SPYYY, was not found in the CBOE directory.

In [5]: data.chains
Out[5]: pandas.core.frame.DataFrame
```

Where available, symbols are verified against a source-specific symbol directory.  This is accessible from the Options data object as the attribute named, `SYMBOLS`.

```python
data.SYMBOLS.filter(like = "SPY", axis = 0)
```

| Symbol   | Company Name                   | DPM Name                 | Post/Station   |
|:---------|:-------------------------------|:-------------------------|:---------------|
| SPY      | SPDR S&P 500 ETF TR TR UNIT    | Morgan Stanley & Co. LLC | 8/1            |
| SPYG     | SPDR SER TR PRTFLO S&P500 GW   | Belvedere Trading LLC    | 6/1            |
| SPYD     | SPDR SER TR PRTFLO S&P500 HI   | Citadel Securities LLC   | 6/1            |
| SPYV     | SPDR SER TR PRTFLO S&P500 VL   | Belvedere Trading LLC    | 6/1            |
| NSPY     | UNIFIED SER TR NIGHTSHARES 500 | Wolverine Trading, LLC   | 3/1            |

:::note
A valid symbol will not always have listed options.
:::

Key information for the underlying asset are stored in the object as `last_price`, `underlying_name`, and `underlying_price`.  The information returned to `underlying_price` will vary by source, but all column headers and index names related to the raw data are formatted in camelCase.

CBOE:

```python
In [7]: data.underlying_price
Out[7]:
type                                 stock
tick                                  down
bid                                 449.18
bidSize                                  1
askSize                                  5
ask                                  449.2
price                               449.28
open                                450.56
high                                451.36
low                                 448.49
close                               449.28
volume                            69772484
previousClose                       449.28
change                               -0.28
changePercent                      -0.0623
ivThirty                            10.947
ivThirtyChange                         0.0
lastTradeTimestamp     2023-07-14T16:00:00
ivThirtyOneYearHigh              30.646999
hvThirtyOneYearHigh              30.648199
ivThirtyOneYearLow                  10.692
hvThirtyOneYearLow                 10.0721
ivSixtyOneYearHigh               28.674999
hvSixtyOneYearHigh                 29.5842
ivSixtyOneYearLow                   11.245
hvsixtyOneYearLow                   11.833
ivNinetyOneYearHigh                 27.862
hvNinetyOneYearHigh              26.808901
ivNinetyOneYearLow                  11.827
hvNinetyOneYearLow                 13.3855
Name: SPY, dtype: object
```

TMX:

```python
In [8]: data = openbb.stocks.options.load_options_chains("XIU", "TMX")

In [9]: data.underlying_price
Out[9]:
time                15:59:56.910
previousClose              30.86
transactions                 393
volume                     50751
value                    1567628
valueCAD                 1567628
open                       30.97
price                      30.85
change                     -0.01
changePercent              -0.03
tick                        0.01
low                       30.835
high                       30.97
vwap                       30.89
fiftyTwoWeekHigh           31.86
fiftyTwoWeekLow           27.375
Name: XIU, dtype: object
```

Not every source will return implied volatility or Greeks data.  The two object attributes, `hasGreeks` and `hasIV`, act as validators for downstream functions.

```python
In [10]: data.hasIV
Out[10]: False

In [11]: data.get_skew()
Options data object does not have Implied Volatility and is required for this function.
```

#### Historical EOD Chains

Historical EOD chains data is currently available from `Intrinio` or `TMX`.  The amount of historical data will depend on the subscription status with `Intrinio`, but is available from the beginning of 2009 from `TMX`.  Add the `date` argument when loading the data.  The price data of the underlying asset will reflect the closing price on the date entered.

```python
In [12]: data = openbb.stocks.options.load_options_chains("CCO", "TMX", date = "2016-06-29")

In [13]: data.underlying_price
Out[13]:
date             2016-06-29
bid                   13.99
ask                   14.01
bidSize                  29
askSize                  20
price                  14.0
volume               801176
previousClose         13.73
change                 0.27
open                  13.88
high                  14.09
low                    13.8
valueCAD           11198995
transactions           3283
symbol                  CCO
Name: Cameco Corporation, dtype: object
```

## Additional Class Methods

The class methods work with the Options data object to query the loaded chains data in different ways.  Column headers at this stage are cleaned and presentable for view.  There are two types of operations, `get` and `chart`, with the latter being a subset of the former. The docstring (`data?` - and as shown in a section above) lists them all, as Methods, with a short description. The nuances of the functions are explained within the docstrings of each.  Variations to the combinations of parameters will yield over thirty unique charts and provide nearly infinite ways to query to data stored in the object.

:::note

All `chart_` methods have boolean arguments for `raw` and `external_axes`. These return an interactive table in the PyWry window or the Plotly figure object, respectively. In a Jupyter Notebook, they will be displayed inline.

Returning the command to a variable provides the ability to style and customize charts as desired.

```python
fig = data.chart_volatility(expirations=data.expirations[1], external_axes = True)
```

:::

### `get_stats()`

```python
Parameters
----------
by: str
    Whether to calculate by strike or expiration.  Default is expiration.
query: DataFrame
    Entry point to perform DataFrame operations on self.chains at the input stage.

Returns
-------
pd.DataFrame
    Pandas DataFrame with the calculated statistics.
```

Ratios are defined as Put/Call.

```python
data = openbb.stocks.options.load_options_chains("VIX")
data.get_stats().iloc[1]
```

|              |   2023-07-26 |
|:-------------|-------------:|
| Puts OI      |      2018    |
| Calls OI     |     45875    |
| Total OI     |     47893    |
| OI Ratio     |         0.04 |
| Puts OTM     |       873    |
| Calls OTM    |     45747    |
| Puts ITM     |      1145    |
| Calls ITM    |       128    |
| OTM Ratio    |         0.02 |
| ITM Percent  |         2.66 |
| Puts Volume  |       264    |
| Calls Volume |      2156    |
| Total Volume |      2420    |
| Volume Ratio |         0.12 |
| Vol-OI Ratio |         0.05 |

The `query` parameter provides an entry point for DataFrame operations to take place prior to calculating.  For example, filtering for only the options which traded during the last session.

```python
data.get_stats(query = data.chains[vix.chains["lastTradeTimestamp"] > "2023-07-14"])
```

| Expiration   |          Puts OI |         Calls OI |         Total OI |   OI Ratio |   Puts Volume |   Calls Volume |   Total Volume |   Volume Ratio |   Vol-OI Ratio |
|:-------------|-----------------:|-----------------:|-----------------:|-----------:|--------------:|---------------:|---------------:|---------------:|---------------:|
| 2023-07-19   |    1569778    |      3323396  |      4893174 |       0.47 |        113460 |         130416 |         243876 |           0.87 |           0.05 |
| 2023-07-26   |   1855           |  29273           |  31128           |       0.06 |           264 |           2156 |           2420 |           0.12 |           0.08 |
| 2023-08-02   |   1154           |   2498           |   3652           |       0.46 |            12 |            786 |            798 |           0.02 |           0.22 |
| 2023-08-09   |    330           |    961           |   1291           |       0.34 |            43 |            354 |            397 |           0.12 |           0.31 |
| 2023-08-16   | 907980           |      2246707 |      3154687 |       0.4  |         48668 |         197148 |         245816 |           0.25 |           0.08 |
| 2023-08-23   |      0           |     49           |     49           |       0    |             7 |            145 |            152 |           0.05 |           3.1  |
| 2023-09-20   | 614369           |      2097742 |      2712111 |       0.29 |         20750 |          19260 |          40010 |           1.08 |           0.01 |
| 2023-10-18   | 165239           |      1099858 |      1265097  |       0.15 |          3304 |          14912 |          18216 |           0.22 |           0.01 |
| 2023-11-15   |  70142           | 742698           | 812840           |       0.09 |            82 |            514 |            596 |           0.16 |           0    |
| 2023-12-20   |  44580           | 259815           | 304395           |       0.17 |         10797 |          12471 |          23268 |           0.87 |           0.08 |
| 2024-01-17   |  20860           |  43733           |  64593           |       0.48 |         23574 |          23690 |          47264 |           1    |           0.73 |
| 2024-02-14   |   1347           |   6567           |   7914           |       0.21 |            67 |            203 |            270 |           0.33 |           0.03 |
| 2024-03-20   |     63           |   1861           |   1924           |       0.03 |             8 |            219 |            227 |           0.04 |           0.12 |

### chart_stats()

The volume and open interest metrics can be visualized in a number of ways. In general, they are bucketed as volume and open interest by strike or expiration.

```python
data.chart_stats()
```

![Vix % of Total Volume vs. Strike](https://github.com/deeleeramone/OpenBBTerminal/assets/85772166/70d55645-7510-4c1e-9e56-c6b37ef40249)

```python
data.chart_stats(by="strike", oi=True)
```

![VIX % of Total Open Interest vs. Strike](https://github.com/deeleeramone/OpenBBTerminal/assets/85772166/9798ed44-23c3-4a54-9c20-ea6450c035d9)

```python
data.chart_stats(by="strike", oi=True, percent=False)
```

![VIX Open Interest vs. Strike](https://github.com/deeleeramone/OpenBBTerminal/assets/85772166/b1bed9c5-4338-4fb5-8ffe-a67eba6c5219)

```python
data.chart_stats(ratios=True)
```

![VIX Volume and Open Interest Ratios](https://github.com/deeleeramone/OpenBBTerminal/assets/85772166/0c459c96-267b-472e-8323-cb547af0e0e4)

### Options Strategies

These methods calculate common, single-leg, strategies and return one result. The target expiry date is expressed as the number of days until expiration, and the closest expiry to supplied value will be returned. There are six types of strategies currently supported:

- `get_straddle()`
- `get_strangle()`
- `get_synthetic_long()`
- `get_synthetic_short()`
- `get_vertical_call_spread()`
- `get_vertical_put_spread()`

:::note

Looking for a place to get started as a contributor, and enjoy trading options? Strategies are an excellent starting point!

:::

All strategies share a common default setting, `days=30`.  Vertical spreads require two strike prices, and they are entered as `sold`, `bought`.  A bull call or put spread is entered with a bought price lower than the sold price.

```python
data.get_vertical_call_spread(30,13,12.50)
```

|                         | Bull Call Spread   |
|:------------------------|:-------------------|
| Symbol                  | VIX                |
| Underlying Price        | 13.34              |
| Expiration              | 2023-08-16         |
| DTE                     | 31                 |
| Strike 1                | 13.0               |
| Strike 2                | 12.5               |
| Strike 1 Premium        | 2.9                |
| Strike 2 Premium        | 3.4                |
| Cost                    | 0.5                |
| Cost Percent            | 3.7481             |
| Breakeven Lower         | 13.0               |
| Breakeven Lower Percent | -2.5487            |
| Breakeven Upper         | nan                |
| Breakeven Upper Percent | nan                |
| Max Profit              | 0.0                |
| Max Loss                | -0.5               |
| Payoff Ratio            | 0.0                |

```python
data.get_vertical_put_spread(30,13,12.5)
```

|                         | Bull Put Spread      |
|:------------------------|:---------------------|
| Symbol                  | VIX                  |
| Underlying Price        | 13.34                |
| Expiration              | 2023-08-16           |
| DTE                     | 31                   |
| Strike 1                | 13.0                 |
| Strike 2                | 12.5                 |
| Strike 1 Premium        | -0.17                |
| Strike 2 Premium        | 0.12                 |
| Cost                    | -0.05 |
| Cost Percent            | 0.3748               |
| Breakeven Lower         | nan                  |
| Breakeven Lower Percent | nan                  |
| Breakeven Upper         | 12.95                |
| Breakeven Upper Percent | 2.92    |
| Max Profit              | 0.05  |
| Max Loss                | -0.45 |
| Payoff Ratio            | 0.1111               |

#### `get_strategies()`

This takes all of the individual strategies and combines them into a single endpoint that can iterate over all expiry dates.

```python
data.get_strategies(days = 30, straddle_strike = data.last_price, strangle_moneyness = 30, vertical_calls = [20,15], vertical_puts = [12,15], synthetic_longs = 16, synthetic_shrots = 14)
```

|                         | 2023-08-16          | 2023-08-16        | 2023-08-16     | 2023-08-16      | 2023-08-16       | 2023-08-16         |
|:------------------------|:--------------------|:------------------|:---------------|:----------------|:-----------------|:-------------------|
| DTE                     | 31                  | 31                | 31             | 31              | 31               | 31                 |
| Strategy                | Long Straddle       | Long Strangle     | Synthetic Long | Synthetic Short | Bull Call Spread | Bear Put Spread    |
| Underlying Price        | 13.34               | 13.34             | 13.34          | 13.34           | 13.34            | 13.34              |
| Strike 1                | 13.5                | 17.0              | 14.0           | 16.0            | 20.0             | 12.0               |
| Strike 2                | 13.5                | 10.0              | 14.0           | 16.0            | 15.0             | 15.0               |
| Strike 1 Premium        | 2.62                | 1.28              | 2.31           | -1.46           | -0.83             | -0.04               |
| Strike 2 Premium        | 0.33                | 0.01              | -0.49          | 1.74            | 1.83             | 1.04               |
| Cost                    | 2.95                | 1.29              | 1.82           | 0.28            | 1.0              | 1.0                |
| Cost Percent            | 22.1139             | 9.6702            | 13.6432        | 2.099           | 7.4963           | 7.4963             |
| Breakeven Upper         | 16.45               | 18.29             | 15.82          | nan             | nan              | nan                |
| Breakeven Upper Percent | 23.3133  | 37.1064 | 18.5907        | nan             | nan              | nan                |
| Breakeven Lower         | 10.55               | 8.71              | nan            | 15.72           | 16.0             | 14.0               |
| Breakeven Lower Percent | -20.9145 | -34.7076          | nan            | 17.8411         | 19.94            | 17.5412 |
| Max Profit              | inf                 | inf               | inf            | 15.72           | 4.0              | 2.0                |
| Max Loss                | -2.95               | -1.29             | -15.82         | inf             | -1.0             | -1.0               |
| Payoff Ratio            | inf                 | inf               | nan            | nan             | 4.0              | 2.0                |

The default state of `get_strategies()` is to return all ATM straddles.  This information can be useful for charting the term structure and expected move of the underlying asset.

### Volatility

There are two types of views for volatility, smiles and surfaces.

#### `chart_volatility()`

As a default state, the put and call volatility smiles from the expiration in position 1, contained in the list `data.expirations[1]`, are displayed.

```python
data.chart_volatility()
```

![VIX IV Smile](https://github.com/deeleeramone/OpenBBTerminal/assets/85772166/1bf4534a-7ae8-4770-9b07-5e793889beb9)

The implied volatility can also be visualized as the forward curve at a specific strike or % moneyness.

```python
data.chart_volatility(strike=20)
```

![VIX Volatility at $20 Strike](https://github.com/deeleeramone/OpenBBTerminal/assets/85772166/e2b0dba6-2a51-4ff2-9e43-3667de15ae21)

```python
data.chart_volatility(moneyness=30)
```

![VIX Volatility at 30% OTM](https://github.com/deeleeramone/OpenBBTerminal/assets/85772166/c344724b-8544-4cd1-8cab-25e1924137a5)

#### `chart_surface()`

A portion, or the entire, volatility surface is presented as a 3-D chart. The data is arranged by types, selectable with the `option_type` parameter, choosing one of: `otm`, `itm`, `calls`, `puts`. The default state is `otm`. The X and Y axes can be narrowed to focus on a range of time and strike.

```python
data.chart_surface(dte_range = [30,300], strike_range = [10,30])
```

![VIX OTM IV Surface](https://github.com/deeleeramone/OpenBBTerminal/assets/85772166/410769fe-b7da-40bf-915e-68901b3caf13)

### Skew

Unlike volatility, there are both model and view components for the IV skew of the chain.

#### `get_skew()`

By default, this callable calculates the skew of every option.  It can return either vertical or horizontal skew.  Vertical skew can be narrowed to a specific expiry, and horizontal skew is determined by % OTM.

```python
data.get_skew(data.expirations[1]).query("12 <= `Strike` <= 15")
```

|     | Expiration   |   Strike | Option Type   |     IV |   ATM IV |    Skew |
|----:|:-------------|---------:|:--------------|-------:|---------:|--------:|
| 116 | 2023-07-26   |     12   | put           | 1.1136 |   0.9283 |  0.1853 |
| 117 | 2023-07-26   |     12.5 | put           | 1.0246 |   0.9283 |  0.0963 |
| 118 | 2023-07-26   |     13   | put           | 0.9666 |   0.9283 |  0.0383 |
| 119 | 2023-07-26   |     13.5 | put           | 0.9283 |   0.9283 |  0      |
| 120 | 2023-07-26   |     14   | call          | 0.4994 |   0.4994 |  0      |
| 121 | 2023-07-26   |     14   | put           | 0.8702 |   0.9283 | -0.0581 |
| 122 | 2023-07-26   |     14.5 | call          | 0.6156 |   0.4994 |  0.1162 |
| 123 | 2023-07-26   |     14.5 | put           | 0.8899 |   0.9283 | -0.0384 |
| 124 | 2023-07-26   |     15   | call          | 0.6245 |   0.4994 |  0.1251 |
| 125 | 2023-07-26   |     15   | put           | 0.9002 |   0.9283 | -0.0281 |

```python
vix.get_skew(moneyness=20)
```

| expiration   |   Call Strike |   Call IV |   Call ATM IV |   Call Skew |   Put Strike |   Put IV |   Put ATM IV |   Put Skew |   ATM Skew |   IV Skew |
|:-------------|--------------:|----------:|--------------:|------------:|-------------:|---------:|-------------:|-----------:|-----------:|----------:|
| 2023-07-19   |            16 |    1.0996 |        0.599  |      0.5006 |         10.5 |   1.0505 |       0.6328 |     0.4177 |    -0.0338 |    0.0829 |
| 2023-07-26   |            16 |    0.8708 |        0.4994 |      0.3714 |         10.5 |   0.9101 |       0.9283 |    -0.0182 |    -0.4289 |    0.3896 |
| 2023-08-02   |            16 |    0.855  |        0.5026 |      0.3524 |         10.5 |   0.7438 |       0.6755 |     0.0683 |    -0.1729 |    0.2841 |
| 2023-08-09   |            16 |    0.7861 |        0.4926 |      0.2935 |         10.5 |   0.6712 |       0.6575 |     0.0137 |    -0.1649 |    0.2798 |
| 2023-08-16   |            16 |    0.8364 |        0.6284 |      0.208  |         10.5 |   0.6041 |       0.6117 |    -0.0076 |     0.0167 |    0.2156 |
| 2023-08-23   |            16 |    0.9273 |        0.8918 |      0.0355 |         10.5 |   0.5492 |       0.6356 |    -0.0864 |     0.2562 |    0.1219 |
| 2023-09-20   |            16 |    0.7023 |        0.5481 |      0.1542 |         10   |   0.5344 |       0.548  |    -0.0136 |     0.0001 |    0.1678 |
| 2023-10-18   |            16 |    0.6447 |        0.5183 |      0.1264 |         10   |   0.4751 |       0.5178 |    -0.0427 |     0.0005 |    0.1691 |
| 2023-11-15   |            16 |    0.6064 |        0.5069 |      0.0995 |         10   |   0.4548 |       0.4947 |    -0.0399 |     0.0122 |    0.1394 |
| 2023-12-20   |            16 |    0.5716 |        0.4754 |      0.0962 |         10   |   0.426  |       0.4734 |    -0.0474 |     0.002  |    0.1436 |
| 2024-01-17   |            16 |    0.5224 |        0.4248 |      0.0976 |         10   |   0.4372 |       0.4372 |     0      |    -0.0124 |    0.0976 |
| 2024-02-14   |            16 |    0.494  |        0.4228 |      0.0712 |         10   |   0.4136 |       0.4258 |    -0.0122 |    -0.003  |    0.0834 |
| 2024-03-20   |            16 |    0.4533 |        0.4008 |      0.0525 |         10   |   0.4665 |       0.4162 |     0.0503 |    -0.0154 |    0.0022 |

#### chart_skew()

As a default state, the put and call skew smiles from the expiration in position 1, contained in the list `data.expirations[1]`, are displayed.

`data.chart_skew()`

![VIX IV Skew](https://github.com/deeleeramone/OpenBBTerminal/assets/85772166/509ac801-85bc-41e9-9f6c-7654e471db77)

Multiple expirations can be displayed by entering a list to the `expirations` parameter.

`data.chart_skew(expirations=[data.expirations[6],data.expirations[10]])`

![Multiple Expirations - VIX IV Skew](https://github.com/deeleeramone/OpenBBTerminal/assets/85772166/604407aa-bb0a-44dd-8051-0665ddb90b96)

The forward curve is also callable by strike.

`data.chart_skew(strike = 20)`

![VIX IV Skew at $20 Strike](https://github.com/deeleeramone/OpenBBTerminal/assets/85772166/949674b9-7366-4beb-b278-2ee5c0d5dd71)
