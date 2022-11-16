---
title: rot
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# rot

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_dd_finnhub_model.get_rating_over_time

```python title='openbb_terminal/decorators.py'
def get_rating_over_time() -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L17)

Description: Get rating over time data. [Source: Finnhub]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to get ratings from | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Get dataframe with ratings |

## Examples



</TabItem>
<TabItem value="view" label="View">

## stocks_dd_finnhub_view.rating_over_time

```python title='openbb_terminal/decorators.py'
def rating_over_time() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L75)

Description: Rating over time (monthly). [Source: Finnhub]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| ticker | str | Ticker to get ratings from | None | False |
| limit | int | Number of last months ratings to show | None | False |
| raw | bool | Display raw data only | None | False |
| export | str | Export dataframe data to csv,json,xlsx file | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>