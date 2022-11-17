---
title: bols
description: OpenBB SDK Function
---

# bols

## econometrics_regression_model.get_bols

```python title='openbb_terminal/econometrics/regression_model.py'
def get_bols(regression_variables: List[Tuple], data: Dict[str, pd.DataFrame]) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/regression_model.py#L283)

Description: The between estimator is an alternative, usually less efficient estimator, can can be used to

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| regression_variables | list | The regressions variables entered where the first variable is
the dependent variable. | None | False |
| data | dict | A dictionary containing the datasets. | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| The dataset used, the dependent variable, the independent variable and | None |

## Examples

