---
title: bpag
description: The 'bpag' page provides comprehensive information about the Breusch-Pagan
  test calculation in econometrics. The page contains source code and models for heteroscedasticity
  and regression, including parameters, return types, and export format for data.
keywords:
- bpag
- heteroscedasticity
- Breusch-Pagan Test
- OLS Model
- econometrics
- regression model
- bpag_chart
- export data
- statsmodels
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics.bpag - Reference | OpenBB SDK Docs" />

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

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
