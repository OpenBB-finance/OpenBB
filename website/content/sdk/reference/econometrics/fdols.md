---
title: fdols
description: This documentation page provides information on First Differencing (fdols)
  - an alternative to using fixed effects when there is possible correlation. It contains
  the source code link, explanation of parameters and return details.
keywords:
- First Differencing
- fdols
- Fixed effects
- Dependent variable
- Independent variable
- Regression variables
- OLS model
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics.fdols - Reference | OpenBB SDK Docs" />

First differencing is an alternative to using fixed effects when there might be correlation.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/regression_model.py#L399)]

```python
openbb.econometrics.fdols(Y: pd.DataFrame, X: pd.DataFrame)
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
| Tuple[DataFrame, Any, List[Any], Any] | The dataset used,<br/>Dependent variable,<br/>Independent variable,<br/>First Difference OLS model |
---
