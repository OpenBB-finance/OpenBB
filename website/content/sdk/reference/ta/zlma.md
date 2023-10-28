---
title: zlma
description: This page provides an in-depth view of the zlma function, which is used
  to calculate zero-lagged exponential moving average (ZLEMA) for stocks. The page
  includes the source code and details of parameters and returns.
keywords:
- ZLEMA
- stock analysis
- technical analysis
- openbb.ta.zlma function
- exponential moving average
- OpenBB finance
- overlap_model.py
- dataframe
- EMA
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="ta.zlma - Reference | OpenBB SDK Docs" />

Gets zero-lagged exponential moving average (ZLEMA) for stock

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/overlap_model.py#L115)]

```python
openbb.ta.zlma(data: pd.Series, length: int = 50, offset: int = 0)
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
