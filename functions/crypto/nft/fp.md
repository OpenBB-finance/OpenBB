---
title: fp
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# fp

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_nft_pricefloor_model.get_floor_price

```python title='openbb_terminal/cryptocurrency/nft/nftpricefloor_model.py'
def get_floor_price(slug: Any) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/nft/nftpricefloor_model.py#L46)

Description: Get nft collections [Source: https://nftpricefloor.com/]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | nft collections |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_nft_pricefloor_view.display_floor_price

```python title='openbb_terminal/cryptocurrency/nft/nftpricefloor_view.py'
def display_floor_price(slug: str, limit: int, export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]], raw: bool) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/nft/nftpricefloor_view.py#L88)

Description: Display NFT collection floor price over time. [Source: https://nftpricefloor.com/]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| slug | str | NFT collection slug | None | False |
| raw | bool | Flag to display raw data | None | False |
| limit | int | Number of raw data to show | None | False |
| export | str | Format to export data | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (2 axes are expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>