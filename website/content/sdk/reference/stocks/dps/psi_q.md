---
title: psi_q
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# psi_q

<Tabs>
<TabItem value="model" label="Model" default>

Plots the short interest of a stock. This corresponds to the

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/dark_pool_shorts/quandl_model.py#L18)]

```python
openbb.stocks.dps.psi_q(symbol: str, nyse: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | ticker to get short interest from | None | False |
| nyse | bool | data from NYSE if true, otherwise NASDAQ | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | short interest volume data |
---



</TabItem>
<TabItem value="view" label="Chart">

Plot the short interest of a stock. This corresponds to the

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/stocks/dark_pool_shorts/quandl_view.py#L96)]

```python
openbb.stocks.dps.psi_q_chart(symbol: str, nyse: bool = False, limit: int = 10, raw: bool = False, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| symbol | str | ticker to get short interest from | None | False |
| nyse | bool | data from NYSE if true, otherwise NASDAQ | False | True |
| limit | int | Number of past days to show short interest | 10 | True |
| raw | bool | Flag to print raw data instead | False | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (2 axes are expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>