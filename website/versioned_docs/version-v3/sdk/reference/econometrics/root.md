---
title: root
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# root

<Tabs>
<TabItem value="model" label="Model" default>

Calculate test statistics for unit roots

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/econometrics_model.py#L168)]

```python
openbb.econometrics.root(data: pd.Series, fuller_reg: str = "c", kpss_reg: str = "c")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.Series | Series or column of DataFrame of target variable | None | False |
| fuller_reg | str | Type of regression of ADF test | c | True |
| kpss_reg | str | Type of regression for KPSS test | c | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe with results of ADF test and KPSS test |
---



</TabItem>
<TabItem value="view" label="Chart">

Determine the normality of a timeseries.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/econometrics_view.py#L197)]

```python
openbb.econometrics.root_chart(data: pd.Series, dataset: str = "", column: str = "", fuller_reg: str = "c", kpss_reg: str = "c", export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.Series | Series of target variable | None | False |
| dataset | str | Name of the dataset |  | True |
| column | str | Name of the column |  | True |
| fuller_reg | str | Type of regression of ADF test. Choose c, ct, ctt, or nc | c | True |
| kpss_reg | str | Type of regression for KPSS test. Choose c or ct | c | True |
| export | str | Format to export data. |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>