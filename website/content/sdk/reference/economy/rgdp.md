---
title: rgdp
description: Gross domestic product (GDP) is the standard measure of the value added
keywords:
- economy
- rgdp
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy.rgdp - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Gross domestic product (GDP) is the standard measure of the value added

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/oecd_model.py#L565)]

```python wordwrap
openbb.economy.rgdp(countries: Optional[List[str]], units: str = "PC_CHGPY", start_date: Any = "", end_date: Any = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| countries | list | List of countries to get data for | None | False |
| units | str | Units to get data in. Either 'PC_CHGPP', 'PC_CHGPY' or 'IDX.<br/>Default is percentage change from the same quarter of the previous year. | PC_CHGPY | True |
| start_date | str | Start date of data, in YYYY-MM-DD format |  | True |
| end_date | str | End date of data, in YYYY-MM-DD format |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with the gdp data |
---



</TabItem>
<TabItem value="view" label="Chart">

Gross domestic product (GDP) is the standard measure of the value added

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/oecd_view.py#L133)]

```python wordwrap
openbb.economy.rgdp_chart(countries: Optional[List[str]], units: str = "PC_CHGPY", start_date: str = "", end_date: str = "", raw: bool = False, export: str = "", sheet_name: str = "", external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| countries | list | List of countries to get data for | None | False |
| units | str | Units to get data in. Either 'PC_CHGPP', 'PC_CHGPY' or 'IDX.<br/>Default is percentage change from the same quarter of the previous year. | PC_CHGPY | True |
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