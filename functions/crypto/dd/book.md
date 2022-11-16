---
title: book
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# book

<Tabs>
<TabItem value="model" label="Model" default>

## crypto_dd_binance_model.get_order_book

```python title='openbb_terminal/decorators.py'
def get_order_book() -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L139)

Description: Get order book for currency. [Source: Binance]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| from_symbol | str | Cryptocurrency symbol | None | False |
| limit | int | Limit parameter. Adjusts the weight | None | False |
| to_symbol | str | Quote currency (what to view coin vs) | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe containing orderbook |

## Examples



</TabItem>
<TabItem value="view" label="View">

## crypto_dd_binance_view.display_order_book

```python title='openbb_terminal/cryptocurrency/due_diligence/binance_view.py'
def display_order_book(from_symbol: str, limit: int, to_symbol: str, export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/binance_view.py#L24)

Description: Get order book for currency. [Source: Binance]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| from_symbol | str | Cryptocurrency symbol | None | False |
| limit | int | Limit parameter. Adjusts the weight | None | False |
| to_symbol | str | Quote currency (what to view coin vs) | None | False |
| export | str | Export dataframe data to csv,json,xlsx | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>