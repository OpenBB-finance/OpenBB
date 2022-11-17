---
title: ema
description: OpenBB SDK Function
---

# ema

## forecast_model.add_ema

```python title='openbb_terminal/forecast/forecast_model.py'
def add_ema(dataset: pd.DataFrame, target_column: str, period: int) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/forecast_model.py#L147)

Description: A moving average provides an indication of the trend of the price movement

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| dataset | pd.DataFrame | The dataset you wish to clean | None | False |
| target_column | str | The column you wish to add the EMA to | None | False |
| period | int | Time Span | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
|  | Dataframe with added EMA column |

## Examples

