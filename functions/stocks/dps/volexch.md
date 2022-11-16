---
title: volexch
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# volexch

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_dps_nyse_model.get_short_data_by_exchange

```python title='openbb_terminal/stocks/dark_pool_shorts/nyse_model.py'
def get_short_data_by_exchange(symbol: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/dark_pool_shorts/nyse_model.py#L15)

Description: Gets short data for 5 exchanges [https://ftp.nyse.com] starting at 1/1/2021

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker to get data for | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of short data by exchange |

## Examples



</TabItem>
<TabItem value="view" label="View">

## stocks_dps_nyse_view.display_short_by_exchange

```python title='openbb_terminal/stocks/dark_pool_shorts/nyse_view.py'
def display_short_by_exchange(symbol: str, raw: bool, sortby: str, ascend: bool, mpl: bool, export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/dark_pool_shorts/nyse_view.py#L29)

Description: Display short data by exchange

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker | None | False |
| raw | bool | Flag to display raw data | None | False |
| sortby | str | Column to sort by | None | False |
| ascend | bool | Sort in ascending order | None | False |
| mpl | bool | Display using matplotlib | None | False |
| export | str | Format  of export data | None | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>