---
title: inf
description: 'This page discusses two main functions of the OpenBBTerminal: one for
  gathering US inflation data and the other for displaying this data in a chart. The
  model function retrieves historical inflation data from AlphaVantage and returns
  a DataFrame, while the chart function presents this data using a customizable interface.'
keywords:
- Inflation Data
- AlphaVantage
- Data Visualization
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy.inf - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get historical Inflation for United States from AlphaVantage

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/alphavantage_model.py#L139)]

```python
openbb.economy.inf(start_year: int = 2010)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_year | int | Start year for plot, by default 2010 | 2010 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame of inflation rates |
---

</TabItem>
<TabItem value="view" label="Chart">

Display US Inflation from AlphaVantage

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/alphavantage_view.py#L202)]

```python
openbb.economy.inf_chart(start_year: int = 2010, raw: bool = False, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| start_year | int | Start year for plot, by default 2010 | 2010 | True |
| raw | bool | Flag to show raw data, by default False | False | True |
| export | str | Format to export data, by default "" |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
