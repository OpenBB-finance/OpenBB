---
title: top_dexes
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# top_dexes

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_disc_dappradar_model.get_top_dexes

```python title='openbb_terminal/cryptocurrency/discovery/dappradar_model.py'
def get_top_dexes(sortby: str, limit: int) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/dappradar_model.py#L123)

Description: Get top dexes by daily volume and users [Source: https://dappradar.com/]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| sortby | str | Key by which to sort data | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Top decentralized exchanges. Columns: Name, Daily Users, Daily Volume [$] |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_disc_dappradar_view.display_top_dexes

```python title='openbb_terminal/cryptocurrency/discovery/dappradar_view.py'
def display_top_dexes(limit: int, export: str, sortby: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/discovery/dappradar_view.py#L97)

Description: Displays top decentralized exchanges [Source: https://dappradar.com/]

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