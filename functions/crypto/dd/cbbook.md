---
title: cbbook
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# cbbook

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_dd_coinbase_model.get_order_book

```python title='openbb_terminal/cryptocurrency/due_diligence/coinbase_model.py'
def get_order_book(symbol: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/coinbase_model.py#L59)

Description: Get orders book for chosen trading pair. [Source: Coinbase]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[np.array, np.array, str, dict] | array with bid prices, order sizes and cumulative order sizes
array with ask prices, order sizes and cumulative order sizes
trading pair
dict with raw data |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_dd_coinbase_view.display_order_book

```python title='openbb_terminal/cryptocurrency/due_diligence/coinbase_view.py'
def display_order_book(symbol: str, export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/coinbase_view.py#L23)

Description: Displays a list of available currency pairs for trading. [Source: Coinbase]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Trading pair of coins on Coinbase e.g ETH-USDT or UNI-ETH | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>