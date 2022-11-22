---
title: rtps
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# rtps

<Tabs>
<TabItem value="model" label="Model" default>

Get real-time performance sector data

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/alphavantage_model.py#L19)]

```python
openbb.economy.rtps()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.Dataframe | Real-time performance data |
---



</TabItem>
<TabItem value="view" label="Chart">

Display Real-Time Performance sector. [Source: AlphaVantage]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/alphavantage_view.py#L27)]

```python
openbb.economy.rtps_chart(raw: bool = False, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| raw | bool | Output only raw data | False | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>