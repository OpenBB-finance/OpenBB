---
title: bpag
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# bpag

<Tabs>
<TabItem value="model" label="Model" default>

Calculate test statistics for heteroscedasticity

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/regression_model.py#L550)]

```python
openbb.econometrics.bpag(model: statsmodels.regression.linear_model.RegressionResultsWrapper)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| model | OLS Model | Model containing residual values. | None | False |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Test results from the Breusch-Pagan Test |
---



</TabItem>
<TabItem value="view" label="Chart">

Show Breusch-Pagan heteroscedasticity test

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/regression_view.py#L182)]

```python
openbb.econometrics.bpag_chart(model: statsmodels.regression.linear_model.RegressionResultsWrapper, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| model | OLS Model | OLS model that has been fit. | None | False |
| export | str | Format to export data |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>