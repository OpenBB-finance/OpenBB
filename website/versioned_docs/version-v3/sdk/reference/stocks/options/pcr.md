---
title: pcr
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# pcr

<Tabs>
<TabItem value="model" label="Model" default>

Gets put call ratio over last time window [Source: AlphaQuery.com]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/alphaquery_model.py#L17)]

```python
openbb.stocks.options.pcr(symbol: str, window: int = 30, start_date: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol to look for | None | False |
| window | int | Window to consider, by default 30 | 30 | True |
| start_date | Optional[str] | Start date to plot  (e.g., 2021-10-01), by default last 366 days | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Put call ratio |
---

## Examples

```python
from openbb_terminal.sdk import openbb
pcr_df = openbb.stocks.options.pcr("B")
```

---



</TabItem>
<TabItem value="view" label="Chart">

Display put call ratio [Source: AlphaQuery.com]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/options/alphaquery_view.py#L26)]

```python
openbb.stocks.options.pcr_chart(symbol: str, window: int = 30, start_date: str = "2021-11-24", export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |
| window | int | Window length to look at, by default 30 | 30 | True |
| start_date | str | Starting date for data, by default (datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d") | 2021-11-24 | True |
| export | str | Format to export data, by default "" |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>