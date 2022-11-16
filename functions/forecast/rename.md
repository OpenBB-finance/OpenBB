---
title: rename
description: OpenBB SDK Function
---

# rename

## forecast_model.rename_column

```python title='openbb_terminal/forecast/forecast_model.py'
def rename_column(data: pd.DataFrame, old_column: str, new_column: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/forecast_model.py#L453)

Description: Rename a column in a dataframe

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | The dataframe to have a column renamed | None | False |
| old_column | str | The column that will have its name changed | None | False |
| new_column | str | The name to update to | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | The dataframe with the renamed column |

## Examples

