---
title: top_nfts
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# top_nfts

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_disc_dappradar_model.get_top_nfts

```python title='openbb_terminal/cryptocurrency/discovery/dappradar_model.py'
def get_top_nfts(sortby: str, limit: int) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/dappradar_model.py#L78)

Description: Get top nft collections [Source: https://dappradar.com/]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| sortby | str | Key by which to sort data | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | NFTs Columns: Name, Protocols, Floor Price [$], Avg Price [$], Market Cap [$], Volume [$] |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_disc_dappradar_view.display_top_nfts

```python title='openbb_terminal/cryptocurrency/discovery/dappradar_view.py'
def display_top_nfts(limit: int, sortby: str, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/dappradar_view.py#L20)

Description: Displays top nft collections [Source: https://dappradar.com/]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of records to display | None | False |
| sortby | str | Key by which to sort data | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>