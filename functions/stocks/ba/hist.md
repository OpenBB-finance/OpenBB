---
title: hist
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# hist

<Tabs>
<TabItem value="model" label="Model" default>

## stocks_ba_sentimentinvestor_model.get_historical

```python title='openbb_terminal/decorators.py'
def get_historical() -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L19)

Description: Get hour-level sentiment data for the chosen symbol

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker to view sentiment data | None | False |
| start_date | str | Initial date like string or unix timestamp (e.g. 12-21-2021) | None | False |
| end_date | str | End date like string or unix timestamp (e.g. 12-21-2021) | None | False |
| number | int | Number of results returned by API call
Maximum 250 per api call | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of historical sentiment |

## Examples



</TabItem>
<TabItem value="view" label="View">

## stocks_ba_sentimentinvestor_view.display_historical

```python title='openbb_terminal/decorators.py'
def display_historical() -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/decorators.py#L30)

Description: Display historical sentiment data of a ticker,

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to view sentiment data | None | False |
| start_date | str | Initial date like string or unix timestamp (e.g. 2021-12-21) | None | False |
| end_date | str | End date like string or unix timestamp (e.g. 2022-01-15) | None | False |
| number | int | Number of results returned by API call
Maximum 250 per api call | None | False |
| raw | boolean | Whether to display raw data, by default False | False | False |
| limit | int | Number of results display on the terminal
Default: 10 | 10 | False |
| export | str | Format to export data | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (2 axes are expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>