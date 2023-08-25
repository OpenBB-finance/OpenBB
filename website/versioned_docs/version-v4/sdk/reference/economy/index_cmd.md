---
title: index
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# index

<Tabs>
<TabItem value="model" label="Model" default>

Get data on selected indices over time [Source: Yahoo Finance]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/yfinance_model.py#L672)]

```python
openbb.economy.index(indices: list, interval: str = "1d", start_date: int = None, end_date: int = None, column: str = "Adj Close", returns: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| indices | list | A list of indices to get data. Available indices can be accessed through economy.available_indices(). | None | False |
| interval | str | Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo<br/>Intraday data cannot extend last 60 days | 1d | True |
| start_date | str | The starting date, format "YEAR-MONTH-DAY", i.e. 2010-12-31. | None | True |
| end_date | str | The end date, format "YEAR-MONTH-DAY", i.e. 2020-06-05. | None | True |
| column | str | Which column to load in, by default "Adjusted Close". | Adj Close | True |
| returns | bool | Flag to show cumulative returns on index | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.Dataframe | Dataframe with historical data on selected indices. |
---

## Examples

```python
from openbb_terminal.sdk import openbb
openbb.economy.available_indices()
openbb.economy.index(["^GSPC", "sp400"])
```

---



</TabItem>
<TabItem value="view" label="Chart">

Load (and show) the selected indices over time [Source: Yahoo Finance]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/yfinance_view.py#L30)]

```python
openbb.economy.index_chart(indices: list, interval: str = "1d", start_date: int = None, end_date: int = None, column: str = "Adj Close", returns: bool = False, raw: bool = False, external_axes: Optional[List[axes]] = None, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| indices | list | A list of indices you wish to load (and plot).<br/>Available indices can be accessed through economy.available_indices(). | None | False |
| interval | str | Valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo<br/>Intraday data cannot extend last 60 days | 1d | True |
| start_date | str | The starting date, format "YEAR-MONTH-DAY", i.e. 2010-12-31. | None | True |
| end_date | str | The end date, format "YEAR-MONTH-DAY", i.e. 2020-06-05. | None | True |
| column | str | Which column to load in, by default this is the Adjusted Close. | Adj Close | True |
| returns | bool | Flag to show cumulative returns on index | False | True |
| raw | bool | Whether to display the raw output. | False | True |
| external_axes | Optional[List[plt.axes]] | External axes to plot on | None | True |
| export | str | Export data to csv,json,xlsx or png,jpg,pdf,svg file |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Plots the Series. |  |
---



</TabItem>
</Tabs>