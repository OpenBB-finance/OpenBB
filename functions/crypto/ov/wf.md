---
title: wf
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# wf

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_ov_withdrawalfees_model.get_overall_withdrawal_fees

```python title='openbb_terminal/cryptocurrency/overview/withdrawalfees_model.py'
def get_overall_withdrawal_fees(limit: int) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/withdrawalfees_model.py#L120)

Description: Scrapes top coins withdrawal fees

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of coins to search, by default n=100, one page has 100 coins, so 1 page is scraped. | n | False |

## Returns

| Type | Description |
| ---- | ----------- |
|  | Coin, Lowest, Average, Median, Highest, Exchanges Compared |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_ov_withdrawalfees_view.display_overall_withdrawal_fees

```python title='openbb_terminal/cryptocurrency/overview/withdrawalfees_view.py'
def display_overall_withdrawal_fees(limit: int, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/overview/withdrawalfees_view.py#L18)

Description: Top coins withdrawal fees

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of coins to search | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>