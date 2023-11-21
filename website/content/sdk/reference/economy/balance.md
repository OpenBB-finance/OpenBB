---
title: balance
description: General government deficit is defined as the balance of income and expenditure of government,
keywords:
- economy
- balance
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy.balance - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

General government deficit is defined as the balance of income and expenditure of government,

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/oecd_model.py#L938)]

```python wordwrap
openbb.economy.balance(countries: Optional[List[str]], start_date: Any = "", end_date: Any = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| countries | list | List of countries to get data for | None | False |
| start_date | str | Start date of data, in YYYY-MM-DD format |  | True |
| end_date | str | End date of data, in YYYY-MM-DD format |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with the balance data |
---



</TabItem>
<TabItem value="view" label="Chart">

General government balance is defined as the balance of income and expenditure of government,

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/oecd_view.py#L456)]

```python wordwrap
openbb.economy.balance_chart(countries: Optional[List[str]], start_date: str = "", end_date: str = "", raw: bool = False, export: str = "", sheet_name: str = "", external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| countries | list | List of countries to get data for | None | False |
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