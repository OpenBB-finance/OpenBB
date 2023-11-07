---
title: ema
description: This page provides information on OpenBB's EMA (Exponential Moving Average)
  functionality, a method often used in technical analysis of stocks. The mathematical
  model's source code, parameters, and returns are clearly outlined.
keywords:
- ema
- exponential moving average
- technical analysis
- stock
- overlap model
- dataframe
- pd.Series
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="ta.ema - Reference | OpenBB SDK Docs" />

Gets exponential moving average (EMA) for stock

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/overlap_model.py#L19)]

```python
openbb.ta.ema(data: pd.Series, length: int = 50, offset: int = 0)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.Series | Dataframe of dates and prices | None | False |
| length | int | Length of EMA window | 50 | True |
| offset | int | Length of offset | 0 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe containing prices and EMA |
---
