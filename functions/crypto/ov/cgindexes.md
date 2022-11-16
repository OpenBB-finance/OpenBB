---
title: cgindexes
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# cgindexes

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_ov_pycoingecko_model.get_indexes

```python title='openbb_terminal/cryptocurrency/overview/pycoingecko_model.py'
def get_indexes(sortby: str, ascend: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/pycoingecko_model.py#L319)

Description: Get list of crypto indexes from CoinGecko API [Source: CoinGecko]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |

## Returns

| Type | Description |
| ---- | ----------- |
| pandas.DataFrame | Name, Id, Market, Last, MultiAsset |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_ov_pycoingecko_view.display_indexes

```python title='openbb_terminal/cryptocurrency/overview/pycoingecko_view.py'
def display_indexes(sortby: str, ascend: bool, limit: int, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/pycoingecko_view.py#L635)

Description: Shows list of crypto indexes. [Source: CoinGecko]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of records to display | None | False |
| sortby | str | Key by which to sort data | None | False |
| ascend | bool | Flag to sort data descending | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>