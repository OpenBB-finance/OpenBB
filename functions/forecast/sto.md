---
title: sto
description: OpenBB SDK Function
---

# sto

## forecast_model.add_sto

```python title='openbb_terminal/forecast/forecast_model.py'
def add_sto(dataset: pd.DataFrame, close_column: str, high_column: str, low_column: str, period: int) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/forecast_model.py#L175)

Description: Stochastic Oscillator %K and %D : A stochastic oscillator is a momentum indicator comparing a particular closing

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| dataset | pd.DataFrame | The dataset you wish to calculate for | None | False |
| period | int | Span | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
|  | Dataframe with added STO K & D columns |

## Examples

