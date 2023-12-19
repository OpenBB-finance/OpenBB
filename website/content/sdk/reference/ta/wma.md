---
title: wma
description: This page provides a comprehensive guide on how to get the Weighted Moving
  Average (WMA) for stock using OpenBB's wma function. This includes relevant parameters
  and return values.
keywords:
- Weighted Moving Average
- WMA
- Stock Analysis
- Python Function
- Technical Analysis
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="ta.wma - Reference | OpenBB SDK Docs" />

Gets weighted moving average (WMA) for stock

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/overlap_model.py#L67)]

```python
openbb.ta.wma(data: pd.Series, length: int = 50, offset: int = 0)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.Series | Dataframe of dates and prices | None | False |
| length | int | Length of SMA window | 50 | True |
| offset | int | Length of offset | 0 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe containing prices and WMA |
---
