---
title: pols
description: The page provides detailed information on using PooledOLS in OpenBB,
  a plain OLS that can comprehend various panel data structures. It includes parameters
  and return types for the 'openbb.econometrics.pols' function.
keywords:
- pols
- PooledOLS
- OLS
- panel data structures
- openbb.econometrics.pols
- regression_variables
- data
- PooledOLS model
- Dependent variable
- Independent variable
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="econometrics.pols - Reference | OpenBB SDK Docs" />

PooledOLS is just plain OLS that understands that various panel data structures.

Source Code: [[link](https://github.com/OpenBB-finance/OpenBBTerminal/tree/main/openbb_terminal/econometrics/regression_model.py#L239)]

```python
openbb.econometrics.pols(Y: pd.DataFrame, X: pd.DataFrame)
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
| Tuple[DataFrame, Any, List[Any], Any] | The dataset used,<br/>Dependent variable,<br/>Independent variable,<br/>PooledOLS model |
---
