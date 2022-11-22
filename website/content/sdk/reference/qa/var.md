---
title: var
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# var

<Tabs>
<TabItem value="model" label="Model" default>

Gets value at risk for specified stock dataframe.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_model.py#L224)]

```python
openbb.qa.var(data: pd.DataFrame, use_mean: bool = False, adjusted_var: bool = False, student_t: bool = False, percentile: Union[int, float] = 99.9, portfolio: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Data dataframe | None | False |
| use_mean | bool | If one should use the data mean for calculation | False | True |
| adjusted_var | bool | If one should return VaR adjusted for skew and kurtosis | False | True |
| student_t | bool | If one should use the student-t distribution | False | True |
| percentile | Union[int,float] | VaR percentile | 99.9 | True |
| portfolio | bool | If the data is a portfolio | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame with Value at Risk per percentile |
---



</TabItem>
<TabItem value="view" label="Chart">

Prints table showing VaR of dataframe.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_view.py#L1048)]

```python
openbb.qa.var_chart(data: pd.DataFrame, symbol: str = "", use_mean: bool = False, adjusted_var: bool = False, student_t: bool = False, percentile: float = 99.9, data_range: int = 0, portfolio: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.Dataframe | Data dataframe | None | False |
| use_mean | bool | if one should use the data mean return | False | True |
| symbol | str | name of the data |  | True |
| adjusted_var | bool | if one should have VaR adjusted for skew and kurtosis (Cornish-Fisher-Expansion) | False | True |
| student_t | bool | If one should use the student-t distribution | False | True |
| percentile | int | var percentile | 99.9 | True |
| data_range | int | Number of rows you want to use VaR over | 0 | True |
| portfolio | bool | If the data is a portfolio | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>