---
title: ols
description: OpenBB SDK Function
---

# ols

## econometrics_regression_model.get_ols

```python title='openbb_terminal/econometrics/regression_model.py'
def get_ols(regression_variables: List[Tuple], data: Dict[str, pd.DataFrame], show_regression: bool, export: str) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/regression_model.py#L136)

Description: Performs an OLS regression on timeseries data. [Source: Statsmodels]

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| regression_variables | list | The regressions variables entered where the first variable is
the dependent variable. | None | False |
| data | dict | A dictionary containing the datasets. | None | False |
| show_regression | bool | Whether to show the regression results table. | None | False |
| export | str | Format to export data | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| The dataset used, the dependent variable, the independent variable and | None |

## Examples

