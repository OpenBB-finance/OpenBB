---
title: Introduction to Forex
keywords: "sdk, api, forex, fx, foreign, exchange, currency, pair, pairs, forward, rate, rates, eurodollar, usd, us, dollar, euro, yen, franc, central, bank, currencies, oanda"
excerpt: "This guide introduces the Forex module, within the OpenBB SDK, and provides examples."
geekdocCollapseSection: true
---
The Forex module provides a way for users to get currency pair data, from a number of sources. API keys for them are handled by the [Keys module](https://openbb-finance.github.io/OpenBBTerminal/SDK/keys/). After importing the entire OpenBB SDK, no further action is required to authorize the sources. This module also provides Oanda account holders [additional functionality](https://openbb-finance.github.io/OpenBBTerminal/terminal/forex/oanda/).

For the purpose of demonstration, additional modules will be imported to begin the Python script or Notebook file.

```python
from openbb_terminal.sdk import openbb

import pandas as pd

%matplotlib inline
```

![The Forex Module](https://user-images.githubusercontent.com/85772166/199393284-bf9e2f57-4041-4304-9679-69ac07816fe4.png "The Forex Module")

## How to Use

To load historical data for a desired currency pair, copy and paste the code below:

```python
currency_pair = openbb.forex.load(
    from_symbol='USD',
    to_symbol='EUR',
    source = 'Polygon',
    start_date = '2000-01-01',
    resolution = 'd',
    interval = '1day',
    )
```

Note that `source` can be any of: AlphaVantage, Oanda, Polygon, or, YahooFinance. It returns a Pandas DataFrame:

![openbb.forex.load](https://user-images.githubusercontent.com/85772166/199393745-9c57b9d1-2613-4350-b6c2-a291ee5d9ee9.png "openbb.forex.load")

Cached as a DataFrame, it can then be passed along to any time-series function within the OpenBB SDK; such as, the [Technical Analysis](https://openbb-finance.github.io/OpenBBTerminal/terminal/common/ta/) and [Quantitative Analysis](https://openbb-finance.github.io/OpenBBTerminal/terminal/common/qa/) modules. Pandas can also be used to further process data, for example, using the cached example above:

```python
daily_range = pd.DataFrame(columns = ['range'])

daily_range.range = currency_pair['High']-currency_pair['Low']

openbb.common.qa.bw(daily_range, target = 'range', symbol = 'Daily Variance EUR/USD')

```

![Box Plot of Yearly EUR/USD Variance](https://user-images.githubusercontent.com/85772166/199393844-bb177938-d1b4-4e95-bdcd-5c415508f391.png "Box Plot of Yearly EUR/USD Variance")

One free set of data, from the Oanda subset of functions, is the current forward rates of a currency pair. Data is returned as a table, for example:

```python
openbb.forex.oanda.fwd(from_symbol = 'EUR', to_symbol = 'USD')
```

![openbb.forex.oanda.fwd](https://user-images.githubusercontent.com/85772166/199394298-466b350d-5574-401e-a750-d645192e3db6.png "openbb.forex.oanda.fwd")

This code snippet returns a Pandas DataFrame containing forward points for two currency pairs, JPY/USD & USD/EUR:

```python
from openbb_terminal.sdk import openbb

import pandas as pd

JPYUSD = openbb.forex.oanda.fwd(to_symbol='JPY', from_symbol='USD')
Expiration = list(JPYUSD.index)
JPYUSD_points = list(JPYUSD.Points)
USDEUR = openbb.forex.oanda.fwd(to_symbol='USD', from_symbol='EUR')
USDEUR_points = list(USDEUR.Points)

fwd_spread = Expiration,JPYUSD_points,USDEUR_points

pair_spreads = pd.DataFrame.from_dict(fwd_spread).transpose()
pair_spreads = pair_spreads.reset_index()

pd.DataFrame(pair_spreads).rename(columns = {
    0: "Expiration",
    1: "JPY/USD Points",
    2: "USD/EUR Points",
    }, inplace = True)

pair_spreads.set_index(['Expiration'], inplace = True)

pair_spreads = pd.DataFrame(pair_spreads, columns = ['JPY/USD Points', 'USD/EUR Points'])

pair_spreads
```
![Points Spread](https://user-images.githubusercontent.com/85772166/199394778-a4aa6e9f-af18-42c3-b9af-43cf9a037508.png "Comparing JPY/USD USD/EUR Points")
