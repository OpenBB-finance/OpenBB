---
title: tyld
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# tyld

<Tabs>
<TabItem value="model" label="Model" default>

Get historical yield for a given maturity

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/alphavantage_model.py#L230)]

```python
openbb.economy.tyld(interval: str = "m", maturity: str = "10y", start_date: str = "2010-01-01")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| interval | str | Interval for data.  Can be "d","w","m" for daily, weekly or monthly, by default "m" | m | True |
| start_date | str | Start date for data.  Should be in YYYY-MM-DD format, by default "2010-01-01" | 2010-01-01 | True |
| maturity | str | Maturity timeline.  Can be "3mo","5y","10y" or "30y", by default "10y" | 10y | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of historical yields |
---



</TabItem>
<TabItem value="view" label="Chart">

Display historical treasury yield for given maturity

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/alphavantage_view.py#L315)]

```python
openbb.economy.tyld_chart(interval: str = "m", maturity: str = "10y", start_date: str = "2010-01-01", raw: bool = False, export: str = "", external_axes: Optional[List[matplotlib.axes._axes.Axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| interval | str | Interval for data.  Can be "d","w","m" for daily, weekly or monthly, by default "m" | m | True |
| maturity | str | Maturity timeline.  Can be "3mo","5y","10y" or "30y", by default "10y" | 10y | True |
| start_date | str | Start date for data.  Should be in YYYY-MM-DD format, by default "2010-01-01" | 2010-01-01 | True |
| raw | bool | Flag to display raw data, by default False | False | True |
| export | str | Format to export data, by default "" |  | True |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>