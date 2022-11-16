---
title: dwat
description: OpenBB SDK Function
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# dwat

<Tabs>
<TabItem value="model" label="Model" default>

## econometrics_regression_model.get_dwat

```python title='openbb_terminal/econometrics/regression_model.py'
def get_dwat(residual: pd.DataFrame) -> DataFrame:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/regression_model.py#L474)

Description: Calculate test statistics for Durbing Watson autocorrelation

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| residual | OLS Model | Model containing residual values. | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| Test statistic of the Durbin Watson test. | None |

## Examples



</TabItem>
<TabItem value="view" label="View">

## econometrics_regression_view.display_dwat

```python title='openbb_terminal/econometrics/regression_view.py'
def display_dwat(dependent_variable: pd.Series, residual: pd.DataFrame, plot: bool, export: str, external_axes: Optional[List[axes]]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/regression_view.py#L85)

Description: Show Durbin-Watson autocorrelation tests

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| dependent_variable | pd.Series | The dependent variable. | None | False |
| residual | OLS Model | The residual of an OLS model. | None | False |
| plot | bool | Whether to plot the residuals | None | False |
| export | str | Format to export data | None | False |
| external_axes | Optional[List[plt.axes]] | External axes to plot on | None | False |

## Returns

This function does not return anything

## Examples



</TabItem>
</Tabs>