---
title: sidtc
description: Documentation for sidtc, a tool command that retrieves and sorts short
  interest and days-to-cover data.
keywords:
- sidtc
- short interest
- days-to-cover
- stockgrid
- OpenBB-finance
- stock data
- floating short
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="stocks.dps.sidtc - Reference | OpenBB SDK Docs" />

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
