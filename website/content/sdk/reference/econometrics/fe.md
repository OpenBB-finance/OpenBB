---
title: fe
description: OpenBB SDK Function
---

# fe

When effects are correlated with the regressors the RE and BE estimators are not consistent.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/regression_model.py#L351)]

```python
openbb.econometrics.fe(Y: pd.DataFrame, X: pd.DataFrame, entity_effects: bool = False, time_effects: bool = False)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| regression_variables | list | The regressions variables entered where the first variable is<br/>the dependent variable. | None | True |
| data | dict | A dictionary containing the datasets. | None | True |
| entity_effects | bool | Whether to include entity effects | False | True |
| time_effects | bool | Whether to include time effects | False | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[DataFrame, Any, List[Any], Any] | The dataset used,<br/>Dependent variable,<br/>Independent variable,<br/>PanelOLS model with Fixed Effects |
---

