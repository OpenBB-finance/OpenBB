---
title: mcapdom
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# mcapdom

<Tabs>
<TabItem value="model" label="Model" default>

Returns market dominance of a coin over time

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/messari_model.py#L81)]

```python
openbb.crypto.dd.mcapdom(symbol: str, interval: str = "1d", start_date: Optional[str] = None, end_date: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to check market cap dominance | None | False |
| interval | str | Interval frequency (possible values are: 5m, 15m, 30m, 1h, 1d, 1w) | 1d | True |
| start_date | Optional[str] | Initial date like string (e.g., 2021-10-01) | None | True |
| end_date | Optional[str] | End date like string (e.g., 2021-10-01) | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | market dominance percentage over time |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots market dominance of a coin over time

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/cryptocurrency/due_diligence/messari_view.py#L181)]

```python
openbb.crypto.dd.mcapdom_chart(symbol: str, start_date: Optional[str] = None, end_date: Optional[str] = None, interval: str = "1d", export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | Crypto symbol to check market cap dominance | None | False |
| start_date | Optional[str] | Initial date like string (e.g., 2021-10-01) | None | True |
| end_date | Optional[str] | End date like string (e.g., 2021-10-01) | None | True |
| interval | str | Interval frequency (possible values are: 5m, 15m, 30m, 1h, 1d, 1w) | 1d | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>