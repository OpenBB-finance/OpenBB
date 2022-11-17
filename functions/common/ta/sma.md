---
title: sma
description: OpenBB SDK Function
---

# sma

## common_ta_overlap_model.sma

```python title='openbb_terminal/common/technical_analysis/overlap_model.py'
def sma(data: pd.Series, length: int, offset: int) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/overlap_model.py#L43)

Description: Gets simple moving average (EMA) for stock

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.Series | Dataframe of dates and prices | None | False |
| length | int | Length of SMA window | None | False |
| offset | int | Length of offset | None | False |
| Returns | None | None | None | None |
| ---------- | None | None | None | None |
| pd.DataFrame | None | Dataframe containing prices and SMA | None | None |

## Returns

This function does not return anything

## Examples

