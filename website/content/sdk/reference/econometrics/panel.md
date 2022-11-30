---
title: panel
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# panel

<Tabs>
<TabItem value="model" label="Model" default>

Based on the regression type, this function decides what regression to run.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/regression_model.py#L34)]

```python
openbb.econometrics.panel(Y: pd.DataFrame, X: pd.DataFrame, regression_type: str = "OLS", entity_effects: bool = False, time_effects: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| Y | pd.DataFrame | Dataframe containing the dependent variable. | None | False |
| X | pd.DataFrame | Dataframe containing the independent variables. | None | False |
| regression_type | str | The type of regression you wish to execute. | OLS | True |
| entity_effects | bool | Whether to apply Fixed Effects on entities. | False | True |
| time_effects | bool | Whether to apply Fixed Effects on time. | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Any | A regression model |
---

## Examples

```python
from openbb_terminal.sdk import openbb
df = openbb.econometrics.load("wage_panel")
df = df.set_index(["nr","year"])
X = df[["exper","educ","union"]]
Y = df["lwage"]
pooled_ols_model = openbb.econometrics.panel(Y,X,"POLS")
print(pooled_ols_model.summary)
```

```
PooledOLS Estimation Summary
================================================================================
Dep. Variable:                  lwage   R-squared:                        0.1634
Estimator:                  PooledOLS   R-squared (Between):              0.1686
No. Observations:                4360   R-squared (Within):               0.1575
Date:                Sun, Nov 13 2022   R-squared (Overall):              0.1634
Time:                        13:04:02   Log-likelihood                   -3050.4
Cov. Estimator:            Unadjusted
                                        F-statistic:                      283.68
Entities:                         545   P-value                           0.0000
Avg Obs:                       8.0000   Distribution:                  F(3,4356)
Min Obs:                       8.0000
Max Obs:                       8.0000   F-statistic (robust):             283.68
                                        P-value                           0.0000
Time periods:                       8   Distribution:                  F(3,4356)
Avg Obs:                       545.00
Min Obs:                       545.00
Max Obs:                       545.00
                            Parameter Estimates
==============================================================================
            Parameter  Std. Err.     T-stat    P-value    Lower CI    Upper CI
------------------------------------------------------------------------------
const         -0.0308     0.0620    -0.4965     0.6196     -0.1523      0.0908
exper          0.0561     0.0028     20.220     0.0000      0.0507      0.0616
educ           0.1080     0.0045     24.034     0.0000      0.0992      0.1168
union          0.1777     0.0172     10.344     0.0000      0.1441      0.2114
==============================================================================
```
---



</TabItem>
<TabItem value="view" label="Chart">

Based on the regression type, this function decides what regression to run.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/regression_view.py#L23)]

```python
openbb.econometrics.panel_chart(Y: pd.DataFrame, X: pd.DataFrame, regression_type: str = "OLS", entity_effects: bool = False, time_effects: bool = False, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | dict | A dictionary containing the datasets. | None | True |
| regression_variables | list | The regressions variables entered where the first variable is<br/>the dependent variable.<br/>each column/dataset combination. | None | True |
| regression_type | str | The type of regression you wish to execute. Choose from:<br/>OLS, POLS, RE, BOLS, FE | OLS | True |
| entity_effects | bool | Whether to apply Fixed Effects on entities. | False | True |
| time_effects | bool | Whether to apply Fixed Effects on time. | False | True |
| export | str | Format to export data |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| The dataset used, the dependent variable, the independent variable and |  |
---



</TabItem>
</Tabs>