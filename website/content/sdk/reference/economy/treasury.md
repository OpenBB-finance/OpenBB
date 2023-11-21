---
title: treasury
description: The page provides comprehensive documentation and source code for fetching
  and visualizing U.S. treasury rates data with different options for type of treasuries,
  maturities, and data frequencies.
keywords:
- U.S. treasury rates
- EconDB
- data frequency
- treasury maturities
- economy.treasury
- economy.treasury_chart
- Data Visualization
- Source Code
- Parameters
- Returns
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy.treasury - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get treasury rates from Federal Reserve

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/fedreserve_model.py#L39)]

```python wordwrap
openbb.economy.treasury(maturity: Union[Literal['1m', '3m', '6m', '1y', '2y', '3y', '5y', '7y', '10y', '20y', '30y'], List[Literal['1m', '3m', '6m', '1y', '2y', '3y', '5y', '7y', '10y', '20y', '30y']], NoneType] = None, start_date: str = "2005-01-01", end_date: Optional[str] = "2023-11-21")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| maturity | maturityType | Maturity to get, by default all | None | True |
| start_date | str | Start date of data, by default "2005-01-01" | 2005-01-01 | True |
| end_date | str | End date , by default today | 2023-11-21 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with date as index and maturity as columns |
---

## Examples

```python
from openbb_terminal.sdk import openbb
treasury_rates = openbb.economy.treasury()
```

---



</TabItem>
<TabItem value="view" label="Chart">

Display U.S. Treasury rates [Source: EconDB]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/fedreserve_view.py#L34)]

```python wordwrap
openbb.economy.treasury_chart(maturities: Union[Literal['1m', '3m', '6m', '1y', '2y', '3y', '5y', '7y', '10y', '20y', '30y'], List[Literal['1m', '3m', '6m', '1y', '2y', '3y', '5y', '7y', '10y', '20y', '30y']]] = "1y", start_date: str = "1900-01-01", end_date: Optional[str] = "2023-11-21", raw: bool = False, external_axes: bool = False, export: str = "", sheet_name: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| maturities | list | Treasury maturities to display. | 1y | True |
| start_date | str | Starting date, format "YEAR-MONTH-DAY", i.e. 2010-12-31. | 1900-01-01 | True |
| end_date | Optional[str] | End date, format "YEAR-MONTH-DAY", i.e. 2020-06-05. | 2023-11-21 | True |
| raw | bool | Whether to display the raw output. | False | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |
| export | str | Export data to csv,json,xlsx or png,jpg,pdf,svg file |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Plots the Treasury Series. |  |
---



</TabItem>
</Tabs>