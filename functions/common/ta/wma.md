---
title: wma
description: OpenBB SDK Function
---

# wma

## common_ta_overlap_model.wma

```python title='openbb_terminal/common/technical_analysis/overlap_model.py'
def wma(data: pd.Series, length: int, offset: int) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/overlap_model.py#L67)

Description: Gets weighted moving average (WMA) for stock

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.Series | Dataframe of dates and prices | None | False |
| length | int | Length of SMA window | None | False |
| offset | int | Length of offset | None | False |
| Returns | None | None | None | None |
| ---------- | None | None | None | None |
| df_ta | pd.DataFrame | Dataframe containing prices and WMA | None | False |

## Returns

This function does not return anything

## Examples

