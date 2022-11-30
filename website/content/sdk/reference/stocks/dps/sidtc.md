---
title: sidtc
description: OpenBB SDK Function
---

# sidtc

Get short interest and days to cover. [Source: Stockgrid]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/dark_pool_shorts/stockgrid_model.py#L76)]

```python
openbb.stocks.dps.sidtc(sortby: str = "float")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| sortby | str | Field for which to sort by, where 'float': Float Short %%,<br/>'dtc': Days to Cover, 'si': Short Interest | float | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Short interest and days to cover data |
---

