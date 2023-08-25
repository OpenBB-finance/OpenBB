---
title: norm
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# norm

<Tabs>
<TabItem value="model" label="Model" default>

The distribution of returns and generate statistics on the relation to the normal curve.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/econometrics_model.py#L113)]

```python
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

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/econometrics_view.py#L129)]

```python
openbb.econometrics.norm_chart(data: pd.Series, dataset: str = "", column: str = "", plot: bool = True, export: str = "", external_axes: Optional[List[axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.Series | Series of custom data | None | False |
| dataset | str | Dataset name |  | True |
| column | str | Column for y data |  | True |
| plot | bool | Whether you wish to plot a histogram | True | True |
| export | str | Format to export data. |  | True |
| external_axes | Optional[List[plt.axes]] | External axes to plot on | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>