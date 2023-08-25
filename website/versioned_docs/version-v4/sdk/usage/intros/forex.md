---
title: Forex
keywords: [forex, currency, money, hedge, dollar, euro, pound, currencies, market, openbb sdk, how to, usage, examples, import statement, load, average true range, forward rate, path, type, description]
description: The Forex menu enables you to load any combination of currencies (e.g. USDEUR or JPYGBP), show current quote and historical data as well as forward rates.
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Forex - SDK | OpenBB Docs" />

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
```

### Load

The `load` function has the ability to request data from multiple sources:

- AlphaVantage
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

### Quote

Get real-time exchange rates.

```python
openbb.forex.quote("EURUSD", source = "AlphaVantage")
```

|                       | Realtime Currency Exchange Rate   |
|:----------------------|:----------------------------------|
| 1. From_Currency Code | USD                               |
| 2. From_Currency Name | United States Dollar              |
| 3. To_Currency Code   | EUR                               |
| 4. To_Currency Name   | Euro                              |
| 5. Exchange Rate      | 0.91580000                        |
| 6. Last Refreshed     | 2023-07-03 17:00:01               |
| 7. Time Zone          | UTC                               |
| 8. Bid Price          | 0.91576000                        |
| 9. Ask Price          | 0.91580000                        |

### Forward Rates

```python
fwd_usdeur = openbb.forex.fwd('EUR', 'USD')

fwd_usdeur
```

| Expiration    |     Ask |     Bid |     Mid |   Points |
|:--------------|--------:|--------:|--------:|---------:|
| Overnight     | 0.91608 | 0.91602 | 0.91605 |   -0.825 |
| Tomorrow Next | 0.91608 | 0.91601 | 0.91604 |   -0.855 |
| Spot Next     | 0.91612 | 0.91606 | 0.91609 |   -0.425 |
| One Week      | 0.91586 | 0.9158  | 0.91583 |   -2.995 |
| Two Weeks     | 0.91557 | 0.9155  | 0.91553 |   -5.985 |
| Three Weeks   | 0.91526 | 0.91519 | 0.91523 |   -9.05  |
| One Month     | 0.9147  | 0.91463 | 0.91466 |  -14.685 |
| Two Months    | 0.91339 | 0.91331 | 0.91335 |  -27.81  |
| Three Months  | 0.91201 | 0.91194 | 0.91198 |  -41.54  |
| Four Months   | 0.91064 | 0.91055 | 0.9106  |  -55.34  |
| Five Months   | 0.90939 | 0.9093  | 0.90934 |  -67.885 |
| Six Months    | 0.90743 | 0.90732 | 0.90737 |  -87.555 |
| Seven Months  | 0.90616 | 0.90604 | 0.9061  | -100.32  |
| Eight Months  | 0.90501 | 0.90489 | 0.90495 | -111.795 |
| Nine Months   | 0.9037  | 0.90358 | 0.90364 | -124.88  |
| Ten Months    | 0.90254 | 0.9024  | 0.90247 | -136.6   |
| Eleven Months | 0.90146 | 0.90132 | 0.90139 | -147.375 |
| One Year      | 0.90041 | 0.90025 | 0.90033 | -158.025 |
| Two Years     | 0.89063 | 0.89017 | 0.8904  | -257.31  |

Currency pairs will have different term structure composition in the other direction:

```python
fwd_eurusd = openbb.forex.fwd('USD', 'EUR')

fwd_eurusd
```

| Expiration    |     Ask |     Bid |     Mid |    Points |
|:--------------|--------:|--------:|--------:|----------:|
| Overnight     | 1.09166 | 1.09164 | 1.09165 |    0.985  |
| Tomorrow Next | 1.09161 | 1.09159 | 1.0916  |    0.515  |
| Spot Next     | 1.09161 | 1.09159 | 1.0916  |    0.5085 |
| One Week      | 1.09192 | 1.09189 | 1.09191 |    3.565  |
| Two Weeks     | 1.09228 | 1.09225 | 1.09226 |    7.13   |
| Three Weeks   | 1.09264 | 1.09261 | 1.09263 |   10.78   |
| One Month     | 1.09332 | 1.09329 | 1.09331 |   17.549  |
| Two Months    | 1.09488 | 1.09484 | 1.09486 |   33.14   |
| Three Months  | 1.09655 | 1.0965  | 1.09653 |   49.7665 |
| Four Months   | 1.09822 | 1.09815 | 1.09818 |   66.32   |
| Five Months   | 1.09974 | 1.09967 | 1.09971 |   81.56   |
| Six Months    | 1.10215 | 1.10208 | 1.10211 |  105.6    |
| Seven Months  | 1.10372 | 1.1036  | 1.10366 |  121.08   |
| Eight Months  | 1.10512 | 1.105   | 1.10506 |  135.06   |
| Nine Months   | 1.10673 | 1.10661 | 1.10667 |  151.23   |
| Ten Months    | 1.10817 | 1.10805 | 1.10811 |  165.64   |
| Eleven Months | 1.10951 | 1.10941 | 1.10946 |  179.09   |
| One Year      | 1.11082 | 1.1107  | 1.11076 |  192.08   |
| Two Years     | 1.12338 | 1.12296 | 1.12317 |  316.24   |
| Three Years   | 1.13422 | 1.1332  | 1.13371 |  421.62   |
| Four Years    | 1.14476 | 1.14374 | 1.14425 |  527      |
| Five Years    | 1.15647 | 1.15445 | 1.15546 |  639.1    |
| Six Years     | 1.16796 | 1.16644 | 1.1672  |  756.5    |
| Seven Years   | 1.17936 | 1.17734 | 1.17835 |  868      |
| Ten Years     | 1.21166 | 1.20664 | 1.20915 | 1176      |

Not all currency pairs will have the same length of term structure.

```python
fwd_eurjpy = openbb.forex.fwd('JPY', 'EUR')
fwd_pairs = fwd_eurjpy.join(fwd_usdeur, on = ['Expiration'], lsuffix = ' EUR/JPY', rsuffix=' USD/EUR')

fwd_pairs
```

| Expiration    |   Ask EUR/JPY |   Bid EUR/JPY |   Mid EUR/JPY |   Points EUR/JPY |   Ask USD/EUR |   Bid USD/EUR |   Mid USD/EUR |   Points USD/EUR |
|:--------------|--------------:|--------------:|--------------:|-----------------:|--------------:|--------------:|--------------:|-----------------:|
| Overnight     |       157.959 |       157.951 |       157.955 |           -3.17  |       0.91608 |       0.91602 |       0.91605 |           -0.825 |
| Tomorrow Next |       157.959 |       157.951 |       157.955 |            0     |       0.91608 |       0.91601 |       0.91604 |           -0.855 |
| Spot Next     |       157.959 |       157.951 |       157.955 |           -1.585 |       0.91612 |       0.91606 |       0.91609 |           -0.425 |
| One Week      |       157.958 |       157.95  |       157.954 |          -11.12  |       0.91586 |       0.9158  |       0.91583 |           -2.995 |
| Two Weeks     |       157.957 |       157.949 |       157.953 |          -22.34  |       0.91557 |       0.9155  |       0.91553 |           -5.985 |
| Three Weeks   |       157.956 |       157.948 |       157.952 |          -33.41  |       0.91526 |       0.91519 |       0.91523 |           -9.05  |
| One Month     |       157.954 |       157.946 |       157.95  |          -53.221 |       0.9147  |       0.91463 |       0.91466 |          -14.685 |
| Two Months    |       157.949 |       157.941 |       157.945 |         -102.35  |       0.91339 |       0.91331 |       0.91335 |          -27.81  |
| Three Months  |       157.944 |       157.936 |       157.94  |         -153.575 |       0.91201 |       0.91194 |       0.91198 |          -41.54  |
| Four Months   |       157.938 |       157.93  |       157.934 |         -209.635 |       0.91064 |       0.91055 |       0.9106  |          -55.34  |
| Five Months   |       157.933 |       157.925 |       157.929 |         -260.55  |       0.90939 |       0.9093  |       0.90934 |          -67.885 |
| Six Months    |       157.927 |       157.919 |       157.923 |         -318.365 |       0.90743 |       0.90732 |       0.90737 |          -87.555 |
| Seven Months  |       157.922 |       157.913 |       157.918 |         -374.29  |       0.90616 |       0.90604 |       0.9061  |         -100.32  |
| Eight Months  |       157.917 |       157.908 |       157.912 |         -425.68  |       0.90501 |       0.90489 |       0.90495 |         -111.795 |
| Nine Months   |       157.911 |       157.903 |       157.907 |         -479.26  |       0.9037  |       0.90358 |       0.90364 |         -124.88  |
| Ten Months    |       157.906 |       157.897 |       157.901 |         -536.525 |       0.90254 |       0.9024  |       0.90247 |         -136.6   |
| Eleven Months |       157.9   |       157.892 |       157.896 |         -586.775 |       0.90146 |       0.90132 |       0.90139 |         -147.375 |
| One Year      |       157.895 |       157.887 |       157.891 |         -637.185 |       0.90041 |       0.90025 |       0.90033 |         -158.025 |
| Two Years     |       157.841 |       157.831 |       157.836 |        -1190.55  |       0.89063 |       0.89017 |       0.8904  |         -257.31  |
