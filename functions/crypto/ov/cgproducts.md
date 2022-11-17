---
title: cgproducts
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# cgproducts

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_ov_pycoingecko_model.get_finance_products

```python title='openbb_terminal/cryptocurrency/overview/pycoingecko_model.py'
def get_finance_products(sortby: str, ascend: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/pycoingecko_model.py#L286)

Description: Get list of financial products from CoinGecko API

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| sortby | str | Key by which to sort data | None | False |
| ascend | bool | Flag to sort data ascending | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Rank,  Platform, Identifier, Supply_Rate, Borrow_Rate |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_ov_pycoingecko_view.display_products

```python title='openbb_terminal/cryptocurrency/overview/pycoingecko_view.py'
def display_products(sortby: str, ascend: bool, limit: int, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/pycoingecko_view.py#L595)

Description: Shows list of financial products. [Source: CoinGecko]

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