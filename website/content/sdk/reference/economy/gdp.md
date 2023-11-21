---
title: gdp
description: This page provides in-depth documentation about the 'gdp' function in
  the openbb economy package. It details how to retrieve real GDP data for the U.S.
  on a yearly or quarterly basis, and how to produce a chart visualizing this data.
keywords:
- economy
- gdp
- data retrieval
- visualization
- API documentation
- yearly data
- quarterly data
- AlphaVantage
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="economy.gdp - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Gross domestic product (GDP) is the standard measure of the value added created

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/oecd_model.py#L475)]

```python wordwrap
openbb.economy.gdp(countries: Optional[str] = "united_states", units: str = "USD", start_date: Any = "", end_date: Any = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| countries | list | List of countries to get data for | united_states | True |
| units | str | Units to get data in. Either 'USD' or 'USD_CAP'.<br/>Default is US dollars per capita. | USD | True |
| start_date | str | Start date of data, in YYYY-MM-DD format |  | True |
| end_date | str | End date of data, in YYYY-MM-DD format |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with gdp data |
---



</TabItem>
<TabItem value="view" label="Chart">

Gross domestic product (GDP) is the standard measure of the value added created

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/economy/oecd_view.py#L34)]

```python wordwrap
openbb.economy.gdp_chart(countries: Optional[str] = "united_states", units: str = "USD", start_date: str = "", end_date: str = "", raw: bool = False, export: str = "", sheet_name: str = "", external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| countries | list | List of countries to get data for | united_states | True |
| units | str | Units to get data in. Either 'USD' or 'USD_CAP'.<br/>Default is US dollars per capita. | USD | True |
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