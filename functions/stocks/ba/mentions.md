---
title: mentions
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# mentions

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_ba_google_model.get_mentions

```python title='openbb_terminal/common/behavioural_analysis/google_model.py'
def get_mentions(symbol: str) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/google_model.py#L16)

Description: Get interest over time from google api [Source: google]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of interest over time |

## Examples



</TabItem>
<TabItem value="view" label="View">

## stocks_ba_google_view.display_mentions

```python title='openbb_terminal/common/behavioural_analysis/google_view.py'
def display_mentions(symbol: str, start_date: str, export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/google_view.py#L26)

Description: Plot weekly bars of stock's interest over time. other users watchlist. [Source: Google]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol | None | False |
| start_date | str | Start date as YYYY-MM-DD string | None | False |
| export | str | Format to export data | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>