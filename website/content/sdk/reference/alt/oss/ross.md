---
title: ross
description: This documentation page provides detailed information about the 'ross'
  functions of the OpenBB Terminal. These functions help to retrieve and visualize
  data about startups from the ROSS index.
keywords:
- ross function
- data retrieval
- startups data
- ROSS index
- visualization
- dataframe
- chart
- data sort
- growth line chart
- data export
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="alt.oss.ross - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Get startups from ROSS index [Source: https://runacap.com/].

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/alternative/oss/runa_model.py#L104)]

```python wordwrap
openbb.alt.oss.ross()
```

---

## Parameters

This function does not take any parameters.

---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | list of startups |
---



</TabItem>
<TabItem value="view" label="Chart">

Plots list of startups from ross index [Source: https://runacap.com/]

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/alternative/oss/runa_view.py#L21)]

```python wordwrap
openbb.alt.oss.ross_chart(limit: int = 10, sortby: str = "Stars AGR [%]", ascend: bool = False, show_chart: bool = False, show_growth: bool = True, chart_type: str = "stars", export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| limit | int | Number of startups to search | 10 | True |
| sortby | str | Key by which to sort data. Default: Stars AGR [%] | Stars AGR [%] | True |
| ascend | bool | Flag to sort data descending | False | True |
| show_chart | bool | Flag to show chart with startups | False | True |
| show_growth | bool | Flag to show growth line chart | True | True |
| chart_type | str | Chart type {stars,forks} | stars | True |
| export | str | Export dataframe data to csv,json,xlsx file |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>