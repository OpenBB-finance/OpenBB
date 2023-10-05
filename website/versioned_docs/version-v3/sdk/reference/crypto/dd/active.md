---
title: active
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# active

<Tabs>
<TabItem value="model" label="Model" default>

Returns active addresses of a certain symbol

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/glassnode_model.py#L311)]

```python
openbb.crypto.dd.active(symbol: str, interval: str = "24h", start_date: str = "2010-01-01", end_date: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Asset to search active addresses (e.g., BTC) | None | False |
| interval | str | Interval frequency (e.g., 24h) | 24h | True |
| start_date | str | Initial date, format YYYY-MM-DD | 2010-01-01 | True |
| end_date | str | Final date, format YYYY-MM-DD | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | active addresses over time |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots active addresses of a certain symbol over time

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/glassnode_view.py#L32)]

```python
openbb.crypto.dd.active_chart(symbol: str, start_date: str = "2010-01-01", end_date: Optional[str] = None, interval: str = "24h", export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Asset to search active addresses (e.g., BTC) | None | False |
| start_date | str | Initial date, format YYYY-MM-DD | 2010-01-01 | True |
| end_date | Optional[str] | Final date, format YYYY-MM-DD | None | True |
| interval | str | Interval frequency (possible values are: 24h, 1w, 1month) | 24h | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>