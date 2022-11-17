---
title: granger
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# granger

<Tabs>
<TabItem value="model" label="Model" default>

## econometrics_model.get_granger_causality

```python title='openbb_terminal/econometrics/econometrics_model.py'
def get_granger_causality(dependent_series: Any, independent_series: Any, lags: Any) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/econometrics_model.py#L208)

Description: Calculate granger tests

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| dependent_series | Series | The series you want to test Granger Causality for. | None | False |
| independent_series | Series | The series that you want to test whether it Granger-causes time_series_y | None | False |
| lags | int | The amount of lags for the Granger test. By default, this is set to 3. | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
<TabItem value="view" label="View">

## econometrics_view.display_granger

```python title='openbb_terminal/econometrics/econometrics_view.py'
def display_granger(dependent_series: pd.Series, independent_series: pd.Series, lags: int, confidence_level: float, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/econometrics_view.py#L254)

Description: Show granger tests

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| dependent_series | Series | The series you want to test Granger Causality for. | None | False |
| independent_series | Series | The series that you want to test whether it Granger-causes dependent_series | None | False |
| lags | int | The amount of lags for the Granger test. By default, this is set to 3. | None | False |
| confidence_level | float | The confidence level you wish to use. By default, this is set to 0.05. | None | False |
| export | str | Format to export data | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>