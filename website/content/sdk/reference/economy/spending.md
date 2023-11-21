---
title: spending
description: General government spending provides an indication of the size
keywords:
- economy
- spending
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy.spending - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

General government spending provides an indication of the size

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/oecd_model.py#L1090)]

```python wordwrap
openbb.economy.spending(countries: Optional[List[str]], perspective: str = "TOT", units: str = "PC_GDP", start_date: Any = "", end_date: Any = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| countries | list | List of countries to get data for | None | False |
| perspective | str | The type of spending. Choose form the following:<br/>    TOT (Total)<br/>    RECULTREL (Recreation, culture and religion)<br/>    HOUCOMM (Housing and community amenities)<br/>    PUBORD (Public order and safety)<br/>    EDU (Education)<br/>    ENVPROT (Environmental protection)<br/>    GRALPUBSER (General public services)<br/>    SOCPROT (Social protection)<br/>    ECOAFF (Economic affairs)<br/>    DEF (Defence)<br/>    HEALTH (Health) | TOT | True |
| units | str | Units to get data in. Either 'PC_GDP' or 'THOUSAND_USD_PER_CAPITA'.<br/>Default is Percentage of GDP. | PC_GDP | True |
| start_date | str | Start date of data, in YYYY-MM-DD format |  | True |
| end_date | str | End date of data, in YYYY-MM-DD format |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with the spending data |
---



</TabItem>
<TabItem value="view" label="Chart">

General government spending provides an indication of the size

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/oecd_view.py#L633)]

```python wordwrap
openbb.economy.spending_chart(countries: Optional[List[str]], perspective: str = "TOT", units: str = "PC_GDP", start_date: str = "", end_date: str = "", raw: bool = False, export: str = "", sheet_name: str = "", external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| countries | list | List of countries to get data for | None | False |
| units | str | Units to get data in. Either 'PC_GDP' or 'THND_USD_CAP'.<br/>Default is Percentage of GDP. | PC_GDP | True |
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