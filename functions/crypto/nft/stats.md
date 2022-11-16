---
title: stats
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# stats

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_nft_opensea_model.get_collection_stats

```python title='openbb_terminal/cryptocurrency/nft/opensea_model.py'
def get_collection_stats(slug: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/nft/opensea_model.py#L17)

Description: Get stats of a nft collection [Source: opensea.io]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | collection stats |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_nft_opensea_view.display_collection_stats

```python title='openbb_terminal/cryptocurrency/nft/opensea_view.py'
def display_collection_stats(slug: str, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/nft/opensea_view.py#L15)

Description: Display collection stats. [Source: opensea.io]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| slug | str | Opensea collection slug.
If the name of the collection is Mutant Ape Yacht Club the slug is mutant-ape-yacht-club | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>