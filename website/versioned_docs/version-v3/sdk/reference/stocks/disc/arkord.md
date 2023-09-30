---
title: arkord
description: OpenBB SDK Function
---

# arkord

Returns ARK orders in a Dataframe

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/discovery/ark_model.py#L23)]

```python
openbb.stocks.disc.arkord(buys_only: bool = False, sells_only: bool = False, fund: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| buys_only | bool | Flag to filter on buys only | False | True |
| sells_only | bool | Flag to sort on sells only | False | True |
| fund | str | Optional filter by fund |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| DataFrame | ARK orders data frame with the following columns -<br/>(ticker, date, shares, weight, fund, direction) |
---

