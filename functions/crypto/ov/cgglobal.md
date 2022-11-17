---
title: cgglobal
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# cgglobal

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_ov_pycoingecko_model.get_global_markets_info

```python title='openbb_terminal/cryptocurrency/overview/pycoingecko_model.py'
def get_global_markets_info() -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/pycoingecko_model.py#L451)

Description: Get global statistics about crypto markets from CoinGecko API like:

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |

## Returns

| Type | Description |
| ---- | ----------- |
| pandas.DataFrame | Market_Cap, Volume, Market_Cap_Percentage |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_ov_pycoingecko_view.display_global_market_info

```python title='openbb_terminal/cryptocurrency/overview/pycoingecko_view.py'
def display_global_market_info(pie: bool, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/pycoingecko_view.py#L240)

Description: Shows global statistics about crypto. [Source: CoinGecko]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| pie | bool | Whether to show a pie chart | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>