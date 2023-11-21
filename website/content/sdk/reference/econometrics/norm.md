---
title: norm
description: This page provides a detailed guide for testing normality in data series
  using Python with a graphical representation of normal distribution. It also explains
  how to export data and use external axes for plotting.
keywords:
- Econometrics
- OpenBB-finance
- Data normality test
- Timeseries
- Histogram
- Data exporting
- Data plotting
- Data Science
- Statistics
- Normal distribution
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics.norm - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

The distribution of returns and generate statistics on the relation to the normal curve.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/econometrics_model.py#L130)]

```python wordwrap
openbb.econometrics.norm(data: pd.Series)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.Series | A series or column of a DataFrame to test normality for | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe containing statistics of normality |
---



</TabItem>
<TabItem value="view" label="Chart">

Determine the normality of a timeseries.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/econometrics_view.py#L204)]

```python wordwrap
openbb.econometrics.norm_chart(data: pd.Series, dataset: str = "", column: str = "", plot: bool = True, export: str = "", sheet_name: Optional[str] = None, external_axes: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.Series | Series of custom data | None | False |
| dataset | str | Dataset name |  | True |
| column | str | Column for y data |  | True |
| plot | bool | Whether you wish to plot a histogram | True | True |
| sheet_name | str | Optionally specify the name of the sheet the data is exported to. | None | True |
| export | str | Format to export data. |  | True |
| external_axes | bool | Whether to return the figure object or not, by default False | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>