---
title: corr
description: This page shares details on how to use 'corr' and 'corr_chart' functions
  of OpenBB Terminal's forecast module. The 'corr' function returns correlation for
  a given DataFrame, and 'corr_chart' function plots correlation coefficients for
  dataset features.
keywords:
- forecast module
- corr function
- correlation coefficients
- data analysis
- corr_chart function
- plot correlation coefficients
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="forecast.corr - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<Tabs>
<TabItem value="model" label="Model" default>

Returns correlation for a given df

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/forecast_model.py#L521)]

```python
openbb.forecast.corr(data: pd.DataFrame)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | The df to produce statistics for | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | The df with the new data |
---

</TabItem>
<TabItem value="view" label="Chart">

Plot correlation coefficients for dataset features

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/forecast/forecast_view.py#L170)]

```python
openbb.forecast.corr_chart(dataset: pd.DataFrame, export: str = "", external_axes: Optional[List[axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| dataset | pd.DataFrame | The dataset fore calculating correlation coefficients | None | False |
| export | str | Format to export image |  | True |
| external_axes | Optional[List[plt.axes]] | External axes to plot on | None | True |


---

## Returns

This function does not return anything

---

</TabItem>
</Tabs>
