---
title: dwat
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# dwat

<Tabs>
<TabItem value="model" label="Model" default>

Calculate test statistics for Durbin Watson autocorrelation

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/regression_model.py#L486)]

```python
openbb.econometrics.dwat(model: statsmodels.regression.linear_model.RegressionResultsWrapper)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| model | statsmodels.regression.linear_model.RegressionResultsWrapper | Previously fit statsmodels OLS. | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| float | Test statistic of the Durbin Watson test. |
---

## Examples

```python
from openbb_terminal.sdk import openbb
df = openbb.econometrics.load("wage_panel")
Y, X = df["lwage"], df[["exper","educ"]]
model = openbb.econometrics.ols(Y,X)
durbin_watson_value = openbb.econometrics.dwat(model)
```

```
0.96
```
---



</TabItem>
<TabItem value="view" label="Chart">

Show Durbin-Watson autocorrelation tests

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/regression_view.py#L81)]

```python
openbb.econometrics.dwat_chart(model: statsmodels.regression.linear_model.RegressionResultsWrapper, dependent_variable: pd.Series, plot: bool = True, export: str = "", external_axes: Optional[List[axes]] = None)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| model | OLS Model | A fit statsmodels OLS model. | None | False |
| dependent_variable | pd.Series | The dependent variable for plotting | None | False |
| plot | bool | Whether to plot the residuals | True | True |
| export | str | Format to export data |  | True |
| external_axes | Optional[List[plt.axes]] | External axes to plot on | None | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>