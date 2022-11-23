---
title: granger
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# granger

<Tabs>
<TabItem value="model" label="Model" default>

Calculate granger tests

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/econometrics_model.py#L210)]

```python
openbb.econometrics.granger(dependent_series: pd.Series, independent_series: pd.Series, lags: int = 3)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| dependent_series | Series | The series you want to test Granger Causality for. | None | False |
| independent_series | Series | The series that you want to test whether it Granger-causes time_series_y | None | False |
| lags | int | The amount of lags for the Granger test. By default, this is set to 3. | 3 | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| dict | Dictionary containing results of Granger test |
---



</TabItem>
<TabItem value="view" label="Chart">

Show granger tests

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/econometrics_view.py#L247)]

```python
openbb.econometrics.granger_chart(dependent_series: pd.Series, independent_series: pd.Series, lags: int = 3, confidence_level: float = 0.05, export: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| dependent_series | Series | The series you want to test Granger Causality for. | None | False |
| independent_series | Series | The series that you want to test whether it Granger-causes dependent_series | None | False |
| lags | int | The amount of lags for the Granger test. By default, this is set to 3. | 3 | True |
| confidence_level | float | The confidence level you wish to use. By default, this is set to 0.05. | 0.05 | True |
| export | str | Format to export data |  | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>