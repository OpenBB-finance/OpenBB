---
title: Forex
---
The Forex module provides a way for users to get currency pair data, from a number of sources. API keys for them are handled by the Keys module. After importing the entire OpenBB SDK, no further action is required to authorize the sources. This module also provides Oanda account holders with broker integration.

## How to Use

Below is a brief description of each function within the Forex module:

|Path |Type |Description |
|:------------------------------|:----------:|------------------------------:|
|openbb.forex.candle |Function |OHLC Chart & Optional Moving Averages |
|openbb.forex.fwd |Function |Forward Rates of Currency Pairs |
|openbb.forex.get_currency_list |List |List of Currency Symbols |
|openbb.forex.load |Function |Load Historical OHLC Data for Currency Pairs |
|openbb.forex.oanda |Sub-Module |Oanda Broker Integration |
|openbb.forex.quote |Function |Realtime Currency Exchange Rate |

The contents of the menu is printed with:

```python
help(openbb.forex)
```

## Examples

### Import Statements

The examples in this guide will assume that the import statements below are present:

```python
from openbb_terminal.sdk import openbb
import pandas as pd
%matplotlib inline
```

### Load

The `load` function has the ability to request data from multiple sources:

- AlphaVantage
- Oanda
- Polygon
- YahooFinance (default)

Using the default source:

```python
currency_pair = openbb.forex.load(
    from_symbol='USD',
    to_symbol='EUR',
    start_date = '2000-01-01',
    interval = '1week')

currency_pair.head(3)
```

| date                |    Open |    High |     Low |   Close |   Adj Close |   Volume |
|:--------------------|--------:|--------:|--------:|--------:|------------:|---------:|
| 2003-12-01 00:00:00 | 0.83098 | 0.83724 | 0.82028 | 0.82163 |     0.82163 |        0 |
| 2003-12-08 00:00:00 | 0.82183 | 0.82488 | 0.81261 | 0.82068 |     0.82068 |        0 |
| 2003-12-15 00:00:00 | 0.82055 | 0.82115 | 0.80373 | 0.80919 |     0.80919 |        0 |

To use an alternate source, add the `source` argument to the syntax:

```python
currency_pair = openbb.forex.load(
    from_symbol= 'USD',
    to_symbol= 'EUR',
    source = 'Polygon',
    start_date = '2000-01-01',
    interval = '1week')

currency_pair.head(3)
```

| date                |   Volume |     vw |   Open |   Close |    High |     Low |   Transactions |
|:--------------------|---------:|-------:|-------:|--------:|--------:|--------:|---------------:|
| 2012-01-29 00:00:00 |     3758 | 0.761  | 0.7565 |  0.7597 | 0.7676  | 0.7565  |           3758 |
| 2012-02-05 00:00:00 |     5605 | 0.7566 | 0.762  |  0.7581 | 0.7672  | 0.75081 |           5605 |
| 2012-02-12 00:00:00 |     9045 | 0.7611 | 0.757  |  0.7603 | 0.77053 | 0.75278 |           9045 |

The amount and granularity of historical data available will vary by source. The two tables above illustrate some of those differences.

### Average True Range

The loaded data can now be used as inputs for other functions and calculations, such as the average true range over a four week window.

```python
weekly_atr = openbb.ta.atr(data = currency_pair, window = 4)
currency_pair = currency_pair.join(weekly_atr)

currency_pair.tail(1)
```

| date                |   Volume |    vw |    Open |   Close |    High |   Low |   Transactions |    ATRe_4 |
|:--------------------|---------:|------:|--------:|--------:|--------:|------:|---------------:|----------:|
| 2022-11-13 00:00:00 |   481918 | 0.965 | 0.96479 | 0.96205 | 0.97351 | 0.954 |         481918 | 0.0281756 |

### Forward Rates

```python
fwd_usdeur = openbb.forex.fwd('EUR', 'USD')

fwd_usdeur
```

| Expiration    |     Ask |     Bid |     Mid |   Points |
|:--------------|--------:|--------:|--------:|---------:|
| Overnight     | 0.96194 | 0.96188 | 0.96191 |   -0.645 |
| Tomorrow Next | 0.96194 | 0.96187 | 0.9619  |   -0.655 |
| Spot Next     | 0.9618  | 0.96174 | 0.96177 |   -1.97  |
| One Week      | 0.96154 | 0.96148 | 0.96151 |   -4.61  |
| Two Weeks     | 0.96108 | 0.96101 | 0.96104 |   -9.265 |
| Two Years     | 0.92285 | 0.92237 | 0.92261 | -393.605 |

Currency pairs will have different term structure composition in the other direction:

```python
fwd_eurusd = openbb.forex.fwd('USD', 'EUR')

fwd_eurusd
```

| Expiration   |     Ask |     Bid |     Mid |   Points |
|:-------------|--------:|--------:|--------:|---------:|
| One Year     | 1.06639 | 1.06589 | 1.06614 |    263.9 |
| Two Years    | 1.0874  | 1.0867  | 1.08705 |    473   |
| Three Years  | 1.10033 | 1.09933 | 1.09983 |    600.8 |
| Four Years   | 1.10774 | 1.10544 | 1.10659 |    668.4 |
| Five Years   | 1.11918 | 1.11588 | 1.11753 |    777.8 |
| Six Years    | 1.1267  | 1.1239  | 1.1253  |    855.5 |
| Seven Years  | 1.1372  | 1.1334  | 1.1353  |    955.5 |
| Ten Years    | 1.1652  | 1.1584  | 1.1618  |   1220.5 |

Not all currency pairs will have the same length of term structure.

```python
fwd_jpyeur = openbb.forex.oanda.fwd('JPY', 'EUR')
fwd_pairs = fwd_jpyeur.join(fwd_usdeur, on = ['Expiration'], lsuffix = ' JPY/EUR', rsuffix=' USD/EUR')

fwd_pairs
```

| Expiration    |   Ask JPY/EUR |   Bid JPY/EUR |   Mid JPY/EUR |   Points JPY/EUR |   Ask USD/EUR |   Bid USD/EUR |   Mid USD/EUR |   Points USD/EUR |
|:--------------|--------------:|--------------:|--------------:|-----------------:|--------------:|--------------:|--------------:|-----------------:|
| Overnight     |       144.994 |       144.982 |       144.988 |          -0.565  |       0.96194 |       0.96188 |       0.96191 |           -0.645 |
| Tomorrow Next |       144.994 |       144.982 |       144.988 |          -1.775  |       0.96194 |       0.96187 |       0.9619  |           -0.655 |
| Spot Next     |       144.994 |       144.982 |       144.988 |          -0.585  |       0.9618  |       0.96174 |       0.96177 |           -1.97  |
| One Week      |       144.994 |       144.982 |       144.988 |          -4.23   |       0.96154 |       0.96148 |       0.96151 |           -4.61  |
| Two Weeks     |       144.993 |       144.981 |       144.987 |          -8.73   |       0.96108 |       0.96101 |       0.96104 |           -9.265 |
| Three Weeks   |       144.993 |       144.981 |       144.987 |         -13.08   |       0.96061 |       0.96055 |       0.96058 |          -13.905 |
| One Month     |       144.992 |       144.98  |       144.986 |         -18.6865 |       0.95989 |       0.95982 |       0.95985 |          -21.155 |
| Two Months    |       144.989 |       144.977 |       144.983 |         -46.995  |       0.95697 |       0.95689 |       0.95693 |          -50.445 |
| Three Months  |       144.987 |       144.974 |       144.981 |         -73.347  |       0.95468 |       0.95459 |       0.95463 |          -73.39  |
| Four Months   |       144.984 |       144.972 |       144.978 |        -103.125  |       0.95291 |       0.95281 |       0.95286 |          -91.11  |
