---
title: get_regression_data
description: OpenBB SDK Function
---

# get_regression_data

This function creates a DataFrame with the required regression data as

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/regression_model.py#L112)]

```python
openbb.econometrics.get_regression_data(regression_variables: List[tuple], data: Dict[str, pd.DataFrame], regression_type: str = "")
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| regression_variables | list | The regressions variables entered where the first variable is<br/>the dependent variable. | None | False |
| data | dict | A dictionary containing the datasets. | None | False |
| regression_type | str | The type of regression that is executed. |  | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[DataFrame, Any, List[Any]] | The dataset used,<br/>Dependent variable,<br/>Independent variable,<br/>OLS model. |
---

