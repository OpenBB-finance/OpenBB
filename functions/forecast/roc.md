---
title: roc
description: OpenBB SDK Function
---

# roc

## forecast_model.add_roc

```python title='openbb_terminal/forecast/forecast_model.py'
def add_roc(dataset: pd.DataFrame, target_column: str, period: int) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/forecast_model.py#L267)

Description: A momentum oscillator, which measures the percentage change between the current

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| dataset | pd.DataFrame | The dataset you wish to calculate with | None | False |
| target_column | str | The column you wish to add the ROC to | None | False |
| period | int | Time Span | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
|  | Dataframe with added ROC column |

## Examples

