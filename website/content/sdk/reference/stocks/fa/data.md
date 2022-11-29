---
title: data
description: OpenBB SDK Function
---

# data

Get fundamental data from finviz

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/fundamental_analysis/finviz_model.py#L15)]

```python
openbb.stocks.fa.data(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of fundamental data |
---

## Examples

```python
from openbb_terminal.sdk import openbb
openbb.stocks.fa.data("IWV")
```

---

