---
title: slopes
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# slopes

<Tabs>
<TabItem value="model" label="Model" default>

Load cases and find slope over period.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/alternative/covid/covid_model.py#L173)]

```python
openbb.alt.covid.slopes(days_back: int = 30, limit: int = 50, threshold: int = 10000, ascend: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| days_back | int | Number of historical days to consider | 30 | True |
| limit | int | Number of rows to show | 50 | True |
| threshold | int | Threshold for total number of cases | 10000 | True |
| ascend | bool | Flag to sort in ascending order | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe containing slopes |
---



</TabItem>
<TabItem value="view" label="Chart">

Prints table showing countries with the highest case slopes.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/alternative/covid/covid_view.py#L220)]

```python
openbb.alt.covid.slopes_chart(days_back: int = 30, limit: int = 10, threshold: int = 10000, ascend: bool = False, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| days_back | int | Number of historical days to get slope for | 30 | True |
| limit | int | Number to show in table | 10 | True |
| ascend | bool | Flag to sort in ascending order | False | True |
| threshold | int | Threshold for total cases over period | 10000 | True |
| export | str | Format to export data |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>