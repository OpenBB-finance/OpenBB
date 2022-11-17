---
title: spos
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# spos

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_dps_stockgrid_model.get_net_short_position

```python title='openbb_terminal/stocks/dark_pool_shorts/stockgrid_model.py'
def get_net_short_position(symbol: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/dark_pool_shorts/stockgrid_model.py#L169)

Description: Get net short position. [Source: Stockgrid]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock to get data from | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Net short position |

## Examples



</TabItem>
<TabItem value="view" label="View">

## stocks_dps_stockgrid_view.net_short_position

```python title='openbb_terminal/stocks/dark_pool_shorts/stockgrid_view.py'
def net_short_position(symbol: str, limit: int, raw: bool, export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/dark_pool_shorts/stockgrid_view.py#L249)

Description: Plot net short position. [Source: Stockgrid]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock to plot for | None | False |
| limit | int | Number of last open market days to show | None | False |
| raw | bool | Flag to print raw data instead | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (2 axes are expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>