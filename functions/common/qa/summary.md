---
title: summary
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# summary

<Tabs>
<TabItem value="model" label="Model" default>

## common_qa_model.get_summary

```python title='openbb_terminal/common/quantitative_analysis/qa_model.py'
def get_summary(data: pd.DataFrame) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_model.py#L25)

Description: Print summary statistics

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe to get summary statistics for | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Summary statistics |

## Examples



</TabItem>
<TabItem value="view" label="View">

## common_qa_view.display_summary

```python title='openbb_terminal/common/quantitative_analysis/qa_view.py'
def display_summary(data: pd.DataFrame, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_view.py#L53)

Description: Show summary statistics

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | DataFrame to get statistics of | None | False |
| export | str | Format to export data | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>