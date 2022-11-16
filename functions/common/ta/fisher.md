---
title: fisher
description: OpenBB SDK Function
---

# fisher

## common_ta_momentum_model.fisher

```python title='openbb_terminal/common/technical_analysis/momentum_model.py'
def fisher(data: pd.DataFrame, window: int) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/technical_analysis/momentum_model.py#L165)

Description: Fisher Transform

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of OHLC prices | None | False |
| window | int | Length for indicator window | None | False |
| Returns | None | None | None | None |
| ---------- | None | None | None | None |
| df_ta | pd.DataFrame | Dataframe of technical indicator | None | False |

## Returns

This function does not return anything

## Examples

