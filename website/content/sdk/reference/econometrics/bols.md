---
title: bols
description: The page provides detailed instructions on how to use the 'Between estimator',
  which is part of the openbb.econometrics.bols Python function. It covers parameters,
  return values, and the code to be used.
keywords:
- Between estimator
- OLS model
- Dependent variable
- Independent variable
- openbb.econometrics.bols
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics.bols - Reference | OpenBB SDK Docs" />

The between estimator is an alternative, usually less efficient estimator, can can be used to

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/regression_model.py#L314)]

```python
openbb.econometrics.bols(Y: pd.DataFrame, X: pd.DataFrame)
```

---

## Parameters

| Name | Type | Description | Default | Optional |
| ---- | ---- | ----------- | ------- | -------- |
| regression_variables | list | The regressions variables entered where the first variable is<br/>the dependent variable. | None | True |
| data | dict | A dictionary containing the datasets. | None | True |


---

## Returns

| Type | Description |
| ---- | ----------- |
| Tuple[DataFrame, Any, List[Any], Any] | The dataset used,<br/>Dependent variable,<br/>Independent variable,<br/>Between OLS model. |
---
