---
title: season
description: OpenBB SDK Function
---

# season

## forecast_view.display_seasonality

```python title='openbb_terminal/forecast/forecast_view.py'
def display_seasonality(data: pd.DataFrame, column: str, export: str, m: Optional[int], max_lag: int, alpha: float, external_axes: Optional[List[axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/forecast_view.py#L120)

Description: Plot seasonality from a dataset

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | The dataframe to plot | None | False |
| column | str | The column of the dataframe to analyze | None | False |
| export | str | Format to export image | None | False |
| m | Optional[int] | Optionally, a time lag to highlight on the plot. Default is none. | none | False |
| max_lag | int | The maximal lag order to consider. Default is 24. | 24 | False |
| alpha | float | The confidence interval to display. Default is 0.05. | 0.05 | False |
| external_axes | Optional[List[plt.axes]] | External axes to plot on | None | False |

## Returns

This function does not return anything

## Examples

