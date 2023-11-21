---
title: gdp
description: This page provides in-depth documentation about the 'gdp' function in
  the openbb economy package. It details how to retrieve real GDP data for the U.S.
  on a yearly or quarterly basis, and how to produce a chart visualizing this data.
keywords:
- economy
- gdp
- data retrieval
- visualization
- API documentation
- yearly data
- quarterly data
- AlphaVantage
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy.gdp - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get annual or quarterly Real GDP for US

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/alphavantage_model.py#L44)]

```python
openbb.economy.gdp(interval: str = "q", start_year: int = 2010)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| interval | str | Interval for GDP, by default "a" for annual, by default "q" | q | True |
| start_year | int | Start year for plot, by default 2010 | 2010 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of GDP |
---

</TabItem>
<TabItem value="view" label="Chart">

Display US GDP from AlphaVantage

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/alphavantage_view.py#L88)]

```python
openbb.economy.gdp_chart(interval: str = "q", start_year: int = 2010, raw: bool = False, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| interval | str | Interval for GDP.  Either "a" or "q", by default "q" | q | True |
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
