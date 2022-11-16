---
title: regions
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# regions

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_ba_google_model.get_regions

```python title='openbb_terminal/common/behavioural_analysis/google_model.py'
def get_regions(symbol: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/google_model.py#L44)

Description: Get interest by region from google api [Source: google]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to look at | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of interest by region |

## Examples



</TabItem>
<TabItem value="view" label="View">

## stocks_ba_google_view.display_regions

```python title='openbb_terminal/common/behavioural_analysis/google_view.py'
def display_regions(symbol: str, limit: int, export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/google_view.py#L156)

Description: Plot bars of regions based on stock's interest. [Source: Google]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol | None | False |
| limit | int | Number of regions to show | None | False |
| export | str | Format to export data | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>