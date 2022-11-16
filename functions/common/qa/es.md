---
title: es
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# es

<Tabs>
<TabItem value="model" label="Model" default>

## common_qa_model.get_es

```python title='openbb_terminal/common/quantitative_analysis/qa_model.py'
def get_es(data: pd.DataFrame, use_mean: bool, distribution: str, percentile: Union[float, int], portfolio: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_model.py#L357)

Description: Gets Expected Shortfall for specified stock dataframe.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Data dataframe | None | False |
| use_mean | bool | If one should use the data mean for calculation | None | False |
| distribution | str | Type of distribution, options: laplace, student_t, normal | None | False |
| percentile | Union[float,int] | VaR percentile | None | False |
| portfolio | bool | If the data is a portfolio | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | DataFrame with Expected Shortfall per percentile |

## Examples



</TabItem>
<TabItem value="view" label="View">

## common_qa_view.display_es

```python title='openbb_terminal/common/quantitative_analysis/qa_view.py'
def display_es(data: pd.DataFrame, symbol: str, use_mean: bool, distribution: str, percentile: float, portfolio: bool) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_view.py#L1066)

Description: Displays expected shortfall.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Data dataframe | None | False |
| use_mean |  | if one should use the data mean return | None | False |
| symbol | str | name of the data | None | False |
| distribution | str | choose distribution to use: logistic, laplace, normal | None | False |
| percentile | int | es percentile | None | False |
| portfolio | bool | If the data is a portfolio | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>