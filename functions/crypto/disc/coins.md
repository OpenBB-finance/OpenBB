---
title: coins
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# coins

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_disc_pycoingecko_model.get_coins

```python title='openbb_terminal/cryptocurrency/discovery/pycoingecko_model.py'
def get_coins(limit: int, category: str, sortby: str, ascend: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/pycoingecko_model.py#L121)

Description: Get N coins from CoinGecko [Source: CoinGecko]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of top coins to grab from CoinGecko | None | False |
| category | str | Category of the coins we want to retrieve | None | False |
| sortby | str | Key to sort data | None | False |
| ascend | bool | Sort data in ascending order | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pandas.DataFrame | N coins |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_disc_pycoingecko_view.display_coins

```python title='openbb_terminal/cryptocurrency/discovery/pycoingecko_view.py'
def display_coins(category: str, limit: int, sortby: str, export: str, ascend: bool) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/pycoingecko_view.py#L35)

Description: Display top coins [Source: CoinGecko]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| category | str | If no category is passed it will search for all coins. (E.g., smart-contract-platform) | None | False |
| limit | int | Number of records to display | None | False |
| sortby | str | Key to sort data | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |
| ascend | bool | Sort data in ascending order | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>