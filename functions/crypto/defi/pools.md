---
title: pools
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# pools

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_defi_graph_model.get_uni_pools_by_volume

```python title='openbb_terminal/cryptocurrency/defi/graph_model.py'
def get_uni_pools_by_volume() -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/graph_model.py#L253)

Description: Get uniswap pools by volume. [Source: https://thegraph.com/en/]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Trade-able pairs listed on Uniswap by top volume. |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_defi_graph_view.display_uni_pools

```python title='openbb_terminal/cryptocurrency/defi/graph_view.py'
def display_uni_pools(limit: int, sortby: str, ascend: bool, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/graph_view.py#L170)

Description: Displays uniswap pools by volume.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of records to display | None | False |
| sortby | str | Key by which to sort data. The table can be sorted by every of its columns
(see https://bit.ly/3ORagr1 then press ctrl-enter or execute the query). | None | False |
| ascend | bool | Flag to sort data descending | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>