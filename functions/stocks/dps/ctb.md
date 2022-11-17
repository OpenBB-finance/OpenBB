---
title: ctb
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# ctb

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_dps_stocksera_model.get_cost_to_borrow

```python title='openbb_terminal/stocks/dark_pool_shorts/stocksera_model.py'
def get_cost_to_borrow(symbol: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/dark_pool_shorts/stocksera_model.py#L19)

Description: Get cost to borrow of stocks [Source: Stocksera]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | ticker to get cost to borrow from | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Cost to borrow |

## Examples



</TabItem>
<TabItem value="view" label="View">

## stocks_dps_stocksera_view.plot_cost_to_borrow

```python title='openbb_terminal/stocks/dark_pool_shorts/stocksera_view.py'
def plot_cost_to_borrow(symbol: str, data: pd.DataFrame, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/dark_pool_shorts/stocksera_view.py#L30)

Description: Plots the cost to borrow of a stock. [Source: Stocksera]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | ticker to get cost to borrow from | None | False |
| data | pd.DataFrame | Cost to borrow dataframe | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (2 axes are expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>