---
title: trend
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# trend

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_ba_sentimentinvestor_model.get_trending

```python title='openbb_terminal/common/behavioural_analysis/sentimentinvestor_model.py'
def get_trending(start_date: str, hour: int, number: int) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/sentimentinvestor_model.py#L130)

Description: Get sentiment data on the most talked about tickers

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | str | Initial date, format YYYY-MM-DD | None | False |
| hour | int | Hour of the day in 24-hour notation (e.g. 14) | None | False |
| number | int | Number of results returned by API call
Maximum 250 per api call | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of trending data |

## Examples



</TabItem>
<TabItem value="view" label="View">

## stocks_ba_sentimentinvestor_view.display_trending

```python title='openbb_terminal/decorators.py'
def display_trending() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L147)

Description: Display most talked about tickers within

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_date | str | Initial date, format YYYY-MM-DD | None | False |
| hour | int | Hour of the day in 24-hour notation (e.g. 14) | None | False |
| number | int | Number of results returned by API call
Maximum 250 per api call | None | False |
| limit | int | Number of results display on the terminal
Default: 10 | 10 | False |
| export | str | Format to export data | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>