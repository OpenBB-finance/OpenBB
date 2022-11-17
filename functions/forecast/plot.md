---
title: plot
description: OpenBB SDK Function
---

# plot

## forecast_view.display_plot

```python title='openbb_terminal/forecast/forecast_view.py'
def display_plot(data: pd.DataFrame, columns: List[str], export: str, external_axes: Optional[List[axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/forecast_view.py#L74)

Description: Plot data from a dataset

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | The dataframe to plot | None | False |
| columns | List[str] | The columns to show | None | False |
| export | str | Format to export image | None | False |
| external_axes | Optional[List[plt.axes]] | External axes to plot on | None | False |

## Returns

This function does not return anything

## Examples

