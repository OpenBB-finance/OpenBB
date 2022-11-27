---
title: gh
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# gh

<Tabs>
<TabItem value="model" label="Model" default>

Returns  a list of developer activity for a given coin and time interval.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/santiment_model.py#L29)]

```python
openbb.crypto.dd.gh(symbol: str, dev_activity: bool = False, interval: str = "1d", start_date: Optional[str] = None, end_date: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to check github activity | None | False |
| dev_activity | bool | Whether to filter only for development activity | False | True |
| interval | str | Interval frequency (e.g., 1d) | 1d | True |
| start_date | Optional[str] | Initial date like string (e.g., 2021-10-01) | None | True |
| end_date | Optional[str] | End date like string (e.g., 2021-10-01) | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | developer activity over time |
---



</TabItem>
<TabItem value="view" label="Chart">

Returns a list of github activity for a given coin and time interval.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/santiment_view.py#L25)]

```python
openbb.crypto.dd.gh_chart(symbol: str, start_date: Optional[str] = None, dev_activity: bool = False, end_date: Optional[str] = None, interval: str = "1d", export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to check github activity | None | False |
| dev_activity | bool | Whether to filter only for development activity | False | True |
| start_date | Optional[str] | Initial date like string (e.g., 2021-10-01) | None | True |
| end_date | Optional[str] | End date like string (e.g., 2021-10-01) | None | True |
| interval | str | Interval frequency (some possible values are: 1h, 1d, 1w) | 1d | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>