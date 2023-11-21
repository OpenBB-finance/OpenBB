---
title: hist
description: The page explains how to get historical option pricing using the OpenBB
  SDK in Python. It provides a detailed guide for parameters and return types along
  with examples. You may choose data source from ChartExchange or Tradier.
keywords:
- Option Pricing
- Historical data
- ChartExchange
- Tradier
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.options.hist - Reference | OpenBB SDK Docs" />

Get historical option pricing.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/options_sdk_helper.py#L101)]

```python
openbb.stocks.options.hist(symbol: str, exp: str, strike: Union[int, float, str], call: bool = True, source: Any = "ChartExchange")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get data for | None | False |
| exp | str | Expiration date | None | False |
| strike | Union[int ,Union[float,str]] | Strike price | None | False |
| call | bool | Flag to indicate a call, by default True | True | True |
| source | str | Source to get data from.  Can be ChartExchange or Tradier, by default "ChartExchange" | ChartExchange | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of historical option pricing |
---

## Examples

```python
from openbb_terminal.sdk import openbb
aapl_150_call = openbb.stocks.options.hist("AAPL", "2022-11-18", 150, call=True, source="ChartExchange")
```

```
Because this generates a dataframe, we can easily plot the close price for a SPY put:
(Note that Tradier requires an API key)
```
```python
openbb.stocks.options.hist("SPY", "2022-11-18", 400, call=False, source="Tradier").plot(y="close)
```

---
