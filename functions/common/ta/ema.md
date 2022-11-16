---
title: ema
description: OpenBB SDK Function
---

# ema

## common_ta_overlap_model.ema

```python title='openbb_terminal/common/technical_analysis/overlap_model.py'
def ema(data: pd.Series, length: int, offset: int) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/overlap_model.py#L19)

Description: Gets exponential moving average (EMA) for stock

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.Series | Dataframe of dates and prices | None | False |
| length | int | Length of EMA window | None | False |
| offset | int | Length of offset | None | False |
| Returns | None | None | None | None |
| ---------- | None | None | None | None |
| pd.DataFrame | None | Dataframe containing prices and EMA | None | None |

## Returns

This function does not return anything

## Examples

