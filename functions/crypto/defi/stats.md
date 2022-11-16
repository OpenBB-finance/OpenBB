---
title: stats
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# stats

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_defi_graph_model.get_uniswap_stats

```python title='openbb_terminal/cryptocurrency/defi/graph_model.py'
def get_uniswap_stats() -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/graph_model.py#L124)

Description: Get base statistics about Uniswap DEX. [Source: https://thegraph.com/en/]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Uniswap DEX statistics like liquidity, volume, number of pairs, number of transactions. |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_defi_graph_view.display_uni_stats

```python title='openbb_terminal/cryptocurrency/defi/graph_view.py'
def display_uni_stats(export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/graph_view.py#L72)

Description: Displays base statistics about Uniswap DEX. [Source: https://thegraph.com/en/]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>