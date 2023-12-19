---
title: re
description: This page provides a detailed look into the Random Effects Model developed
  by OpenBB. It covers the parameters involved such as regression variables and data
  sets, the return type, and a link is provided to access the source code, making
  it a valuable resource for any data scientist interested in econometrics.
keywords:
- random effects model
- regression variables
- data science
- Python code
- econometrics
- pooled OLS model
- independent variable
- dependent variable
- dataset
- github
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics.re - Reference | OpenBB SDK Docs" />

The random effects model is virtually identical to the pooled OLS model except that is accounts for the

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/regression_model.py#L276)]

```python
openbb.econometrics.re(Y: pd.DataFrame, X: pd.DataFrame)
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
| Tuple[DataFrame, Any, List[Any], Any] | The dataset used,<br/>Dependent variable,<br/>Independent variable,<br/>RandomEffects model |
---
