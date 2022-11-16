---
title: sharpe
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# sharpe

<Tabs>
<TabItem value="model" label="Model" default>

## common_qa_model.get_sharpe

```python title='openbb_terminal/common/quantitative_analysis/qa_model.py'
def get_sharpe(data: pd.DataFrame, rfr: float, window: float) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_model.py#L539)

Description: Calculates the sharpe ratio

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | selected dataframe column | None | False |
| rfr | float | risk free rate | None | False |
| window | float | length of the rolling window | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | sharpe ratio |

## Examples



</TabItem>
<TabItem value="view" label="View">

## common_qa_view.display_sharpe

```python title='openbb_terminal/common/quantitative_analysis/qa_view.py'
def display_sharpe(data: pd.DataFrame, rfr: float, window: float) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/qa_view.py#L1114)

Description: Calculates the sharpe ratio

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | selected dataframe column | None | False |
| rfr | float | risk free rate | None | False |
| window | float | length of the rolling window | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>