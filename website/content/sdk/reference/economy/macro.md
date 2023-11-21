---
title: macro
description: This Docusaurus page offers detailed resources related to the 'macro'
  function within the OpenBBTerminal Python package. It presents function parameters,
  provides source code links, and offers examples of two functions that handle querying
  macroeconomic data from the EconDB database and visualizing the received macro data.
keywords:
- docusaurus page
- metadata
- macro function
- EconDB database
- parameters
- countries
- transform
- start_date
- end_date
- symbol
- macro data
- macro chart
- raw
- econdb_model.py
- econdb_view.py
- economy
- macro parameters
- macro countries
- economical data visualization
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy.macro - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

This functions groups the data queried from the EconDB database [Source: EconDB]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/econdb_model.py#L655)]

```python
openbb.economy.macro(parameters: list = None, countries: list = None, transform: str = "", start_date: str = "1900-01-01", end_date: Optional[str] = None, symbol: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| parameters | list | The type of data you wish to download. Available parameters can be accessed through economy.macro_parameters(). | None | True |
| countries | list | The selected country or countries. Available countries can be accessed through economy.macro_countries(). | None | True |
| transform | str | The selected transform. Available transforms can be accessed through get_macro_transform(). |  | True |
| start_date | str | The starting date, format "YEAR-MONTH-DAY", i.e. 2010-12-31. | 1900-01-01 | True |
| end_date | Optional[str] | The end date, format "YEAR-MONTH-DAY", i.e. 2020-06-05. | None | True |
| symbol | str | In what currency you wish to convert all values. |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[pd.DataFrame, Dict[Any, Dict[Any, Any]], str] | A DataFrame with the requested macro data of all chosen countries,<br/>A dictionary containing the units of each country's parameter (e.g. EUR),<br/>A string denomination which can be Trillions, Billions, Millions, Thousands |
---

## Examples

```python
from openbb_terminal.sdk import openbb
macro_df = openbb.economy.macro()
```

---

</TabItem>
<TabItem value="view" label="Chart">

Show the received macro data about a company [Source: EconDB]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/econdb_view.py#L25)]

```python
openbb.economy.macro_chart(parameters: list = None, countries: list = None, transform: str = "", start_date: str = "1900-01-01", end_date: Optional[str] = None, symbol: str = "", raw: bool = False, external_axes: Optional[List[axes]] = None, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| parameters | list | The type of data you wish to display. Available parameters can be accessed through get_macro_parameters(). | None | True |
| countries | list | The selected country or countries. Available countries can be accessed through get_macro_countries(). | None | True |
| transform | str | select data transformation from:<br/>    '' - no transformation<br/>    'TPOP' - total percentage change on period,<br/>    'TOYA' - total percentage since 1 year ago,<br/>    'TUSD' - level USD,<br/>    'TPGP' - Percentage of GDP,<br/>    'TNOR' - Start = 100 |  | True |
| start_date | str | The starting date, format "YEAR-MONTH-DAY", i.e. 2010-12-31. | 1900-01-01 | True |
| end_date | Optional[str] | The end date, format "YEAR-MONTH-DAY", i.e. 2020-06-05. | None | True |
| symbol | str | In what currency you wish to convert all values. |  | True |
| raw | bool | Whether to display the raw output. | False | True |
| external_axes | Optional[List[plt.axes]] | External axes to plot on | None | True |
| export | str | Export data to csv,json,xlsx or png,jpg,pdf,svg file |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Plots the Series. |  |
---

</TabItem>
</Tabs>
