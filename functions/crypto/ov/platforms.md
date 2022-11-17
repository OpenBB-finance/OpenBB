---
title: platforms
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# platforms

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_ov_pycoingecko_model.get_financial_platforms

```python title='openbb_terminal/cryptocurrency/overview/pycoingecko_model.py'
def get_financial_platforms(sortby: str, ascend: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/pycoingecko_model.py#L260)

Description: Get list of financial platforms from CoinGecko API [Source: CoinGecko]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| sortby | str | Key by which to sort data | None | False |
| ascend | bool | Flag to sort data ascending | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Rank, Name, Category, Centralized, Url |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_ov_pycoingecko_view.display_platforms

```python title='openbb_terminal/cryptocurrency/overview/pycoingecko_view.py'
def display_platforms(sortby: str, ascend: bool, limit: int, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/pycoingecko_view.py#L557)

Description: Shows list of financial platforms. [Source: CoinGecko]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of records to display | None | False |
| sortby | str | Key by which to sort data | None | False |
| ascend | bool | Flag to sort data ascending | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>