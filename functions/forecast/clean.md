---
title: clean
description: OpenBB SDK Function
---

# clean

## forecast_model.clean

```python title='openbb_terminal/forecast/forecast_model.py'
def clean(dataset: pd.DataFrame, fill: Optional[str], drop: Optional[str], limit: Optional[int]) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/forecast_model.py#L88)

Description: Clean up NaNs from the dataset

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| dataset | pd.DataFrame | The dataset you wish to clean | None | False |
| fill | Optional[str] | The method of filling NaNs | None | False |
| drop | Optional[str] | The method of dropping NaNs | None | False |
| limit | Optional[int] | The maximum limit you wish to apply that can be forward or backward filled | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
|  | Dataframe with cleaned up data |

## Examples

