---
title: ccpi
description: Inflation measured by consumer price index (CPI) is defined as the change in the prices
keywords:
- economy
- ccpi
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy.ccpi - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Inflation measured by consumer price index (CPI) is defined as the change in the prices

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/oecd_model.py#L827)]

```python wordwrap
openbb.economy.ccpi(countries: Optional[List[str]], perspective: str = "TOT", frequency: str = "Q", units: str = "AGRWTH", start_date: Any = "", end_date: Any = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| countries | list | List of countries to get data for | None | False |
| perspective | str | Perspective of CPI you wish to obtain. This can be ENRG (energy), FOOD (food),<br/>TOT (total) or TOT_FOODENRG (total excluding food and energy)<br/>Default is Total CPI. | TOT | True |
| frequency | str | Frequency to get data in. Either 'M', 'Q' or 'A.<br/>Default is Quarterly (Q). | Q | True |
| units | str | Units to get data in. Either 'AGRWTH' (annual growth rate) or IDX2015 (base = 2015).<br/>Default is Annual Growth Rate (AGRWTH). | AGRWTH | True |
| start_date | str | Start date of data, in YYYY-MM-DD format |  | True |
| end_date | str | End date of data, in YYYY-MM-DD format |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with cpi data |
---



</TabItem>
<TabItem value="view" label="Chart">

Inflation measured by consumer price index (CPI) is defined as the change in the prices

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/oecd_view.py#L347)]

```python wordwrap
openbb.economy.ccpi_chart(countries: Optional[List[str]], perspective: str = "TOT", frequency: str = "Q", units: str = "AGRWTH", start_date: str = "", end_date: str = "", raw: bool = False, export: str = "", sheet_name: str = "", external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| countries | list | List of countries to get data for | None | False |
| perspective | str | Type of CPI you wish to obtain. This can be ENRG (energy), FOOD (food),<br/>TOT (total) or TOT_FOODENRG (total excluding food and energy)<br/>Default is Total CPI. | TOT | True |
| frequency | str | Frequency to get data in. Either 'M', 'Q' or 'A.<br/>Default is Quarterly (Q). | Q | True |
| units | str | Units to get data in. Either 'AGRWTH' (annual growth rate) or IDX2015 (base = 2015).<br/>Default is Annual Growth Rate (AGRWTH). | AGRWTH | True |
| start_date | str | Start date of data, in YYYY-MM-DD format |  | True |
| end_date | str | End date of data, in YYYY-MM-DD format |  | True |
| raw | bool | Whether to display raw data in a table | False | True |
| export | str | Format to export data |  | True |
| sheet_name | str | Optionally specify the name of the sheet the data is exported to. |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Union[OpenBBFigure, None] | OpenBBFigure object if external_axes is True, else None (opens plot in a window) |
---



</TabItem>
</Tabs>