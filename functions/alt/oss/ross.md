---
title: ross
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# ross

<Tabs>
<TabItem value="model" label="Model" default>

## alt_oss_runa_model.get_startups

```python title='openbb_terminal/alternative/oss/runa_model.py'
def get_startups() -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/alternative/oss/runa_model.py#L103)

Description: Get startups from ROSS index [Source: https://runacap.com/]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |

## Returns

| Type | Description |
| ---- | ----------- |
|  | list of startups |

## Examples



</TabItem>
<TabItem value="view" label="View">

## alt_oss_runa_view.display_rossindex

```python title='openbb_terminal/alternative/oss/runa_view.py'
def display_rossindex(limit: int, sortby: str, ascend: bool, show_chart: bool, show_growth: bool, chart_type: str, export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/alternative/oss/runa_view.py#L25)

Description: Display list of startups from ross index [Source: https://runacap.com/]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of startups to search | None | False |
| sortby | str | Key by which to sort data. Default: Stars AGR [%] | Stars | False |
| ascend | bool | Flag to sort data descending | None | False |
| show_chart | bool | Flag to show chart with startups | None | False |
| show_growth | bool | Flag to show growth line chart | None | False |
| chart_type | str | Chart type {stars,forks} | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>