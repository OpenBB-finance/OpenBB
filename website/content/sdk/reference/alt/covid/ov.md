---
title: ov
description: This documentation page provides detailed information on the 'ov' models
  used for retrieving historical cases and deaths-by-country data. It also explains
  the parameters required to run these models, and returns in the form of a DataFrame.
keywords:
- docusaurus
- ov model
- historical data
- cases
- deaths
- country-specific
- dataframe
- parameters
- functions
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="alt.covid.ov - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get historical cases and deaths by country.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/alternative/covid/covid_model.py#L90)]

```python wordwrap
openbb.alt.covid.ov(country: str)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| country | str | Country to get data for | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of historical cases and deaths |
---



</TabItem>
<TabItem value="view" label="Chart">

Prints table showing historical cases and deaths by country.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/alternative/covid/covid_view.py#L156)]

```python wordwrap
openbb.alt.covid.ov_chart(country: str, raw: bool = False, limit: int = 10, export: str = "", sheet_name: Optional[str] = None, plot: bool = True, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| country | str | Country to get data for | None | False |
| raw | bool | Flag to display raw data | False | True |
| limit | int | Number of raw data to show | 10 | True |
| sheet_name | str | Optionally specify the name of the sheet the data is exported to. | None | True |
| export | str | Format to export data |  | True |
| plot | bool | Flag to display historical plot | True | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>