---
title: Introduction to Technical Analysis
keywords: "ta, technical, analysis, ad, adosc, adx, aroon, bbands, cci, cg, donchian, ema, fib, fisher, hma, kc, ma, macd, obv, rsi, sma, stoch, vwap, wma, zlma"
excerpt: "This guide introduces the common Technical Analysis functions, between all asset classes, available through the OpenBB SDK"
geekdocCollapseSection: true
---
The <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/common/ta/" target="_blank">Technical Analysis</a> module, of the OpenBB SDK, provides programmatic access to the same functions available within the <a href="https://openbb-finance.github.io/OpenBBTerminal/terminal/" target="_blank">OpenBB Terminal</a>. This allows the user to feed alternative data and sources to the inputs of functions, to customize the workflow, and to create custom processes with unique analysis. Import the OpenBB SDK in a new Jupyter Notebook file, or Python script, to begin exploring this module. Entering the `.` after `openbb.common.ta` will activate the code completion, which is scrollable with up and down arrow keys.

![openbb.common.ta](https://user-images.githubusercontent.com/85772166/200148349-9d538b3d-28a1-4aaf-8991-ba2cf7b2c35b.png "openbb.common.ta")

Where charts are the output of the OpenBB Terminal, add `%matplotlib widget` to the first cell, and then append the function's syntax with `chart=True`. Importing the Pandas module will allows users to easily work with raw data outputs from the OpenBB SDK. Now, with all three dependencies, the first cell looks like this:

```python
from openbb_terminal.sdk import openbb
import pandas as pd
%matplotlib widget
```

## How to Use

The first step is to load some data as a DataFrame. This can be accomplished through a number of methods, such as:

```python
data = pd.read_csv('file_to_load.csv')
data = openbb.stocks.load(symbol = 'ticker')
data = openbb.crypto.load(symbol = 'ticker')
data = openbb.forex.load(from_symbol = 'currency 1', to_symbol = 'currency 2')
data = openbb.etf.load(symbol = 'ticker')
```

Here is an example, using weekly Microsoft OHLC+V data from 1986:

```python
msft_ohlc = openbb.stocks.load('MSFT', start_date = '1986-06-30', weekly = True)
```

Some Technical Analysis functions will require OHLC data, while others will use only one column from the OHLC+V DataFrame. In the case of the latter, a target column must be defined by the user. For example, `openbb.common.ta.ma`, is a function requiring only one column:

```python
openbb.common.ta.ma(
    data = msft_ohlc['Adj Close'],
    window = [3,27,52],
    ma_type = 'EMA',
    symbol = 'Microsoft - Weekly',
    chart = True,
    )
```

![openbb.common.ta.ma](https://user-images.githubusercontent.com/85772166/200148379-474c8179-4197-4814-97fa-1c544d1124fb.png "openbb.common.ta.ma")

The `rsi` function has different variable input parameters:

```python
openbb.common.ta.rsi(
    data = msft_ohlc['Adj Close'],
    window = 4,
    symbol = 'Microsoft - Weekly',
    chart = True,
    )
```

![openbb.common.ta.rsi](https://user-images.githubusercontent.com/85772166/200148387-72cbcd71-e38d-4611-8512-94e8031e74c2.png "openbb.common.ta.rsi")

To return the values as a DataFrame, remove `chart = True` and the `symbol` argument:

```python
msft_rsi = openbb.common.ta.rsi(
    data = msft_ohlc['Adj Close'],
    window = 4,
    )
msft_ohlc.join(msft_rsi)
```

![RSI as Raw Data](https://user-images.githubusercontent.com/85772166/200148404-b9d7907d-a489-4a4f-8236-f2dca176da7d.png "RSI as Raw Data")

Other functions, like `obv`, require OHLC data. The code block below adds a new column to the OHLC DataFrame, on-balance volume:

```python
msft_obv = openbb.common.ta.obv(data = msft_ohlc).convert_dtypes()
msft_ohlc = msft_ohlc.join(msft_obv)
```

![openbb.common.ta.obv](https://user-images.githubusercontent.com/85772166/200148418-4215776d-cb40-4b47-a107-42bbaa3d9136.png)

The average true range (ATR) is a measurement of volatility. By adjusting the value for `window`, to 2, the specified period for measuring the volatility is now set for two-weeks.

```python
msft_atr = openbb.common.ta.atr(
    data = msft_ohlc,
    window = 2,
    mamode = 'ema',
    )
msft_ohlc = msft_ohlc.join(msft_atr)
```

![openbb.common.ta.atr](https://user-images.githubusercontent.com/85772166/200148441-d95b60c0-92a5-41d1-9ca2-aa8724a95366.png "openbb.common.ta.atr")

Adding Ketler Channels to the DataFrame, or any other function's output, follows a similar syntax:

```python
msft_kc = openbb.common.ta.kc(
    data = msft_ohlc,
    window = 16,
    scalar = 2,
    mamode = 'ema',
    )
msft_ohlc = msft_ohlc.join(msft_kc)
```

![openbb.common.ta.kc](https://user-images.githubusercontent.com/85772166/200148474-a3b6868c-7525-45bc-9ee4-1a86df933f71.png "openbb.common.ta.kc")

Compiling a DataFrame in this manner is useful for creating technical analysis overlays of price charts.
