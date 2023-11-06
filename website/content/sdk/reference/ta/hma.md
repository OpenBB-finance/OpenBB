---
title: hma
description: This page provides documentation on the hma function from OpenBB. This
  function calculates the hull moving average (HMA) of stock prices, using a pandas
  dataframe as input and returning a dataframe with the prices and the HMA.
keywords:
- hma
- hull moving average
- stock technical analysis
- pandas
- SMA window
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="ta.hma - Reference | OpenBB SDK Docs" />

Gets hull moving average (HMA) for stock

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/overlap_model.py#L91)]

```python
openbb.ta.hma(data: pd.Series, length: int = 50, offset: int = 0)
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
| pd.DataFrame | Dataframe containing prices and HMA |
---
