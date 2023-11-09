---
title: sma
description: This page provides a comprehensive guide on how to use the sma function
  in OpenBB to get the Simple Moving Average (SMA) for stock. It also includes source
  code, parameters, and returns descriptions.
keywords:
- sma
- moving average
- stock
- financial technical analysis
- openbb.ta.sma function
- dataframe
- pricing
- programming
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="ta.sma - Reference | OpenBB SDK Docs" />

Gets simple moving average (SMA) for stock

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/overlap_model.py#L43)]

```python
openbb.ta.sma(data: pd.Series, length: int = 50, offset: int = 0)
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
| pd.DataFrame | Dataframe containing prices and SMA |
---
