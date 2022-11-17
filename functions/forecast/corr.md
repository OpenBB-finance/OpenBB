---
title: corr
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# corr

<Tabs>
<TabItem value="model" label="Model" default>

## forecast_model.corr_df

```python title='openbb_terminal/forecast/forecast_model.py'
def corr_df(data: pd.DataFrame) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/forecast_model.py#L497)

Description: Returns correlation for a given df

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | The df to produce statistics for | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | The df with the new data |

## Examples



</TabItem>
<TabItem value="view" label="View">

## forecast_view.display_corr

```python title='openbb_terminal/forecast/forecast_view.py'
def display_corr(dataset: pd.DataFrame, export: str, external_axes: Optional[List[axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/forecast_view.py#L170)

Description: Plot correlation coefficients for dataset features

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| dataset | pd.DataFrame | The dataset fore calculating correlation coefficients | None | False |
| export | str | Format to export image | None | False |
| external_axes | Optional[List[plt.axes]] | External axes to plot on | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>