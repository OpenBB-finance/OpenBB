---
title: pairs
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# pairs

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_defi_graph_model.get_uniswap_pool_recently_added

```python title='openbb_terminal/cryptocurrency/defi/graph_model.py'
def get_uniswap_pool_recently_added(last_days: int, min_volume: int, min_liquidity: int, min_tx: int) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/graph_model.py#L164)

Description: Get lastly added trade-able pairs on Uniswap with parameters like:

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| last_days | int | How many days back to look for added pairs. | None | False |
| min_volume | int | Minimum volume | None | False |
| min_liquidity | int | Minimum liquidity | None | False |
| min_tx | int | Minimum number of transactions done in given pool. | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Lastly added pairs on Uniswap DEX. |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_defi_graph_view.display_recently_added

```python title='openbb_terminal/cryptocurrency/defi/graph_view.py'
def display_recently_added(limit: int, days: int, min_volume: int, min_liquidity: int, min_tx: int, sortby: str, ascend: bool, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/defi/graph_view.py#L102)

Description: Displays Lastly added pairs on Uniswap DEX.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of records to display | None | False |
| days | int | Number of days the pair has been active, | None | False |
| min_volume | int | Minimum trading volume, | None | False |
| min_liquidity | int | Minimum liquidity | None | False |
| min_tx | int | Minimum number of transactions | None | False |
| sortby | str | Key by which to sort data | None | False |
| ascend | bool | Flag to sort data descending | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>