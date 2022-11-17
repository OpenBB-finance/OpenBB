---
title: index
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# index

<Tabs>
<TabItem value="model" label="Model" default>

## economy_yfinance_model.get_indices

```python title='openbb_terminal/economy/yfinance_model.py'
def get_indices(indices: list, interval: str, start_date: int, end_date: int, column: str, returns: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/yfinance_model.py#L670)

Description: Get data on selected indices over time [Source: Yahoo Finance]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| indices | list | A list of indices to get data. Available indices can be accessed through economy.available_indices(). | None | False |
| interval | str | Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
Intraday data cannot extend last 60 days | None | False |
| start_date | str | The starting date, format "YEAR-MONTH-DAY", i.e. 2010-12-31. | None | False |
| end_date | str | The end date, format "YEAR-MONTH-DAY", i.e. 2020-06-05. | None | False |
| column | str | Which column to load in, by default this is the Adjusted Close. | this | False |
| returns | bool | Flag to show cumulative returns on index | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.Dataframe | Dataframe with historical data on selected indices. |

## Examples



</TabItem>
<TabItem value="view" label="View">

## economy_yfinance_view.show_indices

```python title='openbb_terminal/economy/yfinance_view.py'
def show_indices(indices: list, interval: str, start_date: int, end_date: int, column: str, returns: bool, raw: bool, external_axes: Optional[List[axes]], export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/yfinance_view.py#L30)

Description: Load (and show) the selected indices over time [Source: Yahoo Finance]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| indices | list | A list of indices you wish to load (and plot).
Available indices can be accessed through economy.available_indices(). | None | False |
| interval | str | Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
Intraday data cannot extend last 60 days | None | False |
| start_date | str | The starting date, format "YEAR-MONTH-DAY", i.e. 2010-12-31. | None | False |
| end_date | str | The end date, format "YEAR-MONTH-DAY", i.e. 2020-06-05. | None | False |
| column | str | Which column to load in, by default this is the Adjusted Close. | this | False |
| returns | bool | Flag to show cumulative returns on index | None | False |
| raw | bool | Whether to display the raw output. | None | False |
| external_axes | Optional[List[plt.axes]] | External axes to plot on | None | False |
| export | str | Export data to csv,json,xlsx or png,jpg,pdf,svg file | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| Plots the Series. | None |

## Examples



</TabItem>
</Tabs>