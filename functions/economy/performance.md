---
title: performance
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# performance

<Tabs>
<TabItem value="model" label="Model" default>

## economy_finviz_model.get_performance_data

```python title='openbb_terminal/economy/finviz_model.py'
def get_performance_data(group: str, sortby: str, ascend: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/finviz_model.py#L112)

Description: Get group (sectors, industry or country) performance data. [Source: Finviz]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| group | str | Group by category. Available groups can be accessed through get_groups(). | None | False |
| sortby | str | Column to sort by | None | False |
| ascend | bool | Flag to sort in ascending order | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | dataframe with performance data |

## Examples



</TabItem>
<TabItem value="view" label="View">

## economy_finviz_view.display_performance

```python title='openbb_terminal/economy/finviz_view.py'
def display_performance(group: str, sortby: str, ascend: bool, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/finviz_view.py#L72)

Description: View group (sectors, industry or country) performance data. [Source: Finviz]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| group | str | Group by category. Available groups can be accessed through get_groups(). | None | False |
| sortby | str | Column to sort by | None | False |
| ascend | bool | Flag to sort in ascending order | None | False |
| export | str | Export data to csv,json,xlsx or png,jpg,pdf,svg file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>