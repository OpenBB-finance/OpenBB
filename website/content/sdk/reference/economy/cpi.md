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

Obtain CPI data from FRED. [Source: FRED]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/fred_model.py#L306)]

```python wordwrap
openbb.economy.cpi(countries: list, units: str = "growth_same", frequency: str = "monthly", harmonized: bool = False, smart_select: bool = True, options: bool = False, start_date: Optional[str] = None, end_date: Optional[str] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| countries | list | The country or countries you want to see. | None | False |
| units | str | The units you want to see, can be "growth_previous", "growth_same" or "index_2015". | growth_same | True |
| frequency | str | The frequency you want to see, either "annual", monthly" or "quarterly". | monthly | True |
| harmonized | bool | Whether you wish to obtain harmonized data. | False | True |
| smart_select | bool | Whether to assist with the selection. | True | True |
| options | bool | Whether to return the options. | False | True |
| start_date | Optional[str] | Start date, formatted YYYY-MM-DD | None | True |
| end_date | Optional[str] | End date, formatted YYYY-MM-DD | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
<TabItem value="view" label="Chart">

Inflation measured by consumer price index (CPI) is defined as the change in

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/fred_view.py#L187)]

```python wordwrap
openbb.economy.cpi_chart(countries: list, units: str = "growth_same", frequency: str = "monthly", harmonized: bool = False, smart_select: bool = True, options: bool = False, start_date: Optional[str] = None, end_date: Optional[str] = None, raw: bool = False, export: str = "", sheet_name: str = "", external_axes: bool = False, limit: int = 10)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| countries | list | List of countries to plot | None | False |
| units | str | Units of the data, either "growth_same", "growth_previous", "index_2015" | growth_same | True |
| frequency | str | Frequency of the data, either "monthly", "quarterly" or "annual" | monthly | True |
| harmonized | bool | Whether to use harmonized data | False | True |
| smart_select | bool | Whether to automatically select the best series | True | True |
| options | bool | Whether to show options | False | True |
| start_date | Optional[str] | Start date, formatted YYYY-MM-DD | None | True |
| end_date | Optional[str] | End date, formatted YYYY-MM-DD | None | True |
| raw | bool | Show raw data | False | True |
| export | str | Export data to csv or excel file |  | True |
| sheet_name | str | Name of the sheet to export to |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>