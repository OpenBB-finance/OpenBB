---
title: combine
description: OpenBB SDK Function
---

# combine

## forecast_model.combine_dfs

```python title='openbb_terminal/forecast/forecast_model.py'
def combine_dfs(df1: pd.DataFrame, df2: pd.DataFrame, column: str, dataset: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/forecast_model.py#L397)

Description: Adds the given column of df2 to df1

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| df1 | pd.DataFrame | The dataframe to add a column to | None | False |
| df2 | pd.DataFrame | The dataframe to lose a column | None | False |
| column | str | The column to transfer | None | False |
| dataset | str | A name for df2 (shows in name of new column) | None | False |
| Returns | None | None | None | None |
| ---------- | None | None | None | None |
| data | pd.DataFrame | The new dataframe | None | False |

## Returns

This function does not return anything

## Examples

