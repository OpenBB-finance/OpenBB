---
title: fe
description: This page presents the fe function of the OpenBB Econometrics Module,
  explaining its parameters and their functionality. Here, users can find about entity
  effects, time effects, and regressors.
keywords:
- OpenBB Econometrics
- fe function
- entity effects
- time effects
- regressors
- Fixed Effects
- PanelOLS model
- regression model
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics.fe - Reference | OpenBB SDK Docs" />

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
