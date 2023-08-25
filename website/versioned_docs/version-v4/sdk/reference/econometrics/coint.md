---
title: coint
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# coint

<Tabs>
<TabItem value="model" label="Model" default>

Calculate cointegration tests between variable number of input series

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/econometrics_model.py#L249)]

```python
openbb.econometrics.coint(datasets: pd.Series, return_z: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| datasets | pd.Series | Input series to test cointegration for | None | False |
| return_z | bool | Flag to return the z data to plot | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Union[pd.DataFrame,Dict] | Dataframe with results of cointegration tests or a Dict of the z results |
---



</TabItem>
<TabItem value="view" label="Chart">

Estimates long-run and short-run cointegration relationship for series y and x and apply

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/econometrics_view.py#L314)]

```python
openbb.econometrics.coint_chart(datasets: pd.Series, significant: bool = False, plot: bool = True, export: str = "", external_axes: Optional[List[axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| datasets | pd.Series | Variable number of series to test for cointegration | None | False |
| significant | float | Show only companies that have p-values lower than this percentage | False | True |
| plot | bool | Whether you wish to plot the z-values of all pairs. | True | True |
| export | str | Format to export data |  | True |
| external_axes | Optional[List[plt.axes]] | External axes to plot on | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>