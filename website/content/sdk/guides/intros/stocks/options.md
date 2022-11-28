---
title: Options
keywords: ["stocks", "options", "calls", "puts", "gamma", "delta", "iv", "theta", "rho", "greeks", "charm", "vanna", "vomma", "derivatives", "contracts", "^SPX", "^VIX", "^NDX", "chains", "oi", "vol", "volume", "open", "interest", "expiration", "dte", "volatility", "underlying"]
excerpt: "This guide introduces the Stock Options module, within the context of the OpenBB SDK"
geekdocCollapseSection: true
---
The Stock Options module of the OpenBB SDK wraps the functions of the Options sub-menu within the [OpenBB Terminal](/terminal/guides/intros/stocks/options). This allows the user greater flexibility when researching and anlayzing options data. Start a Python script of Notebook file by importing the dependencies:

```python
from openbb_terminal.sdk import openbb

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt

%matplotlib widget
```

## How to Use

All functions within the Options module are printed with: `openbb.stocks.options`

![Options Module Functions](https://user-images.githubusercontent.com/85772166/199891549-1331a65c-6251-4206-b77c-c64dfabe70f4.png "Options Module Functions")

The [Unusual Options function](/sdk/reference/stocks/options/unu/) returns a Tuple containing the DataFrame and a timestamp from when the list was last updated.

```python
unusual_options,timestamp = openbb.stocks.options.unu()
unusual_options
```

![Unusual Options](https://user-images.githubusercontent.com/85772166/199891691-da3af87e-99c3-4d01-881f-62b6b0d3ae34.png "Unusual Options")

Get up to ten years of historical put/call ratios (US equity options only), with the `PCR` function:

```python
pcr_spy = openbb.stocks.options.pcr(symbol = 'SPY', start_date = '2012-11-03')
pcr_spy.rename(columns = {'PCR': 'Put/Call Ratio'})
```

![openbb.stocks.options.pcr](https://user-images.githubusercontent.com/85772166/199892365-f0ece3fa-307f-41cd-9326-d515f1d8b716.png "openbb.stocks.options.pcr")

The list of expiration dates is generated with:

```python
openbb.stocks.options.option_expirations('SPY')
```

Get the raw DataFrame for an options chain from yFinance by using:

```python
SPY221111 = openbb.stocks.options.chains_yf(symbol = 'SPY', expiry = '2022-11-11')

SPY221111
```

![openbb.stocks.options.chains_yf](https://user-images.githubusercontent.com/85772166/199900266-668af99d-ae72-4bca-9b40-14228b25279b.png "openbb.stocks.options.chains_yf")

Getting all option chains for the underlying symbol as a single Pandas DataFrame requires a little bit of scripting prior to analysis. This will query Tradier as the data source:

```python
from openbb_terminal.sdk import openbb
import pandas as pd
import numpy as np

expirations = openbb.stocks.options.option_expirations(symbol = 'SPY')
options_df: pd.DataFrame = []

for expirations in expirations:
    options_df.append(openbb.stocks.options.chains(symbol = 'SPY', expiry = expirations))

options_df = pd.concat(options_df)

options_df.set_index(keys = 'symbol', inplace = True)

options_df
```

Depending on the depth of options available, compiling the data may take upwards of thirty seconds.

![DataFrame With all Expirations](https://user-images.githubusercontent.com/85772166/199893166-35ef062d-c16e-464d-a392-378ef4c6a1ee.png "DataFrame With all Expirations")
