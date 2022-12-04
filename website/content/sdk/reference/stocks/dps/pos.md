---
title: pos
description: OpenBB SDK Function
---

# pos

Get dark pool short positions. [Source: Stockgrid]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/dark_pool_shorts/stockgrid_model.py#L18)]

```python
openbb.stocks.dps.pos(sortby: str = "dpp_dollar", ascend: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| sortby | str | Field for which to sort by, where 'sv': Short Vol. [1M],<br/>'sv_pct': Short Vol. %%, 'nsv': Net Short Vol. [1M],<br/>'nsv_dollar': Net Short Vol. ($100M), 'dpp': DP Position [1M],<br/>'dpp_dollar': DP Position ($1B) | dpp_dollar | True |
| ascend | bool | Data in ascending order | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dark pool short position data |
---

