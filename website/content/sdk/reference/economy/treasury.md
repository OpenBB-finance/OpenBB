---
title: treasury
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# treasury

<Tabs>
<TabItem value="model" label="Model" default>

Get U.S. Treasury rates [Source: EconDB]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/econdb_model.py#L736)]

```python
openbb.economy.treasury(instruments: list = None, maturities: list = None, frequency: str = "monthly", start_date: str = "1900-01-01", end_date: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| instruments | list | Type(s) of treasuries, nominal, inflation-adjusted (long term average) or secondary market.<br/>Available options can be accessed through economy.treasury_maturities(). | None | True |
| maturities | list | Treasury maturities to get. Available options can be accessed through economy.treasury_maturities(). | None | True |
| frequency | str | Frequency of the data, this can be annually, monthly, weekly or daily. | monthly | True |
| start_date | str | Starting date, format "YEAR-MONTH-DAY", i.e. 2010-12-31. | 1900-01-01 | True |
| end_date | Optional[str] | End date, format "YEAR-MONTH-DAY", i.e. 2020-06-05. | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.Dataframe | Holds data of the selected types and maturities |
---

## Examples

```python
from openbb_terminal.sdk import openbb
openbb.economy.treasury()
```

---



</TabItem>
<TabItem value="view" label="Chart">

Display U.S. Treasury rates [Source: EconDB]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/econdb_view.py#L145)]

```python
openbb.economy.treasury_chart(instruments: list = None, maturities: list = None, frequency: str = "monthly", start_date: str = "1900-01-01", end_date: Optional[str] = None, raw: bool = False, external_axes: Optional[List[axes]] = None, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| instruments | list | Type(s) of treasuries, nominal, inflation-adjusted or secondary market.<br/>Available options can be accessed through economy.treasury_maturities(). | None | True |
| maturities | list | Treasury maturities to display. Available options can be accessed through economy.treasury_maturities(). | None | True |
| frequency | str | Frequency of the data, this can be daily, weekly, monthly or annually | monthly | True |
| start_date | str | Starting date, format "YEAR-MONTH-DAY", i.e. 2010-12-31. | 1900-01-01 | True |
| end_date | Optional[str] | End date, format "YEAR-MONTH-DAY", i.e. 2020-06-05. | None | True |
| raw | bool | Whether to display the raw output. | False | True |
| external_axes | Optional[List[plt.axes]] | External axes to plot on | None | True |
| export | str | Export data to csv,json,xlsx or png,jpg,pdf,svg file |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Plots the Treasury Series. |  |
---



</TabItem>
</Tabs>