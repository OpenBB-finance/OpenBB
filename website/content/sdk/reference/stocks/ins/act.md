---
title: act
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# act

<Tabs>
<TabItem value="model" label="Model" default>

Get insider activity. [Source: Business Insider]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/insider/businessinsider_model.py#L17)]

```python
openbb.stocks.ins.act(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to get insider activity data from | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Insider activity data |
---



</TabItem>
<TabItem value="view" label="Chart">

Display insider activity. [Source: Business Insider]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/insider/businessinsider_view.py#L32)]

```python
openbb.stocks.ins.act_chart(data: pd.DataFrame, symbol: str, start_date: Optional[str] = None, interval: str = "1440min", limit: int = 10, raw: bool = False, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Stock dataframe | None | False |
| symbol | str | Due diligence ticker symbol | None | False |
| start_date | Optional[str] | Initial date (e.g., 2021-10-01). Defaults to 3 years back | None | True |
| interval | str | Stock data interval | 1440min | True |
| limit | int | Number of latest days of inside activity | 10 | True |
| raw | bool | Print to console | False | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>