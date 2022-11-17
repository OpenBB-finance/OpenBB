---
title: hma
description: OpenBB SDK Function
---

# hma

## common_ta_overlap_model.hma

```python title='openbb_terminal/common/technical_analysis/overlap_model.py'
def hma(data: pd.Series, length: int, offset: int) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/overlap_model.py#L91)

Description: Gets hull moving average (HMA) for stock

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.Series | Dataframe of dates and prices | None | False |
| length | int | Length of SMA window | None | False |
| offset | int | Length of offset | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe containing prices and HMA |

## Examples

