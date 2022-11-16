---
title: omega
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# omega

<Tabs>
<TabItem value="model" label="Model" default>

## common_qa_model.get_omega

```python title='openbb_terminal/common/quantitative_analysis/qa_model.py'
def get_omega(data: pd.DataFrame, threshold_start: float, threshold_end: float) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_model.py#L638)

Description: Get the omega series

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | stock dataframe | None | False |
| threshold_start | float | annualized target return threshold start of plotted threshold range | None | False |
| threshold_end | float | annualized target return threshold end of plotted threshold range | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
<TabItem value="view" label="View">

## common_qa_view.display_omega

```python title='openbb_terminal/common/quantitative_analysis/qa_view.py'
def display_omega(data: pd.DataFrame, threshold_start: float, threshold_end: float) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_view.py#L1170)

Description: Displays the omega ratio

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | stock dataframe | None | False |
| threshold_start | float | annualized target return threshold start of plotted threshold range | None | False |
| threshold_end | float | annualized target return threshold end of plotted threshold range | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>