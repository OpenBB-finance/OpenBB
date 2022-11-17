---
title: rsi
description: OpenBB SDK Function
---

# rsi

## forecast_model.add_rsi

```python title='openbb_terminal/forecast/forecast_model.py'
def add_rsi(dataset: pd.DataFrame, target_column: str, period: int) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/forecast_model.py#L225)

Description: A momentum indicator that measures the magnitude of recent price changes to evaluate

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| dataset | pd.DataFrame | The dataset you wish to calculate for | None | False |
| target_column | str | The column you wish to add the RSI to | None | False |
| period | int | Time Span | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
|  | Dataframe with added RSI column |

## Examples

