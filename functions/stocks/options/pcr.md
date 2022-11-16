---
title: pcr
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# pcr

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_options_alphaquery_model.get_put_call_ratio

```python title='openbb_terminal/stocks/options/alphaquery_model.py'
def get_put_call_ratio(symbol: str, window: int, start_date: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/alphaquery_model.py#L16)

Description: Gets put call ratio over last time window [Source: AlphaQuery.com]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to look for | None | False |
| window | int | Window to consider, by default 30 | 30 | True |
| start_date | str | Start date to plot, by default last 366 days | last | True |

## Returns

This function does not return anything

## Examples



</TabItem>
<TabItem value="view" label="View">

## stocks_options_alphaquery_view.display_put_call_ratio

```python title='openbb_terminal/stocks/options/alphaquery_view.py'
def display_put_call_ratio(symbol: str, window: int, start_date: str, export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/alphaquery_view.py#L26)

Description: Display put call ratio [Source: AlphaQuery.com]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| window | int | Window length to look at, by default 30 | 30 | True |
| start_date | str | Starting date for data, by default (datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d") | None | True |
| export | str | Format to export data, by default "" | None | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>