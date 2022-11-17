---
title: fe
description: OpenBB SDK Function
---

# fe

## econometrics_regression_model.get_fe

```python title='openbb_terminal/econometrics/regression_model.py'
def get_fe(regression_variables: List[Tuple], data: Dict[str, pd.DataFrame], entity_effects: bool, time_effects: bool) -> None:
```
[Source Code](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/regression_model.py#L326)

Description: When effects are correlated with the regressors the RE and BE estimators are not consistent.

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| regression_variables | list | The regressions variables entered where the first variable is
the dependent variable. | None | False |
| data | dict | A dictionary containing the datasets. | None | False |
| entity_effects | bool | Whether to include entity effects | None | False |
| time_effects | bool | Whether to include time effects | None | False |

## Returns

| Type | Description |
| ---- | ----------- |
| The dataset used, the dependent variable, the independent variable and | None |

## Examples

