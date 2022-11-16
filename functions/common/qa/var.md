---
title: var
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# var

<Tabs>
<TabItem value="model" label="Model" default>

## common_qa_model.get_var

```python title='openbb_terminal/common/quantitative_analysis/qa_model.py'
def get_var(data: pd.DataFrame, use_mean: bool, adjusted_var: bool, student_t: bool, percentile: Union[int, float], portfolio: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_model.py#L226)

Description: Gets value at risk for specified stock dataframe.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Data dataframe | None | False |
| use_mean | bool | If one should use the data mean for calculation | None | False |
| adjusted_var | bool | If one should return VaR adjusted for skew and kurtosis | None | False |
| student_t | bool | If one should use the student-t distribution | None | False |
| percentile | Union[int,float] | VaR percentile | None | False |
| portfolio | bool | If the data is a portfolio | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame with Value at Risk per percentile |

## Examples



</TabItem>
<TabItem value="view" label="View">

## common_qa_view.display_var

```python title='openbb_terminal/common/quantitative_analysis/qa_view.py'
def display_var(data: pd.DataFrame, symbol: str, use_mean: bool, adjusted_var: bool, student_t: bool, percentile: float, data_range: int, portfolio: bool) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_view.py#L1006)

Description: Displays VaR of dataframe.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.Dataframe | Data dataframe | None | False |
| use_mean | bool | if one should use the data mean return | None | False |
| symbol | str | name of the data | None | False |
| adjusted_var | bool | if one should have VaR adjusted for skew and kurtosis (Cornish-Fisher-Expansion) | None | False |
| student_t | bool | If one should use the student-t distribution | None | False |
| percentile | int | var percentile | None | False |
| data_range | int | Number of rows you want to use VaR over | None | False |
| portfolio | bool | If the data is a portfolio | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>