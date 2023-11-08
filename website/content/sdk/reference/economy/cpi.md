---
title: cpi
description: This page provides documentation on the cpi command within the OpenBBTerminal.
  It explains how to use the command to fetch Consumer Price Index data from Alpha
  Vantage and to display the US Consumer Price Index as a chart. It lists all parameters
  and returns for this command.
keywords:
- cpi
- consumer price index
- Alpha Vantage
- dataframe
- matplotlib
- economy
- chart
- parameters
- returns
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy.cpi - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get Consumer Price Index from Alpha Vantage

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/alphavantage_model.py#L182)]

```python
openbb.economy.cpi(interval: str = "m", start_year: int = 2010)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| interval | str | Interval for data.  Either "m" or "s" for monthly or semiannual | m | True |
| start_year | int | Start year for plot, by default 2010 | 2010 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of CPI |
---

</TabItem>
<TabItem value="view" label="Chart">

Display US consumer price index (CPI) from AlphaVantage

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/alphavantage_view.py#L257)]

```python
openbb.economy.cpi_chart(interval: str = "m", start_year: int = 2010, raw: bool = False, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| interval | str | Interval for GDP.  Either "m" or "s" | m | True |
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
