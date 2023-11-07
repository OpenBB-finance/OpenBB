---
title: pos
description: This documentation page is about getting dark pool short positions using
  the 'pos' function in the openbb.stocks.dps python package. Details about parameters
  such as 'sortby' and 'ascend', and the data returned, i.e., pd.DataFrame, are provided.
keywords:
- pos
- dark pool short positions
- Stockgrid
- coding
- openbb.stocks.dps.pos
- parameters
- returns
- Data in ascending order
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.dps.pos - Reference | OpenBB SDK Docs" />

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
