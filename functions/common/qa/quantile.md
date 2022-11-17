---
title: quantile
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# quantile

<Tabs>
<TabItem value="model" label="Model" default>

## common_qa_rolling_model.get_quantile

```python title='openbb_terminal/common/quantitative_analysis/rolling_model.py'
def get_quantile(data: pd.DataFrame, window: int, quantile_pct: float) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/rolling_model.py#L74)

Description: Overlay Median & Quantile

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe of targeted data | None | False |
| window | int | Length of window | None | False |
| quantile_pct | float | Quantile to display | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| pd.DataFrame | Dataframe of median prices over window |

## Examples



</TabItem>
<TabItem value="view" label="View">

## common_qa_rolling_view.display_quantile

```python title='openbb_terminal/common/quantitative_analysis/rolling_view.py'
def display_quantile(data: pd.DataFrame, target: str, symbol: str, window: int, quantile: float, export: str, external_axes: Optional[List[matplotlib.axes._axes.Axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/common/quantitative_analysis/rolling_view.py#L246)

Description: View rolling quantile

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| data | pd.DataFrame | Dataframe | None | False |
| target | str | Column in data to look at | None | False |
| symbol | str | Stock ticker | None | False |
| window | int | Length of window | None | False |
| quantile | float | Quantile to get | None | False |
| export | str | Format to export data | None | False |
| external_axes | Optional[List[plt.Axes]] | External axes (1 axis is expected in the list), by default None | None | True |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>