---
title: sortino
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# sortino

<Tabs>
<TabItem value="model" label="Model" default>

## common_qa_model.get_sortino

```python title='openbb_terminal/common/quantitative_analysis/qa_model.py'
def get_sortino(data: pd.DataFrame, target_return: float, window: float, adjusted: bool) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_model.py#L563)

Description: Calculates the sortino ratio

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | selected dataframe | None | False |
| target_return | float | target return of the asset | None | False |
| window | float | length of the rolling window | None | False |
| adjusted | bool | adjust the sortino ratio | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | sortino ratio |

## Examples



</TabItem>
<TabItem value="view" label="View">

## common_qa_view.display_sortino

```python title='openbb_terminal/common/quantitative_analysis/qa_view.py'
def display_sortino(data: pd.DataFrame, target_return: float, window: float, adjusted: bool) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_view.py#L1138)

Description: Displays the sortino ratio

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | selected dataframe | None | False |
| target_return | float | target return of the asset | None | False |
| window | float | length of the rolling window | None | False |
| adjusted | bool | adjust the sortino ratio | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>