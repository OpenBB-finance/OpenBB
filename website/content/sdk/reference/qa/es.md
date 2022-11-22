---
title: es
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# es

<Tabs>
<TabItem value="model" label="Model" default>

Gets Expected Shortfall for specified stock dataframe.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_model.py#L355)]

```python
openbb.qa.es(data: pd.DataFrame, use_mean: bool = False, distribution: str = "normal", percentile: Union[float, int] = 99.9, portfolio: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Data dataframe | None | False |
| use_mean | bool | If one should use the data mean for calculation | False | True |
| distribution | str | Type of distribution, options: laplace, student_t, normal | normal | True |
| percentile | Union[float,int] | VaR percentile | 99.9 | True |
| portfolio | bool | If the data is a portfolio | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame with Expected Shortfall per percentile |
---



</TabItem>
<TabItem value="view" label="Chart">

Prints table showing expected shortfall.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_view.py#L1108)]

```python
openbb.qa.es_chart(data: pd.DataFrame, symbol: str = "", use_mean: bool = False, distribution: str = "normal", percentile: float = 99.9, portfolio: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Data dataframe | None | False |
| use_mean |  | if one should use the data mean return | False | True |
| symbol | str | name of the data |  | True |
| distribution | str | choose distribution to use: logistic, laplace, normal | normal | True |
| percentile | int | es percentile | 99.9 | True |
| portfolio | bool | If the data is a portfolio | False | True |


---

## Returns

This function does not return anything

---



</TabItem>
</Tabs>