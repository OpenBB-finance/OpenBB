---
title: cghold
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# cghold

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_ov_pycoingecko_model.get_holdings_overview

```python title='openbb_terminal/cryptocurrency/overview/pycoingecko_model.py'
def get_holdings_overview(endpoint: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/pycoingecko_model.py#L102)

Description: Returns public companies that holds ethereum or bitcoin [Source: CoinGecko]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| endpoint | str | "bitcoin" or "ethereum" | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
|  | - str:              Overall statistics
- pandas.DataFrame: Companies holding crypto |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_ov_pycoingecko_view.display_holdings_overview

```python title='openbb_terminal/cryptocurrency/overview/pycoingecko_view.py'
def display_holdings_overview(symbol: str, show_bar: bool, export: str, limit: int) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/pycoingecko_view.py#L135)

Description: Shows overview of public companies that holds ethereum or bitcoin. [Source: CoinGecko]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Cryptocurrency: ethereum or bitcoin | None | False |
| show_bar | bool | Whether to show a bar graph for the data | None | False |
| export | str | Export dataframe data to csv,json,xlsx | None | False |
| limit | int | The number of rows to show | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>