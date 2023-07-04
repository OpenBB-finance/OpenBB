---
title: Options Chains
keywords: [OpenBB, sdk, Options, stocks, derivatives, puts, calls, oi, vol, greeks, voi, volatility,  chains, usage, iv, gamma, delta, theta, strategies, skew, straddle, strangle, spread, vertical, horizontal]
excerpt: This guide introduces the Options class and data object.
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Options Chains - SDK | OpenBB Docs" />

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
-------
Object: Options
    chains: pd.DataFrame
        The complete options chain for the ticker.
    expirations: list[str]
        List of unique expiration dates. (YYYY-MM-DD)
    strikes: list[float]
        List of unique strike prices.
    last_price: float
        The last price of the underlying asset.
    underlying_name: str
        The name of the underlying asset.
    underlying_price: pd.Series
        The price and recent performance of the underlying asset.
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
        The symbol directory for the source, when available.

        Methods
        -------
        get_stats: Callable
            Function to get a table of summary statistics, by strike or by expiration.
        get_straddle: Callable
            Function to get straddles and the payoff profile.
        get_strangle: Callable
            Function to calculate strangles and the payoff profile.
        get_vertical_call_spread: Callable
            Function to get vertical call spreads.
        get_vertical_put_spreads: Callable
            Function to get vertical put spreads.
        get_strategies: Callable
            Function to get multiple straddles and strangles at different expirations and moneyness.
        get_skew: Callable
            Function to get the vertical or horizontal skewness of the options.
```

## How to Use

### `load_options_chains()`

The default source to load data from is, `CBOE`.  Use the command below to get started.

```python
from openbb_terminal.sdk import openbb
spy = openbb.stocks.options.load_options_chains("SPY")
```

The result is returned as the object described in the previous section.

![Options Data Object](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/fd581725-15aa-4ede-b302-10acac387f5c)

The object is still returned if an unsupported symbol is requested and a message will be printed.

```python
In [14]: data = openbb.stocks.options.load_options_chains("spyyy")
The symbol, SPYYY, was not found in the CBOE directory.

In [15]: data.chains
Out[15]: pandas.core.frame.DataFrame
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
In [28]: data.underlying_price
Out[28]: 
type                                 stock
tick                                  down
bid                                 439.46
bidSize                                 69
askSize                                  4
ask                                  439.6
price                               439.46
open                                442.95
high                              443.6078
low                                 438.97
close                               439.46
volume                           114143567
previousClose                       439.46
change                               -3.14
changePercent                      -0.7145
ivThirty                            11.285
ivThirtyChange                       0.075
lastTradeTimestamp     2023-06-16T16:00:00
ivThirtyOneYearHigh              30.646999
hvThirtyOneYearHigh              31.074301
ivThirtyOneYearLow                  10.707
hvThirtyOneYearLow                 11.7216
ivSixtyOneYearHigh               28.674999
hvSixtyOneYearHigh                 29.5842
ivSixtyOneYearLow                   11.723
hvsixtyOneYearLow                  11.9912
ivNinetyOneYearHigh                 27.862
hvNinetyOneYearHigh                27.1943
ivNinetyOneYearLow                  12.278
hvNinetyOneYearLow                 14.2944
Name: SPY, dtype: object
```

TMX:

```python
In [29]: data = openbb.stocks.options.load_options_chains("XIU", "TMX")

In [30]: data.underlying_price
Out[30]: 
time                14:34:44.970
previousClose              30.38
transactions                 181
volume                     23932
value                     725365
valueCAD                  725365
open                       30.35
price                      30.32
change                     -0.06
changePercent               -0.2
tick                        0.01
low                        30.27
high                       30.35
vwap                       30.31
fiftyTwoWeekHigh           31.86
fiftyTwoWeekLow           27.375
Name: XIU, dtype: object
```

Not every source will return implied volatility or Greeks data.  The two object attributes, `hasGreeks` and `hasIV`, act as validators for downstream functions.

```python
In [31]: data.hasIV
Out[31]: False

In [32]: data.get_skew()
Options data object does not have Implied Volatility and is required for this function.
```

#### Historical EOD Chains

Historical EOD chains data is currently available from `Intrinio` or `TMX`.  The amount of historical data will depend on the subscription status with `Intrinio`, but is available from the beginning of 2009 from `TMX`.  Add the `date` argument when loading the data.  The price data of the underlying asset will reflect the closing price on the date entered.

```python
In [35]: data = openbb.stocks.options.load_options_chains("CCO", "TMX", date = "2016-06-29")

In [36]: data.underlying_price
Out[36]: 
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

### Additional Class Methods

The class methods work with the Options data object to query the loaded chains data in different ways.  Column headers at this stage are cleaned and presentable for view.

```python
vix = openbb.stocks.options.load_options_chains("vix")
```

![VIX Options Chains](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/f9ba96fe-6726-49bf-8e41-c38daa045f38)

#### `get_stats()`

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
In [13]: vix.get_stats().iloc[0]
Out[13]: 
Puts OI         1826742.00
Calls OI        3959642.00
Total OI        5786384.00
OI Ratio              0.46
Puts OTM         234220.00
Calls OTM       3940976.00
Puts ITM        1592522.00
Calls ITM         18666.00
OTM Ratio             0.06
ITM Percent          27.84
Puts Volume      133712.00
Calls Volume     192200.00
Total Volume     325912.00
Volume Ratio          0.70
Vol-OI Ratio          0.06
Name: 2023-06-21, dtype: float64
```

The `query` parameter provides an entry point for DataFrame operations to take place prior to calculating.  For example, filtering for only the options which traded during the last session.

```python
vix.get_stats(query = vix.chains[vix.chains["lastTradeTimestamp"] > "2023-06-16"])
```

| Expiration   |          Puts OI |         Calls OI |         Total OI |   OI Ratio |   Puts Volume |   Calls Volume |   Total Volume |   Volume Ratio |   Vol-OI Ratio |
|:-------------|-----------------:|-----------------:|-----------------:|-----------:|--------------:|---------------:|---------------:|---------------:|---------------:|
| 2023-06-21   |    1818770 |      3302044 |      5120814 |       0.55 |        133712 |         192200 |         325912 |           0.7  |           0.06 |
| 2023-06-28   |   2991           |  16053           |  19044           |       0.19 |           914 |           2578 |           3492 |           0.35 |           0.18 |
| 2023-07-05   |   2597           |   5618           |   8215           |       0.46 |            62 |           1200 |           1262 |           0.05 |           0.15 |
| 2023-07-12   |    612           |   2052           |   2664           |       0.3  |           121 |            547 |            668 |           0.22 |           0.25 |
| 2023-07-19   | 936874           |      2557905  |      3494779 |       0.37 |        154543 |         159949 |         314492 |           0.97 |           0.09 |
| 2023-07-26   |      5           |    356           |    361           |       0.01 |             5 |            304 |            309 |           0.02 |           0.86 |
| 2023-08-16   | 493541           |      1734097  |      2227638 |       0.28 |         23490 |          35505 |          58995 |           0.66 |           0.03 |
| 2023-09-20   | 452010           |      1903413 |     2355423 |       0.24 |         30856 |          68592 |          99448 |           0.45 |           0.04 |
| 2023-10-18   |  96489           | 593946           | 690435           |       0.16 |          3083 |           2202 |           5285 |           1.4  |           0.01 |
| 2023-11-15   |  72737           | 251719           | 324456           |       0.29 |          3786 |          14937 |          18723 |           0.25 |           0.06 |
| 2023-12-20   |  32617           | 132189           | 164806           |       0.25 |           650 |          27993 |          28643 |           0.02 |           0.17 |
| 2024-01-17   |  10002           |  48855           |  58857           |       0.2  |          4179 |          16991 |          21170 |           0.25 |           0.36 |
| 2024-02-14   |    219           |   5936           |   6155           |       0.04 |            21 |            730 |            751 |           0.03 |           0.12 |

#### `get_straddle`, `get_strangle`, `get_vertical_call_spread`, `get_vertical_put_spread`

These are common single-leg strategies that return one result.  The target expiry date is expressed as the number of days until expiration.  All four have a `days` parameter with a default of thirty-days, and the spreads require two strikes. User-supplied inputs do not have to be valid choices, they will be estimated using internal helper functions for the nearest strike prices and DTE.

- Call/Put spreads have: `sold_strike`, `bought_strike`.  Bullish and Bearish are decided by the sold strike being higher or lower than the bought price.  Strike 1 is the `sold_strike`; Strike 2 is the `bought_strike`.
- `get_straddle` has a parameter, `strike`, which by default is the last price of the underlying.  A short straddle can be returned by entering a negative value for the `strike`.  Strike 1 is the call; Strike 2 is the put.
- `get_strangle` has a similar parameter, except as `moneyness`.  This returns the upper/lower OTM strike values for the call and put.  A short strangle is returned by entering a negative value for `moneyness`.  Strike 1 is the call; Strike 2 is the put.

```python
In [20]: vix.get_strangle(5)
Out[20]: 
                        Long Strangle
Symbol                            VIX
Underlying Price                14.19
Expiration                 2023-06-21
DTE                                 2
Strike 1                         15.0
Strike 2                         13.0
Strike 1 Premium                 0.33
Strike 2 Premium                 0.08
Cost                             0.41
Cost Percent                   2.8894
Breakeven Upper                 15.41
Breakeven Upper Percent        8.5976
Breakeven Lower                 12.59
Breakeven Lower Percent      -11.2755
Max Profit                        inf
Max Loss                        -0.41
Payoff Ratio                      inf
```

#### `get_strategies()`

This takes all of the individual strategies and combines them into a single endpoint that can iterate over all expiry dates.

```python
vix.get_strategies(days = 42, strangle_moneyness=[5,-10], vertical_calls = [20,18]).transpose()
```

| Expiration              | 2023-07-26    | 2023-07-26         | 2023-07-26          | 2023-07-26         |
|:------------------------|:--------------|:-------------------|:--------------------|:-------------------|
| DTE                     | 37            | 37                 | 37                  | 37                 |
| Strategy                | Long Strangle | Short Strangle     | Bull Call Spread    | Bear Put Spread    |
| Underlying Price        | 14.19         | 14.19              | 14.19               | 14.19              |
| Strike 1                | 15.0          | 16.0               | 16.0                | 10.0               |
| Strike 2                | 13.0          | 13.0               | 14.0                | 14.0               |
| Strike 1 Premium        | 3.93          | 1.46               | 1.46                | 0.0                |
| Strike 2 Premium        | 0.24          | 0.0                | 4.74                | 0.44               |
| Cost                    | 4.17          | -1.46              | 3.28  | 0.44               |
| Cost Percent            | 29.3869       | 10.2889            | 23.1149             | 3.1008             |
| Breakeven Upper         | 19.17         | 17.46              | nan                 | nan                |
| Breakeven Upper Percent | 35.0951       | 23.0444 | nan                 | nan                |
| Breakeven Lower         | 8.83          | 11.54              | 17.28               | 13.56              |
| Breakeven Lower Percent | -37.7731      | -18.6751           | 21.7759             | 32.6287 |
| Max Profit              | inf           | 1.46               | -1.28 | 3.56               |
| Max Loss                | -4.17         | inf                | -3.28 | -0.44              |
| Payoff Ratio            | inf           | 0.0                | 0.3902              | 8.0909             |

The default state of `get_strategies()` is to return all ATM straddles.  This information can be useful for charting the term structure and expected move of the underlying asset.

```python
structure = data.get_strategies()[["Expiration", "Cost"]].set_index("Expiration")
openbb.qa.line(structure["Cost"], title = "Cost of ATM VIX Straddle", log_y= False)
```

![Cost of Straddle](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/4d16778c-78bb-44e3-8068-3ba1ceca44c3)

Additional strategies will be added in the future.

#### `get_skew()`

By default, this callable calculates the skew of every option.  It can return either vertical or horizontal skew.  Vertical skew can be narrowed to a specific expiry, and horizontal skew is determined by % OTM.

```python
vix.get_skew("2023-06-21")
```

| Expiration   |   Strike | Option Type   |     IV |    Skew |
|:-------------|---------:|:--------------|-------:|--------:|
| 2023-06-21   |       10 | call          | 1.2749 |  0.5981 |
| 2023-06-21   |       10 | put           | 1.3512 |  0.6414 |
| 2023-06-21   |       11 | call          | 0.9428 |  0.266  |
| 2023-06-21   |       11 | put           | 1.0314 |  0.3216 |
| 2023-06-21   |       12 | call          | 0.9604 |  0.2836 |
| 2023-06-21   |       12 | put           | 1.0147 |  0.3049 |
| 2023-06-21   |       13 | call          | 0.671  | -0.0058 |
| 2023-06-21   |       13 | put           | 0.7065 | -0.0033 |
| 2023-06-21   |       14 | call          | 0.6768 |  0      |
| 2023-06-21   |       14 | put           | 0.7098 |  0      |

```python
vix.get_skew(moneyness=20)
```

| expiration   |   Call Strike |   Call IV |   Call ATM IV |   Call Skew |   Put Strike |   Put IV |   Put ATM IV |   Put Skew |   ATM Skew |   IV Skew |
|:-------------|--------------:|----------:|--------------:|------------:|-------------:|---------:|-------------:|-----------:|-----------:|----------:|
| 2023-06-21   |            17 |    1.6378 |        0.9257 |      0.7121 |           11 |   1.6498 |       0.8968 |     0.753  |     0.0289 |   -0.0409 |
| 2023-06-28   |            17 |    1      |        0.5025 |      0.4975 |           11 |   1.0319 |       0.8148 |     0.2171 |    -0.3123 |    0.2804 |
| 2023-07-05   |            17 |    0.8918 |        0.606  |      0.2858 |           11 |   0.8285 |       0.7384 |     0.0901 |    -0.1324 |    0.1957 |
| 2023-07-12   |            17 |    0.7042 |        0.5777 |      0.1265 |           11 |   0.7267 |       0.6661 |     0.0606 |    -0.0884 |    0.0659 |
| 2023-07-19   |            17 |    0.8596 |        0.6367 |      0.2229 |           11 |   0.6395 |       0.6491 |    -0.0096 |    -0.0124 |    0.2325 |
| 2023-07-26   |            17 |    0.6861 |        0.401  |      0.2851 |           11 |   0.6581 |       0.6783 |    -0.0202 |    -0.2773 |    0.3053 |
| 2023-08-16   |            17 |    0.7509 |        0.5939 |      0.157  |           11 |   0.5296 |       0.5886 |    -0.059  |     0.0053 |    0.216  |
| 2023-09-20   |            17 |    0.6463 |        0.5248 |      0.1215 |           11 |   0.4893 |       0.5313 |    -0.042  |    -0.0065 |    0.1635 |
| 2023-10-18   |            17 |    0.5949 |        0.5326 |      0.0623 |           11 |   0.4496 |       0.5    |    -0.0504 |     0.0326 |    0.1127 |
| 2023-11-15   |            17 |    0.5506 |        0.4747 |      0.0759 |           11 |   0.559  |       0.4756 |     0.0834 |    -0.0009 |   -0.0075 |
| 2023-12-20   |            17 |    0.5206 |        0.4523 |      0.0683 |           11 |   0.5264 |       0.4428 |     0.0836 |     0.0095 |   -0.0153 |
| 2024-01-17   |            17 |    0.4887 |        0.4599 |      0.0288 |           11 |   0.5298 |       0.4288 |     0.101  |     0.0311 |   -0.0722 |
| 2024-02-14   |            17 |    0.4999 |        0.4683 |      0.0316 |           11 |   0.4704 |       0.422  |     0.0484 |     0.0463 |   -0.0168 |
