---
title: mentions
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# mentions

<Tabs>
<TabItem value="model" label="Model" default>

Get interest over time from google api [Source: google].

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/google_model.py#L16)]

```python
openbb.stocks.ba.mentions(symbol: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Stock ticker symbol | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of interest over time |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots weekly bars of stock's interest over time. other users watchlist. [Source: Google].

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/behavioural_analysis/google_view.py#L26)]

```python
openbb.stocks.ba.mentions_chart(symbol: str, start_date: str = "", export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Ticker symbol | None | False |
| start_date | str | Start date as YYYY-MM-DD string |  | True |
| export | str | Format to export data |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>