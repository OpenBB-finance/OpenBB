---
title: normality
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# normality

<Tabs>
<TabItem value="model" label="Model" default>

## common_qa_model.get_normality

```python title='openbb_terminal/common/quantitative_analysis/qa_model.py'
def get_normality(data: pd.DataFrame) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_model.py#L83)

Description: Look at the distribution of returns and generate statistics on the relation to the normal curve.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of targeted data | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe containing statistics of normality |

## Examples



</TabItem>
<TabItem value="view" label="View">

## common_qa_view.display_normality

```python title='openbb_terminal/common/quantitative_analysis/qa_view.py'
def display_normality(data: pd.DataFrame, target: str, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_view.py#L769)

Description: View normality statistics

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | DataFrame | None | False |
| target | str | Column in data to look at | None | False |
| export | str | Format to export data | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>