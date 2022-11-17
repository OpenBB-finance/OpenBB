---
title: rise
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# rise

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_ba_google_model.get_rise

```python title='openbb_terminal/common/behavioural_analysis/google_model.py'
def get_rise(symbol: str, limit: int) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/google_model.py#L106)

Description: Get top rising related queries with this stock's query [Source: google]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| limit | int | Number of queries to show | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe containing rising related queries |

## Examples



</TabItem>
<TabItem value="view" label="View">

## stocks_ba_google_view.display_rise

```python title='openbb_terminal/common/behavioural_analysis/google_view.py'
def display_rise(symbol: str, limit: int, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/google_view.py#L243)

Description: Print top rising related queries with this stock's query. [Source: Google]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol | None | False |
| limit | int | Number of queries to show | None | False |
| export | str | Format to export data | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>