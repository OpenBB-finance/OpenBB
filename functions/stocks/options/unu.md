---
title: unu
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# unu

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_options_fdscanner_model.unusual_options

```python title='openbb_terminal/stocks/options/fdscanner_model.py'
def unusual_options(limit: int) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/fdscanner_model.py#L18)

Description: Get unusual option activity from fdscanner.com

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number to show | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe containing options information |

## Examples



</TabItem>
<TabItem value="view" label="View">

## stocks_options_fdscanner_view.display_options

```python title='openbb_terminal/stocks/options/fdscanner_view.py'
def display_options(limit: int, sortby: str, ascend: bool, calls_only: bool, puts_only: bool, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/fdscanner_view.py#L15)

Description: Displays the unusual options table

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of rows to show | None | False |
| sortby | str | Data column to sort on | None | False |
| ascend | bool | Whether to sort in ascend order | None | False |
| calls_only | bool | Flag to only show calls | None | False |
| puts_only | bool | Flag to show puts only | None | False |
| export | str | File type to export | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>