---
title: expirations
description: OpenBB SDK Function
---

# expirations

Get Option Chain Expirations

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/options_sdk_helper.py#L69)]

```python
openbb.stocks.options.expirations(symbol: str, source: str = "Nasdaq")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Symbol to get chain for | None | False |
| source | str | Source to get data from, by default "Nasdaq" | Nasdaq | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of full option chain. |
---

## Examples

```python
from openbb_terminal.sdk import openbb
SPX_expirations = openbb.stocks.options.expirations("SPX", source = "Tradier")
```

---

