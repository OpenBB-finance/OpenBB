---
title: spread
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# spread

<Tabs>
<TabItem value="model" label="Model" default>

## common_qa_rolling_model.get_spread

```python title='openbb_terminal/common/quantitative_analysis/rolling_model.py'
def get_spread(data: pd.DataFrame, window: int) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/rolling_model.py#L42)

Description: Standard Deviation and Variance

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | DataFrame of targeted data | None | False |
| window | int | Length of window | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of rolling standard deviation |

## Examples



</TabItem>
<TabItem value="view" label="View">

## common_qa_rolling_view.display_spread

```python title='openbb_terminal/common/quantitative_analysis/rolling_view.py'
def display_spread(data: pd.DataFrame, target: str, symbol: str, window: int, export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/rolling_view.py#L136)

Description: View rolling spread

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe | None | False |
| target | str | Column in data to look at | None | False |
| target | str | Column in data to look at | None | False |
| symbol | str | Stock ticker | None | False |
| window | int | Length of window | None | False |
| export | str | Format to export data | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (3 axes are expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>