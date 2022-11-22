---
title: ov
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# ov

<Tabs>
<TabItem value="model" label="Model" default>

Get historical cases and deaths by country.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/alternative/covid/covid_model.py#L105)]

```python
openbb.alt.covid.ov(country: str, limit: int = 100)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| country | str | Country to get data for | None | False |
| limit | int | Number of raw data to show | 100 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of historical cases and deaths |
---



</TabItem>
<TabItem value="view" label="Chart">

Prints table showing historical cases and deaths by country.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/alternative/covid/covid_view.py#L131)]

```python
openbb.alt.covid.ov_chart(country: str, raw: bool = False, limit: int = 10, export: str = "", plot: bool = True)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| country | str | Country to get data for | None | False |
| raw | bool | Flag to display raw data | False | True |
| limit | int | Number of raw data to show | 10 | True |
| export | str | Format to export data |  | True |
| plot | bool | Flag to display historical plot | True | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>