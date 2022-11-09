---
title: Introduction to ETF
keywords: "etf, etfs, etn, fund, funds, blackrock, vanguard, fidelity, statestreet, spdr, exchange-traded, SPY, QQQ, TQQQ, SQQQ"
excerpt: "This guide introduces the ETF module within the context of the OpenBB SDK"
geekdocCollapseSection: true

---
The ETF module wraps the functions from the ETF menu, within the OpenBB Terminal, allowing programmatic access to the commands. Import the OpenBB SDK module, and then find the ETF functions similarly to how the Terminal menus are navigated. The code completion will be activated after entering the `.` in: `openbb.etf`

```python
from openbb_terminal.sdk import openbb
import pandas as pd
%matplotlib widget
```

![ETF Module](https://user-images.githubusercontent.com/85772166/200064234-7de67c2a-a20e-42fe-adac-ba589c08d8ac.png "The ETF Module")

## How to Use

ETFs are categorized into different buckets, use. the code block below as a way to generate the list of all categories:

```python
etf_list = pd.DataFrame.from_dict(openbb.etf.etf_by_category('')).transpose()
etf_list.set_index(keys = ['category', 'family'])
etf_list.sort_values(by=['total_assets'], ascending = False)

categories = list(etf_list['category'].drop_duplicates())
```

![ETF Categories](https://user-images.githubusercontent.com/85772166/200064425-e333220c-cf5f-4d9c-a544-eba508dc9afe.png "ETF Categories")

After determining the category to research, the same code block can be repeated, replacing the empty category in the syntax:

```python
etf_category = pd.DataFrame.from_dict(openbb.etf.etf_by_category('Trading--Leveraged Equity')).transpose()
etf_category.sort_values(by=['total_assets'], ascending = False)
```

![Leveraged ETFs](https://user-images.githubusercontent.com/85772166/200064491-378f5ad1-bf28-426a-ace9-a0891329b7e5.png "Leveraged ETFs")

A list of all tickers in the category can be generated from the index of the DataFrame:

```python
tickers = list(etf_category.index)
```

This list of tickers can then be used for comparison analysis, or portfolio optimization. For example, comparing the performance metrics of all Technology ETFs available:

```python
performance = openbb.stocks.ca.screener(similar = tickers, data_type = 'performance')
performance.sort_values(by=['Perf Quart'])
```

![Comparing Performance Metrics of Technology ETFs](https://user-images.githubusercontent.com/85772166/200064802-d91b4552-e912-4c99-8c04-883f2fef18dc.png "Comparing Performance Metrics of Technology ETFs")

To peer into the holdings of a specific ETF:

```python
openbb.etf.holdings('NXTG')
```

![openbb.etf.holdings](https://user-images.githubusercontent.com/85772166/200064952-f3bd2d60-10b1-4b1a-816c-f5b8ac3a8781.png "openbb.etf.holdings")

The ETF screener is accessible through the SDK. Values for the screener are set in the file: `~/OpenBBTerminal/openbb_terminal/etf/screener/presets/etf_config.ini`

```python
openbb.etf.scr.screen(preset='etf_config.ini')
```

In this example, the configuration file is set to return results with a maximum Beta value of -2.

![ETF Screener](https://user-images.githubusercontent.com/85772166/200065448-b3348e25-b0e0-4555-9711-3baf7169d44d.png "ETF Screener")

The current top gainers, losers, and volume for ETFs is returned with:

```python
openbb.etf.disc.mover(sort_type = 'decliners')

openbb.etf.disc.mover(sort_type = 'gainers')

openbb.etf.disc.mover(sort_type = 'active')
```

![openbb.etf.disc.mover()](https://user-images.githubusercontent.com/85772166/200065107-e85c93a7-9cab-4298-b701-0230a171eb6a.png "openbb.etf.disc.mover()")
